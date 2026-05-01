from collections.abc import Callable
from datetime import date as dt_date, datetime, time, timedelta
from typing import Any

from pydantic import BaseModel, field_validator

from market_agent.clients.mock_market import MockMarketDataClient
from market_agent.config import KST
from market_agent.models import Candidate, MarketSnapshot, PricePoint


class FinanceDataReaderDailyRow(BaseModel):
    market_date: dt_date
    close: float

    @field_validator("close")
    @classmethod
    def validate_close(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("close must be positive")
        return value


def _default_data_reader(symbol: str, start: str, end: str):
    import FinanceDataReader as fdr

    return fdr.DataReader(symbol, start, end)


def _default_stock_listing(market: str):
    import FinanceDataReader as fdr

    return fdr.StockListing(market)


class FinanceDataReaderKoreaMarketDataClient:
    source = "FinanceDataReader"
    indexes = {"KOSPI previous session": "KS11", "KOSDAQ previous session": "KQ11"}

    def __init__(
        self,
        fallback_client: MockMarketDataClient | None = None,
        data_reader: Callable[[str, str, str], Any] | None = None,
        stock_listing: Callable[[str], Any] | None = None,
        lookback_days: int = 14,
        candidate_limit: int = 30,
    ) -> None:
        self.fallback_client = fallback_client or MockMarketDataClient()
        self.data_reader = data_reader or _default_data_reader
        self.stock_listing = stock_listing or _default_stock_listing
        self.lookback_days = lookback_days
        self.candidate_limit = candidate_limit

    def get_market_context(self) -> list[MarketSnapshot]:
        return [self._get_index_snapshot(name, symbol) for name, symbol in self.indexes.items()]

    def get_candidates(self) -> list[Candidate]:
        try:
            candidates = self._get_krx_universe_candidates()
            if not candidates:
                raise ValueError("FinanceDataReader KRX universe returned no candidates")
            return candidates
        except Exception as exc:
            fallback = []
            for candidate in self.fallback_client.get_candidates():
                fallback.append(
                    Candidate(
                        **{
                            **candidate.__dict__,
                            "source": f"{candidate.source} (fallback after {self.source} universe failure: {exc})",
                            "universe_status": "fallback_used",
                        }
                    )
                )
            return fallback

    def get_intraday_prices(self, tickers: list[str]) -> list[PricePoint]:
        return self.fallback_client.get_intraday_prices(tickers)

    def _get_index_snapshot(self, name: str, symbol: str) -> MarketSnapshot:
        try:
            rows = self._fetch_daily_rows(symbol)
            if len(rows) < 2:
                raise ValueError("provider returned fewer than two daily rows")
            previous, latest = rows[-2], rows[-1]
            change_percent = (latest.close - previous.close) / previous.close * 100
            data_timestamp = datetime.combine(latest.market_date, time(15, 30), tzinfo=KST)
            return MarketSnapshot(
                name=name,
                source=self.source,
                data_timestamp=data_timestamp,
                summary=f"Previous close {latest.close:.2f} from read-only provider.",
                change_percent=change_percent,
                is_mock=False,
                market_date=latest.market_date,
            )
        except Exception as exc:
            now = datetime.now(KST)
            return MarketSnapshot(
                name=name,
                source=self.source,
                data_timestamp=now,
                summary=f"데이터 수집 실패: {exc}",
                change_percent=0.0,
                is_mock=False,
                market_date=now.date(),
                collection_failed=True,
            )

    def _fetch_daily_rows(self, symbol: str) -> list[FinanceDataReaderDailyRow]:
        end = datetime.now(KST).date()
        start = end - timedelta(days=self.lookback_days)
        frame = self.data_reader(symbol, start.isoformat(), end.isoformat())
        rows: list[FinanceDataReaderDailyRow] = []
        for index, values in frame.tail(2).iterrows():
            market_date = index.date() if hasattr(index, "date") else dt_date.fromisoformat(str(index))
            rows.append(FinanceDataReaderDailyRow(market_date=market_date, close=values["Close"]))
        return rows

    def _get_krx_universe_candidates(self) -> list[Candidate]:
        frame = self.stock_listing("KRX")
        rows = list(frame.to_dict("records")) if hasattr(frame, "to_dict") else list(frame)
        ranked_rows = sorted(rows, key=_liquidity_value, reverse=True)[: self.candidate_limit]
        fetched_at = datetime.now(KST)
        market_date = fetched_at.date()
        candidates: list[Candidate] = []
        for row in ranked_rows:
            ticker = str(row.get("Code") or row.get("Symbol") or row.get("Ticker") or "").zfill(6)
            name = str(row.get("Name") or row.get("name") or ticker)
            if not ticker or ticker == "000000":
                continue
            previous_change_pct = _float_or_none(row.get("ChagesRatio") or row.get("ChangeRate") or row.get("Change"))
            trading_value = _float_or_none(row.get("Amount") or row.get("TradingValue") or row.get("Value"))
            volume = _float_or_none(row.get("Volume"))
            asset_type = _asset_type(name, row)
            market = str(row.get("Market") or row.get("MarketId") or "KRX")
            liquidity_score = _score_by_scale(trading_value or volume or 0.0)
            move_abs = abs(previous_change_pct or 0.0)
            candidates.append(
                Candidate(
                    ticker=ticker,
                    name=name,
                    theme=_theme_for(name, asset_type),
                    catalyst=_catalyst_for(previous_change_pct, trading_value, volume),
                    valuation_note="실시간 재무/밸류에이션 미연결: 가격/유동성 기반 1차 universe 후보.",
                    quality_note="KRX universe 기반 read-only 후보. 재무 품질 평가는 아직 미반영.",
                    risk_note=_risk_for(asset_type, previous_change_pct),
                    theme_relevance=0.45 + min(0.30, liquidity_score * 0.30),
                    catalyst_strength=0.45 + min(0.25, move_abs / 20),
                    valuation=0.50,
                    quality=0.45 + min(0.30, liquidity_score * 0.30),
                    risk=min(0.85, 0.35 + move_abs / 20),
                    source=self.source,
                    data_timestamp=fetched_at,
                    market_date=market_date,
                    is_mock=False,
                    market=market,
                    asset_type=asset_type,
                    previous_close=_float_or_none(row.get("Close")),
                    previous_change_pct=previous_change_pct,
                    trading_value=trading_value,
                    volume=volume,
                    fetched_at=fetched_at,
                    universe_status="live",
                )
            )
        return candidates


def _liquidity_value(row: dict) -> float:
    return _float_or_none(row.get("Amount") or row.get("TradingValue") or row.get("Value") or row.get("Volume")) or 0.0


def _float_or_none(value) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _score_by_scale(value: float) -> float:
    if value >= 1_000_000_000_000:
        return 1.0
    if value >= 100_000_000_000:
        return 0.8
    if value >= 10_000_000_000:
        return 0.6
    if value >= 1_000_000_000:
        return 0.4
    return 0.2


def _asset_type(name: str, row: dict) -> str:
    market = str(row.get("Market") or row.get("MarketId") or "").upper()
    if "ETF" in market or any(prefix in name.upper() for prefix in ["KODEX", "TIGER", "ACE", "KBSTAR", "SOL", "KOSEF"]):
        return "etf"
    return "stock"


def _theme_for(name: str, asset_type: str) -> str:
    upper = name.upper()
    if asset_type == "etf":
        return "Market/sector ETF"
    if "에너지" in name or "정유" in name or "가스" in name:
        return "Energy/commodity sensitivity"
    if "삼성전자" in name or "하이닉스" in name:
        return "Semiconductor large-cap"
    if "현대차" in name or "기아" in name:
        return "Exporter/auto large-cap"
    if "NAVER" in upper or "카카오" in name:
        return "Platform/growth large-cap"
    return "KRX liquidity leader"


def _catalyst_for(change_pct: float | None, trading_value: float | None, volume: float | None) -> str:
    if change_pct is not None and abs(change_pct) >= 3:
        return f"전일 변동률 {change_pct:+.2f}%로 가격 반응 확인 필요."
    if trading_value or volume:
        return "KRX universe 내 유동성 상위 후보."
    return "KRX universe 기반 1차 관찰 후보."


def _risk_for(asset_type: str, change_pct: float | None) -> str:
    if change_pct is not None and abs(change_pct) >= 5:
        return "전일 변동성이 커 장중 되돌림 리스크 확인 필요."
    if asset_type == "etf":
        return "지수/섹터 방향성에 민감한 ETF 리스크."
    return "시장 risk tone과 외국인 수급 변화에 민감할 수 있음."

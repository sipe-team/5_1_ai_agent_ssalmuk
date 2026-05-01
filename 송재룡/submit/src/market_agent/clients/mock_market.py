from datetime import datetime

from market_agent.config import KST
from market_agent.models import Candidate, MarketSnapshot, PricePoint


class MockMarketDataClient:
    source = "MockMarketDataClient"

    def __init__(self, now: datetime | None = None) -> None:
        self.now = now or datetime.now(KST)

    def get_market_context(self) -> list[MarketSnapshot]:
        market_date = self.now.date()
        return [
            MarketSnapshot("KOSPI previous session", self.source, self.now, "Semiconductors led a broad rebound.", 0.82, market_date=market_date),
            MarketSnapshot("NASDAQ previous session", self.source, self.now, "AI infrastructure names outperformed overnight.", 1.14, market_date=market_date),
            MarketSnapshot("USD/KRW", self.source, self.now, "Won stabilized after recent volatility.", -0.21, market_date=market_date),
        ]

    def get_candidates(self) -> list[Candidate]:
        return [
            Candidate("005930", "Samsung Electronics", "AI semiconductors", "Memory pricing recovery", "Undemanding versus cycle recovery", "Scale leader with strong balance sheet", "Export and FX sensitivity", 0.95, 0.88, 0.70, 0.90, 0.35, self.source, self.now, market_date=self.now.date(), market="KOSPI", universe_status="mock"),
            Candidate("000660", "SK hynix", "AI semiconductors", "HBM demand remains strong", "Premium multiple but earnings upgrades", "Technology leadership in HBM", "High expectations risk", 0.98, 0.92, 0.62, 0.86, 0.45, self.source, self.now, market_date=self.now.date(), market="KOSPI", universe_status="mock"),
            Candidate("035420", "NAVER", "AI services", "Search and commerce AI integration", "Moderate valuation reset", "Dominant domestic platform", "Execution risk", 0.76, 0.68, 0.74, 0.78, 0.40, self.source, self.now, market_date=self.now.date(), market="KOSPI", universe_status="mock"),
            Candidate("373220", "LG Energy Solution", "Battery supply chain", "EV policy support headlines", "Valuation reflects weak cycle", "Global customer base", "EV demand uncertainty", 0.70, 0.64, 0.58, 0.73, 0.55, self.source, self.now, market_date=self.now.date(), market="KOSPI", universe_status="mock"),
            Candidate("069500", "KODEX 200", "Broad market beta", "Index participation if risk appetite improves", "Diversified exposure", "Liquid ETF", "Market-wide drawdown risk", 0.64, 0.57, 0.80, 0.82, 0.25, self.source, self.now, market_date=self.now.date(), market="ETF", asset_type="etf", universe_status="mock"),
            Candidate("005380", "Hyundai Motor", "Exporter value", "Shareholder return and FX tailwinds", "Attractive cash-flow yield", "Improving brand and margins", "Cyclical auto demand", 0.61, 0.62, 0.83, 0.77, 0.38, self.source, self.now, market_date=self.now.date(), market="KOSPI", universe_status="mock"),
        ]

    def get_intraday_prices(self, tickers: list[str]) -> list[PricePoint]:
        base_prices = {"005930": 78000, "000660": 176000, "035420": 184000, "373220": 385000, "069500": 37200, "005380": 251000}
        points: list[PricePoint] = []
        for index, ticker in enumerate(tickers):
            open_price = float(base_prices.get(ticker, 100000))
            latest_price = round(open_price * (1 + (index - 1) * 0.004), 2)
            points.append(PricePoint(ticker, open_price, latest_price, self.now, self.source, market_date=self.now.date()))
        return points

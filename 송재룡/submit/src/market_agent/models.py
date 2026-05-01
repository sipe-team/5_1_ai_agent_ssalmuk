from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class MarketSnapshot:
    name: str
    source: str
    data_timestamp: datetime
    summary: str
    change_percent: float
    is_mock: bool = True
    market_date: date | None = None
    collection_failed: bool = False


@dataclass(frozen=True)
class NewsItem:
    source: str
    published_at: datetime
    title: str
    summary: str
    url: str | None = None
    is_mock: bool = True
    snippet: str | None = None
    raw_keyword: str | None = None
    fetched_at: datetime | None = None
    collection_failed: bool = False


@dataclass(frozen=True)
class CleanNewsItem:
    title: str
    source: str
    published_at: datetime
    url: str | None
    snippet: str
    raw_keyword: str | None
    fetched_at: datetime | None
    category: str
    market_impact_hint: str
    priority: int
    importance_score: float
    is_mock: bool = True
    collection_failed: bool = False


@dataclass(frozen=True)
class MarketNewsInsight:
    overall_risk_tone: str
    key_market_variables: list[str]
    korea_market_implications: list[str]
    watch_points: list[str]
    data_gaps: list[str]


@dataclass(frozen=True)
class Candidate:
    ticker: str
    name: str
    theme: str
    catalyst: str
    valuation_note: str
    quality_note: str
    risk_note: str
    theme_relevance: float
    catalyst_strength: float
    valuation: float
    quality: float
    risk: float
    source: str = "MockMarketDataClient"
    data_timestamp: datetime | None = None
    market_date: date | None = None
    is_mock: bool = True
    market: str | None = None
    asset_type: str = "stock"
    previous_close: float | None = None
    previous_change_pct: float | None = None
    trading_value: float | None = None
    volume: float | None = None
    fetched_at: datetime | None = None
    universe_status: str = "mock"


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: Candidate
    score: float
    score_breakdown: dict | None = None


@dataclass(frozen=True)
class PricePoint:
    ticker: str
    open_price: float
    latest_price: float
    data_timestamp: datetime
    source: str
    is_mock: bool = True
    market_date: date | None = None

    @property
    def return_percent(self) -> float:
        if self.open_price == 0:
            return 0.0
        return (self.latest_price - self.open_price) / self.open_price * 100

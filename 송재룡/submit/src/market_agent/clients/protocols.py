from typing import Protocol

from market_agent.models import Candidate, MarketSnapshot, NewsItem, PricePoint


class MarketDataClient(Protocol):
    def get_market_context(self) -> list[MarketSnapshot]: ...

    def get_candidates(self) -> list[Candidate]: ...

    def get_intraday_prices(self, tickers: list[str]) -> list[PricePoint]: ...


class NewsClient(Protocol):
    def get_top_news(self) -> list[NewsItem]: ...


class Notifier(Protocol):
    def send_message(self, text: str) -> None: ...

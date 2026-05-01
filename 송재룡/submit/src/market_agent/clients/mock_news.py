from datetime import datetime

from market_agent.config import KST
from market_agent.models import NewsItem


class MockNewsClient:
    source = "MockNewsClient"

    def __init__(self, now: datetime | None = None) -> None:
        self.now = now or datetime.now(KST)

    def get_top_news(self) -> list[NewsItem]:
        return [
            NewsItem(self.source, self.now, "AI chip demand remains resilient", "Global chip suppliers signaled firm demand for advanced memory."),
            NewsItem(self.source, self.now, "Korea policy focus turns to shareholder returns", "Authorities continued to emphasize market reform and capital efficiency."),
            NewsItem(self.source, self.now, "US rates steady as risk assets rise", "Overnight macro tone was supportive but still data-dependent."),
        ]

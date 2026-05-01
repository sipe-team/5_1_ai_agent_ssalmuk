import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx
from pydantic import BaseModel, Field

from market_agent.config import KST
from market_agent.models import NewsItem


class NaverSearchNewsItem(BaseModel):
    title: str
    link: str | None = None
    originallink: str | None = None
    description: str = ""
    pub_date: str = Field(alias="pubDate")


class NaverSearchNewsResponse(BaseModel):
    items: list[NaverSearchNewsItem] = []


class NaverNewsClient:
    source = "Naver Search News API"
    endpoint = "https://openapi.naver.com/v1/search/news.json"

    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        query: str,
        display: int = 5,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.query = query
        self.display = display
        self.timeout_seconds = timeout_seconds

    def get_top_news(self) -> list[NewsItem]:
        fetched_at = datetime.now(KST)
        try:
            if not self.client_id or not self.client_secret:
                raise ValueError("Naver Search API credentials are required")
            response = httpx.get(
                self.endpoint,
                params={"query": self.query, "display": self.display, "sort": "date"},
                headers={"X-Naver-Client-Id": self.client_id, "X-Naver-Client-Secret": self.client_secret},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = NaverSearchNewsResponse.model_validate(response.json())
            if not payload.items:
                raise ValueError("Naver Search News API returned no items")
            return [self._normalize_item(item, fetched_at) for item in payload.items]
        except Exception as exc:
            return [
                NewsItem(
                    source=self.source,
                    published_at=fetched_at,
                    title="데이터 수집 실패",
                    summary=f"Naver 뉴스 데이터 수집 실패: {exc}",
                    is_mock=False,
                    snippet=f"Naver 뉴스 데이터 수집 실패: {exc}",
                    raw_keyword=self.query,
                    fetched_at=fetched_at,
                    collection_failed=True,
                )
            ]

    def _normalize_item(self, item: NaverSearchNewsItem, fetched_at: datetime) -> NewsItem:
        published_at = parsedate_to_datetime(item.pub_date).astimezone(KST)
        snippet = _clean_html(item.description)
        return NewsItem(
            source=self.source,
            published_at=published_at,
            title=_clean_html(item.title),
            summary=snippet,
            url=item.originallink or item.link,
            is_mock=False,
            snippet=snippet,
            raw_keyword=self.query,
            fetched_at=fetched_at,
        )


def _clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value)).strip()

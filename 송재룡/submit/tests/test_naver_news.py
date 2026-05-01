import httpx

from market_agent.clients.naver_news import NaverNewsClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self) -> None:
        return None


def test_naver_news_client_normalizes_search_response(monkeypatch) -> None:
    def fake_get(url, params, headers, timeout):
        assert url.endswith("/v1/search/news.json")
        assert params == {"query": "한국 증시", "display": 5, "sort": "date"}
        assert headers["X-Naver-Client-Id"] == "client-id"
        assert headers["X-Naver-Client-Secret"] == "client-secret"
        assert timeout == 3.0
        return FakeResponse(
            {
                "items": [
                    {
                        "title": "&lt;b&gt;한국&lt;/b&gt; 증시 상승",
                        "originallink": "https://news.example/original",
                        "link": "https://news.example/naver",
                        "description": "&lt;b&gt;코스피&lt;/b&gt;가 상승했습니다.",
                        "pubDate": "Thu, 30 Apr 2026 09:15:00 +0900",
                    }
                ]
            }
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    news = NaverNewsClient("client-id", "client-secret", "한국 증시", timeout_seconds=3.0).get_top_news()

    assert len(news) == 1
    assert news[0].title == "한국 증시 상승"
    assert news[0].source == "Naver Search News API"
    assert news[0].published_at.isoformat() == "2026-04-30T09:15:00+09:00"
    assert news[0].url == "https://news.example/original"
    assert news[0].snippet == "코스피가 상승했습니다."
    assert news[0].summary == "코스피가 상승했습니다."
    assert news[0].raw_keyword == "한국 증시"
    assert news[0].fetched_at is not None
    assert not news[0].is_mock
    assert not news[0].collection_failed


def test_naver_news_client_reports_missing_credentials_without_network(monkeypatch) -> None:
    def fake_get(url, params, headers, timeout):
        raise AssertionError("network should not be called without credentials")

    monkeypatch.setattr(httpx, "get", fake_get)

    news = NaverNewsClient(None, None, "한국 증시").get_top_news()

    assert len(news) == 1
    assert news[0].title == "데이터 수집 실패"
    assert news[0].collection_failed
    assert not news[0].is_mock
    assert "credentials are required" in news[0].summary


def test_naver_news_client_reports_http_error(monkeypatch) -> None:
    def fake_get(url, params, headers, timeout):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "get", fake_get)

    news = NaverNewsClient("client-id", "client-secret", "한국 증시").get_top_news()

    assert len(news) == 1
    assert news[0].collection_failed
    assert "Naver 뉴스 데이터 수집 실패" in news[0].summary
    assert news[0].raw_keyword == "한국 증시"

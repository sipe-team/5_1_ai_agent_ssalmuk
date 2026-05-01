from datetime import datetime

from market_agent.clients.mock_market import MockMarketDataClient
from market_agent.config import KST
from market_agent.db import Repository
from market_agent.models import NewsItem
from market_agent.pipelines import run_premarket_pipeline


class FakeNewsClient:
    def get_top_news(self) -> list[NewsItem]:
        now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
        return [NewsItem("Naver Search News API", now, "FOMC 금리 동결", "연준이 기준금리를 유지했다", is_mock=False, raw_keyword="한국 증시", fetched_at=now)]


class FakeNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_message(self, text: str) -> None:
        self.messages.append(text)


def test_premarket_pipeline_uses_cleaned_news(tmp_path) -> None:
    notifier = FakeNotifier()
    report = run_premarket_pipeline(
        MockMarketDataClient(datetime(2026, 4, 30, 8, 0, tzinfo=KST)),
        FakeNewsClient(),
        notifier,
        Repository(tmp_path / "market_agent.sqlite3"),
        datetime(2026, 4, 30, 8, 0, tzinfo=KST),
    )

    assert "프리마켓 리포트" in report
    assert "핵심 판단" in report
    assert "시장 x 뉴스 해석" in report
    assert "금리 부담" in report
    assert "이유:" in report
    assert "리스크:" in report
    assert "확인:" in report
    for raw_label in ["risk_off", "fx_risk", "geopolitical_risk", "market_flow", "risk tone", "유동성 proxy", "있음.;", "시장 시장 분위기"]:
        assert raw_label not in report
    assert notifier.messages == [report]


def test_premarket_pipeline_can_use_full_report(tmp_path) -> None:
    notifier = FakeNotifier()
    report = run_premarket_pipeline(
        MockMarketDataClient(datetime(2026, 4, 30, 8, 0, tzinfo=KST)),
        FakeNewsClient(),
        notifier,
        Repository(tmp_path / "market_agent.sqlite3"),
        datetime(2026, 4, 30, 8, 0, tzinfo=KST),
        report_mode="full",
    )

    assert report.startswith("Premarket Report")
    assert "시장 해석 요약" in report
    assert "중요도 점수:" in report

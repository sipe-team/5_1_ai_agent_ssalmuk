from datetime import datetime

from market_agent.config import KST
from market_agent.market_news_insights import build_market_news_insight
from market_agent.models import CleanNewsItem, MarketSnapshot


def market_snapshot() -> MarketSnapshot:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    return MarketSnapshot("KOSPI previous session", "FinanceDataReader", now, "Previous close", -1.0, is_mock=False, market_date=now.date())


def clean_news(title: str, snippet: str, category: str) -> CleanNewsItem:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    return CleanNewsItem(
        title=title,
        source="Naver Search News API",
        published_at=now,
        url=None,
        snippet=snippet,
        raw_keyword="한국 증시",
        fetched_at=now,
        category=category,
        market_impact_hint="참고용 영향 힌트",
        priority=1,
        importance_score=0.8,
        is_mock=False,
    )


def test_market_news_insight_marks_geopolitical_oil_news_risk_off() -> None:
    insight = build_market_news_insight([market_snapshot()], [clean_news("중동 전쟁 리스크", "고유가와 원유 공급 우려", "geopolitical")])

    assert insight.overall_risk_tone == "risk_off"
    assert "geopolitical_risk" in insight.key_market_variables
    assert "oil_price_shock" in insight.key_market_variables
    assert any("고유가" in item for item in insight.korea_market_implications)


def test_market_news_insight_adds_rate_fx_watch_point() -> None:
    insight = build_market_news_insight(
        [market_snapshot()],
        [
            clean_news("FOMC 금리 인상 우려", "미국채 금리 상승", "rates_fomc"),
            clean_news("원달러 환율 급등", "원화 약세", "fx"),
        ],
    )

    assert insight.overall_risk_tone == "mixed"
    assert "rate_fx_risk" in insight.key_market_variables
    assert any("금리, 미국채, 환율" in item for item in insight.watch_points)


def test_market_news_insight_reports_data_gaps_when_news_missing() -> None:
    insight = build_market_news_insight([market_snapshot()], [])

    assert insight.overall_risk_tone == "unclear"
    assert "news_missing" in insight.data_gaps
    assert "limited_signal" in insight.key_market_variables

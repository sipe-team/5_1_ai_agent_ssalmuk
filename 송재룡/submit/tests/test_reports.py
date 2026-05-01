from datetime import datetime

from market_agent.clients.mock_market import MockMarketDataClient
from market_agent.clients.mock_news import MockNewsClient
from market_agent.config import KST
from market_agent.models import Candidate, CleanNewsItem, MarketNewsInsight, MarketSnapshot, NewsItem, PricePoint, ScoredCandidate
from market_agent.reports import format_compact_premarket_report, format_hourly_update, format_premarket_report
from market_agent.scoring import rank_candidates


def test_premarket_report_includes_required_metadata() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)
    news_client = MockNewsClient(now)

    report = format_premarket_report(
        now,
        market_client.get_market_context(),
        news_client.get_top_news(),
        rank_candidates(market_client.get_candidates()),
    )

    assert "Premarket Report - 2026-04-30 08:00 KST" in report
    assert "Data label: MOCK" in report
    assert "source=MockMarketDataClient" in report
    assert "출처/시각: MockNewsClient / 2026-04-30 08:00 KST" in report
    assert "시장 변수 뉴스 체크" in report
    assert "News Themes" not in report
    assert "Research/watchlist only" in report
    assert "No orders are placed" in report


def test_hourly_update_formats_simulated_returns() -> None:
    now = datetime(2026, 4, 30, 10, 0, tzinfo=KST)
    report = format_hourly_update(
        now,
        [PricePoint("005930", open_price=100.0, latest_price=103.5, data_timestamp=now, source="Mock")],
    )

    assert "simulated buy at open" in report
    assert "return=+3.50%" in report
    assert "Data label: MOCK" in report


def test_premarket_report_shows_market_data_collection_failure() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    news_client = MockNewsClient(now)
    market_client = MockMarketDataClient(now)

    report = format_premarket_report(
        now,
        [MarketSnapshot("KOSPI previous session", "FinanceDataReader", now, "데이터 수집 실패: timeout", 0.0, is_mock=False, market_date=now.date(), collection_failed=True)],
        news_client.get_top_news(),
        rank_candidates(market_client.get_candidates()),
    )

    assert "Data label: MIXED" in report
    assert "KOSPI previous session: 데이터 수집 실패" in report
    assert "source=FinanceDataReader" in report
    assert "market_date=2026-04-30" in report


def test_premarket_report_shows_news_collection_failure() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)

    report = format_premarket_report(
        now,
        market_client.get_market_context(),
        [NewsItem("Naver Search News API", now, "데이터 수집 실패", "Naver 뉴스 데이터 수집 실패: timeout", is_mock=False, raw_keyword="한국 증시", fetched_at=now, collection_failed=True)],
        rank_candidates(market_client.get_candidates()),
    )

    assert "Data label: MIXED" in report
    assert "[원문 뉴스] 데이터 수집 실패" in report
    assert "관찰 포인트: 데이터 수집 실패" in report
    assert "출처/시각: Naver Search News API / 2026-04-30 08:00 KST" in report
    assert "검색어: 한국 증시" in report
    assert "수집 시각: 2026-04-30 08:00 KST" in report


def test_premarket_report_formats_cleaned_news_with_source_and_timestamp() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)

    report = format_premarket_report(
        now,
        market_client.get_market_context(),
        [
            CleanNewsItem(
                title="FOMC 금리 동결",
                source="Naver Search News API",
                published_at=now,
                url="https://news.example/fomc",
                snippet="연준이 기준금리를 유지했다",
                raw_keyword="한국 증시",
                fetched_at=now,
                category="rates_fomc",
                market_impact_hint="금리/FOMC 경로 변화가 equity discount rate와 risk appetite에 영향을 줄 수 있는 시나리오.",
                priority=1,
                importance_score=0.78,
                is_mock=False,
            )
        ],
        rank_candidates(market_client.get_candidates()),
    )

    assert "시장 변수 뉴스 체크" in report
    assert "정제된 뉴스 기반 참고용 리스크 요약" in report
    assert "[금리/통화정책] FOMC 금리 동결" in report
    assert "관찰 포인트: 연준이 기준금리를 유지했다" in report
    assert "영향 힌트: 금리/FOMC 경로 변화" in report
    assert "중요도 점수: 0.78" in report
    assert "출처/시각: Naver Search News API / 2026-04-30 08:00 KST" in report
    assert "URL: https://news.example/fomc" in report


def test_premarket_report_limits_cleaned_news_to_top_items() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)
    news = [
        CleanNewsItem(
            title=f"뉴스 {index}",
            source="Naver Search News API",
            published_at=now,
            url=None,
            snippet="시장 변수 관찰",
            raw_keyword="한국 증시",
            fetched_at=now,
            category="market",
            market_impact_hint="시장 수급과 지수 흐름을 확인할 참고용 context.",
            priority=5,
            importance_score=1.0 - index * 0.1,
            is_mock=False,
        )
        for index in range(6)
    ]

    report = format_premarket_report(now, market_client.get_market_context(), news, rank_candidates(market_client.get_candidates()))

    assert "뉴스 0" in report
    assert "뉴스 4" in report
    assert "뉴스 5" not in report


def test_compact_premarket_report_includes_section_status_and_mock_watchlist() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)
    news = [
        CleanNewsItem(
            title="FOMC 금리 동결",
            source="Naver Search News API",
            published_at=now,
            url="https://very-long.example/news/fomc?utm_source=naver&utm_medium=search",
            snippet="연준이 기준금리를 유지했다",
            raw_keyword="한국 증시",
            fetched_at=now,
            category="rates_fomc",
            market_impact_hint="금리/FOMC 경로 변화가 equity discount rate와 risk appetite에 영향을 줄 수 있는 시나리오.",
            priority=1,
            importance_score=0.78,
            is_mock=False,
        )
    ]
    insight = MarketNewsInsight("mixed", ["rate_fx_risk"], ["rate/fx 부담이 성장주에 영향을 줄 수 있는 시나리오."], ["금리와 환율 압력 관찰 필요."], [])

    report = format_compact_premarket_report(now, market_client.get_market_context(), news, rank_candidates(market_client.get_candidates()), insight)

    assert report.startswith("Premarket Compact - 2026-04-30 08:00 KST")
    assert "데이터 상태: 시장=mock / 뉴스=live / 관찰 후보=mock" in report
    assert "후보 선정은 mock 기반" in report
    assert "핵심 요약" in report
    assert "시장 데이터" in report
    assert "뉴스 변수" in report
    assert "관찰 후보" in report
    assert "출처: Naver Search News API / 2026-04-30 08:00 KST" in report
    assert "URL:" not in report
    assert "투자 권유" in report


def test_compact_premarket_report_formats_agent_content() -> None:
    from market_agent.agents.models import CandidateExplanation, CompactReportContent

    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    content = CompactReportContent(
        generated_at=now,
        data_status_line="데이터 상태: 시장=live / 뉴스=live / 관찰 후보=mock",
        candidate_basis_line="후보 선정은 mock 기반이며, 설명은 현재 시장/뉴스 context 기준입니다.",
        headline="시장 변수별 시나리오 점검이 필요합니다.",
        market_news_summary="시장 흐름과 뉴스 변수를 결합한 참고용 해석입니다.",
        market_evidence="KOSPI -1.00%, KOSDAQ -2.00%",
        news_evidence=["FOMC 금리 동결 / Naver / 2026-04-30 08:00"],
        key_market_variables=["rate_fx_risk"],
        intraday_watch_points=["금리와 환율 확인 필요."],
        candidate_explanations=[CandidateExplanation(ticker="005930", name="Samsung Electronics", is_mock=True, linked_market_variables=["rate_fx_risk"], connected_variables=["금리·환율 부담"], score_reasons=["오늘 시장 변수와 후보 민감도 매칭 반영"], watch_points=["장중 확인"], observation_reason="mock 기반 관찰 이유", today_observation_reason="오늘 관찰 이유", positive_scenario="긍정 시나리오", risk_scenario="리스크 시나리오", risks=["리스크 시나리오"], intraday_check_point="장중 확인")],
        caveats=["투자 권유가 아닙니다."],
        data_gaps=[],
    )

    report = format_compact_premarket_report(now, [], [], [], content=content)

    assert "시장 x 뉴스 해석" in report
    assert "시장 근거: KOSPI -1.00%, KOSDAQ -2.00%" in report
    assert "뉴스 근거:" in report
    assert "이유: 오늘 관찰 이유" in report
    assert "연결 변수: 금리·환율 부담" in report
    assert "점수 근거: 오늘 시장 변수와 후보 민감도 매칭 반영" in report
    assert "static_score" not in report
    assert "dynamic_context_score" not in report
    assert "리스크: 리스크 시나리오" in report
    assert "확인: 장중 확인" in report


def test_compact_premarket_report_marks_failed_section_status() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)
    failed_market = [MarketSnapshot("KOSPI previous session", "FinanceDataReader", now, "데이터 수집 실패: timeout", 0.0, is_mock=False, market_date=now.date(), collection_failed=True)]

    report = format_compact_premarket_report(now, failed_market, [], rank_candidates(market_client.get_candidates()))

    assert "데이터 상태: 시장=failed / 뉴스=failed / 관찰 후보=mock" in report
    assert "KOSPI previous session: 데이터 수집 실패" in report


def test_compact_premarket_report_marks_fallback_watchlist_status() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    market_client = MockMarketDataClient(now)
    fallback_candidates = [ScoredCandidate(Candidate(**{**item.candidate.__dict__, "universe_status": "fallback_used"}), item.score) for item in rank_candidates(market_client.get_candidates())]

    report = format_compact_premarket_report(now, market_client.get_market_context(), [], fallback_candidates)

    assert "관찰 후보=fallback" in report
    assert "후보 universe: fallback/mock" in report

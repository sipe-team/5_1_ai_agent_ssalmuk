from datetime import datetime

from market_agent.agents.candidate_context import CandidateContextAgent
from market_agent.agents.candidate_profiles import get_static_profile
from market_agent.agents.candidate_tagging import CandidateTaggingAgent
from market_agent.agents.market_data import MarketDataAgent
from market_agent.agents.models import (
    CandidateContextInput,
    CandidateTaggingInput,
    MarketDataInput,
    MarketNewsSynthesis,
    MarketNewsSynthesisInput,
    NewsContextInput,
    RiskReviewInput,
)
from market_agent.agents.news_context import NewsContextAgent
from market_agent.agents.orchestrator import PremarketAgentOrchestrator
from market_agent.agents.risk_review import RiskReviewAgent
from market_agent.agents.synthesis import MarketNewsSynthesisAgent
from market_agent.config import KST
from market_agent.models import Candidate, CleanNewsItem, MarketSnapshot, ScoredCandidate


def snapshots(change: float = -1.0) -> list[MarketSnapshot]:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    return [
        MarketSnapshot("KOSPI previous session", "FinanceDataReader", now, "Previous close", change, is_mock=False, market_date=now.date()),
        MarketSnapshot("KOSDAQ previous session", "FinanceDataReader", now, "Previous close", change, is_mock=False, market_date=now.date()),
    ]


def clean_news(title: str, category: str, score: float = 0.8) -> CleanNewsItem:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    return CleanNewsItem(title, "Naver Search News API", now, None, title, "한국 증시", now, category, "참고용 영향 힌트", 1, score, is_mock=False)


def scored_candidate() -> ScoredCandidate:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidate = Candidate("005930", "Samsung Electronics", "AI semiconductors", "Memory pricing recovery", "Valuation", "Quality", "FX sensitivity", 0.9, 0.8, 0.7, 0.8, 0.3, data_timestamp=now)
    return ScoredCandidate(candidate, 80.0)


def synthesis_with_variables(*variables: str) -> MarketNewsSynthesis:
    return MarketNewsSynthesis(overall_risk_tone="mixed", core_view="핵심 판단", market_news_connection="연결 해석", key_market_variables=list(variables), intraday_watch_points=["확인 필요"], data_gaps=[])


def test_market_data_agent_interprets_weak_kospi_kosdaq_as_risk_off() -> None:
    analysis = MarketDataAgent().run(MarketDataInput(snapshots=snapshots(-1.0)))

    assert analysis.risk_tone == "risk_off"
    assert analysis.source_status == "live"
    assert analysis.evidence


def test_news_context_agent_extracts_geopolitical_rate_fx_variables() -> None:
    analysis = NewsContextAgent().run(NewsContextInput(news=[clean_news("전쟁 리스크", "geopolitical"), clean_news("FOMC 금리", "rates_fomc"), clean_news("환율 급등", "fx")]))

    assert "geopolitical_risk" in analysis.key_variables
    assert "rate_policy_risk" in analysis.key_variables
    assert "fx_risk" in analysis.key_variables


def test_market_news_synthesis_agent_combines_market_and_news_sentence() -> None:
    market = MarketDataAgent().run(MarketDataInput(snapshots=snapshots(-1.0)))
    news = NewsContextAgent().run(NewsContextInput(news=[clean_news("전쟁 리스크", "geopolitical")]))

    synthesis = MarketNewsSynthesisAgent().run(MarketNewsSynthesisInput(market=market, news=news))

    assert synthesis.overall_risk_tone == "risk_off"
    assert "시장 분위기" in synthesis.market_news_connection
    assert synthesis.core_view


def test_candidate_context_agent_creates_candidate_explanations() -> None:
    synthesis = MarketNewsSynthesis(overall_risk_tone="mixed", core_view="핵심 판단", market_news_connection="연결 해석", key_market_variables=["rate_policy_risk"], intraday_watch_points=["금리 확인 필요"], data_gaps=[])

    explanations = CandidateContextAgent().run(CandidateContextInput(candidates=[scored_candidate()], synthesis=synthesis))

    assert explanations[0].observation_reason
    assert explanations[0].positive_scenario
    assert explanations[0].risk_scenario
    assert explanations[0].intraday_check_point
    assert explanations[0].is_mock


def test_candidate_context_agent_does_not_overstate_weak_relevance() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidate = Candidate("123456", "Unrelated Co", "Local consumer", "Catalyst", "Valuation", "Quality", "Demand risk", 0.5, 0.5, 0.5, 0.5, 0.4, data_timestamp=now, is_mock=False, universe_status="live")
    synthesis = MarketNewsSynthesis(overall_risk_tone="mixed", core_view="핵심 판단", market_news_connection="연결 해석", key_market_variables=["rate_policy_risk"], intraday_watch_points=["금리 확인 필요"], data_gaps=[])

    explanation = CandidateContextAgent().run(CandidateContextInput(candidates=[ScoredCandidate(candidate, 50.0)], synthesis=synthesis))[0]

    assert explanation.linked_market_variables == ["limited_direct_link"]
    assert "직접 연결성은 제한적" in explanation.observation_reason


def test_candidate_context_agent_uses_distinct_company_explanations() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidates = [
        ScoredCandidate(Candidate("005930", "삼성전자", "Semiconductor large-cap", "Catalyst", "Valuation", "Quality", "FX sensitivity", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 80),
        ScoredCandidate(Candidate("000660", "SK하이닉스", "Semiconductor large-cap", "Catalyst", "Valuation", "Quality", "High expectations risk", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 79),
        ScoredCandidate(Candidate("005380", "현대차", "Exporter/auto large-cap", "Catalyst", "Valuation", "Quality", "Cyclical demand", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 78),
        ScoredCandidate(Candidate("035420", "NAVER", "Platform/growth large-cap", "Catalyst", "Valuation", "Quality", "Growth valuation risk", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 77),
    ]
    synthesis = MarketNewsSynthesis(overall_risk_tone="mixed", core_view="핵심 판단", market_news_connection="연결 해석", key_market_variables=["fx_risk", "geopolitical_risk"], intraday_watch_points=["확인 필요"], data_gaps=[])

    explanations = CandidateContextAgent().run(CandidateContextInput(candidates=candidates, synthesis=synthesis))
    summaries = [item.display_summary for item in explanations]

    assert len(set(summaries)) == 4
    assert "환율 민감도 확인" in summaries[0]
    assert "지정학" in summaries[1] or "위험자산" in summaries[1]
    assert "원가/유가 리스크 확인" in summaries[2]
    assert "위험자산 선호 확인" in summaries[3]


def test_static_profile_is_anchor_not_today_reason() -> None:
    candidate = scored_candidate().candidate

    profile = get_static_profile(candidate)

    assert profile.sector == "반도체"
    assert "환율 민감도 확인" not in profile.base_sensitivity_tags
    assert profile.source == "static_profile"


def test_dynamic_tag_changes_with_market_variables() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidate = Candidate("035420", "NAVER", "Platform/growth large-cap", "Catalyst", "Valuation", "Quality", "Risk", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live")
    agent = CandidateTaggingAgent()

    fx_context = agent.run(CandidateTaggingInput(candidate=candidate, synthesis=synthesis_with_variables("fx_risk")))
    rate_context = agent.run(CandidateTaggingInput(candidate=candidate, synthesis=synthesis_with_variables("rate_policy_risk")))

    assert fx_context.dynamic_context.dynamic_tags == ["직접 연결성 제한적"]
    assert "성장주 밸류에이션 부담 확인" in rate_context.dynamic_context.dynamic_tags


def test_weak_relevance_candidate_gets_low_confidence_and_limited_link_note() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidate = Candidate("123456", "Unrelated Co", "Local consumer", "Catalyst", "Valuation", "Quality", "Risk", 0.5, 0.5, 0.5, 0.5, 0.4, data_timestamp=now, is_mock=False, universe_status="live")

    result = CandidateTaggingAgent().run(CandidateTaggingInput(candidate=candidate, synthesis=synthesis_with_variables("fx_risk")))

    assert result.static_profile.sector == "분류 미확인"
    assert result.dynamic_context.confidence <= 0.35
    assert "직접 연결성은 제한적" in result.dynamic_context.reason


def test_same_static_profile_candidates_get_duplicate_role_note() -> None:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    candidates = [
        ScoredCandidate(Candidate("005930", "삼성전자", "Semiconductor large-cap", "Catalyst", "Valuation", "Quality", "Risk", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 80),
        ScoredCandidate(Candidate("005935", "삼성전자우", "Semiconductor large-cap", "Catalyst", "Valuation", "Quality", "Risk", 0.8, 0.8, 0.5, 0.6, 0.3, data_timestamp=now, is_mock=False, universe_status="live"), 79),
    ]

    explanations = CandidateContextAgent().run(CandidateContextInput(candidates=candidates, synthesis=synthesis_with_variables("fx_risk")))

    assert "환율 민감도 확인" in explanations[0].display_summary
    assert explanations[0].display_summary != explanations[1].display_summary
    assert "역할 차이" in explanations[1].display_summary


def test_risk_review_agent_softens_investment_language() -> None:
    synthesis = MarketNewsSynthesis(overall_risk_tone="mixed", core_view="상승 확정 추천", market_news_connection="매수 유망", key_market_variables=["market_flow"], intraday_watch_points=["확인 필요"], data_gaps=[])
    explanation = CandidateContextAgent().run(CandidateContextInput(candidates=[scored_candidate()], synthesis=synthesis))[0].model_copy(update={"positive_scenario": "매수 추천 상승 확정"})

    reviewed = RiskReviewAgent().run(RiskReviewInput(synthesis=synthesis, candidate_explanations=[explanation]))

    text = reviewed.core_view + reviewed.market_news_connection + reviewed.candidate_explanations[0].positive_scenario
    assert "추천" not in text
    assert "상승 확정" not in text
    assert reviewed.caveats


def test_premarket_agent_orchestration_order() -> None:
    result = PremarketAgentOrchestrator().run(datetime(2026, 4, 30, 8, 0, tzinfo=KST), snapshots(-1.0), [clean_news("전쟁 리스크", "geopolitical")], [scored_candidate()])

    assert result.execution_order == [
        "MarketDataAgent",
        "NewsContextAgent",
        "MarketNewsSynthesisAgent",
        "CandidateContextAgent",
        "RiskReviewAgent",
        "ReportEditorAgent",
    ]
    assert result.compact_content.headline

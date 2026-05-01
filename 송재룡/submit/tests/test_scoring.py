from datetime import datetime

from market_agent.config import KST
from market_agent.models import Candidate
from market_agent.scoring import rank_candidates, score_breakdown, score_candidate


def candidate(ticker: str, relevance: float, risk: float = 0.2) -> Candidate:
    return Candidate(
        ticker=ticker,
        name=f"Name {ticker}",
        theme="Theme",
        catalyst="Catalyst",
        valuation_note="Valuation",
        quality_note="Quality",
        risk_note="Risk",
        theme_relevance=relevance,
        catalyst_strength=0.8,
        valuation=0.7,
        quality=0.9,
        risk=risk,
        data_timestamp=datetime(2026, 4, 30, 8, 0, tzinfo=KST),
    )


def test_score_candidate_uses_risk_as_penalty() -> None:
    low_risk = candidate("000001", relevance=0.8, risk=0.1)
    high_risk = candidate("000002", relevance=0.8, risk=0.9)

    assert score_candidate(low_risk) > score_candidate(high_risk)


def test_rank_candidates_is_deterministic_with_ticker_tie_break() -> None:
    ranked = rank_candidates([candidate("000002", 0.8), candidate("000001", 0.8)], limit=2)

    assert [item.candidate.ticker for item in ranked] == ["000001", "000002"]


def test_score_candidate_uses_market_news_context_for_liquid_etf() -> None:
    item = candidate("069500", 0.6)
    item = Candidate(**{**item.__dict__, "asset_type": "etf", "trading_value": 100_000_000_000, "theme": "Market/sector ETF"})

    base = score_candidate(item)
    contextual = score_candidate(item, {"market_risk_tone": "risk_off", "news_categories": ["market"], "market_variables": ["market_flow"]})

    assert contextual > base


def test_score_breakdown_separates_static_and_dynamic_context_score() -> None:
    item = candidate("005930", 0.8)
    item = Candidate(**{**item.__dict__, "theme": "Semiconductor large-cap", "market": "KOSPI"})

    breakdown = score_breakdown(item, {"market_risk_tone": "risk_off", "market_variables": ["fx_risk"], "news_categories": ["fx"]})

    assert breakdown["static_score"] > 0
    assert breakdown["dynamic_context_score"] > 0
    assert breakdown["total_score"] == round(breakdown["static_score"] + breakdown["dynamic_context_score"], 2)

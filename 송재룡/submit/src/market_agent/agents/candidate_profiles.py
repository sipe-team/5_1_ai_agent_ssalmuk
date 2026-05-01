from market_agent.agents.models import CandidateStaticProfile
from market_agent.models import Candidate


STATIC_PROFILES = {
    "005930": ("반도체", "메모리/대형 수출주", "KOSPI 대형주", ["fx_sensitive", "foreign_flow", "large_cap_defense", "semiconductor_cycle"]),
    "005935": ("반도체", "우선주/배당 선호", "KOSPI 대형주", ["fx_sensitive", "foreign_flow", "preferred_share", "large_cap_defense"]),
    "000660": ("반도체", "메모리/HBM", "KOSPI 대형주", ["growth_sensitive", "semiconductor_cycle", "foreign_flow"]),
    "005380": ("자동차", "수출/경기민감", "KOSPI 대형주", ["fx_sensitive", "oil_cost", "cyclical_demand"]),
    "000270": ("자동차", "수출/경기민감", "KOSPI 대형주", ["fx_sensitive", "oil_cost", "cyclical_demand"]),
    "035420": ("인터넷/플랫폼", "성장주/플랫폼", "KOSPI 성장주", ["rate_sensitive", "growth_valuation", "risk_appetite"]),
    "035720": ("인터넷/플랫폼", "성장주/플랫폼", "KOSPI 성장주", ["rate_sensitive", "growth_valuation", "risk_appetite"]),
    "069500": ("ETF", "KOSPI200 ETF", "지수 ETF", ["market_beta", "index_direction"]),
}


def get_static_profile(candidate: Candidate) -> CandidateStaticProfile:
    if candidate.ticker in STATIC_PROFILES:
        sector, industry, index_role, tags = STATIC_PROFILES[candidate.ticker]
        confidence = 0.9
        source = "static_profile"
    else:
        sector = "분류 미확인"
        industry = candidate.asset_type or "분류 미확인"
        index_role = candidate.market or "분류 미확인"
        tags = _fallback_tags(candidate)
        confidence = 0.35 if tags else 0.2
        source = "fallback_profile"
    return CandidateStaticProfile(
        ticker=candidate.ticker,
        name=candidate.name,
        asset_type=candidate.asset_type,
        market=candidate.market,
        sector=sector,
        industry=industry,
        index_role=index_role,
        base_sensitivity_tags=tags,
        source=source,
        confidence=confidence,
    )


def _fallback_tags(candidate: Candidate) -> list[str]:
    if candidate.asset_type == "etf":
        return ["market_beta", "index_direction"]
    if "large-cap" in candidate.theme.lower():
        return ["large_cap_defense", "foreign_flow"]
    return []

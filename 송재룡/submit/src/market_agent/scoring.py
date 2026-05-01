from market_agent.agents.candidate_profiles import get_static_profile
from market_agent.models import Candidate, ScoredCandidate


WEIGHTS = {
    "theme_relevance": 0.35,
    "catalyst_strength": 0.25,
    "valuation": 0.15,
    "quality": 0.15,
    "risk_control": 0.10,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_candidate(candidate: Candidate, score_context: dict | None = None) -> float:
    breakdown = score_breakdown(candidate, score_context)
    return breakdown["total_score"]


def _base_factor_score(candidate: Candidate) -> float:
    risk_control = 1 - _clamp(candidate.risk)
    score = (
        _clamp(candidate.theme_relevance) * WEIGHTS["theme_relevance"]
        + _clamp(candidate.catalyst_strength) * WEIGHTS["catalyst_strength"]
        + _clamp(candidate.valuation) * WEIGHTS["valuation"]
        + _clamp(candidate.quality) * WEIGHTS["quality"]
        + risk_control * WEIGHTS["risk_control"]
    )
    return round(_clamp(score) * 100, 2)


def score_breakdown(candidate: Candidate, score_context: dict | None = None) -> dict:
    static_score = _static_score(candidate)
    dynamic_context_score = _dynamic_context_score(candidate, score_context or {})
    duplicate_penalty = float((score_context or {}).get("duplicate_penalty", 0.0))
    contextual = round(_clamp((static_score + dynamic_context_score - duplicate_penalty) / 100) * 100, 2)
    return {
        "static_score": static_score,
        "dynamic_context_score": dynamic_context_score,
        "duplicate_penalty": duplicate_penalty,
        "total_score": contextual,
    }


def rank_candidates(candidates: list[Candidate], limit: int = 5, score_context: dict | None = None) -> list[ScoredCandidate]:
    profile_counts: dict[tuple[str, str], int] = {}
    scored = []
    for candidate in candidates:
        profile = get_static_profile(candidate)
        profile_key = (profile.sector, profile.index_role)
        duplicate_count = profile_counts.get(profile_key, 0) if profile.source == "static_profile" else 0
        if profile.source == "static_profile":
            profile_counts[profile_key] = duplicate_count + 1
        candidate_context = {**(score_context or {}), "duplicate_penalty": 2.0 * duplicate_count}
        breakdown = score_breakdown(candidate, candidate_context)
        scored.append(ScoredCandidate(candidate, breakdown["total_score"], breakdown))
    return sorted(scored, key=lambda item: (-item.score, item.candidate.ticker))[:limit]


def _static_score(candidate: Candidate) -> float:
    profile = get_static_profile(candidate)
    score = _base_factor_score(candidate)
    if candidate.trading_value or candidate.volume:
        score += 3.0
    if candidate.asset_type == "etf":
        score += 2.0
    if "대형주" in profile.index_role or "ETF" in profile.index_role:
        score += 1.5
    if profile.source == "fallback_profile":
        score -= 4.0
    return round(_clamp(score / 100) * 100, 2)


def _dynamic_context_score(candidate: Candidate, context: dict) -> float:
    profile = get_static_profile(candidate)
    variables = _normalized_market_variables(context)
    score = 0.0
    if "fx_risk" in variables and "fx_sensitive" in profile.base_sensitivity_tags:
        score += 2.5
    if any(item in variables for item in ["rate_policy_risk", "rate_risk"]) and "rate_sensitive" in profile.base_sensitivity_tags:
        score += 2.5
    if "geopolitical_risk" in variables and any(item in profile.base_sensitivity_tags for item in ["oil_cost", "risk_appetite"]):
        score += 2.0
    if "market_flow" in variables and "market_beta" in profile.base_sensitivity_tags:
        score += 2.0
    if context.get("market_risk_tone") == "risk_off" and "large_cap_defense" in profile.base_sensitivity_tags:
        score += 1.5
    return round(score, 2)


def _context_bonus(candidate: Candidate, context: dict) -> float:
    bonus = 0.0
    variables = set(context.get("market_variables", []))
    categories = set(context.get("news_categories", []))
    market_tone = context.get("market_risk_tone")
    if candidate.trading_value or candidate.volume:
        bonus += 0.03
    if candidate.previous_change_pct is not None and abs(candidate.previous_change_pct) <= 3:
        bonus += 0.01
    if candidate.asset_type == "etf" and (market_tone == "risk_off" or "market" in categories):
        bonus += 0.03
    if "fx" in categories and any(word in candidate.theme.lower() for word in ["exporter", "large-cap", "semiconductor"]):
        bonus += 0.02
    if "geopolitical" in categories and "market_flow" in variables and candidate.asset_type == "etf":
        bonus += 0.01
    return bonus


def _normalized_market_variables(context: dict) -> set[str]:
    variables = set(context.get("market_variables", []))
    categories = set(context.get("news_categories", []))
    category_map = {
        "fx": "fx_risk",
        "rates_fomc": "rate_policy_risk",
        "geopolitical": "geopolitical_risk",
        "financial_stress": "liquidity_stress",
        "market": "market_flow",
    }
    variables.update(category_map[item] for item in categories if item in category_map)
    return variables

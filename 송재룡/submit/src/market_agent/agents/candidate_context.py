from market_agent.agents.candidate_tagging import CandidateTaggingAgent
from market_agent.agents.models import CandidateContextInput, CandidateExplanation, CandidateTaggingInput
from market_agent.agents.presentation import theme_label, variable_labels


class CandidateContextAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client
        self.tagging_agent = CandidateTaggingAgent(llm_client)

    def run(self, input_data: CandidateContextInput) -> list[CandidateExplanation]:
        variables = input_data.synthesis.key_market_variables
        explanations: list[CandidateExplanation] = []
        seen_profile_keys: dict[tuple[str, str], int] = {}
        for item in input_data.candidates:
            candidate = item.candidate
            mock_note = "후보 선정은 mock 기반이며, " if candidate.is_mock else ""
            tagging = self.tagging_agent.run(CandidateTaggingInput(candidate=candidate, synthesis=input_data.synthesis))
            linked = tagging.dynamic_context.matched_market_variables or _linked_variables(candidate.theme, variables)
            connected = variable_labels(linked) if linked != ["limited_direct_link"] else ["직접 연결성 제한"]
            score_reasons = _score_reasons(item.score_breakdown, tagging)
            profile_key = (tagging.static_profile.sector, tagging.static_profile.index_role)
            duplicate_count = seen_profile_keys.get(profile_key, 0)
            seen_profile_keys[profile_key] = duplicate_count + 1
            display_summary = _display_summary(tagging, linked, mock_note, duplicate_count)
            check_points = _display_check_points(candidate, linked, tagging)
            risk = _risk_scenario(candidate, input_data.synthesis.overall_risk_tone, linked)
            explanations.append(
                CandidateExplanation(
                    ticker=candidate.ticker,
                    name=candidate.name,
                    is_mock=candidate.is_mock,
                    universe_status=candidate.universe_status,
                    linked_market_variables=linked,
                    static_profile_summary=f"{tagging.static_profile.sector} / {tagging.static_profile.industry}",
                    today_observation_reason=tagging.dynamic_context.reason,
                    connected_variables=connected,
                    score_reasons=score_reasons,
                    watch_points=check_points,
                    risks=[risk],
                    observation_reason=_observation_reason(candidate, linked, mock_note),
                    positive_scenario=_positive_scenario(candidate),
                    risk_scenario=risk,
                    intraday_check_point=_check_point(candidate, linked),
                    display_summary=display_summary,
                    display_check_points=check_points,
                )
            )
        return explanations


def _linked_variables(theme: str, variables: list[str]) -> list[str]:
    lowered = theme.lower()
    linked: list[str] = []
    if "market" in lowered or "beta" in lowered or "etf" in lowered:
        linked.append("market_flow")
    if any(item in variables for item in ["rate_policy_risk", "fx_risk"]):
        if any(word in lowered for word in ["exporter", "large-cap", "semiconductor", "platform", "growth"]):
            linked.extend([item for item in variables if item in ["rate_policy_risk", "fx_risk"]])
    if "geopolitical_risk" in variables:
        linked.append("geopolitical_risk")
    if "liquidity_stress" in variables and ("etf" in lowered or "large-cap" in lowered or "liquidity" in lowered):
        linked.append("liquidity_stress")
    return list(dict.fromkeys(linked)) or ["limited_direct_link"]


def _observation_reason(candidate, linked: list[str], mock_note: str) -> str:
    if linked == ["limited_direct_link"]:
        return f"{mock_note}직접 연결성은 제한적이며 가격 반응 확인용 참고 후보입니다."
    liquidity = " 거래대금/거래량도 함께 확인할 수 있습니다." if candidate.trading_value or candidate.volume else ""
    return f"{mock_note}{theme_label(candidate.theme)}와 {', '.join(variable_labels(linked))} 관찰에 연결됩니다.{liquidity}"


def _positive_scenario(candidate) -> str:
    move = f" 전일 변화 {candidate.previous_change_pct:+.2f}%" if candidate.previous_change_pct is not None else ""
    return f"{candidate.catalyst}{move} 조건이 유지되는지 확인하는 시나리오."


def _risk_scenario(candidate, tone: str, linked: list[str]) -> str:
    risk_note = _clean_risk_note(candidate.risk_note)
    if "geopolitical_risk" in linked:
        return f"{risk_note} 유가나 위험자산 선호가 약해질 경우 변동성 확대 리스크가 있습니다."
    if "fx_risk" in linked or "rate_policy_risk" in linked:
        return f"{risk_note} 금리·환율·외국인 수급 변화가 리스크 요인입니다."
    return f"{risk_note} 가격 반응 확인이 필요합니다."


def _check_point(candidate, linked: list[str]) -> str:
    if candidate.asset_type == "etf" or "market_flow" in linked:
        return "지수 방향성과 거래대금 확인 필요."
    if "fx_risk" in linked:
        return "환율과 외국인 수급 확인 필요."
    return "가격 반응과 거래량 확인 필요."


def _display_summary(tagging, linked: list[str], mock_note: str, duplicate_count: int) -> str:
    profile = tagging.static_profile
    dynamic = tagging.dynamic_context
    if dynamic.dynamic_tags == ["직접 연결성 제한적"] or linked == ["limited_direct_link"]:
        return f"{mock_note}현재 시장 변수와 직접 연결성은 제한적이며 가격 반응 확인용 후보입니다."
    duplicate_note = " 같은 성격의 후보가 이미 있어 상대강도와 역할 차이를 함께 봐야 합니다." if duplicate_count else ""
    tag_text = ", ".join(dynamic.dynamic_tags[:2])
    return f"{mock_note}{profile.index_role} 성격을 가진 {profile.sector} 후보로, 오늘은 {tag_text} 관점에서 관찰합니다.{duplicate_note}"


def _score_reasons(score_breakdown: dict | None, tagging) -> list[str]:
    reasons = []
    if score_breakdown:
        if score_breakdown.get("static_score", 0) > 0:
            reasons.append("유동성·자산유형·지수 역할 기반 기본 점수 반영")
        if score_breakdown.get("dynamic_context_score", 0) > 0:
            reasons.append("오늘 시장 변수와 후보 민감도 매칭 반영")
    reasons.extend(tagging.dynamic_context.dynamic_tags[:2])
    return list(dict.fromkeys(reasons))


def _display_check_points(candidate, linked: list[str], tagging) -> list[str]:
    profile = tagging.static_profile
    dynamic_tags = tagging.dynamic_context.dynamic_tags
    if "지수 방향성 확인" in dynamic_tags or candidate.asset_type == "etf":
        return ["KOSPI/KOSDAQ 방향", "거래대금 증가 여부"]
    if "환율 민감도 확인" in dynamic_tags:
        return ["환율 방향", "외국인 수급"]
    if "성장주 밸류에이션 부담 확인" in dynamic_tags:
        return ["금리 민감 성장주 흐름", "성장주 대비 상대강도"]
    if "원가/유가 리스크 확인" in dynamic_tags:
        return ["유가/원가 변수", f"{profile.sector} 동반 흐름"]
    if "대형주 방어력 확인" in dynamic_tags:
        return ["KOSPI 대비 상대수익률", "외국인 매매 동향"]
    if linked == ["limited_direct_link"]:
        return ["가격 반응", "거래량 변화"]
    return ["가격 반응", "거래량 변화"]


def _clean_risk_note(value: str) -> str:
    cleaned = value.replace("시장 risk tone", "시장 분위기").replace("risk tone", "시장 분위기").strip()
    cleaned = cleaned.replace("시장 분위기과", "시장 분위기와")
    cleaned = cleaned.rstrip(".; ")
    return f"{cleaned}." if cleaned else "가격 변동 리스크."

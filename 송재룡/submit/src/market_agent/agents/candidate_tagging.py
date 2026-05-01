from market_agent.agents.candidate_profiles import get_static_profile
from market_agent.agents.models import CandidateDynamicContext, CandidateTaggingInput, CandidateTaggingResult
from market_agent.agents.presentation import variable_label


class CandidateTaggingAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client

    def run(self, input_data: CandidateTaggingInput) -> CandidateTaggingResult:
        profile = get_static_profile(input_data.candidate)
        variables = input_data.synthesis.key_market_variables
        dynamic_tags: list[str] = []
        matched: list[str] = []
        evidence: list[str] = []
        data_gaps: list[str] = []
        _match("fx_risk", "fx_sensitive", "환율 민감도 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        if "rate_policy_risk" in variables or "rate_risk" in variables:
            _match("rate_policy_risk" if "rate_policy_risk" in variables else "rate_risk", "rate_sensitive", "성장주 밸류에이션 부담 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        _match("geopolitical_risk", "oil_cost", "원가/유가 리스크 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        _match("geopolitical_risk", "risk_appetite", "위험자산 선호 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        _match("geopolitical_risk", "semiconductor_cycle", "지정학/반도체 공급망 리스크 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        _match("market_flow", "market_beta", "지수 방향성 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        _match("liquidity_stress", "large_cap_defense", "대형주 방어력 확인", variables, profile.base_sensitivity_tags, dynamic_tags, matched, evidence)
        if input_data.synthesis.overall_risk_tone == "risk_off" and "large_cap_defense" in profile.base_sensitivity_tags:
            dynamic_tags.append("대형주 방어력 확인")
            matched.append("risk_off")
            evidence.append("위험 회피 환경에서 대형주 상대 방어력 확인")
        if not dynamic_tags:
            dynamic_tags = ["직접 연결성 제한적"]
            evidence = ["현재 시장 변수와 static profile 민감도의 직접 매칭이 제한적"]
            data_gaps = ["직접 연결성 제한"]
            confidence = min(0.35, profile.confidence)
            reason = "직접 연결성은 제한적이며 가격 반응 확인이 우선입니다."
        else:
            confidence = min(0.95, 0.45 + 0.15 * len(set(dynamic_tags)) + profile.confidence * 0.2)
            reason = f"{profile.sector}/{profile.industry} profile이 {', '.join(variable_label(item) for item in set(matched))}와 연결됩니다."
        return CandidateTaggingResult(
            static_profile=profile,
            dynamic_context=CandidateDynamicContext(
                ticker=input_data.candidate.ticker,
                dynamic_tags=list(dict.fromkeys(dynamic_tags)),
                matched_market_variables=list(dict.fromkeys(matched)),
                evidence=list(dict.fromkeys(evidence)),
                reason=reason,
                confidence=round(confidence, 2),
                data_gaps=data_gaps,
            ),
        )


def _match(variable: str, sensitivity: str, tag: str, variables: list[str], sensitivities: list[str], dynamic_tags: list[str], matched: list[str], evidence: list[str]) -> None:
    if variable in variables and sensitivity in sensitivities:
        dynamic_tags.append(tag)
        matched.append(variable)
        evidence.append(f"{variable_label(variable)} + {sensitivity}")

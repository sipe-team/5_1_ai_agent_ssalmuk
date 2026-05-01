from market_agent.agents.models import ReviewedPremarketNarrative, RiskReviewInput
from market_agent.agents.utils import soften_investment_language


class RiskReviewAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client

    def run(self, input_data: RiskReviewInput) -> ReviewedPremarketNarrative:
        explanations = []
        for item in input_data.candidate_explanations:
            explanations.append(
                item.model_copy(
                    update={
                        "observation_reason": soften_investment_language(item.observation_reason),
                        "positive_scenario": soften_investment_language(item.positive_scenario),
                        "risk_scenario": soften_investment_language(item.risk_scenario),
                        "intraday_check_point": soften_investment_language(item.intraday_check_point),
                    }
                )
            )
        caveats = ["본 내용은 참고용 시장 관찰 정보이며 투자 권유가 아닙니다."]
        if any(item.is_mock for item in explanations):
            caveats.append("관찰 후보는 mock 기반이며 실제 KRX universe 기반 선정이 아닙니다.")
        if input_data.synthesis.data_gaps:
            caveats.append("일부 데이터 공백이 있어 해석 강도를 낮춰야 합니다.")
        return ReviewedPremarketNarrative(
            overall_risk_tone=input_data.synthesis.overall_risk_tone,
            core_view=soften_investment_language(input_data.synthesis.core_view),
            market_news_connection=soften_investment_language(input_data.synthesis.market_news_connection),
            market_evidence=input_data.synthesis.market_evidence,
            news_evidence=input_data.synthesis.news_evidence,
            key_market_variables=input_data.synthesis.key_market_variables,
            intraday_watch_points=[soften_investment_language(item) for item in input_data.synthesis.intraday_watch_points],
            candidate_explanations=explanations,
            caveats=caveats,
            data_gaps=input_data.synthesis.data_gaps,
        )

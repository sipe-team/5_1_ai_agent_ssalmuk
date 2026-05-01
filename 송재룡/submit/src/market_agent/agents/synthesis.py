from market_agent.agents.models import MarketNewsSynthesis, MarketNewsSynthesisInput
from market_agent.agents.presentation import tone_label, variable_labels
from market_agent.agents.utils import unique


class MarketNewsSynthesisAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client

    def run(self, input_data: MarketNewsSynthesisInput) -> MarketNewsSynthesis:
        market = input_data.market
        news = input_data.news
        data_gaps = unique([*market.data_gaps, *news.data_gaps])
        variables = unique(news.key_variables)
        if data_gaps and variables == ["limited_news_signal"]:
            tone = "unclear"
        elif market.risk_tone == "risk_off" or any(item in variables for item in ["geopolitical_risk", "liquidity_stress"]):
            tone = "risk_off"
        elif market.risk_tone == "risk_on" and not any(item in variables for item in ["rate_policy_risk", "fx_risk"]):
            tone = "risk_on"
        else:
            tone = "mixed"
        core_view = _core_view(tone, market.market_strength_summary, variable_labels(variables), data_gaps)
        connection = f"전일 시장 분위기는 {tone_label(market.risk_tone)}에 가깝고, 뉴스에서는 {', '.join(variable_labels(variables))}이 관찰됩니다. 단일 방향 판단보다 장중 수급과 가격 반응 확인이 우선입니다."
        watch_points = []
        if "geopolitical_risk" in variables:
            watch_points.append("지정학 리스크가 유가와 위험자산 선호로 확산되는지 확인 필요.")
        if "rate_policy_risk" in variables or "fx_risk" in variables:
            watch_points.append("금리, 미국채, 환율 압력이 외국인 수급과 성장주 valuation에 미치는 영향 관찰 필요.")
        if "liquidity_stress" in variables:
            watch_points.append("금융 스트레스가 신용 여건과 유동성으로 전이되는지 확인 필요.")
        if not watch_points:
            watch_points.append("시장 변수 신호가 제한적이므로 지수와 수급 변화를 우선 확인 필요.")
        return MarketNewsSynthesis(
            overall_risk_tone=tone,
            core_view=core_view,
            market_news_connection=connection,
            market_evidence=market.user_evidence,
            news_evidence=news.evidence_news,
            key_market_variables=variables,
            intraday_watch_points=watch_points,
            data_gaps=data_gaps,
        )


def _core_view(tone: str, market_summary: str, variables: list[str], data_gaps: list[str]) -> str:
    if data_gaps and tone == "unclear":
        return "데이터 공백이 있어 국내장 방향성 해석은 제한적입니다. 확인 가능한 시장 변수부터 점검해야 합니다."
    if tone == "risk_off":
        return f"{market_summary} 뉴스에서는 {', '.join(variables)}이 함께 관찰됩니다. 오늘 장 초반은 공격적인 방향 판단보다 외국인 수급, 환율, 대형주 방어력을 먼저 확인하는 흐름이 적절합니다."
    if tone == "risk_on":
        return "시장 흐름은 우호적이나, 관찰 후보는 확인된 변수 안에서 참고용으로만 봐야 합니다."
    return f"{market_summary} 뉴스 변수는 {', '.join(variables)}로 정리됩니다. 단정적 방향보다 변수별 시나리오 점검이 필요합니다."

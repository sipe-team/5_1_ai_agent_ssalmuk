from market_agent.agents.models import NewsContextAnalysis, NewsContextInput
from market_agent.agents.presentation import shorten, variable_label
from market_agent.agents.utils import section_status, unique


VARIABLE_BY_CATEGORY = {
    "geopolitical": "geopolitical_risk",
    "rates_fomc": "rate_policy_risk",
    "fx": "fx_risk",
    "financial_stress": "liquidity_stress",
    "market": "market_flow",
}


class NewsContextAgent:
    def __init__(self, llm_client=None, high_importance_limit: int = 3) -> None:
        self.llm_client = llm_client
        self.high_importance_limit = high_importance_limit

    def run(self, input_data: NewsContextInput) -> NewsContextAnalysis:
        news = input_data.news
        gaps: list[str] = []
        if not news:
            gaps.append("news_missing")
        if any(item.collection_failed for item in news):
            gaps.append("news_collection_failed")
        variables = [VARIABLE_BY_CATEGORY[item.category] for item in news if item.category in VARIABLE_BY_CATEGORY]
        high_importance = sorted(news, key=lambda item: item.importance_score, reverse=True)[: self.high_importance_limit]
        evidence_news = [f"{shorten(item.title)} / {item.source} / {item.published_at.astimezone().strftime('%Y-%m-%d %H:%M')}" for item in high_importance[:2]]
        weak_notes = [f"{item.title}: 개별 기업/섹터 뉴스로 과대해석 주의." for item in news if item.category == "non_macro"]
        return NewsContextAnalysis(
            key_variables=unique(variables) or ["limited_news_signal"],
            high_importance_news=high_importance,
            evidence_news=evidence_news,
            weak_relevance_notes=weak_notes,
            source_status=section_status(news),
            data_gaps=gaps,
        )

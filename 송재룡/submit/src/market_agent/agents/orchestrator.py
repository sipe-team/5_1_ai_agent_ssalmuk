from datetime import datetime

from market_agent.agents.candidate_context import CandidateContextAgent
from market_agent.agents.market_data import MarketDataAgent
from market_agent.agents.models import (
    CandidateContextInput,
    MarketDataInput,
    MarketNewsSynthesisInput,
    NewsContextInput,
    PremarketAgentResult,
    ReportEditorInput,
    RiskReviewInput,
)
from market_agent.agents.news_context import NewsContextAgent
from market_agent.agents.report_editor import ReportEditorAgent
from market_agent.agents.risk_review import RiskReviewAgent
from market_agent.agents.synthesis import MarketNewsSynthesisAgent
from market_agent.agents.utils import section_status
from market_agent.models import CleanNewsItem, MarketSnapshot, ScoredCandidate


class PremarketAgentOrchestrator:
    def __init__(self, llm_client=None) -> None:
        self.market_data_agent = MarketDataAgent(llm_client)
        self.news_context_agent = NewsContextAgent(llm_client)
        self.synthesis_agent = MarketNewsSynthesisAgent(llm_client)
        self.candidate_context_agent = CandidateContextAgent(llm_client)
        self.risk_review_agent = RiskReviewAgent(llm_client)
        self.report_editor_agent = ReportEditorAgent(llm_client)

    def run(self, generated_at: datetime, market_context: list[MarketSnapshot], news: list[CleanNewsItem], candidates: list[ScoredCandidate]) -> PremarketAgentResult:
        order: list[str] = []
        market_analysis = self.market_data_agent.run(MarketDataInput(snapshots=market_context)); order.append("MarketDataAgent")
        news_context = self.news_context_agent.run(NewsContextInput(news=news)); order.append("NewsContextAgent")
        synthesis = self.synthesis_agent.run(MarketNewsSynthesisInput(market=market_analysis, news=news_context)); order.append("MarketNewsSynthesisAgent")
        candidate_explanations = self.candidate_context_agent.run(CandidateContextInput(candidates=candidates, synthesis=synthesis)); order.append("CandidateContextAgent")
        reviewed = self.risk_review_agent.run(RiskReviewInput(synthesis=synthesis, candidate_explanations=candidate_explanations)); order.append("RiskReviewAgent")
        compact = self.report_editor_agent.run(
            ReportEditorInput(
                narrative=reviewed,
                generated_at=generated_at,
                market_status=section_status(market_context),
                news_status=section_status(news),
                watchlist_status=section_status([item.candidate for item in candidates]),
            )
        ); order.append("ReportEditorAgent")
        return PremarketAgentResult(
            market_analysis=market_analysis,
            news_context=news_context,
            synthesis=synthesis,
            candidate_explanations=candidate_explanations,
            reviewed_narrative=reviewed,
            compact_content=compact,
            execution_order=order,
        )

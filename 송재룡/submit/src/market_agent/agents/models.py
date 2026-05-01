from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from market_agent.models import Candidate, CleanNewsItem, MarketSnapshot, ScoredCandidate


RiskTone = Literal["risk_on", "risk_off", "mixed", "unclear"]


class AgentModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class MarketDataInput(AgentModel):
    snapshots: list[MarketSnapshot]


class MarketDataAnalysis(AgentModel):
    risk_tone: RiskTone
    index_moves: list[str]
    evidence: list[str]
    user_evidence: str = ""
    market_strength_summary: str = ""
    source_status: str
    data_gaps: list[str]


class NewsContextInput(AgentModel):
    news: list[CleanNewsItem]


class NewsContextAnalysis(AgentModel):
    key_variables: list[str]
    high_importance_news: list[CleanNewsItem]
    evidence_news: list[str] = []
    weak_relevance_notes: list[str]
    source_status: str
    data_gaps: list[str]


class MarketNewsSynthesisInput(AgentModel):
    market: MarketDataAnalysis
    news: NewsContextAnalysis


class MarketNewsSynthesis(AgentModel):
    overall_risk_tone: RiskTone
    core_view: str
    market_news_connection: str
    market_evidence: str = ""
    news_evidence: list[str] = []
    key_market_variables: list[str]
    intraday_watch_points: list[str]
    data_gaps: list[str]


class CandidateContextInput(AgentModel):
    candidates: list[ScoredCandidate]
    synthesis: MarketNewsSynthesis


class CandidateStaticProfile(AgentModel):
    ticker: str
    name: str
    asset_type: str
    market: str | None = None
    sector: str
    industry: str
    index_role: str
    base_sensitivity_tags: list[str]
    source: str
    confidence: float


class CandidateDynamicContext(AgentModel):
    ticker: str
    dynamic_tags: list[str]
    matched_market_variables: list[str]
    evidence: list[str]
    reason: str
    confidence: float
    data_gaps: list[str]


class CandidateTaggingInput(AgentModel):
    candidate: Candidate
    synthesis: MarketNewsSynthesis


class CandidateTaggingResult(AgentModel):
    static_profile: CandidateStaticProfile
    dynamic_context: CandidateDynamicContext


class CandidateExplanation(AgentModel):
    ticker: str
    name: str
    is_mock: bool
    universe_status: str = "mock"
    linked_market_variables: list[str]
    static_profile_summary: str = ""
    today_observation_reason: str = ""
    connected_variables: list[str] = Field(default_factory=list)
    score_reasons: list[str] = Field(default_factory=list)
    watch_points: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    observation_reason: str
    positive_scenario: str
    risk_scenario: str
    intraday_check_point: str
    display_summary: str = ""
    display_check_points: list[str] = Field(default_factory=list)


class RiskReviewInput(AgentModel):
    synthesis: MarketNewsSynthesis
    candidate_explanations: list[CandidateExplanation]


class ReviewedPremarketNarrative(AgentModel):
    overall_risk_tone: RiskTone
    core_view: str
    market_news_connection: str
    market_evidence: str = ""
    news_evidence: list[str] = []
    key_market_variables: list[str]
    intraday_watch_points: list[str]
    candidate_explanations: list[CandidateExplanation]
    caveats: list[str]
    data_gaps: list[str]


class ReportEditorInput(AgentModel):
    narrative: ReviewedPremarketNarrative
    generated_at: datetime
    market_status: str
    news_status: str
    watchlist_status: str


class CompactReportContent(AgentModel):
    generated_at: datetime
    data_status_line: str
    candidate_basis_line: str
    headline: str
    market_news_summary: str
    market_evidence: str
    news_evidence: list[str]
    key_market_variables: list[str]
    intraday_watch_points: list[str]
    candidate_explanations: list[CandidateExplanation]
    caveats: list[str]
    data_gaps: list[str]


class PremarketAgentResult(AgentModel):
    market_analysis: MarketDataAnalysis
    news_context: NewsContextAnalysis
    synthesis: MarketNewsSynthesis
    candidate_explanations: list[CandidateExplanation]
    reviewed_narrative: ReviewedPremarketNarrative
    compact_content: CompactReportContent
    execution_order: list[str]

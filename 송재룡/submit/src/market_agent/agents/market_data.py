from market_agent.agents.models import MarketDataAnalysis, MarketDataInput
from market_agent.agents.presentation import market_evidence_line, market_strength_sentence
from market_agent.agents.utils import section_status


class MarketDataAgent:
    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client

    def run(self, input_data: MarketDataInput) -> MarketDataAnalysis:
        snapshots = input_data.snapshots
        gaps: list[str] = []
        if not snapshots:
            gaps.append("market_context_missing")
        if any(item.collection_failed for item in snapshots):
            gaps.append("market_data_collection_failed")
        index_moves = [f"{item.name} {item.change_percent:+.2f}%" for item in snapshots if not item.collection_failed]
        korea_indexes = [item for item in snapshots if ("KOSPI" in item.name or "KOSDAQ" in item.name) and not item.collection_failed]
        negative_count = sum(1 for item in korea_indexes if item.change_percent < -0.5)
        positive_count = sum(1 for item in korea_indexes if item.change_percent > 0.5)
        if gaps and not korea_indexes:
            tone = "unclear"
        elif negative_count >= 2:
            tone = "risk_off"
        elif positive_count >= 2:
            tone = "risk_on"
        elif negative_count or positive_count:
            tone = "mixed"
        else:
            tone = "mixed"
        evidence = index_moves or ["시장 데이터가 부족해 지수 흐름 근거가 제한적."]
        return MarketDataAnalysis(
            risk_tone=tone,
            index_moves=index_moves,
            evidence=evidence,
            user_evidence=market_evidence_line(snapshots),
            market_strength_summary=market_strength_sentence(snapshots),
            source_status=section_status(snapshots),
            data_gaps=gaps,
        )

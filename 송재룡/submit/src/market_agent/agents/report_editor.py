from market_agent.agents.models import CompactReportContent, ReportEditorInput
from market_agent.agents.presentation import variable_labels


class ReportEditorAgent:
    def __init__(self, llm_client=None, candidate_limit: int = 5) -> None:
        self.llm_client = llm_client
        self.candidate_limit = candidate_limit

    def run(self, input_data: ReportEditorInput) -> CompactReportContent:
        narrative = input_data.narrative
        return CompactReportContent(
            generated_at=input_data.generated_at,
            data_status_line=f"데이터 상태: 시장={input_data.market_status} / 뉴스={input_data.news_status} / 관찰 후보={input_data.watchlist_status}",
            candidate_basis_line=_candidate_basis_line(input_data.watchlist_status),
            headline=_shorten(narrative.core_view, 140),
            market_news_summary=_shorten(narrative.market_news_connection, 180),
            market_evidence=getattr(narrative, "market_evidence", ""),
            news_evidence=getattr(narrative, "news_evidence", []),
            key_market_variables=variable_labels(narrative.key_market_variables),
            intraday_watch_points=[_shorten(item, 120) for item in narrative.intraday_watch_points[:3]],
            candidate_explanations=narrative.candidate_explanations[: self.candidate_limit],
            caveats=narrative.caveats,
            data_gaps=narrative.data_gaps,
        )


def _shorten(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def _candidate_basis_line(status: str) -> str:
    if status == "mock":
        return "후보 선정은 mock 기반이며, 설명은 현재 시장/뉴스 context 기준입니다."
    if status == "fallback":
        return "후보 universe: fallback/mock. Live universe 실패 후 mock 후보로 참고용 설명을 생성했습니다."
    if status == "live":
        return "후보 universe: live KRX 기반. 설명은 현재 시장/뉴스 context 기준입니다."
    return f"후보 universe: {status}"

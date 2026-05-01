from datetime import datetime

from market_agent.config import KST
from market_agent.agents.models import CompactReportContent
from market_agent.agents.presentation import variable_labels
from market_agent.models import CleanNewsItem, MarketNewsInsight, MarketSnapshot, NewsItem, PricePoint, ScoredCandidate


DISCLAIMER = "Research/watchlist only. Not financial advice. No orders are placed."
PREMARKET_NEWS_LIMIT = 5


def _fmt_dt(value: datetime) -> str:
    return value.astimezone(KST).strftime("%Y-%m-%d %H:%M %Z")


def _data_label(is_mock_values: list[bool]) -> str:
    if all(is_mock_values):
        return "Data label: MOCK"
    if any(is_mock_values):
        return "Data label: MIXED"
    return "Data label: LIVE"


def _section_status(items) -> str:
    if not items:
        return "failed"
    if any(getattr(item, "collection_failed", False) for item in items):
        return "failed"
    statuses = [getattr(item, "universe_status", None) for item in items]
    if any(status == "fallback_used" for status in statuses):
        return "fallback"
    if statuses and all(status == "live" for status in statuses):
        return "live"
    if all(getattr(item, "is_mock", False) for item in items):
        return "mock"
    if any(getattr(item, "is_mock", False) for item in items):
        return "mixed"
    return "live"


def _news_category_label(category: str) -> str:
    labels = {
        "rates_fomc": "금리/통화정책",
        "geopolitical": "지정학/전쟁 리스크",
        "fx": "환율/외환",
        "financial_stress": "금융 스트레스",
        "market": "시장 수급/지수",
        "non_macro": "개별 기업/섹터",
        "data_gap": "데이터 공백",
    }
    return labels.get(category, category)


def format_premarket_report(
    generated_at: datetime,
    market_context: list[MarketSnapshot],
    news: list[NewsItem] | list[CleanNewsItem],
    candidates: list[ScoredCandidate],
    insight: MarketNewsInsight | None = None,
) -> str:
    lines = [
        f"Premarket Report - {_fmt_dt(generated_at)}",
        _data_label([*[item.is_mock for item in market_context], *[item.is_mock for item in news], *[item.candidate.is_mock for item in candidates]]),
        "",
        "Market Context",
    ]
    for item in market_context:
        status = "데이터 수집 실패" if item.collection_failed else f"{item.change_percent:+.2f}%"
        market_date = item.market_date.isoformat() if item.market_date else "unknown"
        lines.append(f"- {item.name}: {status} | {item.summary} | source={item.source} at {_fmt_dt(item.data_timestamp)} | market_date={market_date}")
    if insight:
        lines.extend(["", "시장 해석 요약", f"- Risk tone: {insight.overall_risk_tone}"])
        lines.append(f"- Key variables: {', '.join(insight.key_market_variables)}")
        if insight.korea_market_implications:
            lines.append("- Korea market implications:")
            lines.extend(f"  - {item}" for item in insight.korea_market_implications)
        if insight.watch_points:
            lines.append("- Watch points:")
            lines.extend(f"  - {item}" for item in insight.watch_points)
        if insight.data_gaps:
            lines.append(f"- Data gaps: {', '.join(insight.data_gaps)}")
    lines.extend(["", "시장 변수 뉴스 체크", "정제된 뉴스 기반 참고용 리스크 요약입니다. LLM 요약이나 테마 추출 결과가 아닙니다."])
    for item in news[:PREMARKET_NEWS_LIMIT]:
        snippet = item.snippet if isinstance(item, CleanNewsItem) else item.summary
        status = "데이터 수집 실패" if item.collection_failed else snippet
        if isinstance(item, CleanNewsItem):
            lines.append(f"- [{_news_category_label(item.category)}] {item.title}")
            lines.append(f"  - 관찰 포인트: {status}")
            lines.append(f"  - 영향 힌트: {item.market_impact_hint}")
            lines.append(f"  - 우선순위: {item.priority}")
            lines.append(f"  - 중요도 점수: {item.importance_score:.2f}")
        else:
            lines.append(f"- [원문 뉴스] {item.title}")
            lines.append(f"  - 관찰 포인트: {status}")
        lines.append(f"  - 출처/시각: {item.source} / {_fmt_dt(item.published_at)}")
        if item.url:
            lines.append(f"  - URL: {item.url}")
        if item.raw_keyword:
            lines.append(f"  - 검색어: {item.raw_keyword}")
        if item.fetched_at:
            lines.append(f"  - 수집 시각: {_fmt_dt(item.fetched_at)}")
    lines.extend(["", "Top Watchlist"])
    for index, item in enumerate(candidates, start=1):
        candidate = item.candidate
        lines.append(
            f"{index}. {candidate.ticker} {candidate.name} | theme={candidate.theme} | score={item.score:.2f} | catalyst={candidate.catalyst} | valuation={candidate.valuation_note} | quality={candidate.quality_note} | risk={candidate.risk_note} | source={candidate.source}"
        )
    lines.extend(["", DISCLAIMER])
    return "\n".join(lines)


def format_compact_premarket_report(
    generated_at: datetime,
    market_context: list[MarketSnapshot],
    news: list[CleanNewsItem],
    candidates: list[ScoredCandidate],
    insight: MarketNewsInsight | None = None,
    news_limit: int = 3,
    content: CompactReportContent | None = None,
) -> str:
    if content:
        return _format_compact_content(content)
    market_status = _section_status(market_context)
    news_status = _section_status(news)
    watchlist_status = _section_status([item.candidate for item in candidates])
    lines = [
        f"Premarket Compact - {_fmt_dt(generated_at)}",
        f"데이터 상태: 시장={market_status} / 뉴스={news_status} / 관찰 후보={watchlist_status}",
        _candidate_basis_line(watchlist_status),
        "",
        "핵심 요약",
    ]
    if insight:
        lines.append(f"- Risk tone: {insight.overall_risk_tone}")
        lines.append(f"- 시장 변수: {', '.join(insight.key_market_variables)}")
        if insight.watch_points:
            lines.append(f"- 관찰 필요: {insight.watch_points[0]}")
        if insight.data_gaps:
            lines.append(f"- 데이터 공백: {', '.join(insight.data_gaps)}")
    else:
        lines.append("- 시장 해석 요약 없음")

    lines.extend(["", "시장 데이터"])
    for item in market_context:
        status = "데이터 수집 실패" if item.collection_failed else f"{item.change_percent:+.2f}%"
        lines.append(f"- {item.name}: {status} | {item.source} / {_fmt_dt(item.data_timestamp)}")

    lines.extend(["", "뉴스 변수"])
    for item in news[:news_limit]:
        lines.append(f"- [{_news_category_label(item.category)}] {item.title}")
        lines.append(f"  - 영향 힌트: {item.market_impact_hint}")
        lines.append(f"  - 중요도: {item.importance_score:.2f} | 출처: {item.source} / {_fmt_dt(item.published_at)}")

    lines.extend(["", "관찰 후보"])
    for index, item in enumerate(candidates, start=1):
        candidate = item.candidate
        lines.append(f"{index}. {candidate.ticker} {candidate.name} | score={item.score:.2f} | risk={candidate.risk_note}")

    lines.extend(["", "참고용 관찰 정보입니다. 투자 권유가 아니며 주문은 실행되지 않습니다."])
    return "\n".join(lines)


def _candidate_basis_line(status: str) -> str:
    if status == "mock":
        return "후보 선정은 mock 기반이며, 설명은 현재 시장/뉴스 context 기준입니다."
    if status == "fallback":
        return "후보 universe: fallback/mock. Live universe 실패 후 mock 후보로 참고용 설명을 생성했습니다."
    if status == "live":
        return "후보 universe: live KRX 기반. 설명은 현재 시장/뉴스 context 기준입니다."
    return f"후보 universe: {status}"


def _format_compact_content(content: CompactReportContent) -> str:
    lines = [
        "📌 프리마켓 리포트",
        f"생성: {_fmt_dt(content.generated_at)}",
        content.data_status_line,
        content.candidate_basis_line,
        "",
        "🧭 핵심 판단",
        f"- {content.headline}",
        "",
        "🔎 왜 이렇게 보나",
        f"- 시장 근거: {content.market_evidence}",
    ]
    if content.news_evidence:
        lines.append("- 뉴스 근거:")
        lines.extend(f"  - {item}" for item in content.news_evidence[:2])
    lines.extend([
        "",
        "시장 x 뉴스 해석",
        f"- {content.market_news_summary}",
        f"- 주요 변수: {', '.join(content.key_market_variables)}",
    ])
    if content.intraday_watch_points:
        lines.append("- 장중 확인 포인트:")
        lines.extend(f"  - {item}" for item in content.intraday_watch_points)
    if content.data_gaps:
        lines.append(f"- 데이터 공백: {', '.join(content.data_gaps)}")

    lines.extend(["", "👀 오늘의 관찰 후보"])
    for item in content.candidate_explanations:
        lines.append(f"- {item.name} ({item.ticker})")
        lines.append(f"  - 이유: {item.display_summary or item.today_observation_reason or item.observation_reason}")
        lines.append(f"  - 연결 변수: {', '.join(item.connected_variables or variable_labels(item.linked_market_variables))}")
        if item.score_reasons:
            lines.append(f"  - 점수 근거: {', '.join(item.score_reasons[:2])}")
        lines.append(f"  - 확인: {', '.join(item.watch_points or item.display_check_points or [item.intraday_check_point])}")
        lines.append(f"  - 리스크: {', '.join(item.risks or [item.risk_scenario])}")
    if content.caveats:
        lines.extend(["", "⚠️ 참고"])
        lines.extend(f"- {item}" for item in content.caveats)
    return "\n".join(lines)


def format_hourly_update(generated_at: datetime, prices: list[PricePoint]) -> str:
    lines = [
        f"Hourly Tracking Update - {_fmt_dt(generated_at)}",
        "Assumption: simulated buy at open for the selected watchlist.",
        _data_label([point.is_mock for point in prices]) if prices else "Data label: UNKNOWN",
        "",
    ]
    for point in prices:
        lines.append(
            f"- {point.ticker}: open={point.open_price:.2f}, latest={point.latest_price:.2f}, return={point.return_percent:+.2f}% | source={point.source} at {_fmt_dt(point.data_timestamp)} | market_date={point.market_date.isoformat() if point.market_date else 'unknown'}"
        )
    lines.extend(["", DISCLAIMER])
    return "\n".join(lines)


def format_closing_summary(generated_at: datetime, prices: list[PricePoint]) -> str:
    lines = [f"Closing Summary - {_fmt_dt(generated_at)}", _data_label([point.is_mock for point in prices]) if prices else "Data label: UNKNOWN"]
    if not prices:
        return "\n".join([*lines, "No tracked prices available.", "", DISCLAIMER])
    best = max(prices, key=lambda point: point.return_percent)
    worst = min(prices, key=lambda point: point.return_percent)
    average = sum(point.return_percent for point in prices) / len(prices)
    lines.extend(
        [
            f"Best simulated performer: {best.ticker} {best.return_percent:+.2f}%",
            f"Worst simulated performer: {worst.ticker} {worst.return_percent:+.2f}%",
            f"Average simulated return: {average:+.2f}%",
            "",
            DISCLAIMER,
        ]
    )
    return "\n".join(lines)

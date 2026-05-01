import re
from datetime import datetime

from market_agent.config import KST
from market_agent.models import CleanNewsItem, NewsItem


RATE_KEYWORDS = ("금리", "FOMC", "연준", "Fed", "기준금리", "채권", "국채", "긴축", "완화")
GEOPOLITICAL_KEYWORDS = ("전쟁", "지정학", "중동", "우크라이나", "러시아", "이스라엘", "이란", "분쟁", "제재")
FX_KEYWORDS = ("환율", "원달러", "원/달러", "달러", "외환", "원화", "엔화", "위안")
FINANCIAL_STRESS_KEYWORDS = ("금융불안", "신용경색", "부도", "파산", "유동성", "위기", "뱅크런", "디폴트")
MARKET_KEYWORDS = ("증시", "코스피", "코스닥", "주가", "시장", "ETF", "수급", "외국인", "기관")
COMPANY_OR_SECTOR_KEYWORDS = ("삼성전자", "SK하이닉스", "현대차", "NAVER", "반도체", "배터리", "자동차", "바이오")
SEVERITY_KEYWORDS = ("급락", "폭락", "충돌", "전쟁", "금리 인상", "위기", "제재", "환율 급등", "불안", "긴급")


def clean_news_items(raw_items: list[NewsItem], reference_time: datetime | None = None) -> list[CleanNewsItem]:
    scored_at = reference_time or datetime.now(KST)
    cleaned: list[CleanNewsItem] = []
    seen: set[tuple[str, str]] = set()
    for item in raw_items:
        title = _normalize_text(item.title)
        snippet = _normalize_text(item.snippet or item.summary)
        dedupe_key = (_dedupe_text(title), item.url or "")
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        category = _category(title, snippet, item.collection_failed)
        importance_score = _importance_score(item, title, snippet, category, scored_at)
        cleaned.append(
            CleanNewsItem(
                title=title,
                source=item.source,
                published_at=item.published_at,
                url=item.url,
                snippet=snippet,
                raw_keyword=item.raw_keyword,
                fetched_at=item.fetched_at,
                category=category,
                market_impact_hint=_market_impact_hint(category),
                priority=_priority(category),
                importance_score=importance_score,
                is_mock=item.is_mock,
                collection_failed=item.collection_failed,
            )
        )
    return sorted(cleaned, key=lambda item: (-item.importance_score, item.priority, item.published_at), reverse=False)


def _category(title: str, snippet: str, collection_failed: bool) -> str:
    if collection_failed:
        return "data_gap"
    text = f"{title} {snippet}"
    if _contains(text, RATE_KEYWORDS):
        return "rates_fomc"
    if _contains(text, GEOPOLITICAL_KEYWORDS):
        return "geopolitical"
    if _contains(text, FX_KEYWORDS):
        return "fx"
    if _contains(text, FINANCIAL_STRESS_KEYWORDS):
        return "financial_stress"
    if _contains(text, MARKET_KEYWORDS):
        return "market"
    if _contains(text, COMPANY_OR_SECTOR_KEYWORDS):
        return "non_macro"
    return "non_macro"


def _market_impact_hint(category: str) -> str:
    hints = {
        "rates_fomc": "금리/FOMC 경로 변화가 equity discount rate와 risk appetite에 영향을 줄 수 있는 시나리오.",
        "geopolitical": "지정학 리스크가 에너지 가격, 공급망, 위험자산 선호에 영향을 줄 수 있는 시나리오.",
        "fx": "환율 변화가 수출주, 외국인 수급, 원화 자산 선호에 영향을 줄 수 있는 시나리오.",
        "financial_stress": "금융 스트레스가 신용 여건과 위험자산 선호에 영향을 줄 수 있는 리스크 요인.",
        "market": "시장 수급과 지수 흐름을 확인할 참고용 context.",
        "non_macro": "순수 개별 기업/섹터 뉴스일 수 있어 낮은 priority로 참고.",
        "data_gap": "뉴스 데이터 수집 실패로 해석에 공백이 있음.",
    }
    return hints[category]


def _priority(category: str) -> int:
    return {"data_gap": 0, "rates_fomc": 1, "geopolitical": 2, "financial_stress": 3, "fx": 4, "market": 5, "non_macro": 9}[category]


def _importance_score(item: NewsItem, title: str, snippet: str, category: str, reference_time: datetime) -> float:
    score = {
        "data_gap": 0.20,
        "rates_fomc": 0.72,
        "geopolitical": 0.72,
        "financial_stress": 0.76,
        "fx": 0.62,
        "market": 0.45,
        "non_macro": 0.20,
    }[category]
    text = f"{title} {snippet}"
    severity_hits = sum(1 for keyword in SEVERITY_KEYWORDS if keyword.lower() in text.lower())
    score += min(0.18, severity_hits * 0.06)
    if not item.source:
        score -= 0.10
    age_hours = max(0.0, (reference_time.astimezone(KST) - item.published_at.astimezone(KST)).total_seconds() / 3600)
    if age_hours > 72:
        score -= 0.25
    elif age_hours > 24:
        score -= 0.12
    elif age_hours > 12:
        score -= 0.05
    return max(0.0, min(1.0, round(score, 2)))


def _contains(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _dedupe_text(value: str) -> str:
    return re.sub(r"[^0-9a-zA-Z가-힣]+", "", value).lower()

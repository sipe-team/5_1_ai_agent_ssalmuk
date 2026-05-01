def section_status(items) -> str:
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


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def soften_investment_language(value: str) -> str:
    replacements = {
        "추천": "관찰 후보",
        "매수": "관찰",
        "상승 확정": "상승 시나리오",
        "확정": "시나리오",
        "유망": "관찰 필요",
        "보장": "가능성",
        "risk tone": "시장 분위기",
        "valuation": "밸류에이션",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value

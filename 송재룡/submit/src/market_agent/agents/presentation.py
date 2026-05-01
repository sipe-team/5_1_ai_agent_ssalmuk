from market_agent.models import MarketSnapshot


RISK_TONE_LABELS = {
    "risk_off": "위험 회피 우세",
    "risk_on": "위험 선호 우세",
    "mixed": "방향성 혼재",
    "unclear": "판단 유보",
}

VARIABLE_LABELS = {
    "fx_risk": "환율 부담",
    "rate_policy_risk": "금리 부담",
    "rate_risk": "금리 부담",
    "rate_fx_risk": "금리·환율 부담",
    "geopolitical_risk": "지정학 리스크",
    "market_flow": "수급/지수 흐름",
    "oil_price_shock": "유가 변동 리스크",
    "liquidity_stress": "금융시장 스트레스",
    "sector_sensitivity": "섹터 민감도",
    "limited_direct_link": "직접 연결성 제한",
    "limited_news_signal": "뉴스 신호 제한",
    "direct_link_limited": "직접 연결성 제한",
}

THEME_LABELS = {
    "Semiconductor large-cap": "반도체 대형주",
    "Exporter/auto large-cap": "자동차 수출 대형주",
    "Platform/growth large-cap": "플랫폼 성장주",
    "Market/sector ETF": "시장/섹터 ETF",
    "Energy/commodity sensitivity": "에너지·원자재 민감주",
    "KRX liquidity leader": "KRX 거래대금 상위 후보",
}


def tone_label(value: str) -> str:
    return RISK_TONE_LABELS.get(value, value)


def variable_label(value: str) -> str:
    return VARIABLE_LABELS.get(value, value)


def variable_labels(values: list[str]) -> list[str]:
    return [variable_label(value) for value in values]


def theme_label(value: str) -> str:
    return THEME_LABELS.get(value, value)


def shorten(value: str, limit: int = 45) -> str:
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def market_evidence_line(snapshots: list[MarketSnapshot]) -> str:
    kospi = _find_change(snapshots, "KOSPI")
    kosdaq = _find_change(snapshots, "KOSDAQ")
    if kospi is None and kosdaq is None:
        return "시장 데이터 근거가 부족합니다."
    parts = []
    if kospi is not None:
        parts.append(f"KOSPI {kospi:+.2f}%")
    if kosdaq is not None:
        parts.append(f"KOSDAQ {kosdaq:+.2f}%")
    return ", ".join(parts)


def market_strength_sentence(snapshots: list[MarketSnapshot]) -> str:
    kospi = _find_change(snapshots, "KOSPI")
    kosdaq = _find_change(snapshots, "KOSDAQ")
    if kospi is None or kosdaq is None:
        return "국내 지수 데이터가 일부 부족해 시장 체력 판단은 제한적입니다."
    if kospi < 0 and kosdaq < 0:
        weaker = "KOSDAQ 약세가 더 컸습니다" if kosdaq < kospi else "KOSPI 약세가 더 컸습니다"
        return f"{market_evidence_line(snapshots)}로 두 지수가 모두 약세였고, {weaker}. 성장주/중소형주 쪽 위험 회피가 더 강했을 가능성을 확인해야 합니다."
    if kospi > 0 and kosdaq > 0:
        return f"{market_evidence_line(snapshots)}로 두 지수가 모두 강세였습니다. 다만 뉴스 변수와 수급 확인 전까지는 관찰 관점이 적절합니다."
    return f"{market_evidence_line(snapshots)}로 지수 간 방향이 엇갈렸습니다. 시장 내부 수급 차별화를 확인해야 합니다."


def _find_change(snapshots: list[MarketSnapshot], keyword: str) -> float | None:
    for item in snapshots:
        if keyword in item.name and not item.collection_failed:
            return item.change_percent
    return None

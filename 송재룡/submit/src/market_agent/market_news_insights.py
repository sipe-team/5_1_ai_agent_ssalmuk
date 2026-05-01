from market_agent.models import CleanNewsItem, MarketNewsInsight, MarketSnapshot


OIL_KEYWORDS = ("유가", "고유가", "원유", "브렌트", "WTI", "oil")
RATE_FX_CATEGORIES = {"rates_fomc", "fx"}


def build_market_news_insight(market_context: list[MarketSnapshot], news: list[CleanNewsItem]) -> MarketNewsInsight:
    data_gaps = _data_gaps(market_context, news)
    key_market_variables: list[str] = []
    korea_market_implications: list[str] = []
    watch_points: list[str] = []

    has_geopolitical = any(item.category == "geopolitical" for item in news)
    has_oil_pressure = any(_contains_oil_pressure(item) for item in news)
    has_rate_fx = any(item.category in RATE_FX_CATEGORIES for item in news)
    has_financial_stress = any(item.category == "financial_stress" for item in news)

    if has_geopolitical:
        key_market_variables.append("geopolitical_risk")
        watch_points.append("지정학 뉴스가 위험자산 선호와 에너지 가격에 미치는 영향을 관찰 필요.")
        korea_market_implications.append("대외 불확실성이 커질 경우 한국 증시 수급과 수출주 변동성에 부담이 될 수 있는 시나리오.")
    if has_geopolitical and has_oil_pressure:
        key_market_variables.append("oil_price_shock")
        watch_points.append("유가 상승 압력이 동반되는지 확인 필요.")
        korea_market_implications.append("고유가가 원가 부담과 무역수지 기대에 영향을 줄 수 있는 리스크 요인.")
    if has_rate_fx:
        key_market_variables.append("rate_fx_risk")
        watch_points.append("금리, 미국채, 환율 압력이 외국인 수급과 valuation에 미치는 영향을 관찰 필요.")
        korea_market_implications.append("rate/fx 부담이 성장주와 원화 자산 선호에 영향을 줄 수 있는 시나리오.")
    if has_financial_stress:
        key_market_variables.append("liquidity_stress")
        watch_points.append("금융시장 스트레스가 credit spread와 유동성 여건으로 확산되는지 확인 필요.")
        korea_market_implications.append("liquidity stress 확대 시 risk-off 성향이 강해질 수 있는 리스크 요인.")

    if not key_market_variables:
        key_market_variables.append("limited_signal")
        watch_points.append("현재 입력만으로 뚜렷한 시장 변수 판단은 제한적.")

    return MarketNewsInsight(
        overall_risk_tone=_risk_tone(has_geopolitical, has_rate_fx, has_financial_stress, data_gaps),
        key_market_variables=_unique(key_market_variables),
        korea_market_implications=_unique(korea_market_implications),
        watch_points=_unique(watch_points),
        data_gaps=data_gaps,
    )


def _risk_tone(has_geopolitical: bool, has_rate_fx: bool, has_financial_stress: bool, data_gaps: list[str]) -> str:
    if data_gaps and not (has_geopolitical or has_rate_fx or has_financial_stress):
        return "unclear"
    if has_financial_stress or has_geopolitical:
        return "risk_off"
    if has_rate_fx:
        return "mixed"
    if data_gaps:
        return "unclear"
    return "mixed"


def _data_gaps(market_context: list[MarketSnapshot], news: list[CleanNewsItem]) -> list[str]:
    gaps: list[str] = []
    if not market_context:
        gaps.append("market_context_missing")
    if not news:
        gaps.append("news_missing")
    if any(item.collection_failed for item in market_context):
        gaps.append("market_data_collection_failed")
    if any(item.collection_failed for item in news):
        gaps.append("news_collection_failed")
    return gaps


def _contains_oil_pressure(item: CleanNewsItem) -> bool:
    text = f"{item.title} {item.snippet}".lower()
    return any(keyword.lower() in text for keyword in OIL_KEYWORDS)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))

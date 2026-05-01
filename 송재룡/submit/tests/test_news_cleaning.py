from datetime import datetime

from market_agent.config import KST
from market_agent.models import NewsItem
from market_agent.news_cleaning import clean_news_items


def news(title: str, summary: str, url: str | None = None) -> NewsItem:
    now = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    return NewsItem("Naver Search News API", now, title, summary, url=url, is_mock=False, raw_keyword="한국 증시", fetched_at=now)


def test_clean_news_items_removes_duplicates() -> None:
    cleaned = clean_news_items(
        [
            news("한국 증시 상승", "코스피 상승", "https://news.example/a"),
            news("한국 증시 상승", "다른 요약", "https://news.example/a"),
        ]
    )

    assert len(cleaned) == 1
    assert cleaned[0].title == "한국 증시 상승"


def test_clean_news_items_classifies_rates_fomc() -> None:
    cleaned = clean_news_items([news("FOMC 금리 동결", "연준이 기준금리를 유지했다")])

    assert cleaned[0].category == "rates_fomc"
    assert cleaned[0].priority == 1
    assert "금리/FOMC" in cleaned[0].market_impact_hint


def test_clean_news_items_classifies_geopolitical_war() -> None:
    cleaned = clean_news_items([news("중동 전쟁 리스크 확대", "지정학 불확실성이 유가를 흔들었다")])

    assert cleaned[0].category == "geopolitical"
    assert cleaned[0].priority == 2


def test_clean_news_items_classifies_fx() -> None:
    cleaned = clean_news_items([news("원달러 환율 급등", "달러 강세로 원화 약세가 이어졌다")])

    assert cleaned[0].category == "fx"
    assert cleaned[0].priority == 4


def test_clean_news_items_marks_pure_company_news_non_macro() -> None:
    cleaned = clean_news_items([news("삼성전자 신제품 공개", "갤럭시 신제품 판매가 시작됐다")])

    assert cleaned[0].category == "non_macro"
    assert cleaned[0].priority == 9


def test_clean_news_items_keeps_semiconductor_terms_inside_macro_news() -> None:
    cleaned = clean_news_items([news("FOMC 이후 반도체주 강세", "금리 인하 기대와 삼성전자 수급이 함께 부각됐다")])

    assert len(cleaned) == 1
    assert cleaned[0].category == "rates_fomc"
    assert "반도체" in cleaned[0].title
    assert "삼성전자" in cleaned[0].snippet


def test_clean_news_items_scores_severe_macro_news_higher_than_non_macro() -> None:
    reference = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    cleaned = clean_news_items(
        [
            news("삼성전자 신제품 공개", "갤럭시 신제품 판매가 시작됐다"),
            news("전쟁 충돌과 제재 확대", "지정학 위기로 위험자산 변동성이 커졌다"),
        ],
        reference,
    )

    assert cleaned[0].category == "geopolitical"
    assert cleaned[0].importance_score > cleaned[1].importance_score
    assert 0 <= cleaned[0].importance_score <= 1


def test_clean_news_items_penalizes_old_news_and_missing_source() -> None:
    reference = datetime(2026, 4, 30, 8, 0, tzinfo=KST)
    old_item = NewsItem("", datetime(2026, 4, 25, 8, 0, tzinfo=KST), "FOMC 금리 인상", "연준 긴축 우려", is_mock=False)

    cleaned = clean_news_items([old_item], reference)

    assert cleaned[0].category == "rates_fomc"
    assert cleaned[0].importance_score < 0.72

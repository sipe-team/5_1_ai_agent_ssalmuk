from datetime import datetime

from market_agent.agents import PremarketAgentOrchestrator
from market_agent.clients.protocols import MarketDataClient, NewsClient, Notifier
from market_agent.config import KST
from market_agent.db import Repository
from market_agent.news_cleaning import clean_news_items
from market_agent.reports import format_closing_summary, format_compact_premarket_report, format_hourly_update, format_premarket_report
from market_agent.scoring import rank_candidates
from market_agent.models import MarketNewsInsight


def run_premarket_pipeline(
    market_client: MarketDataClient,
    news_client: NewsClient,
    notifier: Notifier,
    repository: Repository,
    now: datetime | None = None,
    report_mode: str = "compact",
    compact_news_limit: int = 3,
) -> str:
    generated_at = now or datetime.now(KST)
    market_context = market_client.get_market_context()
    news = clean_news_items(news_client.get_top_news(), generated_at)
    score_context = _candidate_score_context(market_context, news)
    watchlist = rank_candidates(market_client.get_candidates(), limit=5, score_context=score_context)
    agent_result = PremarketAgentOrchestrator().run(generated_at, market_context, news, watchlist)
    repository.save_watchlist(generated_at, watchlist)
    if report_mode == "full":
        insight = MarketNewsInsight(
            overall_risk_tone=agent_result.synthesis.overall_risk_tone,
            key_market_variables=agent_result.synthesis.key_market_variables,
            korea_market_implications=[agent_result.synthesis.core_view],
            watch_points=agent_result.synthesis.intraday_watch_points,
            data_gaps=agent_result.synthesis.data_gaps,
        )
        report = format_premarket_report(generated_at, market_context, news, watchlist, insight)
    else:
        report = format_compact_premarket_report(generated_at, market_context, news, watchlist, content=agent_result.compact_content, news_limit=compact_news_limit)
    notifier.send_message(report)
    return report


def _candidate_score_context(market_context, news) -> dict:
    korea = [item for item in market_context if ("KOSPI" in item.name or "KOSDAQ" in item.name) and not item.collection_failed]
    negative_count = sum(1 for item in korea if item.change_percent < -0.5)
    positive_count = sum(1 for item in korea if item.change_percent > 0.5)
    if negative_count >= 2:
        tone = "risk_off"
    elif positive_count >= 2:
        tone = "risk_on"
    else:
        tone = "mixed"
    return {
        "market_risk_tone": tone,
        "market_variables": [item.category for item in news],
        "news_categories": [item.category for item in news],
    }


def run_hourly_tracking_pipeline(
    market_client: MarketDataClient,
    notifier: Notifier,
    repository: Repository,
    now: datetime | None = None,
) -> str:
    generated_at = now or datetime.now(KST)
    tickers = [item.candidate.ticker for item in repository.load_latest_watchlist()]
    prices = market_client.get_intraday_prices(tickers)
    repository.save_tracking_snapshot(generated_at, prices)
    report = format_hourly_update(generated_at, prices)
    notifier.send_message(report)
    return report


def run_closing_summary_pipeline(
    market_client: MarketDataClient,
    notifier: Notifier,
    repository: Repository,
    now: datetime | None = None,
) -> str:
    generated_at = now or datetime.now(KST)
    tickers = [item.candidate.ticker for item in repository.load_latest_watchlist()]
    prices = market_client.get_intraday_prices(tickers)
    repository.save_tracking_snapshot(generated_at, prices)
    report = format_closing_summary(generated_at, prices)
    notifier.send_message(report)
    return report

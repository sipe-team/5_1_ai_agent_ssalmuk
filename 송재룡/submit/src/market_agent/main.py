import argparse

from market_agent.clients import FinanceDataReaderKoreaMarketDataClient, MockMarketDataClient, MockNewsClient, NaverNewsClient, TelegramClient
from market_agent.config import get_settings
from market_agent.db import Repository
from market_agent.logging import configure_logging
from market_agent.pipelines import run_closing_summary_pipeline, run_hourly_tracking_pipeline, run_premarket_pipeline
from market_agent.scheduler import build_scheduler


def _dependencies():
    settings = get_settings()
    configure_logging(settings.log_level)
    repository = Repository(settings.db_path)
    mock_market_client = MockMarketDataClient()
    if settings.market_data_provider == "finance-data-reader":
        market_client = FinanceDataReaderKoreaMarketDataClient(mock_market_client, lookback_days=settings.finance_data_reader_lookback_days, candidate_limit=settings.krx_candidate_universe_limit)
    else:
        market_client = mock_market_client
    if settings.news_provider == "naver":
        news_client = NaverNewsClient(
            settings.naver_client_id,
            settings.naver_client_secret,
            settings.naver_news_query,
            settings.naver_news_display,
            settings.naver_news_timeout_seconds,
        )
    else:
        news_client = MockNewsClient()
    notifier = TelegramClient(settings.telegram_dry_run, settings.telegram_bot_token, settings.telegram_chat_id)
    return market_client, news_client, notifier, repository


def main() -> None:
    parser = argparse.ArgumentParser(description="Korean-market intelligence agent MVP")
    parser.add_argument("command", choices=["premarket", "hourly", "closing", "scheduler"])
    args = parser.parse_args()

    market_client, news_client, notifier, repository = _dependencies()

    if args.command == "premarket":
        settings = get_settings()
        run_premarket_pipeline(market_client, news_client, notifier, repository, report_mode=settings.report_mode, compact_news_limit=settings.compact_news_limit)
    elif args.command == "hourly":
        run_hourly_tracking_pipeline(market_client, notifier, repository)
    elif args.command == "closing":
        run_closing_summary_pipeline(market_client, notifier, repository)
    else:
        scheduler = build_scheduler(
            lambda: run_premarket_pipeline(market_client, news_client, notifier, repository, report_mode=get_settings().report_mode, compact_news_limit=get_settings().compact_news_limit),
            lambda: run_hourly_tracking_pipeline(market_client, notifier, repository),
            lambda: run_closing_summary_pipeline(market_client, notifier, repository),
        )
        scheduler.start()


if __name__ == "__main__":
    main()

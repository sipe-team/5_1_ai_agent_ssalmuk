from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


KST = ZoneInfo("Asia/Seoul")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MARKET_AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "INFO"
    db_path: Path = Path(".data/market_agent.sqlite3")
    market_data_provider: str = "mock"
    finance_data_reader_lookback_days: int = 14
    krx_candidate_universe_limit: int = 30
    news_provider: str = "mock"
    report_mode: str = "compact"
    compact_news_limit: int = 3
    naver_client_id: str | None = None
    naver_client_secret: str | None = None
    naver_news_query: str = "한국 증시"
    naver_news_display: int = 5
    naver_news_timeout_seconds: float = 10.0
    telegram_dry_run: bool = True
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    timezone: str = "Asia/Seoul"

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def get_settings() -> Settings:
    return Settings()

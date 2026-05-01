# Architecture

## Runtime Shape

MVP는 명시적인 client, scoring, reporting, persistence, pipeline으로 구성된 작은 Python package다. 외부 연동은 protocol 뒤에 두어 pipeline logic을 다시 쓰지 않고 mock data를 real read-only data로 교체할 수 있게 한다.

## Modules

- `market_agent.config`: `pydantic-settings` 기반 configuration.
- `market_agent.logging`: structured JSON logging 설정.
- `market_agent.models`: market data, news, candidate, report, tracking에 쓰는 shared dataclass.
- `market_agent.clients`: protocol, mock market/news client, Telegram notifier.
- `market_agent.scoring`: deterministic candidate scoring and ranking.
- `market_agent.reports`: premarket, hourly, closing text formatting.
- `market_agent.db`: SQLite schema와 persistence helper.
- `market_agent.pipelines`: premarket, hourly tracking, closing workflow.
- `market_agent.scheduler`: APScheduler job definition과 KST market-session helper.
- `market_agent.main`: local CLI entry point.

## Data Flow

1. Premarket pipeline이 market snapshot과 news를 load한다.
2. Scoring이 candidate security를 순위화한다.
3. 상위 candidate를 daily watchlist로 저장한다.
4. Report formatter가 Telegram에 안전한 text report를 만든다.
5. Hourly pipeline이 최신 watchlist와 mock intraday price를 load한다.
6. Tracking snapshot을 저장하고 formatting한다.

## Extension Points

- `MockMarketDataClient`를 실제 KRX/global data client로 교체한다.
- `FinanceDataReaderKoreaMarketDataClient`는 국내 전일 지수 context만 read-only provider에서 가져오고, 미구현 영역은 mock delegate를 사용하되 리포트에 `MIXED`로 표시한다.
- `MockNewsClient`를 실제 news/search provider로 교체한다.
- `NaverNewsClient`는 Naver Search News API 응답을 `NewsItem`으로 최소 정규화하고, 실패는 data gap으로 리포트에 노출한다.
- notifier protocol을 구현해 Slack을 추가한다.
- SQLite schema로 감당하기 어려운 요구가 확인된 뒤에만 persistence를 확장한다.

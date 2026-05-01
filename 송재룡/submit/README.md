# My Stock Advisor

한국 시장 참고용 인텔리전스 agent MVP입니다. 기본적으로 mock data로 장전 관찰 후보 리포트를 만들고, Telegram dry-run 출력으로 전송하며, 선택된 KRX 거래 가능 후보의 장중 가상 성과를 추적합니다.

## Setup

```bash
uv sync
cp .env.example .env
```

## Run Locally

```bash
uv run market-agent premarket
uv run market-agent hourly
uv run market-agent closing
uv run market-agent scheduler
```

기본 설정은 mock data와 Telegram dry-run mode를 사용합니다. 실제 거래, 주문 실행, broker 계좌 변경 기능은 구현하지 않습니다.

## Test

```bash
uv run pytest
```

## Configuration

설정은 `MARKET_AGENT_` environment prefix를 사용합니다. 지원 변수는 `.env.example`을 참고하세요.

기본 `MARKET_AGENT_MARKET_DATA_PROVIDER=mock`은 deterministic mock data를 사용합니다. 국내 전일 시장 지수만 `FinanceDataReader` read-only provider로 연결하려면 `MARKET_AGENT_MARKET_DATA_PROVIDER=finance-data-reader`로 설정하세요. 이 경우 후보 선정과 장중 tracking fixture는 아직 mock data라 리포트가 `Data label: MIXED`로 표시됩니다. Provider 수집 실패 시 mock으로 조용히 대체하지 않고 리포트에 `데이터 수집 실패`가 표시됩니다.

`MARKET_AGENT_MARKET_DATA_PROVIDER=finance-data-reader`일 때 관찰 후보는 `FinanceDataReader.StockListing("KRX")` universe에서 거래대금/거래량 기반 1차 후보군을 만듭니다. `MARKET_AGENT_KRX_CANDIDATE_UNIVERSE_LIMIT`로 후보 universe 크기를 조정합니다. Universe 수집 실패 시 mock 후보를 fallback으로 사용하지만 compact report에 `후보 universe: fallback/mock`으로 표시합니다.

기본 `MARKET_AGENT_NEWS_PROVIDER=mock`은 deterministic mock news를 사용합니다. Naver Search News API를 사용하려면 `MARKET_AGENT_NEWS_PROVIDER=naver`, `MARKET_AGENT_NAVER_CLIENT_ID`, `MARKET_AGENT_NAVER_CLIENT_SECRET`을 설정하세요. Query는 `MARKET_AGENT_NAVER_NEWS_QUERY`, timeout은 `MARKET_AGENT_NAVER_NEWS_TIMEOUT_SECONDS`로 조정합니다. API 실패 시 mock으로 조용히 대체하지 않고 리포트에 `데이터 수집 실패`가 표시됩니다.

리포트는 기본 `MARKET_AGENT_REPORT_MODE=compact`로 Telegram에 읽기 쉬운 축약 포맷을 사용합니다. 기존 상세 포맷은 `MARKET_AGENT_REPORT_MODE=full`로 실행할 수 있습니다. Compact 뉴스 개수는 `MARKET_AGENT_COMPACT_NEWS_LIMIT`로 조정합니다. Telegram 전송은 긴 메시지를 문단 단위로 split하며, dry-run에서도 chunk 번호가 출력됩니다.

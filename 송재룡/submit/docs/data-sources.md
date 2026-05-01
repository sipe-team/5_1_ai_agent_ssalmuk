# Data Sources

## MVP Sources

현재 MVP는 deterministic mock client를 사용한다. Mock output에는 source name과 timestamp를 명확히 표시해야 하며, live data처럼 보이게 작성하지 않는다.

국내 전일 시장 지수는 선택적으로 `FinanceDataReaderKoreaMarketDataClient`를 통해 `FinanceDataReader` read-only provider에서 가져올 수 있다. 이 provider는 `KS11`, `KQ11`로 `KOSPI previous session`, `KOSDAQ previous session`만 live로 정규화한다. 후보 선정과 장중 가격은 mock client가 계속 담당한다. 이 혼합 상태는 리포트에서 `Data label: MIXED`로 드러나야 한다.

후보 universe는 `FinanceDataReader.StockListing("KRX")`에서 가져온 listing data를 1차 source로 사용한다. MVP에서는 `ticker`, `name`, `market`, `asset_type`, `previous_close`, `previous_change_pct`, `trading_value`, `volume`, `source`, `fetched_at`, `market_date`를 가능한 범위에서 정규화하고, 거래대금/거래량/전일 변동률 기반의 얕은 scoring input으로만 사용한다. Universe 수집 실패 시 mock 후보를 fallback으로 쓰되 리포트에 `fallback/mock` 상태를 표시한다.

뉴스는 선택적으로 `NaverNewsClient`를 통해 Naver Search News API에서 가져올 수 있다. `MARKET_AGENT_NEWS_PROVIDER=naver`, `MARKET_AGENT_NAVER_CLIENT_ID`, `MARKET_AGENT_NAVER_CLIENT_SECRET`을 설정해야 한다. 외부 응답은 `title`, `source`, `published_at`, `url`, `snippet`, `raw_keyword`, `fetched_at` 중심의 `NewsItem`으로 최소 정규화한다. API 실패나 credential 누락은 mock fallback 없이 `데이터 수집 실패` news item으로 리포트에 드러나야 한다.

## Market Data Needed Later

- 전일 한국 market index performance.
- 전일 미국 market index performance.
- KRX 거래 가능 stock 및 ETF universe.
- 선정된 candidate의 open, latest, close price.
- 선택적으로 valuation 및 quality metric.

## News Data Needed Later

- 한국 시장 뉴스.
- 글로벌 macro 및 sector 뉴스.
- 미국 overnight market narrative.
- Source name, publication timestamp, title, URL, snippet, raw keyword, fetched timestamp.

## Client Contract

Market client는 snapshot, candidate security, intraday price를 제공해야 한다. News client는 timestamp가 있는 news item list를 제공해야 한다. Pipeline은 data가 mock인지 real인지에 따라 business logic을 바꾸지 않아야 하며, report 단계에서 mock/live 상태를 명확히 표시해야 한다.

## Safety

- Mock data와 live data를 조용히 섞지 않는다.
- Live provider의 timestamp를 지어내지 않는다.
- Real provider에서 필수 data가 빠지면 조용히 진행하지 말고 명확히 실패한다.
- Live data를 쓰더라도 출력은 참고용 관찰 후보와 리스크 설명으로 제한한다.
- Provider 실패 시 mock으로 조용히 대체하지 말고 리포트에 `데이터 수집 실패`를 표시한다.
- Naver news provider는 분류, 중복 제거, keyword 필터링 없이 provider 응답을 최소 정규화한다.

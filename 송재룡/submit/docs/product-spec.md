# Product Spec

## Goal

매일 장전 리포트를 생성하고, KRX 거래 가능 종목/ETF 5개를 참고용 관찰 후보로 선정하며, 장중 가상 성과를 추적하는 한국 시장 인텔리전스 agent를 만든다.

## MVP User Flow

1. 08:00 `Asia/Seoul` 기준으로 mock market, news, macro context를 수집한다.
2. 뉴스와 시장 흐름에서 theme를 추출하고 관련 stock 또는 ETF를 scoring한다.
3. 상위 5개 candidate를 리서치 목적의 watchlist로 저장한다.
4. 장전 리포트를 Telegram으로 보낸다. 기본값은 dry-run 출력이다.
5. 한국 정규장 중 선정 후보를 시가에 매수했다고 가정한 시나리오 성과를 추적한다.
6. 09:00부터 15:30 KST까지 hourly tracking update를 보낸다.
7. 장 마감 후 closing summary를 보낸다.

## Non-Goals

- 실제 거래를 하지 않는다.
- 주문 실행 기능을 만들지 않는다.
- broker 계좌 연동을 하지 않는다.
- 개인화된 금융 조언을 제공하지 않는다.

## Product Constraints

- Timezone: `Asia/Seoul`.
- Runtime: uv로 관리하는 Python 3.12.
- Scheduler: APScheduler.
- Persistence: SQLite first.
- Notification: Telegram first, Slack은 이후 선택 확장.
- Report에는 source name과 data timestamp를 반드시 포함한다.
- 투자 관련 문구는 단정하지 않고 관찰 후보, 시나리오, 리스크, 참고용 표현을 사용한다.

## MVP Acceptance Criteria

- 개발자가 mock data로 장전 리포트를 로컬 실행할 수 있다.
- 시스템이 선정 후보를 저장하고 이후 hourly tracking에서 재사용한다.
- scoring, report formatting, scheduler time behavior를 다루는 테스트가 있다.
- Telegram은 credential과 dry-run override가 명시되기 전까지 dry-run mode를 기본값으로 유지한다.

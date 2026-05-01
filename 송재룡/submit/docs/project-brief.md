# Project Brief

## Goal

한국 시장을 대상으로 한 참고용 인텔리전스 agent를 만든다.

## Core Requirements

1. 매일 08:00 `Asia/Seoul` 기준으로 다음 정보를 분석한다.
   - 전일 한국 시장 흐름
   - 전일 미국 시장 흐름
   - 한국 및 글로벌 뉴스
   - macro context

2. 시장 데이터와 뉴스 흐름을 결합해 장전 리포트를 만든다.

3. 리포트는 우선 Telegram으로 보낸다. Slack은 선택 확장 항목이다.

4. 추출된 theme와 관련된 주식/ETF 5개를 참고용 관찰 후보로 선정한다. 기준은 다음과 같다.
   - theme relevance
   - positive catalyst
   - valuation
   - quality
   - risk

5. 한국 정규장 중에는 선정된 KRX 거래 가능 후보를 시가에 매수했다고 가정한 시나리오 성과를 추적한다.

6. 장 마감 전까지 hourly update를 보낸다.

## Constraints

- 실제 주문 실행은 하지 않는다.
- 출력은 참고용 리서치/관찰 후보 정보로만 다룬다.
- 시간대는 `Asia/Seoul`을 사용한다.
- 데이터 timestamp와 source name을 포함한다.
- 완벽한 architecture보다 빠르게 동작하는 MVP를 우선한다.
- Python 3.12, uv, APScheduler, SQLite를 먼저 사용한다.
- Telegram을 우선하고 Slack은 선택 사항으로 둔다.

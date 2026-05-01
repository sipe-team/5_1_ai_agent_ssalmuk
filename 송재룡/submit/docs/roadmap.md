# Roadmap

## Slice 1: Vertical Mock MVP

- Mock market 및 news client.
- SQLite persistence.
- Premarket report pipeline.
- Hourly 및 closing tracking pipeline.
- Telegram dry-run notifier.
- Focused test.

## Slice 2: Real Read-Only Data

- Market client protocol 뒤에 실제 market data provider 하나를 연결한다.
- News client protocol 뒤에 실제 news provider 하나를 연결한다.
- Provider health check와 timestamp validation을 추가한다.
- Live data 사용 시 mock/live labeling과 source timestamp를 유지한다.

## Slice 3: Operations

- Scheduler를 long-lived process로 실행한다.
- Deployment note를 추가한다.
- Failed job alerting을 추가한다.
- Database backup guidance를 추가한다.

## Slice 4: Report Quality

- Theme extraction을 개선한다.
- Source link를 추가한다.
- Real provider에서 valuation/quality data를 추가한다.
- End-of-day attribution을 추가하되, 참고용 가상 성과와 리스크 중심으로 표현한다.

## Explicitly Out of Scope

- Real trading.
- Broker integration.
- Order placement.
- Account mutation.
- 수익 보장, 매수 추천, 예측 확정 표현.

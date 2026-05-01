# Report Contract

## Required Report Metadata

- Report type.
- `Asia/Seoul` 기준 generation timestamp.
- Source name.
- Data timestamp.
- Mock/live data labeling.

## Premarket Report Sections

- 날짜와 report type이 포함된 header.
- 한국 및 미국 시장 context.
- News theme.
- 상위 5개 watchlist candidate.
- Risk note와 research-only disclaimer.

## Candidate Fields

- Ticker.
- Name.
- Theme.
- Score.
- Positive catalyst.
- Valuation note.
- Quality note.
- Risk note.

## Hourly Tracking Sections

- Timestamp가 포함된 header.
- Assumption: 시가에 가상 매수한 시나리오.
- Candidate table: open, latest, return percent.
- Research-only disclaimer.

## Closing Summary Sections

- Timestamp가 포함된 header.
- 가상 성과 기준 best/worst performer.
- Average simulated return.
- Data source와 mock/live status에 대한 note.

## Language Guardrails

- 리포트는 투자 조언이 아니라 참고용 리서치 정보로 표현한다.
- `추천`, `확정`, `보장`, `예측 확정`처럼 단정적인 표현을 피한다.
- `관찰 후보`, `시나리오`, `리스크`, `참고용`, `가상 성과` 표현을 우선 사용한다.

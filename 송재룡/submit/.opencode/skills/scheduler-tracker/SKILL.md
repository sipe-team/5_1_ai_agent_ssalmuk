# Scheduler Tracker Skill

Schedule definition 또는 intraday tracking을 변경할 때 사용하는 skill입니다.

## Workflow

1. `docs/product-spec.md`와 `docs/architecture.md`를 읽는다.
2. `Asia/Seoul` timezone semantics를 보존한다.
3. 08:00 premarket, 정규장 hourly tracking, closing summary의 scheduler definition을 명시적으로 유지한다.
4. Time-window가 바뀌면 scheduler test를 갱신한다.
5. Tracking은 open price 기준의 simulated scenario로만 유지한다.

## Safety

- 실제 거래나 주문 실행을 추가하지 않는다.
- Tracking output은 가상 성과와 참고용 시나리오로 설명한다.

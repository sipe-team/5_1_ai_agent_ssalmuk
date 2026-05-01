# Report Pipeline Skill

Report generation 또는 delivery를 변경할 때 사용하는 skill입니다.

## Workflow

1. `docs/report-contract.md`, `docs/product-spec.md`, `docs/architecture.md`를 읽는다.
2. Contract가 갱신되지 않는 한 report section을 안정적으로 유지한다.
3. Source name, data timestamp, mock/live labeling을 포함한다.
4. Telegram dry-run behavior를 기본적으로 안전하게 유지한다.
5. Report contract가 바뀌면 formatting test를 갱신한다.

## Safety

- Report는 참고용 리서치/관찰 후보 정보로만 표현한다.
- 개인화된 금융 조언처럼 보이는 문구를 사용하지 않는다.
- `추천`, `확정`, `보장`, `예측 확정`처럼 단정적인 투자 표현을 피한다.

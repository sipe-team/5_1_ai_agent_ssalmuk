# Wire Real Data

Mock data source를 read-only real provider로 교체할 때 사용하는 command입니다.

## Steps

1. `docs/data-sources.md`, `docs/architecture.md`, `docs/report-contract.md`를 읽는다.
2. Contract가 부족하지 않다면 기존 client protocol을 안정적으로 유지한다.
3. Provider configuration은 `pydantic-settings`와 `.env.example`에 추가한다.
4. Provider timestamp와 source name을 검증한다.
5. Test와 local run을 위해 mock client를 유지한다.
6. Mocked provider response를 사용한 focused test를 추가한다.

## Guardrails

- Read-only data만 다룬다.
- Broker 또는 account mutation을 추가하지 않는다.
- Real data에서 mock data로 조용히 fallback하지 않는다. 필요하면 report에 명확히 표시한다.
- Live data 기반 출력도 참고용 관찰 후보와 리스크 설명으로 제한한다.

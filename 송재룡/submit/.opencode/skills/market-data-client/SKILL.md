# Market Data Client Skill

Market data integration을 변경할 때 사용하는 skill입니다.

## Workflow

1. `docs/data-sources.md`와 `docs/architecture.md`를 읽는다.
2. Real provider에 문서화된 contract 변경이 필요하지 않다면 market client protocol을 보존한다.
3. Test를 위한 deterministic mock fixture를 유지한다.
4. 반환 model에 source name과 provider timestamp를 포함한다.
5. 필수 live data가 빠지면 명확히 실패한다.

## Safety

- Trading, broker, account mutation behavior를 추가하지 않는다.
- Report output에서 mock data는 mock으로 표시한다.
- Live data를 지어내지 않고, timestamp를 임의로 만들지 않는다.

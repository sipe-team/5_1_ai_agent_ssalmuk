# Bootstrap MVP

Vertical MVP 기반을 새로 만들거나 정리할 때 사용하는 command입니다.

## Steps

1. `docs/project-brief.md`, `docs/product-spec.md`, `docs/architecture.md`를 읽는다.
2. `AGENTS.md`가 짧게 유지되고 상세 spec을 중복하지 않는지 확인한다.
3. 상세 요구사항은 `opencode.jsonc` instruction이 아니라 `docs/*.md`에 둔다.
4. Mock 가능한 client를 유지하면서 가장 얇은 end-to-end slice를 구현한다.
5. 완료 보고 전에 focused test로 동작을 확인한다.

## Guardrails

- Telegram은 기본적으로 dry-run 안전 모드로 유지한다.
- 실제 거래, broker 주문, 계좌 변경 기능은 구현하지 않는다.
- `Asia/Seoul` scheduling semantics를 보존한다.
- 출력은 투자 조언이 아니라 참고용 관찰 후보와 시나리오 정보로 표현한다.

# Scoring Policy

## Purpose

Scoring은 참고용 watchlist candidate의 우선순위를 정하기 위한 것이다. Trading signal이 아니며 주문 실행을 유발해서는 안 된다.

## MVP Score Components

각 component는 0부터 1까지 점수화한다.

- Theme relevance: 35%.
- Positive catalyst: 25%.
- Valuation attractiveness: 15%.
- Business quality: 15%.
- Risk control: 10%.

## Risk Handling

Risk가 높을수록 risk-control component는 낮아진다. Real client는 scoring 전에 심각한 missing data가 있는 candidate를 제외해야 한다. Mock client는 완전하고 deterministic한 fixture를 사용한다.

## Tie-Breaking

Deterministic output을 위해 score descending, ticker ascending 순서로 정렬한다.

## Change Control

Scoring weight를 바꾸는 변경은 같은 변경 안에서 test와 이 문서를 함께 갱신해야 한다.

## Language Guardrails

Score는 후보 간 비교를 위한 참고 지표다. 높은 score를 수익 가능성 확정이나 매수 추천으로 표현하지 않는다.

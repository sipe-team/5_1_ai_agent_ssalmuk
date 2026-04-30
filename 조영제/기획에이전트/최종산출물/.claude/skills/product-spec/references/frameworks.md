# PM 프레임워크 참조 (PM Frameworks Reference)

SKILL.md의 Step 2(디스커버리)와 Step 4(구조화)에서 참조됩니다.
각 프레임워크는 적용 시점, 공식/템플릿, 한국어 용어를 포함합니다.

## Opportunity Solution Tree (Teresa Torres)

**출처**: Teresa Torres, *Continuous Discovery Habits* (2021)
**적용 시점**: Step 2 — 문제 공간 탐색 시
**구조**:
- Level 1: 비즈니스 성과 (Outcome)
- Level 2: 기회 (Opportunity) — 사용자 니즈, 페인포인트, 욕구
- Level 3: 솔루션 (Solution) — 각 기회에 대한 해결책
- Level 4: 실험 (Experiment) — 솔루션 검증 방법

**활용법**: 기획서의 "배경 및 문제 정의" 섹션에서 문제를 구조화할 때 사용.
사용자 인터뷰 결과를 기회로 매핑하고, 각 기회에 대해 솔루션을 도출.

## JTBD — Jobs To Be Done (Anthony Ulwick / Clayton Christensen)

**출처**: Anthony Ulwick, *What Customers Want* (2005); Clayton Christensen, *Competing Against Luck* (2016)
**적용 시점**: Step 2 — 사용자 니즈 정의 시
**공식**: "When [상황], I want to [동기], so I can [기대 결과]"
**한국어 변환**: "[상황]일 때, [동기]하고 싶다. 그래야 [기대 결과]할 수 있으니까."

**활용법**: 기획서의 "사용자 정의" 섹션에서 페르소나의 Job을 정의할 때 사용.

## RICE Scoring (Intercom)

**출처**: Sean McBride, Intercom (2016)
**적용 시점**: Step 4 — 요구사항 우선순위 결정 시
**공식**: `RICE = (Reach × Impact × Confidence) / Effort`
- Reach: 일정 기간 내 영향받는 사용자 수 (숫자)
- Impact: 개인당 영향도 (3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal)
- Confidence: 추정 확신도 (100%=high, 80%=medium, 50%=low)
- Effort: 소요 인력-월 (person-months)

**활용법**: 기능 요구사항의 우선순위(P0/P1/P2) 결정 근거로 사용.

## ICE Scoring

**적용 시점**: RICE보다 빠른 우선순위 결정이 필요할 때
**공식**: `ICE = Impact × Confidence × Ease`
- 각 항목 1~10 스케일
- Impact: 목표 달성 기여도
- Confidence: 성공 확신도
- Ease: 구현 용이성

## INVEST Criteria (Bill Wake)

**출처**: Bill Wake (2003)
**적용 시점**: Step 4 — 유저 스토리 품질 검증 시
**체크리스트**:
- **I**ndependent (독립적): 다른 스토리와 독립적으로 개발/배포 가능한가?
- **N**egotiable (협상 가능): 구현 방식에 유연성이 있는가?
- **V**aluable (가치 있는): 사용자 또는 비즈니스에 명확한 가치를 제공하는가?
- **E**stimable (추정 가능): 개발팀이 규모를 추정할 수 있는가?
- **S**mall (작은): 한 스프린트 내에 완료할 수 있는 크기인가?
- **T**estable (테스트 가능): 명확한 인수 조건이 있는가?

**활용법**: 모든 유저 스토리는 INVEST 6개 항목을 통과해야 기획서에 포함.

## Kano Model (Noriaki Kano)

**출처**: Noriaki Kano (1984)
**적용 시점**: Step 4 — 기능 분류 시
**카테고리**:
- **필수 (Must-be)**: 없으면 불만, 있어도 당연 → P0
- **성능 (Performance)**: 많을수록 만족 → P1
- **매력 (Delighter)**: 없어도 불만 없지만, 있으면 감동 → P2
- **무관심 (Indifferent)**: 있든 없든 상관없음 → 범위 외
- **역효과 (Reverse)**: 있으면 오히려 불만 → 제거

**활용법**: 기능 요구사항에 Kano 카테고리를 태깅하여 우선순위 결정 보조.

## Lean Canvas (Ash Maurya)

**출처**: Ash Maurya, *Running Lean* (2012)
**적용 시점**: Step 2 — 초기 단계 제품/기능의 전체 그림 파악 시
**9개 블록**: 문제, 고객 세그먼트, 고유 가치 제안, 솔루션, 채널, 수익원, 비용구조, 핵심 지표, 경쟁 우위

**활용법**: 신규 제품이나 큰 기능의 PRD 작성 전 전체 비즈니스 맥락을 정리할 때 사용.

## MoSCoW Prioritization

**적용 시점**: Step 4 — 요구사항 우선순위 결정의 대안
**카테고리**:
- **Must have**: 없으면 출시 불가
- **Should have**: 중요하지만 없어도 출시 가능
- **Could have**: 있으면 좋지만 필수는 아님
- **Won't have (this time)**: 이번엔 안 함, 명시적으로 제외

**활용법**: RICE 점수화가 과한 경우, 빠른 분류에 사용.

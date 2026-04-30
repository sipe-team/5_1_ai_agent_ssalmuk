# 기획서 타입별 템플릿 (Spec Type Templates)

이 문서는 기획서 타입별 상세 템플릿을 정의합니다. SKILL.md의 Step 4에서 참조됩니다.

---

## PRD

PRD (제품 요구사항 정의서)는 **기본 기획서 타입**입니다. 가장 상세하며, 모든 이해관계자(개발자, 디자이너, PM)가 참조하는 마스터 문서입니다.

### 템플릿 구조

```
[REQUIRED] 1. 개요 (Overview)
```
- 문서 제목, 작성자, 작성일, 버전, 상태(초안/검토중/확정)
- 한 줄 요약: 이 기획서가 다루는 것
- 관련 문서 링크 (있는 경우)

```
[REQUIRED] 2. 이해관계자 맵 (Stakeholder Map — RACI)
```

| 역할 | 이름/팀 | R (실행) | A (승인) | C (협의) | I (통보) |
|------|--------|---------|---------|---------|---------|
| PM | | ✓ | | | |
| 개발 리드 | | | | ✓ | |
| 디자인 | | | | ✓ | |
| QA | | | | | ✓ |

- 의사결정 프로세스: 누가 최종 승인하는가?
- 리뷰 주기: 주간/격주/마일스톤별

```
[REQUIRED] 3. 배경 및 문제 정의 (Background & Problem Definition)
```
- 현재 상황 (As-Is)
- 문제점 또는 기회
- 이 문제를 지금 해결해야 하는 이유
- 영향 받는 사용자/시스템

```
[REQUIRED] 4. 목표 및 성공 지표 (Goals & Success Metrics)
```
- 비즈니스 목표 (measurable)
- 사용자 목표
- 성공 지표 (KPI): 지표명, 현재값, 목표값, 측정방법
- 비목표 (Non-goals): 명시적으로 이번 범위에서 제외하는 것

```
[REQUIRED] 5. 사용자 정의 (User Definition)
```
- 대상 사용자 페르소나
- 사용자 세그먼트별 니즈
- 사용자 여정 요약

```
[REQUIRED] 6. 요구사항 (Requirements)
```
- 기능 요구사항 (Functional): ID, 설명, 우선순위(P0/P1/P2), 인수 조건
- 비기능 요구사항 (Non-functional): 성능, 보안, 확장성, 접근성
  **비기능 요구사항 상세 템플릿 (NFR Detail)**:

  | 항목 | 수치 목표 | 현재 베이스라인 | 측정 방법 |
  |------|----------|-------------|----------|
  | API 응답시간 (p95) | < 500ms | 850ms | APM 모니터링 |
  | 처리량 (TPS) | > 100 req/s | 45 req/s | 부하 테스트 |
  | 에러율 | < 0.1% | 0.3% | 서버 로그 |
  | 가용성 (SLA) | 99.95% | 99.9% | 업타임 모니터링 |

- 기술 제약사항: 사용 기술 스택, 호환성, 의존성

**사이드이펙트 영향 테이블 (Side Effect Impact)**:

| 영향 받는 기능/시스템 | 변경 내용 | 회귀 테스트 필요 | 회귀 TC ID | 우선순위 |
|-------------------|----------|---------------|-----------|---------|
| 예: 주문 내역 | 결제수단 표시 변경 | Y | TC-ORDER-001 | P1 |

```
[REQUIRED] 7. 사용자 시나리오 (User Scenarios)
```
- 핵심 시나리오 (Happy Path)
- 엣지 케이스
- 에러 시나리오
- 각 시나리오: Given/When/Then 형식
- 각 시나리오에 TC ID 부여: `TC-{기능}-{번호}` (예: TC-PAY-001)

```
[REQUIRED] 8. 인터랙션 명세 (Interaction Specification)
```
개발자가 구현 시 되묻지 않도록, 모든 사용자 인터랙션을 명시합니다.

**8-1. 클릭 명세 (Click Specification)**

화면별 모든 클릭 가능한 요소의 동작을 정의합니다.

| 화면 | 요소 | 컴포넌트 | 액션 | 동작 | 네비게이션 | 비고 |
|------|------|----------|------|------|-----------|------|
| 상품 상세 | "바로 구매" 버튼 | Button/primary | tap | 결제 확인 화면 표시 | push | 로그인 필요, 비로그인 시 로그인 화면 push |
| 결제 확인 | "배송지 변경" 링크 | TextLink/secondary | tap | 배송지 목록 모달 표시 | modal | 선택 후 자동 닫힘 |
| 결제 확인 | "결제하기" 버튼 | Button/primary | tap | 결제 API 호출 | - | 중복 탭 방지 (debounce 500ms) |
| 결제 확인 | "← 뒤로" | NavBar/back | tap | 이전 화면 복귀 | pop | 결제 진행 중이면 확인 다이얼로그 |
| 결제 완료 | "주문 상세 보기" | Button/tertiary | tap | 주문 상세 화면 이동 | replace | 결제 확인 화면을 스택에서 제거 |

네비게이션 타입:
- `push`: 스택에 추가 (뒤로 가기 가능)
- `replace`: 현재 화면 교체 (뒤로 가기 시 이전-이전 화면)
- `pop`: 스택에서 제거 (뒤로 가기)
- `modal`: 오버레이로 표시 (닫기 가능)
- `deeplink`: 외부에서 진입 가능한 URL 경로

**8-2. UI 상태 명세 (UI State Specification)**

각 화면/컴포넌트의 4가지 필수 상태를 정의합니다.

| 화면/컴포넌트 | 로딩 (Loading) | 성공 (Success) | 빈 값 (Empty) | 에러 (Error) |
|-------------|---------------|---------------|--------------|-------------|
| 결제수단 목록 | 스켈레톤 UI (카드 3장 형태) | 저장된 카드 목록 표시 | "저장된 결제수단이 없습니다. + 새 카드 등록" | "결제수단을 불러올 수 없습니다. + 다시 시도" |
| 배송지 목록 | 스켈레톤 UI | 최근 주소 목록 | "저장된 주소가 없습니다. + 새 주소 입력" | "주소를 불러올 수 없습니다. + 다시 시도" |
| 결제 처리 | 전체 화면 로딩 + "결제 처리 중..." + 예상 시간 | 결제 완료 화면으로 replace | - | 에러 메시지 + "다시 시도" 버튼 |

각 상태에 대해:
- **로딩**: 스켈레톤 UI / 스피너 / 프로그레스 바 중 어떤 것? 최소 표시 시간은?
- **성공**: 정상 데이터 표시. 애니메이션 필요 여부.
- **빈 값 (Empty/Nil)**: 데이터가 0건일 때 표시할 내용. CTA(Call To Action) 버튼 포함 여부.
- **에러**: 에러 메시지 텍스트, 재시도 버튼 여부, 자동 재시도 여부, 폴백 동작.

**8-3. 폼 & 입력 명세 (Form & Input Specification)**

| 필드 | 타입 | 필수 | 유효성 검증 | 에러 메시지 | 비고 |
|------|------|------|-----------|-----------|------|
| 카드 번호 | text (숫자만) | Y | 16자리, Luhn 체크 | "유효한 카드 번호를 입력해주세요" | 4자리마다 자동 공백 |
| 유효기간 | text | Y | MM/YY, 미래 날짜 | "만료된 카드입니다" | MM/YY 자동 포맷 |
| CVC | password | Y | 3~4자리 숫자 | "CVC를 확인해주세요" | 마스킹 처리 |

**8-4. 페이지 전환 흐름 (Navigation Flow)**

```
[시작] → 상품 상세 (push)
  └─ "바로 구매" → 결제 확인 (push)
       ├─ "배송지 변경" → 배송지 목록 (modal) → 선택 → 닫힘
       ├─ "결제수단 변경" → 결제수단 목록 (modal) → 선택 → 닫힘
       ├─ "결제하기" → 결제 처리 (로딩) → 결제 완료 (replace)
       │    └─ "주문 상세" → 주문 상세 (push)
       └─ "← 뒤로" → 상품 상세 (pop)
```

**8-5. 상태 관리 힌트 (State Management Hints)**

주요 데이터의 상태 관리 방식을 명시합니다. 개발자가 로컬 상태/글로벌 상태/서버 캐시를 판단하는 데 사용됩니다.

| 데이터 | 유형 | 캐시 전략 | 무효화 트리거 |
|--------|------|----------|-------------|
| 예: 결제수단 목록 | 서버 상태 (캐시) | 5분 TTL | 새 카드 등록 시 |
| 예: 선택한 배송지 | 페이지 로컬 | - | 페이지 이탈 시 초기화 |
| 예: 로그인 사용자 정보 | 글로벌 상태 | 세션 유지 | 로그아웃 시 |

유형 분류:
- **서버 상태 (캐시)**: API에서 가져와 캐시. React Query/SWR 등 사용.
- **글로벌 상태**: 여러 화면에서 공유. 인증, 설정 등.
- **페이지 로컬**: 해당 화면에서만 사용. 폼 입력값, 선택 상태 등.

**8-6. 디자인 핸드오프 체크리스트 (Design Handoff)**

| 항목 | 내용 |
|------|------|
| 디자인 파일 링크 | Figma / Sketch / Zeplin URL (있는 경우) |
| 반응형 브레이크포인트 | 어떤 해상도에서 레이아웃이 변하는가? |
| 디자인 QA 기준 | 픽셀 퍼펙트 vs 구조 일치 중 어느 수준? |

**반응형 레이아웃 명세**:

| 브레이크포인트 | 해상도 | 레이아웃 변화 |
|-------------|--------|-------------|
| Mobile | < 768px | 1열, 하단 고정 CTA |
| Tablet | 768px~1024px | 2열, 사이드바 축소 |
| Desktop | > 1024px | 3열, 풀 네비게이션 |

> 프로젝트별 브레이크포인트가 다르면 이 기본값을 수정하세요.

```
[CONDITIONAL REQUIRED] 9. API 명세 (API Specification) — 외부/내부 API가 1개 이상이면 필수
```
- 엔드포인트 목록
- Request/Response 스키마
- 에러 코드 정의
- 인증/인가 요구사항

```
[CONDITIONAL REQUIRED] 10. 데이터 모델 (Data Model) — DB 변경이 있으면 필수
```
- 엔티티 정의
- 관계 (Relationships)
- 주요 필드 및 타입
- 인덱스/제약조건

```
[CONDITIONAL REQUIRED] 11. 보안 기준선 (Security Baseline) — 사용자 데이터 처리 시 필수
```

| 항목 | 내용 |
|------|------|
| 인증 방식 | JWT / OAuth2 / API Key / 세션 등 + 토큰 만료 정책 |
| 인가 모델 | 누가 이 기능을 사용할 수 있는가? (역할/권한 기준) |
| PII 포함 여부 | 개인정보 필드 목록 + 암호화/마스킹 처리 방침 |
| 감사 로그 | 필요 여부 + 보존 기간 |

```
[REQUIRED] 12. 스코프 테이블 (Scope Table)
```
In/Out/Future 3열 테이블로 범위를 명시합니다.

| 항목 | In (이번 범위) | Out (이번에 안 함) | Future (향후 검토) |
|------|--------------|-------------------|------------------|
| 예시 | 원클릭 결제 | 해외 결제 | 정기구독 결제 |
| 예시 | 배송지 자동입력 | 포인트 결제 | 쿠폰 통합 |

- In: 이번 PRD에서 다루는 기능. 요구사항 섹션과 1:1 매칭되어야 함
- Out: 명시적으로 이번에 하지 않는 것. 이유 필수
- Future: 이후 버전에서 검토할 것. 예상 시기 명시 권장

```
[REQUIRED] 13. 일정 및 마일스톤 (Timeline & Milestones)
```
- 주요 마일스톤 (최소 3개)
- 크리티컬 패스 의존성
- 외부 블로커
- 예상 일정

**크로스팀 의존성 (Cross-team Dependencies)**:

| 의존 팀/시스템 | 필요한 것 | 제공 예상일 | 담당자 | 블로킹 여부 |
|-------------|----------|-----------|--------|-----------|

**일정 추정 가이드 (Estimation Guide)**:

| 항목 | 내용 |
|------|------|
| 예상 총 스토리 포인트 | 요구사항 기반 SP 합계 |
| 팀 velocity | 스프린트당 처리 가능 SP (최근 3스프린트 평균) |
| 필요 스프린트 수 | 총 SP ÷ velocity |
| 버퍼 | 추정치 × 1.3 (안정적) ~ 1.5 (불확실성 높음) |
| 최종 예상 기간 | 필요 스프린트 × 스프린트 길이 + 버퍼 |

> velocity 데이터가 없으면 "예상 총 SP + 불확실성 수준(상/중/하)"만 기재합니다.

```
[REQUIRED] 14. 리스크 및 완화 방안 (Risks & Mitigation)
```
- 기술적 리스크
- 비즈니스 리스크
- 각 리스크: 발생 확률, 영향도, 완화 방안

```
[CONDITIONAL REQUIRED] 15. 기술 부채 영향 (Tech Debt Impact) — 기존 시스템 변경 시 필수
```

| 항목 | 내용 |
|------|------|
| 영향 받는 레거시 코드 | 변경 대상 레거시 코드/시스템 목록 |
| 하위 호환성 | API v1 유지 여부, 기존 클라이언트 영향 |
| 마이그레이션 필요 | DB 마이그레이션 여부, 무중단 가능 여부 |
| 발생하는 부채 | 이 기능으로 인해 새로 생기는 기술 부채 |
| 부채 상환 계획 | 언제, 어떻게 해결할 것인지 |

```
[OPTIONAL] 16. 런치 플랜 (Launch Plan)
```

- 롤아웃 전략: 전체 공개 / 점진적 (대상 %, 세그먼트)
- 측정 대시보드: 성공 지표 모니터링 위치
- 리뷰 일정: 출시 후 1주/4주/12주 리뷰 기준
- 롤백 트리거: 어떤 지표가 어떤 수준이면 롤백

```
[OPTIONAL] 17. 부록 (Appendix)
```
- 참고 자료
- 관련 문서 링크
- 용어 정의

```
[REQUIRED] 18. 변경 로그 (Change Log)
```

| 날짜 | 유형 | 대상 | 변경 내용 | 사유 |
|------|------|------|----------|------|

- 유형: ADD / MODIFY / REMOVE / SPLIT / DEFER
- 모든 변경에 사유 필수
- 기획서 최초 작성 시 "Initial draft" 한 줄로 시작

### 섹션 요약

| 번호 | 섹션 | 필수 여부 |
|------|------|-----------|
| 1 | 개요 (Overview) | REQUIRED |
| 2 | 이해관계자 맵 (Stakeholder Map — RACI) | REQUIRED |
| 3 | 배경 및 문제 정의 (Background & Problem Definition) | REQUIRED |
| 4 | 목표 및 성공 지표 (Goals & Success Metrics) | REQUIRED |
| 5 | 사용자 정의 (User Definition) | REQUIRED |
| 6 | 요구사항 (Requirements) + 사이드이펙트 영향 테이블 | REQUIRED |
| 7 | 사용자 시나리오 (User Scenarios) | REQUIRED |
| 8 | 인터랙션 명세 (Interaction Specification) | REQUIRED |
| 8-1 | └ 클릭 명세 (Click Specification) | REQUIRED |
| 8-2 | └ UI 상태 명세 — 로딩/성공/빈값/에러 (UI State) | REQUIRED |
| 8-3 | └ 폼 & 입력 명세 (Form & Input) | REQUIRED |
| 8-4 | └ 페이지 전환 흐름 (Navigation Flow) | REQUIRED |
| 8-5 | └ 상태 관리 힌트 (State Management Hints) | REQUIRED |
| 8-6 | └ 디자인 핸드오프 체크리스트 + 반응형 명세 (Design Handoff) | REQUIRED |
| 9 | API 명세 (API Specification) | CONDITIONAL REQUIRED |
| 10 | 데이터 모델 (Data Model) | CONDITIONAL REQUIRED |
| 11 | 보안 기준선 (Security Baseline) | CONDITIONAL REQUIRED |
| 12 | 스코프 테이블 (Scope Table — In/Out/Future) | REQUIRED |
| 13 | 일정 및 마일스톤 (Timeline & Milestones) + 크로스팀 의존성 | REQUIRED |
| 14 | 리스크 및 완화 방안 (Risks & Mitigation) | REQUIRED |
| 15 | 기술 부채 영향 (Tech Debt Impact) | CONDITIONAL REQUIRED |
| 16 | 런치 플랜 (Launch Plan) | OPTIONAL |
| 17 | 부록 (Appendix) | OPTIONAL |
| 18 | 변경 로그 (Change Log) | REQUIRED |

---

## Feature Spec

Feature Spec (기능 명세서)은 **단일 기능**에 집중하는 기획서입니다. PRD보다 좁은 범위를 다루며, 개발자가 바로 구현에 들어갈 수 있을 정도의 상세도를 목표로 합니다.

### 템플릿 구조

```
[REQUIRED] 1. 기능 개요 (Feature Overview)
```
- 기능명
- 한 줄 설명
- 관련 PRD 또는 에픽 링크
- 우선순위 (P0/P1/P2)
- 담당자
- 연관 팀: 이 기능에 영향 받거나 협업이 필요한 팀

```
[REQUIRED] 2. 유저 스토리 (User Stories)
```
- As a [사용자 유형], I want [행동], so that [가치]
- 각 스토리에 대한 우선순위
- 스토리 간 의존 관계

```
[REQUIRED] 3. 기능 요구사항 상세 (Functional Requirements Detail)
```
- 기능 ID별 상세 동작 정의
- 입력값 / 출력값 명세
- 비즈니스 로직 규칙
- 상태 전이 (State Transitions)
- 유효성 검증 규칙 (Validation Rules)

```
[REQUIRED] 4. UI/UX 요구사항 및 인터랙션 명세 (UI/UX & Interaction Specification)
```
- 화면 흐름 (Screen Flow)
- 와이어프레임 또는 디자인 참조

**클릭 명세**: 화면별 클릭 가능 요소 테이블
| 화면 | 요소 | 컴포넌트 | 액션 | 동작 | 네비게이션(push/replace/pop/modal) | 비고 |

**UI 상태 명세**: 화면/컴포넌트별 4가지 필수 상태
| 화면/컴포넌트 | 로딩 (Loading) | 성공 (Success) | 빈 값 (Empty) | 에러 (Error) |

**폼 & 입력 명세**: 입력 필드별 유효성 검증
| 필드 | 타입 | 필수 | 유효성 검증 | 에러 메시지 | 비고 |

**페이지 전환 흐름**: 화면 간 네비게이션 트리
- push: 스택 추가 (뒤로 가기 가능)
- replace: 현재 화면 교체
- pop: 스택 제거
- modal: 오버레이

- 반응형 동작 (Responsive Behavior)
- 중복 탭 방지 (debounce) 규칙
- 권한/로그인 상태별 분기

```
[REQUIRED] 5. API 명세 (API Specification)
```
- 엔드포인트: Method, Path, 설명
- Request 스키마 (Headers, Body, Query Params)
- Response 스키마 (Success, Error)
- 에러 코드 및 메시지 정의
- Rate Limiting 정책 (해당 시)
- 인증/인가 요구사항

```
[REQUIRED] 6. 데이터 모델 (Data Model)
```
- 신규/변경 테이블 또는 컬렉션
- 필드 정의: 필드명, 타입, 필수 여부, 기본값, 설명
- 관계 (FK, Reference)
- 인덱스 정의
- 마이그레이션 필요 여부

```
[REQUIRED] 7. 엣지 케이스 및 테스트 시나리오 (Edge Cases & Test Scenarios)
```
- 정상 시나리오 (Happy Path)
- 경계값 테스트 (Boundary)
- 에러 시나리오
- 동시성 시나리오 (Concurrency)
- 각 시나리오: Given/When/Then 형식
- 테스트 우선순위

### 섹션 요약

| 번호 | 섹션 | 필수 여부 |
|------|------|-----------|
| 1 | 기능 개요 (Feature Overview) | REQUIRED |
| 2 | 유저 스토리 (User Stories) | REQUIRED |
| 3 | 기능 요구사항 상세 (Functional Requirements Detail) | REQUIRED |
| 4 | UI/UX 요구사항 및 인터랙션 명세 (클릭/상태/폼/네비게이션) | REQUIRED |
| 5 | API 명세 (API Specification) | REQUIRED |
| 6 | 데이터 모델 (Data Model) | REQUIRED |
| 7 | 엣지 케이스 및 테스트 시나리오 (Edge Cases & Test Scenarios) | REQUIRED |

---

## User Story

User Story (유저 스토리)는 **사용자 관점**에서 요구사항을 정의하는 경량 기획서입니다. 애자일 스프린트 계획에 직접 활용할 수 있도록 INVEST 원칙을 따릅니다.

### 템플릿 구조

```
[REQUIRED] 1. 에픽 정의 (Epic Definition)
```
- 에픽명
- 에픽 설명: 큰 그림에서 이 작업이 왜 필요한지
- 비즈니스 가치
- 관련 PRD 링크 (있는 경우)
- 에픽 완료 조건 (Definition of Done)

```
[REQUIRED] 2. 유저 스토리 목록 (User Story List)
```
- 각 스토리 형식:
  - **As a** [사용자 유형]
  - **I want** [행동/기능]
  - **So that** [얻고자 하는 가치/목적]
- 스토리 ID
- 우선순위 (P0/P1/P2)
- 스토리 간 의존 관계
- 스프린트 배정 (해당 시)

```
[REQUIRED] 3. 인수 조건 (Acceptance Criteria)
```
- 각 스토리별 인수 조건:
  - **Given** [사전 조건]
  - **When** [사용자 행동]
  - **Then** [기대 결과]
- 하나의 스토리에 여러 인수 조건 가능
- 부정 시나리오 포함 (X가 아닐 때 어떻게 되는지)

```
[REQUIRED] 4. INVEST 체크리스트 (INVEST Checklist)
```
- **I**ndependent: 다른 스토리와 독립적으로 개발/배포 가능한가?
- **N**egotiable: 구현 방법이 유연한가? (What만 정의, How는 개발팀 결정)
- **V**aluable: 사용자 또는 비즈니스에 명확한 가치를 제공하는가?
- **E**stimable: 개발팀이 작업량을 추정할 수 있는가?
- **S**mall: 하나의 스프린트 내에 완료할 수 있는 크기인가?
- **T**estable: 인수 조건이 명확하여 테스트 가능한가?
- 각 항목에 대한 판정 (Pass/Fail)과 근거

```
[REQUIRED] 5. 스토리 포인트 가이드 (Story Point Guide)
```
- 스토리 포인트 기준 (1/2/3/5/8/13)
- 각 스토리별 예상 포인트
- 포인트 산정 근거:
  - 복잡도 (Complexity)
  - 불확실성 (Uncertainty)
  - 작업량 (Effort)
- 스프린트별 총 포인트 합산

### 섹션 요약

| 번호 | 섹션 | 필수 여부 |
|------|------|-----------|
| 1 | 에픽 정의 (Epic Definition) | REQUIRED |
| 2 | 유저 스토리 목록 (User Story List) | REQUIRED |
| 3 | 인수 조건 (Acceptance Criteria) | REQUIRED |
| 4 | INVEST 체크리스트 (INVEST Checklist) | REQUIRED |
| 5 | 스토리 포인트 가이드 (Story Point Guide) | REQUIRED |

---

## Tech Spec

Tech Spec (기술 명세서)은 **개발자를 위한 기술 중심** 기획서입니다. 구현 방법, 아키텍처, 성능, 보안을 상세히 다루며, 코드 리뷰와 기술 논의의 기준 문서로 사용됩니다.

### 템플릿 구조

```
[REQUIRED] 1. 시스템 개요 (System Overview)
```
- 배경 및 동기
- 기술적 목표
- 관련 PRD 또는 Feature Spec 링크
- 기술적 제약사항
- 용어 정의 (Technical Glossary)

```
[REQUIRED] 2. 아키텍처 설계 (Architecture Design)
```
- 시스템 아키텍처 다이어그램 설명
- 컴포넌트 구조 및 역할
- 서비스 간 통신 방식 (REST, gRPC, Message Queue 등)
- 기술 스택 선정 및 근거
- 기존 시스템과의 통합 방안
- 대안 검토 (Alternative Approaches) 및 선택 근거

```
[REQUIRED] 3. API 설계 상세 (API Design Detail)
```
- 엔드포인트 전체 목록
- 각 API별 상세:
  - Method, Path
  - Request Headers, Query Parameters, Body (JSON Schema)
  - Response Body (JSON Schema): 성공/실패
  - HTTP Status Codes
  - 에러 코드 및 메시지 표준
- API 버저닝 전략
- Pagination, Filtering, Sorting 규칙
- Rate Limiting 정책
- 인증/인가 흐름

```
[REQUIRED] 4. 데이터 모델 상세 (Data Model Detail)
```
- ERD 설명 또는 테이블 정의
- 각 테이블/컬렉션:
  - 필드명, 타입, 제약조건, 기본값, 설명
  - Primary Key, Foreign Key
  - 인덱스 (Unique, Composite, Partial)
- 데이터 마이그레이션 계획
- 데이터 보존/삭제 정책 (Retention Policy)
- 읽기/쓰기 패턴 분석

```
[REQUIRED] 5. 시퀀스 다이어그램 설명 (Sequence Diagram Description)
```
- 주요 플로우별 시퀀스 설명:
  - 참여 컴포넌트/서비스
  - 호출 순서
  - 동기/비동기 구분
  - 실패 시 흐름 (Fallback, Retry)
- Mermaid 또는 PlantUML 형식으로 표현 가능하도록 텍스트 기술

```
[REQUIRED] 6. 성능 요구사항 (Performance Requirements)
```
- 응답 시간 목표 (Latency SLA)
- 처리량 목표 (Throughput)
- 동시 사용자 수 예상
- 캐싱 전략 (Cache Layer, TTL, Invalidation)
- DB 쿼리 최적화 고려사항
- 부하 테스트 계획

```
[REQUIRED] 7. 보안 고려사항 (Security Considerations)
```
- 인증/인가 메커니즘
- 데이터 암호화 (전송 중, 저장 시)
- 입력값 검증 및 Sanitization
- SQL Injection, XSS, CSRF 방지 대책
- 민감 데이터 처리 방안 (PII, 결제 정보 등)
- 감사 로그 (Audit Log) 요구사항
- 보안 테스트 계획

```
[REQUIRED] 8. 배포 계획 (Deployment Plan)
```
- 배포 전략 (Blue-Green, Canary, Rolling 등)
- Feature Flag 사용 여부
- 롤백 계획
- DB 마이그레이션 순서
- 모니터링 및 알림 설정
- 배포 체크리스트

### 섹션 요약

| 번호 | 섹션 | 필수 여부 |
|------|------|-----------|
| 1 | 시스템 개요 (System Overview) | REQUIRED |
| 2 | 아키텍처 설계 (Architecture Design) | REQUIRED |
| 3 | API 설계 상세 (API Design Detail) | REQUIRED |
| 4 | 데이터 모델 상세 (Data Model Detail) | REQUIRED |
| 5 | 시퀀스 다이어그램 설명 (Sequence Diagram Description) | REQUIRED |
| 6 | 성능 요구사항 (Performance Requirements) | REQUIRED |
| 7 | 보안 고려사항 (Security Considerations) | REQUIRED |
| 8 | 배포 계획 (Deployment Plan) | REQUIRED |

---

## 타입 선택 가이드 (Type Selection Guide)

| 상황 | 추천 타입 |
|------|-----------|
| 새로운 제품/기능의 전체 기획이 필요할 때 | **PRD** |
| 특정 기능 하나를 상세하게 정의할 때 | **Feature Spec** |
| 애자일 스프린트용 작업 단위가 필요할 때 | **User Story** |
| 개발팀이 구현 방법을 논의/합의할 때 | **Tech Spec** |
| 타입을 지정하지 않은 경우 | **PRD** (기본값) |

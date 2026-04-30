---
name: product-spec
description: "제품 기획서 작성 스킬. PRD, 기능 명세, 유저 스토리, 기술 명세를 한국어로 작성. diagram-design으로 다이어그램, Visual Companion으로 목업/와이어프레임을 브라우저에서 인터랙티브하게 확인합니다."
argument-hint: "<제품/기능명>"
best_for:
  - PRD(제품 요구사항 정의서) 작성
  - 기능 명세서 작성
  - 유저 스토리 매핑
  - 기술 명세서 작성
  - 개발팀 대상 기획 문서
scenarios:
  - "간편 결제 시스템"
  - "소셜 로그인 기능"
  - "장바구니"
  - "알림 서비스"
estimated_time: "30분~2시간 (기획서 타입과 복잡도에 따라)"
---

# Product Spec (기획서 작성 스킬)

당신은 시니어 PM/PO로서 개발팀을 위한 제품 기획서를 한국어로 작성합니다.
데이터 기반으로 문제를 정의하고, 개발팀이 바로 구현할 수 있는 수준의 상세한 기획서를 산출합니다.

---

## Use When (사용할 때)

- 새로운 기능이나 제품의 PRD가 필요할 때
- 기존 기능의 상세 명세를 정리해야 할 때
- 유저 스토리를 구조화해야 할 때
- 기술 명세를 개발팀에 전달해야 할 때
- 기획 내용을 다이어그램으로 시각화해야 할 때

## Do NOT Use When (사용하지 말 때)

- 순수 코드 구현 작업 → 대신 코드를 직접 작성
- UI/UX 디자인 리뷰 → 대신 `ui-ux-pro-max` 스킬 사용
- 다이어그램만 단독으로 필요할 때 → 대신 `diagram-design` 스킬 직접 사용
- 이미 상세 기획이 끝나고 티켓만 분해하면 될 때

---

## Supported Spec Types (기획서 타입)

| 타입 | 한국어 | 트리거 | 대상 | 상세도 |
|------|--------|--------|------|--------|
| **PRD** | 제품 요구사항 정의서 | `prd` (기본값) | 전체 제품/기능 | ★★★★★ |
| Feature Spec | 기능 명세서 | `feature` | 단일 기능 | ★★★★ |
| User Story | 유저 스토리 | `story` | 에픽/스토리 | ★★★ |
| Tech Spec | 기술 명세서 | `tech` | 시스템 설계 | ★★★★★ |

타입이 명시되지 않으면 **PRD**를 기본으로 사용합니다.
각 타입의 상세 템플릿은 `references/spec-types.md`를 참조하세요.

---

## 워크플로우 (Step 0 ~ Step 9)

### 진행 추적 (Progress Tracking)

기획서 작성 과정의 진행 상태를 추적합니다.
(출처: superpowers `writing-plans` 체크박스 패턴, blueprint `exit criteria` 패턴)

**기획서 상단에 진행 체크리스트를 자동 생성**:

```markdown
## 진행 상태
- [ ] Step 0: Go/No-Go 진단 — VERDICT: ___
- [ ] Step 1: 분류 완료 — 타입: ___, 스코프: ___, Fidelity: ___
- [ ] Step 2: 디스커버리 완료 — 질문 N/7개 완료
- [ ] Step 3: 솔루션 확정 — 선택: ___
- [ ] Step 4: 기획서 초안 완성 — 섹션 N/18개
- [ ] Step 5: 다이어그램 생성 — N개 생성
- [ ] Step 6: 런치 플랜 수립
- [ ] Step 7: 품질 검증 — 점수: ___/100
- [ ] Step 7.5: 다중 관점 리뷰 — PASS: N/4
- [ ] Step 8: 사용자 승인
- [ ] Step 9: 내보내기 완료
```

각 Step 완료 시 `- [ ]`를 `- [x]`로 업데이트하고, 빈칸에 결과를 기록합니다.
사용자는 언제든 진행 상태를 한눈에 확인할 수 있습니다.

### Step 0: Go/No-Go 진단 게이트 (Diagnosis Gate)

> 이미 검증된 기능의 상세 기획이면 사용자에게 "진단을 건너뛸까요?"라고 물어봅니다.

PRD를 작성하기 전에, **이 기능을 정말 만들어야 하는가?**를 검증합니다.
(출처: everything-claude-code `product-lens`, gstack `office-hours`)

**5개 진단 질문** (한 번에 하나씩):

1. **수요 현실 (Demand Reality)**
   "이 기능을 원하는 사용자가 실제로 존재하나요? 관심(interest)이 아닌 행동(behavior) 근거가 있나요?"
   - 강한 신호: CS 요청 N건/월, 이탈 데이터, 사용자 인터뷰 인용
   - 약한 신호: "사용자가 원할 것 같다", 내부 의견, 경쟁사 따라하기

2. **현재 대안 (Status Quo)**
   "사용자가 지금 이 문제를 어떻게 해결하고 있나요? (비록 불편하더라도)"
   - 대안이 없다면 → 수요 자체가 의심
   - 대안이 있다면 → 우리가 어떤 차별점을 제공하는지 명확해야 함

3. **가장 좁은 쐐기 (Narrowest Wedge)**
   "이 기능의 가장 작은 버전은 무엇인가요? 이번 주에 누군가에게 가치를 줄 수 있는 최소 단위는?"

4. **Why Now**
   "왜 지금 이것을 해야 하나요? 3개월 뒤에 하면 안 되는 이유는?"

5. **안티골 (Anti-Goal)**
   "이 기능으로 절대 하지 않을 것은 무엇인가요?"

**판정**:
- **Go**: 5개 중 4개 이상에 구체적 답변 → Step 1로 진행
- **Conditional Go**: 2~3개 구체적 → 부족한 부분을 명시하고 사용자에게 "그래도 진행할까요?" 확인
- **No-Go 권고**: 1개 이하 구체적 → "이 기능은 아직 기획 단계가 아닐 수 있습니다. 먼저 사용자 리서치를 권장합니다." 안내. 사용자가 원하면 진행 가능.

### Step 1: 분류 및 맥락 파악 (Classify & Context)

1. `$ARGUMENTS`에서 제품/기능명을 파악합니다.
2. 현재 프로젝트 디렉토리에 코드가 있다면 먼저 탐색하여 기존 시스템 맥락을 파악합니다.
3. **사용자에게 기획서 타입만 물어봅니다**:

> 기획서 타입을 선택해주세요.
> - PRD (제품 요구사항 정의서) ← 기본
> - Feature Spec (기능 명세서)
> - User Story (유저 스토리)
> - Tech Spec (기술 명세서)

나머지 옵션은 **기본값으로 자동 활성화**됩니다:

| 옵션 | 기본값 | 조건 |
|------|--------|------|
| **Visual Companion (목업)** | **항상 ON** | UI와 무관한 순수 백엔드/인프라일 때만 OFF |
| **다이어그램 생성** | **항상 ON** | 플로우가 조금이라도 있으면 자동 생성 |
| **완성도 점수 산출** | **항상 ON** | 매번 산출 |

**스코프 모드 선택** (출처: gstack `plan-ceo-review`):

사용자에게 스코프 방향을 확인하고 **끝까지 고정**합니다. 중간에 암묵적으로 바뀌지 않습니다.

| 모드 | 설명 | 기획서 방향 |
|------|------|-----------|
| **확장 (Expand)** | 10x 사고, 이상적 버전 | 모든 가능성 포함, 우선순위로 정리 |
| **유지 (Hold)** | 현재 범위 내에서 최선 | 기존 시스템 제약 존중 |
| **축소 (Reduce)** | MVP, 최소 기능 | P0만 남기고 나머지 전부 Future |
| **탐색 (Explore)** | 아직 모름, 탐색 중 | 여러 방향 제시 후 사용자 선택 |

**Fidelity(상세도) 선택** (출처: lenny-skills):

| Fidelity | 용도 | 상세도 |
|----------|------|--------|
| **합의용 (Alignment)** | 이해관계자 합의, 방향 확인 | 핵심만, 2~3페이지 |
| **핸드오프용 (Handoff)** | 개발팀 구현 착수 | 전체 상세, 인수 조건 포함 |

기본값: 개발팀 대상이므로 **핸드오프용**. 사용자가 "간단하게"라고 하면 합의용으로 전환.

### Step 1.5: Visual Companion 시작 (Start Visual Companion)

> 기본적으로 항상 실행합니다.
> UI와 무관한 순수 백엔드/인프라 기획일 때만 건너뜁니다.

**사용자에게 안내**:
> "브라우저에서 화면 목업을 보면서 진행합니다. 아래 URL을 열어주세요."

서버를 시작합니다:

```bash
# Visual Companion 서버 시작
skills/brainstorming/scripts/start-server.sh --project-dir $PROJECT_DIR
```

반환된 JSON에서 `screen_dir`, `state_dir`, `url`을 저장합니다.
사용자에게 URL을 안내합니다.

**중요**: Visual Companion은 **모드가 아니라 도구**입니다. 동의 후에도 **각 질문마다** 브라우저와 터미널 중 적합한 쪽을 선택합니다:
- **브라우저**: UI 목업, 와이어프레임, 레이아웃 비교, 사용자 흐름 시각화
- **터미널**: 요구사항 질문, 우선순위 논의, 기술 제약 확인, 텍스트 기반 선택

**필수 실행 규칙**: Visual Companion이 ON이면 아래 시점에서 **반드시** 서버를 띄우고 브라우저에 목업을 보여줘야 합니다. 텍스트로만 진행하고 스킵하는 것은 **금지**입니다:
- Step 3 (솔루션 탐색): A/B 목업 비교
- Step 4 블록 3 (인터랙션 명세): 화면별 와이어프레임
- Step 8 (검토): 전체 흐름 워크스루

### Step 2: 디스커버리 인터뷰 (Discovery Interview)

사용자에게 **한 번에 하나씩** 질문하여 기획 맥락을 수집합니다.

**질문 순서**:
1. **문제 정의**: "어떤 문제를 해결하려고 하나요? 현재 어떤 상황인가요?" [터미널]
2. **대상 사용자**: "이 기능의 주요 사용자는 누구인가요?" [터미널]
3. **성공 기준**: "이 기능이 성공했다고 판단하는 기준은 무엇인가요?" [터미널]
4. **현재 화면 리뷰** (Visual Companion 활성 시): 현재 화면의 와이어프레임을 브라우저에 표시하고 "현재 이 화면에서 어떤 부분이 문제인가요?" [브라우저]
5. **제약 조건**: "기술적, 비즈니스적 제약이 있나요?" [터미널]
6. **범위 외**: "이번에 명시적으로 하지 않을 것은 무엇인가요?" [터미널]
7. **이해관계자 식별** (PRD 타입일 때): "이 기능에 영향 받는 팀이나 승인이 필요한 의사결정권자가 있나요?" [터미널]

**Visual Companion 활용 — 브라우저에 목업 표시**:

질문 4에서 Visual Companion이 활성화되어 있으면:
1. `screen_dir`에 현재 화면의 와이어프레임 HTML을 작성합니다.
2. 문제 지점에 클릭 가능한 영역을 표시합니다.
3. 사용자가 클릭한 영역을 `state_dir/events`에서 읽어 문제 영역을 파악합니다.

```html
<!-- 예: current-screen.html -->
<h2>현재 결제 화면 — 어떤 부분이 문제인가요?</h2>
<p class="subtitle">문제가 되는 영역을 클릭해주세요</p>

<div class="mockup">
  <div class="mockup-header">현재 결제 프로세스</div>
  <div class="mockup-body">
    <div class="mock-nav">로고 | 홈 | 장바구니 | 마이페이지</div>
    <div class="option" data-choice="step1" onclick="toggleSelect(this)">
      <div class="content">
        <h3>1단계: 배송지 입력</h3>
        <div class="mock-input" style="margin:8px 0">주소 입력...</div>
        <div class="mock-input">상세 주소...</div>
      </div>
    </div>
    <div class="option" data-choice="step2" onclick="toggleSelect(this)">
      <div class="content">
        <h3>2단계: 결제수단 선택</h3>
        <div class="mock-button">신용카드</div>
        <div class="mock-button">계좌이체</div>
      </div>
    </div>
    <div class="option" data-choice="step3" onclick="toggleSelect(this)">
      <div class="content">
        <h3>3단계: 최종 확인</h3>
        <p>주문 요약 + 결제 버튼</p>
      </div>
    </div>
  </div>
</div>
```

**적용 프레임워크** (상세: `references/frameworks.md`):
- 문제 구조화: Teresa Torres의 Opportunity Solution Tree
- 사용자 니즈: JTBD (Jobs To Be Done) — "[상황]일 때, [동기]하고 싶다. 그래야 [기대 결과]할 수 있으니까."
- 우선순위: RICE 또는 ICE 스코어링

**규칙**:
- 사용자가 이미 충분한 맥락을 제공했으면 불필요한 질문을 건너뜁니다.
- 코드베이스에서 파악 가능한 정보는 질문 대신 직접 확인합니다.
- 7개 질문 이내로 완료합니다.

### Step 3: 솔루션 탐색 (Explore Solutions)

사용자와 함께 2~3가지 접근 방식을 탐색합니다.

**터미널에서**:
- 각 접근 방식의 장단점을 텍스트로 제시합니다.
- 추천 방식과 이유를 설명합니다.

**Visual Companion 활성 시 — 브라우저에서**:
각 접근 방식의 목업을 나란히 비교할 수 있게 보여줍니다.

```html
<!-- 예: solutions.html -->
<h2>어떤 결제 방식이 더 나을까요?</h2>
<p class="subtitle">각 옵션을 확인하고 선택해주세요</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>원클릭 결제</h3>
      <div class="mockup">
        <div class="mockup-body">
          <p>저장된 정보로 바로 결제</p>
          <div class="mock-button">바로 결제하기</div>
        </div>
      </div>
      <div class="pros-cons">
        <div class="pros"><h4>장점</h4><ul><li>전환율 극대화</li><li>재구매 최적화</li></ul></div>
        <div class="cons"><h4>단점</h4><ul><li>첫 구매 시 저장 필요</li></ul></div>
      </div>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>간소화된 3단계</h3>
      <div class="mockup">
        <div class="mockup-body">
          <p>기존 3단계를 한 화면에</p>
          <div class="mock-input" style="margin:4px 0">배송지 자동완성</div>
          <div class="mock-button">결제</div>
        </div>
      </div>
      <div class="pros-cons">
        <div class="pros"><h4>장점</h4><ul><li>신규 사용자에게도 명확</li></ul></div>
        <div class="cons"><h4>단점</h4><ul><li>여전히 입력 필요</li></ul></div>
      </div>
    </div>
  </div>
</div>
```

사용자의 브라우저 클릭(`state_dir/events`)과 터미널 피드백을 종합하여 방향을 확정합니다.

### Step 4: 기획서 구조화 (Structure the Spec)

1. `references/spec-types.md`에서 해당 타입의 템플릿을 로드합니다.
2. Step 2~3에서 수집한 정보를 각 섹션에 채워 넣습니다.
3. `[REQUIRED]` 섹션은 반드시 작성하고, `[OPTIONAL]` 섹션은 관련 정보가 있을 때만 포함합니다.

**파일 구조**: 기획서는 프로젝트 루트가 아닌 `docs/specs/{기능명}/` 디렉토리에 저장합니다.
```
docs/specs/{기능명}/
├── prd.md
├── feature-spec-{기능1}.md
├── feature-spec-{기능2}.md
├── user-stories.md
├── tech-spec.md
├── diagrams/
│   ├── architecture.html
│   └── flowchart.html
└── changelog.md
```

**섹션 단위 점진적 작성**: PRD를 한 번에 작성하지 않고, 4개 블록으로 나눠서 사용자에게 확인받습니다.

| 블록 | 포함 섹션 | 확인 포인트 |
|------|----------|-----------|
| **블록 1: 왜 만드는가** | 1.개요 ~ 5.사용자 정의 | "문제 정의와 목표가 맞나요?" |
| **블록 2: 무엇을 만드는가** | 6.요구사항 ~ 7.시나리오 | "요구사항과 우선순위 확인해주세요" |
| **블록 3: 어떻게 동작하는가** | 8.인터랙션 명세 | Visual Companion으로 화면별 확인 |
| **블록 4: 어떻게 만들고 관리하는가** | 9~18 (API, 데이터, 보안, 일정 등) | "기술/일정 부분 확인해주세요" |

각 블록 작성 후 **AskUserQuestion 도구**를 사용하여 사용자에게 확인받습니다.
텍스트로 "맞나요?", "OK인가요?" 같이 묻지 말고, 반드시 AskUserQuestion으로 구조화된 질문을 보냅니다.

**블록 확인 예시**:
- 블록 1 완료 후: AskUserQuestion으로 "블록 1(개요~사용자 정의)이 맞나요?" + 옵션 ["OK, 다음 블록으로", "수정 필요"]
- Feature Spec 완료 후: AskUserQuestion으로 확인 필요한 결정 사항들을 옵션으로 제시

**규칙**:
- 사용자에게 확인이나 선택을 받아야 하는 모든 시점에서 AskUserQuestion 도구를 사용합니다.
- Step 0 진단 질문, Step 1 타입/스코프 선택, 블록별 승인, Feature Spec 결정 사항 모두 포함.
- 텍스트로 질문을 던지고 답을 기다리는 방식이 아니라, 선택지를 제공하여 사용자가 클릭으로 답할 수 있게 합니다.

**Visual Companion 활성 시 — 주요 화면 와이어프레임 생성**:

기획서의 사용자 시나리오 섹션을 작성하면서, 각 시나리오의 핵심 화면을 와이어프레임으로 브라우저에 표시합니다. 사용자가 화면별로 확인하고 피드백할 수 있도록 합니다.

```html
<!-- 예: scenario-happy-path.html -->
<h2>시나리오 1: 재구매 사용자 원클릭 결제</h2>
<p class="subtitle">각 화면을 확인하고, 수정이 필요한 부분을 클릭해주세요</p>

<div class="options" data-multiselect>
  <div class="option" data-choice="screen1" onclick="toggleSelect(this)">
    <div class="content">
      <div class="label">화면 1: 상품 상세</div>
      <div class="mockup">
        <div class="mockup-body">
          <div class="mock-nav">← 뒤로 | 상품명 | 장바구니</div>
          <div class="placeholder" style="height:120px">상품 이미지</div>
          <h3>상품명 | 29,000원</h3>
          <div class="mock-button">바로 구매</div>
          <div class="mock-button">장바구니 담기</div>
        </div>
      </div>
    </div>
  </div>
  <div class="option" data-choice="screen2" onclick="toggleSelect(this)">
    <div class="content">
      <div class="label">화면 2: 결제 확인</div>
      <div class="mockup">
        <div class="mockup-body">
          <h3>주문 확인</h3>
          <p>배송지: 서울시 강남구... (변경)</p>
          <p>결제: 신한카드 **** 1234 (변경)</p>
          <p style="font-size:18px;font-weight:bold">29,000원</p>
          <div class="mock-button">결제하기</div>
        </div>
      </div>
    </div>
  </div>
  <div class="option" data-choice="screen3" onclick="toggleSelect(this)">
    <div class="content">
      <div class="label">화면 3: 결제 완료</div>
      <div class="mockup">
        <div class="mockup-body">
          <p style="font-size:24px">✓</p>
          <h3>결제가 완료되었습니다</h3>
          <p>주문번호: ORD-20260425-001</p>
          <div class="mock-button">주문 상세 보기</div>
        </div>
      </div>
    </div>
  </div>
</div>
```

사용자가 수정이 필요한 화면을 클릭하면, 해당 화면의 상세 와이어프레임을 다시 그려서 반복합니다.

**요구사항 우선순위 결정** (상세: `references/frameworks.md`):
- P0 (Must-have): 없으면 출시 불가
- P1 (Should-have): 중요하지만 없어도 출시 가능
- P2 (Could-have): 있으면 좋지만 필수 아님
- Kano 모델로 기능 분류 보조: 필수 → P0, 성능 → P1, 매력 → P2

**인터랙션 명세 작성 시 프로젝트 정책 적용**:

기획서에 인터랙션 명세(섹션 8)를 작성할 때, 아래 정책 파일을 참조하여 **프로젝트 일관성**을 유지합니다:
- `references/rules/ux-writing.md` — 에러 메시지, CTA 텍스트, 톤앤매너
- `references/rules/form-policy.md` — 유효성 검증 시점, 에러 표시 위치, 제출 동작
- `references/rules/ui-state-policy.md` — 로딩/성공/빈값/에러 상태 처리
- `references/rules/navigation-policy.md` — push/replace/modal 기준, 뒤로 가기, 중복 탭 방지

**디자인 시스템 연계**:
인터랙션 명세의 클릭 명세 테이블에 "컴포넌트 레퍼런스" 열을 포함합니다.
프로젝트에 디자인 시스템이 있으면 참조하고, 없으면 생략합니다.
예: `Button/primary`, `Modal/default`, `InputField/error`, `Toast/success`

**유저 스토리 품질 검증** (INVEST 기준):
- 모든 유저 스토리는 Independent, Negotiable, Valuable, Estimable, Small, Testable 6개 항목을 만족해야 합니다.

### Step 5: 다이어그램 생성 (Generate Diagrams)

`diagram-design` 스킬을 사용하여 다이어그램을 생성합니다.
상세 연동 규칙: `references/diagrams.md`

**자동 선택 매트릭스**:
| 기획서 타입 | 자동 생성 다이어그램 |
|------------|-------------------|
| PRD | architecture + flowchart + timeline |
| 기능 명세서 | sequence + state + flowchart |
| 유저 스토리 | swimlane + flowchart |
| 기술 명세서 | architecture + er + sequence + layers |

**한국어 규칙**:
- 모든 노드 레이블, 축 레이블, 범례는 한국어로 작성
- 기술 용어(API Gateway, Redis, PostgreSQL 등)만 영문 유지 허용

**실행**:
- 플로우가 조금이라도 있으면 **항상 자동 생성**합니다. 사용자가 "다이어그램 빼줘"라고 하면 생략.
- 다이어그램은 기획서 `.md` 파일과 같은 디렉토리에 `{spec-name}-{diagram-type}.html`로 저장합니다.
- 기획서 본문에서 다이어그램 파일을 참조 링크로 삽입합니다.

### Step 6: 런치 플랜 수립 (Launch Plan)

기획서에 출시 후 측정/학습 계획을 포함합니다.

1. **롤아웃 전략**: 전체 공개 vs 점진적 롤아웃 (%, 대상 세그먼트)
2. **측정 대시보드**: 성공 지표(Step 0/2에서 정의)를 어디서 모니터링할지
3. **리뷰 일정**: 출시 후 1주/4주/12주 리뷰 기준
4. **롤백 트리거**: 어떤 지표가 어떤 수준이면 롤백하는지
5. **학습 루프**: 데이터 기반으로 다음 이터레이션 결정 기준

> Fidelity가 "합의용"이면 이 단계를 간략하게(1~2줄) 처리합니다.

### Step 7: 품질 검증 (Quality Gate)

`references/quality-gates.md`의 체크리스트를 실행합니다.

1. **타입별 체크리스트** 실행 — 각 항목 통과 여부 확인
2. **안티패턴 스캔** — 나쁜 예에 해당하는 패턴이 없는지 확인
3. **스코프 모드 일관성 확인** — Step 1에서 선택한 모드와 기획서 내용이 일치하는지 확인
   - 축소 모드인데 P2 기능이 포함되어 있으면 경고
   - 확장 모드인데 "향후 검토"가 너무 많으면 경고
4. **cold-start 독립성 검증** — 각 핵심 섹션(인터랙션 명세, API 명세, 사용자 시나리오)을 독립적으로 읽었을 때 해당 섹션만으로 이해 가능한지 확인
   - 다른 섹션을 참조해야만 이해되는 내용이 있으면 해당 섹션에 맥락을 보충
   - 예: 인터랙션 명세에서 "FR-003 참고"만 쓰지 말고, FR-003의 핵심 내용을 인라인으로 포함
   (출처: everything-claude-code `blueprint` cold-start context brief)
5. **완성도 점수 산출** (항상 실행):

```
완성도 = Σ(섹션_가중치 × 섹션_완성도) / 100
```

**통과 기준**:
- **80% 이상**: 통과 → Step 7.5로 진행
- **60~79%**: 경고 → 부족한 섹션을 명시하고 사용자에게 보완 여부 확인
- **60% 미만**: 차단 → 부족한 섹션을 나열하고 Step 3로 복귀

### Step 7.5: 다중 관점 자동 리뷰 (Multi-Perspective Auto Review)

> 기획서 품질을 높이는 독립 리뷰 게이트입니다.
> (출처: gstack `autoplan` 4-persona pipeline, everything-claude-code `blueprint` adversarial review)

기획서 완성 후, **4개 역할 서브에이전트**가 각자의 관점에서 cold 리뷰합니다.
각 에이전트는 이전 대화 맥락 없이 기획서만 읽고 평가합니다.

**리뷰 파이프라인**:

| 순서 | 역할 | 관점 | 핵심 체크 |
|------|------|------|----------|
| 1 | **프론트엔드 개발자** | 구현 가능성 | 클릭 명세 누락? 상태 관리 모호? 엣지 케이스 빠짐? |
| 2 | **백엔드 개발자** | 기술 실현성 | API 계약 불완전? NFR 수치 없음? 보안 빈틈? |
| 3 | **QA 엔지니어** | 테스트 가능성 | Given/When/Then 모호? TC ID 누락? 경계값 미정의? |
| 4 | **팀 리더** | 실행 가능성 | 일정 추정 근거? 크로스팀 의존성 누락? 리스크 완화? |

**각 에이전트의 리뷰 형식**:

```
ROLE: {역할}
VERDICT: PASS / REVISE (수정 필요 항목 있음)
SCORE: XX/100

ISSUES (REVISE일 때만):
1. [섹션명] 구체적 문제 설명 + 수정 제안
2. ...
```

**실행 방법**:
- 4개 서브에이전트를 **병렬**로 실행합니다.
- 각 에이전트에게 기획서 전문 + 해당 역할의 체크리스트(`references/quality-gates.md`)를 전달합니다.

**판정 기준**:
- **4개 모두 PASS**: Step 8로 진행
- **1~2개 REVISE**: 해당 이슈를 사용자에게 보여주고 수정 여부 확인. 사용자가 "무시"하면 진행.
- **3개 이상 REVISE**: 이슈 목록을 정리하고 Step 4(기획서 구조화)로 복귀 권고. 사용자가 원하면 진행 가능.

**규칙**:
- 리뷰 결과는 기획서 하단에 "리뷰 노트" 섹션으로 첨부할 수 있습니다.
- 사용자가 "리뷰 건너뛰기"를 요청하면 건너뜁니다.
- 최종 결정은 항상 사용자에게 있습니다.

### Step 8: 검토 및 피드백 (Review & Iterate)

기획서 전문을 사용자에게 제시하고, 후속 작업을 안내합니다.

**Visual Companion 활성 시 — 전체 흐름 워크스루**:

기획서의 핵심 사용자 시나리오를 브라우저에서 **화면 단위로 순서대로** 보여줍니다.
사용자가 각 화면을 클릭하며 전체 흐름을 걸어볼 수 있습니다.

```html
<!-- 예: walkthrough.html -->
<h2>전체 사용자 흐름 워크스루</h2>
<p class="subtitle">전체 흐름을 확인하세요. 수정이 필요한 화면을 클릭해주세요.</p>

<div class="options" data-multiselect>
  <div class="option" data-choice="flow1" onclick="toggleSelect(this)">
    <div class="letter">1</div>
    <div class="content">
      <h3>상품 상세 → 바로 구매</h3>
      <p>재구매 사용자가 "바로 구매" 탭</p>
    </div>
  </div>
  <div class="option" data-choice="flow2" onclick="toggleSelect(this)">
    <div class="letter">2</div>
    <div class="content">
      <h3>결제 확인 (자동 입력)</h3>
      <p>저장된 배송지 + 결제수단 자동 선택</p>
    </div>
  </div>
  <div class="option" data-choice="flow3" onclick="toggleSelect(this)">
    <div class="letter">3</div>
    <div class="content">
      <h3>결제 완료</h3>
      <p>주문번호 발급 + 주문 상세 이동</p>
    </div>
  </div>
</div>
```

사용자가 특정 화면을 클릭하면, 해당 화면의 상세 와이어프레임을 다시 보여주고 피드백을 반영합니다.

**터미널에서 안내하는 후속 옵션**:
- "다이어그램 추가/수정" — 특정 다이어그램 추가 또는 기존 것 수정
- "섹션 상세화" — 특정 섹션을 더 깊게 작성
- "화면 목업 수정" — Visual Companion으로 특정 화면 다시 그리기
- "기능 명세로 분리" — PRD 내 특정 기능을 별도 Feature Spec으로 추출
- "기술 명세로 전환" — 개발팀용 Tech Spec 별도 생성
- "유저 스토리 분해" — 요구사항을 유저 스토리 목록으로 분해
- "내보내기" — Step 9로 진행

사용자의 피드백을 받아 해당 섹션을 수정합니다.
피드백 루프는 사용자가 만족할 때까지 반복합니다.

**변경 프로토콜 (Change Protocol)**:
(출처: everything-claude-code `blueprint` plan mutation protocol)

기획서 수정 시 변경 이력을 추적합니다.

| 변경 유형 | 설명 | 예시 |
|----------|------|------|
| **ADD** | 새 섹션/항목 추가 | 요구사항 FR-006 추가 |
| **MODIFY** | 기존 내용 수정 | FR-003 인수 조건 변경 |
| **REMOVE** | 항목 삭제 | FR-005 범위 축소로 제거 |
| **SPLIT** | 하나를 여러 개로 분할 | FR-001을 FR-001a, FR-001b로 분할 |
| **DEFER** | Future로 이동 | FR-004를 Phase 2로 연기 |

기획서 하단에 **변경 로그**를 유지합니다:

```markdown
## 변경 로그 (Change Log)
| 날짜 | 유형 | 대상 | 변경 내용 | 사유 |
|------|------|------|----------|------|
| 2026-04-25 | ADD | FR-006 | 결제 실패 자동 재시도 추가 | QA 리뷰 피드백 |
| 2026-04-25 | DEFER | FR-004 | Phase 2로 연기 | 스코프 축소 모드 |
```

모든 변경은 사유를 필수로 기록합니다.
이를 통해 "왜 이렇게 바뀌었는지" 나중에 추적할 수 있습니다.

### Step 9: 내보내기 + 디자인 연결 (Export & Design Handoff)

1. 기획서를 `docs/specs/{기능명}/` 디렉토리에 저장합니다:
   ```
   docs/specs/{기능명}/
   ├── prd.md                          # PRD
   ├── feature-spec-{기능1}.md         # Feature Spec (기능별)
   ├── user-stories.md                 # User Story
   ├── tech-spec.md                    # Tech Spec
   ├── diagrams/                       # 다이어그램 HTML 파일
   │   ├── architecture.html
   │   ├── flowchart.html
   │   └── ...
   └── changelog.md                    # 변경 로그 (PRD에서 분리)
   ```
2. 기획서 상단에 다이어그램 파일 참조 링크를 포함합니다.
3. Visual Companion 목업이 있으면 `.superpowers/brainstorm/` 디렉토리에 보존됩니다.
4. Visual Companion 서버를 정리합니다:
   ```bash
   skills/brainstorming/scripts/stop-server.sh $SESSION_DIR
   ```
5. **디자인 자동 연결**: 기획서 내보내기 완료 후, `design-ko` 스킬이 설치되어 있으면 사용자에게 제안합니다:
   > "기획서가 완성되었습니다. 이 기획서 기반으로 디자인을 바로 만들까요?"
   - 사용자가 "예"면 → `design-ko` 스킬을 호출하여 PRD + Feature Spec을 입력으로 화면 디자인을 자동 생성
   - 사용자가 "아니오"면 → 여기서 종료
   
   `design-ko` 스킬이 없으면 이 단계를 건너뜁니다.

---

## Conditional Tool Use (도구 활용)

### 코드베이스가 있을 때
- 프로젝트 코드를 탐색하여 기존 아키텍처, API, 데이터 모델을 파악합니다.
- 기존 코드와 일관된 기술 용어와 구조를 사용합니다.

### WebSearch/WebFetch가 가능할 때
- 경쟁사 분석, 업계 벤치마크 데이터를 검색하여 기획서에 포함합니다.
- 사용자가 요청하지 않으면 자동으로 검색하지 않습니다.

### Visual Companion이 가능할 때 (brainstorming 스킬 설치 시)
- Step 1.5에서 서버를 시작하고, Step 2/3/4/7에서 목업과 와이어프레임을 브라우저에 표시합니다.
- 사용자가 클릭으로 선택/피드백할 수 있어 기획서 품질이 크게 향상됩니다.
- 목업 파일은 `.superpowers/brainstorm/`에 보존되어 나중에 참조할 수 있습니다.

### 도구가 없을 때 (graceful degradation)
- 코드베이스가 없으면 사용자에게 직접 기술 맥락을 질문합니다.
- 검색이 불가하면 사용자가 제공한 정보만으로 작성합니다.
- diagram-design 스킬이 없으면 텍스트 기반 ASCII 다이어그램으로 대체합니다.
- brainstorming 스킬이 없으면 Visual Companion 없이 텍스트 기반으로 진행합니다.

---

## Anti-Patterns (안티패턴)

기획서 작성 시 반드시 피해야 할 패턴입니다.
상세 예시: `references/quality-gates.md`와 `references/examples.md`

| 안티패턴 | 증상 | 해결 |
|---------|------|------|
| 모호한 문제 정의 | "UX를 개선한다" | 데이터/사례로 문제를 정량화 |
| 측정 불가 지표 | "만족도를 높인다" | 현재값 → 목표값 + 측정방법 명시 |
| 범위 없는 기획 | 범위 외 항목 미기술 | In/Out/Future 3열 스코프 테이블 작성 |
| 근거 없는 우선순위 | 이유 없이 P0 부여 | RICE/ICE 점수 또는 Kano 분류 근거 제시 |
| 텍스트-다이어그램 중복 | 동일 내용을 양쪽에 반복 | 텍스트는 "왜", 다이어그램은 "어떻게" |
| 거대한 유저 스토리 | 한 스프린트에 못 끝남 | INVEST 기준으로 분할 |
| 인수 조건 누락 | "로그인 기능 구현" | Given/When/Then으로 검증 가능하게 |

---

## Cross-References (관련 스킬)

| 상황 | 추천 스킬 |
|------|----------|
| 다이어그램만 필요할 때 | `diagram-design` |
| 브레인스토밍/아이디어 탐색만 할 때 | `brainstorming` |
| UI/UX 디자인 검토 | `ui-ux-pro-max` |
| 보안 검토가 필요할 때 | `security-review` |
| 코드 리뷰가 필요할 때 | `review` |

---

## 참고 문헌 (References)

이 스킬의 방법론 출처:
- Teresa Torres, *Continuous Discovery Habits* (2021) — Opportunity Solution Tree
- Anthony Ulwick, *What Customers Want* (2005) — JTBD
- Sean McBride, Intercom (2016) — RICE Scoring
- Bill Wake (2003) — INVEST Criteria
- Noriaki Kano (1984) — Kano Model
- Ash Maurya, *Running Lean* (2012) — Lean Canvas
- Mike Cohn, *User Stories Applied* (2004) — User Story Format

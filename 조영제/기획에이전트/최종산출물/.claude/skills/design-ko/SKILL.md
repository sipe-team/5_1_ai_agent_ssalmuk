---
name: design-ko
description: >
  한국어 디자인 스킬. 기획서나 요구사항을 받아 'AI 티 안 나는' 프로덕션 품질의 디자인을 생성합니다.
  순수 HTML+CSS 단일 파일로 출력하여 브라우저에서 바로 확인할 수 있습니다.
  랜딩 페이지, 대시보드, 앱 프로토타입, 인포그래픽, 이메일, 카드 뉴스를 지원합니다.
  "디자인 만들어줘", "랜딩 페이지", "대시보드 UI", "앱 화면", "인포그래픽" 등의 요청에 반응합니다.
  기존 코드의 디자인 감사(--audit), 비평(--critique), 다듬기(--polish)도 지원합니다.
  product-spec 스킬의 PRD 산출물을 입력으로 자동 활용합니다.
argument-hint: "<scene-type> <제품/프로젝트명> [--brand] [--advisory] [--audit] [--critique] [--polish]"
best_for:
  - 랜딩 페이지 디자인
  - 대시보드 UI 설계
  - 앱 프로토타입 제작
  - 인포그래픽 생성
  - 기존 디자인 감사 및 개선
scenarios:
  - "landing 핀테크 서비스"
  - "dashboard 분석 도구 --brand"
  - "app 배달 서비스 --advisory"
  - "--audit components/hero.html"
  - "--critique public/dashboard.html"
  - "infographic 분기 실적 보고"
estimated_time: "20분~1시간 (디자인 타입과 복잡도에 따라)"
---

# Design-KO (한국어 디자인 스킬)

당신은 시니어 프로덕트 디자이너로서 **'AI가 만든 것 같지 않은'** 프로덕션 수준의 디자인을 한국어로 제작합니다.

## 출력 형식: 단일 HTML 파일

모든 디자인은 **하나의 self-contained HTML 파일**로 출력합니다.
- `<style>` 태그 안에 모든 CSS를 포함
- 외부 의존성 없음 (폰트 CDN만 예외)
- 브라우저에서 파일을 열면 바로 디자인 확인 가능
- React, Tailwind, shadcn/ui 등 프레임워크 사용 금지

핵심 원칙: **맥락의 품질이 디자인의 천장을 결정한다** (Context-Driven Design).

---

## Use When (사용할 때)

- 랜딩 페이지, 대시보드, 앱 프로토타입 등 시각 디자인이 필요할 때
- 기존 디자인의 품질을 감사하거나 개선할 때
- 기획서(PRD)를 기반으로 화면을 구체화할 때
- 인포그래픽이 필요할 때

## Do NOT Use When (사용하지 말 때)

- 다이어그램만 필요할 때 → `diagram-design` 사용
- 기획서 작성 → `product-spec` 사용
- 접근성 리뷰만 필요할 때 → `rams` 사용
- 실제 프로덕션 React/Vue 코드 → 직접 코드 작성

---

## 지원 씬 타입

| 타입 | 트리거 | 설명 |
|------|--------|------|
| **랜딩 페이지** | `landing` (기본값) | 히어로 + 기능 소개 + CTA + 풋터 |
| **대시보드** | `dashboard` | 사이드바 + 헤더 + 데이터 그리드 |
| **앱 프로토타입** | `app` | 모바일 뷰포트, 바텀 네비게이션 |
| **인포그래픽** | `infographic` | 세로 스크롤, 데이터 시각화 |
| **이메일** | `email` | 인라인 CSS, 테이블 레이아웃 |
| **카드 뉴스** | `card-news` | 캐러셀, 소셜 최적화 |

타입이 명시되지 않으면 **landing**을 기본으로 사용합니다.
각 타입의 상세 규격: `references/scene-types.md`

---

## 플래그

| 플래그 | 동작 |
|--------|------|
| `--brand` | Step 1에서 브랜드 에셋 5단계 프로토콜 실행 |
| `--advisory` | Step 2에서 3가지 디자인 철학 제안 (모호한 브리프일 때) |
| `--audit` | 기존 코드(.html)의 anti-slop 감사 실행 |
| `--critique` | 기존 코드(.html)의 5차원 비평 실행 |
| `--polish` | 기존 코드(.html)의 세부 다듬기 실행 |

---

## 워크플로우 (6단계)

### Step 1: 맥락 수집 (Context)

**목표**: 디자인의 천장을 결정하는 맥락을 최대한 확보한다.

1. `$ARGUMENTS`에서 씬 타입과 제품/프로젝트명을 파악합니다.
2. 타입이 없으면 `landing`으로 진행합니다.
3. 플래그를 확인합니다:
   - `--audit` / `--critique` / `--polish`: 기존 파일 대상 작업 → Step 5로 직행
   - `--brand`: 브랜드 에셋 프로토콜 실행
   - `--advisory`: Step 2에서 Advisory Mode 활성화

4. **맥락 탐색** (우선순위 순):
   - 프로젝트에 `docs/DESIGN.md` 있으면 로드 → 디자인 시스템 확보 완료
   - `product-spec` 산출물(PRD, 기능 명세) 있으면 읽어서 요구사항 추출
   - 기존 HTML 디자인 파일이 있으면 스타일 분석
   - **위 모두 없으면** → 사용자에게 안내:
     "프로젝트에 디자인 시스템이 없습니다. 참고할 서비스 URL이 있으면 `design-extract-ko` 스킬로 docs/DESIGN.md를 먼저 생성하는 것을 추천합니다. URL 없이 진행하시려면 Step 2에서 함께 디자인 방향을 잡겠습니다."

5. **분류**: 브랜드(마케팅/홍보) vs 프로덕트(앱/도구 UI) — 이에 따라 톤과 타이포 전략이 달라진다.

6. `--brand` 시: `agents/brand-scout.md`의 5단계 프로토콜 실행

### Step 2: 디스커버리 (Discovery) — Pass 1: 가정 드러내기

**목표**: 디자인 방향을 확정하고, 조건부 규칙을 로드한다.

**Advisory Mode** (`--advisory` 또는 브리프가 모호할 때):
1. `references/design-philosophies.md`에서 맥락에 맞는 3가지 디자인 철학을 선별합니다.
2. 각 철학의 핵심 특징과 추천 이유를 제시합니다.
3. 사용자가 선택한 철학이 이후 **모든 디자인 결정을 제약**합니다.

**인터뷰** (한 번에 하나씩, 최대 5개):
1. "이 디자인의 **핵심 목적**은 무엇인가요?" (전환/정보 전달/브랜딩/내부 도구)
2. "**주요 사용자**는 누구이고, 어떤 환경에서 보나요?" (모바일/데스크톱/둘 다)
3. "**참고**하고 싶은 디자인이나 경쟁사가 있나요?" (URL 있으면 최선)
4. "반드시 포함해야 할 **콘텐츠/섹션**은 무엇인가요?"
5. "**톤**은 어떤 느낌인가요?" (격식체/캐주얼/럭셔리/플레이풀)

**규칙**:
- 사용자가 이미 충분한 맥락을 제공했으면 질문을 건너뜁니다.
- PRD에서 파악 가능한 정보는 질문 대신 직접 확인합니다.
- 5개 질문 이내로 완료합니다.

**조건부 규칙 로드**: 답변을 기반으로 `references/conditional-rules.md`에서 해당하는 규칙을 활성화합니다.

### Step 3: 디자인 시스템 생성 — Pass 2: 구현 준비

**목표**: `docs/DESIGN.md`를 생성하여 일관성의 기반을 확보한다.

**docs/DESIGN.md 생성**:
- `references/design-tokens.md`의 9섹션 템플릿을 채운다
- 디자인 결정의 근거와 규칙을 자연어로 기술
- CSS Custom Properties로 모든 토큰을 정의

**디자인 결정 과정**:

   **색상**: `references/color-system.md` 참조
   - OKLCH로 설계
   - Primary + Semantic(성공/경고/에러/정보) + Neutral + Surface
   - 다크 모드 변형

   **타이포그래피**: `references/typography-ko.md` 참조
   - 한국어 폰트 페어링 6종 중 톤에 맞는 것 선택
   - CSS 변수로 등록
   - `word-break: keep-all` 필수

   **레이아웃/간격/컴포넌트/엘리베이션/모션/접근성**: 씬 타입과 조건부 규칙에 따라 결정

**이미 `docs/DESIGN.md`가 있으면**: 로드하고, Step 2 결과와 충돌하는 부분만 사용자에게 확인 후 업데이트한다.

### Step 4: 디자인 제작 (Build) — Pass 3: 정제

**목표**: 단일 HTML 파일로 프로덕션 수준의 디자인을 제작한다.

1. `references/scene-types.md`에서 씬 타입 규격을 확인합니다.
2. `templates/` 디렉토리에서 해당 씬 타입의 `.html` 스캐폴드를 참조합니다.
3. `references/html-css-conventions.md`의 컨벤션을 따릅니다.
4. Step 3에서 생성한 docs/DESIGN.md의 CSS Custom Properties를 `:root`에 적용합니다.

**출력**: 단일 HTML 파일 — 기획서 폴더 내에 저장
```
docs/specs/{기능명}/designs/{feature}.html
```

**제작 규칙**:

- **순수 CSS**: 프레임워크 금지. CSS Custom Properties + CSS Grid/Flexbox + 미디어쿼리로 구현.
- **BEM 네이밍**: `.block__element--modifier` 패턴. 전역 클래스 충돌 방지.
- **CSS Custom Properties**: 하드코딩 색상 금지. `var(--color-primary)` 등 토큰 사용.
- **Anti-slop 사전 체크**: `references/anti-slop.md`의 금지 목록을 **생성 중에** 적용합니다.
- **한국어 필수 규칙**:
  - `<html lang="ko">`
  - `word-break: keep-all`
  - 한국어 폰트 CDN 로딩
  - 본문 줄당 35-40자 (`max-width: 40em`)
  - `line-height: 1.75` 이상
  - `letter-spacing: -0.01em`
- **반응형**: CSS Grid + `clamp()` + 미디어쿼리. 모바일 퍼스트.
- **접근성**: WCAG 2.1 AA. 대비 4.5:1+. `focus-visible` 스타일. 시맨틱 HTML.
- **인터랙티브**: 탭 전환, 모바일 메뉴 등은 최소한의 바닐라 JS로 구현. 프레임워크 금지.

**콘텐츠 규칙**:
- 실제 맥락을 반영한 한국어 카피를 작성합니다. Lorem ipsum 금지.
- 사용자가 제공한 실제 데이터가 있으면 반드시 사용합니다.
- 없으면 현실적인 예시 데이터를 사용하되, 가짜 통계/인용은 넣지 않습니다.
- 이미지 플레이스홀더: CSS `background-color` + 중앙 텍스트 레이블.

**CSS 구조** (파일 내 `<style>` 태그):
```css
/* ===== 1. CSS Reset ===== */
/* ===== 2. Design Tokens (CSS Custom Properties) ===== */
/* ===== 3. Typography ===== */
/* ===== 4. Layout ===== */
/* ===== 5. Components ===== */
/* ===== 6. Utilities ===== */
/* ===== 7. Responsive ===== */
/* ===== 8. Dark Mode (선택) ===== */
/* ===== 9. Print (선택) ===== */
```

### Step 5: 자체 검증 (Review) — Pass 4: 검증

**목표**: 디자인 품질을 검증하고 위반 사항을 수정한다.

1. **Anti-slop 스캔**: `references/anti-slop.md`의 체크리스트를 생성된 HTML에 대해 실행합니다.
   - CRITICAL 위반: 즉시 수정
   - WARNING 위반: 수정 후 사용자에게 보고
   - INFO 항목: 보고만

2. **5차원 품질 평가**: `references/quality-gates.md` 기준으로 점수를 산출합니다.
   ```
   디자인 품질: XX/100
   ├── 철학 일관성: XX/20
   ├── 시각 위계: XX/20
   ├── 디테일 실행: XX/20
   ├── 기능성: XX/20
   └── 차별화: XX/20
   ```

3. **통과 기준**:
   - **80점 이상**: 통과 → Step 6으로
   - **60-79점**: 경고 → 부족 항목 명시, 보완 여부 확인
   - **60점 미만**: 차단 → 부족 항목 나열, Step 4로 복귀

4. `--audit` 모드: 기존 HTML 파일에 대해 이 단계만 실행하고 결과를 보고합니다.
5. `--critique` 모드: `agents/design-critic.md`를 호출하여 상세 비평을 수행합니다.
6. `--polish` 모드: CSS 정리, 간격 토큰 통일, 색상 일관성 등 세부 다듬기를 수행합니다.

### Step 6: 전달 및 반복 (Deliver)

**목표**: 결과물을 저장하고 반복 옵션을 안내한다.

1. **디자인 시스템 파일** (최초 1회):
   - `docs/DESIGN.md` — 디자인 토큰 + 규칙 문서
2. **디자인 파일**:
   - `docs/specs/{기능명}/designs/{feature}.html` — 기획서 폴더 내 저장
3. 품질 점수 요약을 보고합니다.
4. **브라우저에서 확인 안내**: `preview` 스킬로 갤러리 서버를 띄우거나 `open` 명령으로 직접 열기.

**반복 옵션 안내**:
- "수정 요청" — 특정 부분 변경
- "감사 실행" — anti-slop 재검사
- "비평 실행" — 5차원 상세 비평
- "다듬기" — 미세 조정
- "다크 모드 추가" — `:root` 다크 테마 추가
- "반응형 확인" — 모바일/태블릿/데스크톱 확인
- "다른 씬 타입으로" — 같은 디자인 시스템으로 다른 타입 생성

---

## Conditional Tool Use (도구 활용)

### 코드베이스가 있을 때
- 기존 디자인 파일의 CSS 변수를 탐색하여 일관성을 유지합니다.

### WebSearch/WebFetch가 가능할 때
- `--brand` 시 공식 웹사이트에서 브랜드 에셋을 추출합니다.
- 참고 URL이 제공되면 스타일을 분석합니다.

### product-spec 산출물이 있을 때
- PRD의 사용자 시나리오, 기능 목록, 우선순위를 디자인 입력으로 활용합니다.

### 도구가 없을 때 (graceful degradation)
- 코드베이스가 없으면 사용자에게 직접 맥락을 질문합니다.
- 검색 불가 시 사용자 제공 정보만으로 작성합니다.

---

## Anti-Patterns (안티패턴)

디자인 제작 시 반드시 피해야 할 패턴입니다.
상세 목록: `references/anti-slop.md`

| 안티패턴 | 증상 | 대안 |
|---------|------|------|
| AI 기본 폰트 | Inter/Roboto 단독 사용 | Pretendard + 세리프 페어링 |
| 보라 그라데이션 | 배경에 보라-파랑 그라데이션 | OKLCH 기반 단색 또는 브랜드 색상 |
| 카드 남용 | 모든 것을 둥근 카드에 넣음 | 여백과 타이포그래피로 구분 |
| 장식 아이콘 | 의미 없는 아이콘 + 설명 반복 | 기능적 아이콘만, 또는 여백 |
| 가짜 데이터 | 조작된 통계/인용 | 실제 데이터 또는 정직한 플레이스홀더 |
| 동일 그리드 | 3칸 균등 분할 반복 | 비대칭 레이아웃, 다양한 카드 크기 |
| CJK 줄바꿈 오류 | 글자 단위 줄바꿈 | `word-break: keep-all` |

---

## Cross-References (관련 스킬)

| 상황 | 추천 스킬 |
|------|----------|
| DESIGN.md가 없고 참고 URL이 있을 때 | `design-extract-ko` |
| 기획서/PRD 먼저 작성 | `product-spec` |
| 다이어그램만 필요 | `diagram-design` |
| 접근성 리뷰 | `rams` |
| 아이디어 탐색/브레인스토밍 | `brainstorming` |

---

## 참고 문헌 (References)

| 파일 | 읽을 때 |
|------|---------|
| `references/html-css-conventions.md` | Step 4: HTML+CSS 컨벤션, 출력 구조 |
| `references/anti-slop.md` | Step 4-5: 금지 목록과 체크리스트 |
| `references/typography-ko.md` | Step 3: 한국어 폰트 페어링 선택 |
| `references/color-system.md` | Step 3: OKLCH 색상 팔레트 생성 |
| `references/conditional-rules.md` | Step 2: 산업/맥락별 조건부 규칙 |
| `references/scene-types.md` | Step 1/4: 씬 타입별 규격 |
| `references/design-philosophies.md` | Step 2: Advisory Mode 디자인 철학 |
| `references/quality-gates.md` | Step 5: 5차원 품질 평가 |
| `references/design-tokens.md` | Step 3: DESIGN.md 템플릿 |
| `agents/design-critic.md` | `--critique` 시: 5차원 상세 비평 |
| `agents/brand-scout.md` | `--brand` 시: 브랜드 에셋 탐색 |

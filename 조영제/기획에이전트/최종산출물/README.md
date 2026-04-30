# heka-product-harness

Claude Code 위에서 **제품 기획 → 명세 → 디자인 → 시각화 → 미리보기**까지 한국어로 처리할 수 있도록 묶어둔 **에이전트 스킬 묶음(Harness)** 입니다.

PM/PO, 백엔드, 프론트엔드, QA, 디자이너 각 역할의 시니어가 머릿속에 가지고 있을 법한 작업 절차를 스킬로 정리해서, "기획서 한 줄"에서 시작해 "개발팀이 바로 착수 가능한 산출물"까지 끌고 가는 것을 목표로 합니다.

## 디렉토리 구조

```
heka-product-harness/
└── .claude/
    └── skills/
        ├── brainstorming/         아이디어 → 디자인 도큐먼트 단계의 디스커버리
        ├── product-spec/          PRD / Feature Spec / User Story / Tech Spec 작성
        ├── prd-update/            기획서 변경을 downstream 명세서로 전파
        ├── be-spec/               백엔드 명세서 자동 도출
        ├── fe-spec/               프론트엔드 명세서 자동 도출
        ├── qa-spec/               QA 테스트 명세서 자동 도출
        ├── design-extract-ko/     레퍼런스 URL → DESIGN.md 디자인 시스템 추출
        ├── design-ko/             한국어 프로덕션 품질 디자인 (HTML+CSS) 생성
        ├── diagram-design/        13종 기술/제품 다이어그램 (HTML+inline SVG)
        └── preview/               docs/specs/ 산출물을 브라우저 갤러리로 미리보기
```

각 스킬은 단일 폴더에 `SKILL.md`(에이전트 지시문)와 필요한 경우 `references/`, `templates/`, `agents/`, `assets/`, `scripts/`를 함께 포함합니다.

## 산출물 폴더 컨벤션

스킬들은 산출물을 다음 위치에 저장하도록 합의되어 있습니다.

```
docs/
├── DESIGN.md                          design-ko / design-extract-ko 의 디자인 시스템
└── specs/
    └── {기능명}/
        ├── prd.md                     product-spec — PRD
        ├── feature-spec-{기능}.md     product-spec — Feature Spec
        ├── user-stories.md            product-spec — User Story
        ├── tech-spec.md               product-spec — Tech Spec
        ├── be-spec.md                 be-spec
        ├── fe-spec.md                 fe-spec
        ├── qa-spec.md                 qa-spec
        ├── changelog.md               prd-update 변경 로그
        ├── designs/*.html             design-ko 산출물
        └── diagrams/*.html            diagram-design 산출물
```

`preview` 스킬은 이 구조를 그대로 스캔해서 갤러리로 보여줍니다.

## 스킬별 역할

### 1. brainstorming
모든 창작 작업(기능 추가, 컴포넌트 생성, 동작 변경)에 **앞서** 의도/요구사항/디자인을 자연스러운 대화로 정제합니다. 한 번에 한 질문, 2~3안 비교, 합의된 디자인 도큐먼트를 `docs/superpowers/specs/`에 커밋한 뒤에야 구현 단계로 넘깁니다. 시각적 옵션이 필요하면 Visual Companion(브라우저)을 옵트인으로 띄울 수 있습니다.

### 2. product-spec
시니어 PM/PO 역할. **PRD / Feature Spec / User Story / Tech Spec** 4종 기획서를 작성합니다.
- Step 0 Go/No-Go 진단부터 Step 9 내보내기까지 10단계 워크플로우
- Visual Companion으로 화면 목업/와이어프레임을 브라우저에서 클릭 비교
- 4역할(FE/BE/QA/팀리더) 다중 관점 자동 리뷰
- 산출물은 `docs/specs/{기능명}/`에 저장되어 다른 스킬의 입력이 됩니다.

### 3. prd-update
변경 관리자 역할. PRD나 Feature Spec이 변경되면 **be-spec / fe-spec / qa-spec를 통째로 다시 만들지 않고 변경 부분만 패치**합니다.
- Phase 1 의존성 맵 구축 → Phase 2 변경 분류(ADD/MODIFY/REMOVE/SPLIT/DEFER) → Phase 3 영향 분석 → Phase 4 적용 → Phase 5 검증 → Phase 6 보고
- "일관성 검사(sync check)" 모드만 단독 실행도 가능

### 4. be-spec
시니어 백엔드 개발자 역할. PRD + Feature Spec을 읽고 **`be-spec.md`** 1개를 도출합니다.
- API 엔드포인트 목록 / 상세 요청·응답 / 데이터 모델(제안) / 비즈니스 로직 의사코드 / 외부 연동 / NFR / 동시성 & 정합성 / 이벤트·알림 / BE 결정 필요 사항
- 기술 스택은 확정하지 않음 — 제안만, 확정은 BE팀

### 5. fe-spec
시니어 프론트엔드 개발자 역할. **`fe-spec.md`** 1개를 도출합니다.
- 화면 인벤토리 / 화면별 컴포넌트 트리 + 인터랙션 + UI 상태 / API 연동 포인트 / 실시간 데이터 / 폼 & 유효성 / 네비게이션 흐름 / DESIGN.md 토큰 참조 / FE 결정 필요 사항
- 프레임워크/상태관리 라이브러리는 지정하지 않음

### 6. qa-spec
시니어 QA 엔지니어 역할. **"기획자가 놓친 시나리오를 발굴"** 하는 것이 핵심 가치입니다.
- 테스트 매트릭스(기존 TC + QA 추가 TC), 10가지 발굴 관점(상태 전이 누락, 타이밍 경쟁, 네트워크, 다중 기기 등), 경계값 분석, 사이드이펙트 회귀, UI 상태 매트릭스, 반응형/비기능 테스트, 인수 조건 ↔ TC 매핑
- 자동화 스크립트나 도구 확정은 하지 않음

### 7. design-extract-ko
레퍼런스 URL에서 **색상·폰트·간격·컴포넌트 패턴**을 추출해 `docs/DESIGN.md` + `tailwind.config.ts` + `globals.css` 3종을 생성합니다.
- 추측이 아닌 **CSS 추출 우선** 원칙
- `--compare`로 여러 URL의 토큰을 비교, `--dark`로 다크 모드 동시 추출
- DESIGN.md가 없을 때 design-ko가 호출하도록 안내됩니다.

### 8. design-ko
한국어 프로덕트 디자이너 역할. **'AI 티 안 나는' 단일 HTML 파일** 디자인을 생성합니다.
- 씬 타입: `landing` / `dashboard` / `app` / `infographic` / `email` / `card-news`
- 6단계: 맥락 수집 → 디스커버리 → DESIGN.md 생성 → 제작 → Anti-slop 검증(5차원 100점 평가) → 전달
- `--brand` / `--advisory` / `--audit` / `--critique` / `--polish` 플래그
- React/Tailwind 프레임워크 금지, 순수 HTML+CSS, 한국어 타이포(`word-break: keep-all` 등) 강제

### 9. diagram-design
13종 다이어그램(architecture / flowchart / sequence / state / ER / timeline / swimlane / quadrant / nested / tree / layers / venn / pyramid)을 **inline SVG 단일 HTML**로 생성합니다.
- 신규 프로젝트 첫 실행 시 스타일 가이드 커스터마이즈 게이트
- 4px 그리드, 노드 9개·아크센트 2개 이하의 복잡도 예산, "삭제가 최고의 디자인" 철학
- minimal light / dark / full editorial / sketchy 변형, 컨설턴트 2×2 매트릭스 특수 변형

### 10. preview
`docs/specs/{기능명}/designs/*.html`과 `diagrams/*.html`을 **외부 의존성 없는 자체 내장 서버**(`scripts/server.cjs`)가 갤러리로 띄웁니다.
- HTTP + WebSocket으로 파일 변경 시 자동 새로고침
- 카드 그리드, 카테고리/기능별 필터
- `package.json` / `vite.config.js`를 건드리지 않으며, 1시간 비활성 시 자동 종료
- `--stop`으로 종료, 상태 파일은 `.preview-server/`에 격리

## 일반적인 사용 흐름

```
brainstorming                (아이디어 정제)
      ↓
product-spec                 (PRD / Feature Spec 작성)
      ↓
   ┌──┴───┬─────────┐
   ↓      ↓         ↓
be-spec  fe-spec  qa-spec   (역할별 명세 병렬 도출)
   │      │         │
   └──┬───┴─────────┘
      ↓
prd-update                   (요구사항 변경 시 downstream 동기화)

design-extract-ko → design-ko + diagram-design → preview
                    (레퍼런스 URL → 디자인 시스템 → 화면/다이어그램 → 갤러리)
```

각 스킬은 **이전 단계의 산출물을 입력으로 받고**, 자신의 산출물을 같은 `docs/specs/{기능명}/` 폴더에 누적합니다. 따라서 어떤 스킬을 단독으로 호출하든 폴더만 보면 작업 맥락이 그대로 복원됩니다.

## 스킬이 공통으로 지키는 규칙

- **상태 관리·보안·런치 플랜·스토리 포인트는 기획서 산출물에서 제외** — 각각 개발팀/보안 리뷰/출시 운영/추정의 영역
- **API·데이터 모델은 기획 확정 후 별도 스킬(be-spec)에서 도출** — PRD에는 포함하지 않음
- **기술 스택은 확정하지 않고 "제안"으로만 표기** — 확정은 해당 직군이 결정
- **기획서에 없는 기능을 임의로 추가하지 않음** — 각 스킬은 "도출 근거"를 모든 항목에 명시

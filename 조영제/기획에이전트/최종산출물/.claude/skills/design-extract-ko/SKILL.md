---
name: design-extract-ko
description: >
  URL에서 디자인 시스템을 추출하는 스킬. 서비스 URL을 입력하면 해당 페이지의 색상, 폰트, 간격, 컴포넌트 패턴을 분석하여
  DESIGN.md + tailwind.config.ts + globals.css를 자동 생성합니다.
  "디자인 추출", "디자인 시스템 뽑아줘", "이 사이트 스타일 분석", "DESIGN.md 만들어줘" 등의 요청에 반응합니다.
  design-ko 스킬에서 프로젝트에 DESIGN.md가 없을 때 이 스킬을 먼저 실행하도록 안내합니다.
argument-hint: "<URL> [추가 URL...] [--compare] [--dark]"
best_for:
  - 기존 서비스의 디자인 시스템 문서화
  - 레퍼런스 사이트 스타일 분석
  - 신규 프로젝트의 DESIGN.md 초기 생성
  - 경쟁사 디자인 비교 분석
scenarios:
  - "https://example.com"
  - "https://example.com --dark"
  - "https://a.com https://b.com --compare"
  - "디자인 시스템 뽑아줘 https://myservice.com"
estimated_time: "5분~15분 (URL 수와 복잡도에 따라)"
---

# Design Extract KO (디자인 추출 스킬)

당신은 시니어 디자인 시스템 엔지니어로서, 실제 운영 중인 웹 서비스의 URL을 분석하여 **DESIGN.md + tailwind.config.ts + globals.css**를 자동 생성합니다.

핵심 원칙: **추측하지 말고 추출하라.** CSS에서 읽은 값이 스크린샷에서 추정한 값보다 항상 정확하다.

---

## Use When (사용할 때)

- 프로젝트에 `docs/DESIGN.md`가 없고, 참고할 서비스 URL이 있을 때
- 기존 서비스의 디자인 시스템을 문서화하고 싶을 때
- 경쟁사나 레퍼런스 사이트의 스타일을 분석하고 싶을 때
- `design-ko` 스킬 사용 전에 디자인 기반을 먼저 잡고 싶을 때

## Do NOT Use When (사용하지 말 때)

- 이미 docs/DESIGN.md가 있을 때 → `design-ko` 스킬로 바로 디자인 제작
- URL 없이 처음부터 디자인 시스템을 만들 때 → `design-ko --advisory`로 철학 선택부터
- 다이어그램이 필요할 때 → `diagram-design`
- 접근성 검사만 할 때 → `rams`

---

## 플래그

| 플래그 | 동작 |
|--------|------|
| `--dark` | 다크 모드 테마도 함께 추출 |
| `--compare` | 여러 URL의 디자인 토큰을 비교 분석 |

---

## 워크플로우 (5단계)

### Step 1: URL 수집 및 검증

1. `$ARGUMENTS`에서 URL을 파싱합니다.
2. URL이 없으면 사용자에게 요청합니다:
   "분석할 서비스의 URL을 알려주세요. 메인 페이지 URL이 가장 좋습니다."
3. URL 접근 가능 여부를 확인합니다 (WebFetch).
4. 접근 불가 시 대안을 안내합니다:
   - "이 URL에 접근할 수 없습니다. 다른 URL이 있나요?"
   - "또는 스크린샷과 함께 색상/폰트 정보를 직접 알려주셔도 됩니다."

### Step 2: 페이지 분석 및 토큰 추출

WebFetch로 페이지 HTML/CSS를 가져와서 다음을 추출합니다:

**2-1. 색상 추출**
```
추출 우선순위:
1. CSS 커스텀 프로퍼티 (--color-*, --primary, --background 등)
2. Tailwind 설정 (tailwind.config.* 파일이 공개되어 있으면)
3. <meta name="theme-color"> 값
4. 주요 요소의 computed color 값
5. 파비콘/OG 이미지에서 브랜드 색상 유추
```

추출할 색상 목록:
- **Primary**: CTA 버튼, 링크, 강조 요소의 색상
- **Background**: `body`, 메인 컨테이너 배경
- **Foreground**: 본문 텍스트 색상
- **Muted**: 보조 텍스트, 캡션 색상
- **Border**: 구분선, 카드 보더 색상
- **Card**: 카드/패널 배경
- **Accent**: 보조 강조 색상 (있으면)
- **Destructive**: 에러/삭제 색상 (있으면)

**2-2. 타이포그래피 추출**
```
추출 대상:
1. <link> 태그의 Google Fonts / 커스텀 폰트 URL
2. font-family 선언 (body, h1-h6)
3. font-size 시스템 (h1~h6, body, caption 각각)
4. font-weight 사용 패턴
5. line-height 값
6. letter-spacing 값
```

**2-3. 간격 및 레이아웃 추출**
```
추출 대상:
1. 컨테이너 max-width
2. 섹션 간 여백 (padding/margin)
3. 카드 내부 padding
4. 그리드 gap
5. border-radius 패턴
```

**2-4. 컴포넌트 패턴 추출**
```
추출 대상:
1. 버튼 스타일 (padding, radius, 색상, 크기)
2. 카드 스타일 (배경, 보더, 그림자, radius)
3. 입력 필드 스타일
4. 네비게이션 패턴
5. 그림자 시스템 (box-shadow 값)
```

**2-5. 다크 모드 (`--dark` 플래그 시)**
```
추출 대상:
1. prefers-color-scheme: dark 미디어쿼리 내 값
2. .dark 클래스 내 값
3. data-theme="dark" 속성 내 값
```

### Step 3: 사용자 검증

추출한 토큰을 정리하여 사용자에게 확인합니다:

```
다음 디자인 토큰을 추출했습니다. 확인해 주세요:

🎨 색상
├── Primary: #4F46E5 (인디고)
├── Background: #FAFAFA (오프화이트)
├── Foreground: #171717 (다크 그레이)
├── Muted: #737373 (미디엄 그레이)
├── Border: #E5E5E5
└── Card: #FFFFFF

📝 타이포그래피
├── 제목: Pretendard (700)
├── 본문: Pretendard (400)
├── 코드: JetBrains Mono
├── 본문 크기: 16px
└── 줄 높이: 1.75

📐 레이아웃
├── 컨테이너: 1200px
├── 카드 radius: 12px
├── 버튼 radius: 8px
└── 기본 간격: 24px

수정할 부분이 있으면 알려주세요. 없으면 이대로 생성합니다.
```

사용자가 수정을 요청하면 반영합니다.

### Step 4: 파일 생성

확인된 토큰으로 **3가지 파일**을 생성합니다:

**4-1. DESIGN.md**
- `design-ko` 스킬의 `references/design-tokens.md` 9섹션 템플릿을 사용
- 추출한 값으로 각 섹션 채우기
- 추출 출처 URL을 §1 브랜드 개요에 기록
- 추출하지 못한 항목은 기본값 + `<!-- 추출 불가: 기본값 사용 -->` 주석

**4-2. tailwind.config.ts**
- `design-ko` 스킬의 `references/shadcn-tailwind.md` §7 구조 사용
- 추출한 색상을 HSL로 변환하여 CSS 변수 참조 구조로
- 추출한 폰트를 fontFamily에 등록
- 한국어 유틸리티 확장 포함

**4-3. globals.css**
- `design-ko` 스킬의 `assets/globals.css`를 기반으로
- `:root` 블록에 추출한 HSL 값 적용
- `.dark` 블록에 다크 모드 값 적용 (`--dark` 플래그 시)
- 한국어 필수 규칙 포함 (word-break, letter-spacing 등)

### Step 5: 전달

1. 3개 파일을 프로젝트 디렉토리에 저장합니다:
   - `DESIGN.md` → `docs/DESIGN.md`
   - `tailwind.config.ts` → 프로젝트 루트 (기존 파일 있으면 별도 이름으로)
   - `app/globals.css` → app 디렉토리 (기존 파일 있으면 차이점만 제시)

2. 추출 요약을 보고합니다.

3. 다음 단계를 안내합니다:
   - "이제 `design-ko` 스킬로 이 디자인 시스템 기반의 화면을 만들 수 있습니다."
   - "DESIGN.md를 수정하고 싶으면 직접 편집하거나 다시 이 스킬을 실행하세요."

---

## `--compare` 모드

여러 URL이 입력되었을 때:

1. 각 URL에서 독립적으로 토큰을 추출합니다.
2. 비교 테이블을 생성합니다:

```
디자인 토큰 비교
                  서비스 A          서비스 B          서비스 C
Primary           #4F46E5           #2563EB           #7C3AED
Background        #FAFAFA           #FFFFFF           #F8FAFC
본문 폰트         Pretendard        Inter             Spoqa Han Sans
본문 크기         16px              15px              16px
카드 radius       12px              8px               16px
컨테이너 폭       1200px            1280px            1140px
```

3. 공통 패턴과 차이점을 분석합니다.
4. 사용자에게 어떤 방향을 채택할지 질문합니다.
5. 선택된 방향 + 혼합 요소로 docs/DESIGN.md를 생성합니다.

---

## 추출 실패 시 대응

| 상황 | 대응 |
|------|------|
| URL 접근 불가 (403, 500) | 다른 URL 요청 또는 수동 입력 안내 |
| SPA라서 HTML이 비어있음 | "이 사이트는 자바스크립트로 렌더링됩니다. 스크린샷과 색상값을 직접 알려주세요." |
| CSS 변수 없음 (인라인 스타일만) | computed style에서 주요 요소 색상 추출 |
| 폰트 감지 불가 | 시스템 폰트 사용 중임을 안내, 한국어 폰트 페어링 추천 |
| 극히 제한된 정보만 추출 | 추출한 것 + `design-ko`의 기본값으로 docs/DESIGN.md 생성, 부족한 항목 명시 |

---

## Cross-References (관련 스킬)

| 상황 | 추천 스킬 |
|------|----------|
| DESIGN.md 생성 후 화면 제작 | `design-ko` |
| 기획서 먼저 작성 | `product-spec` |
| 접근성 검사 | `rams` |
| 브라우저 자동화로 심층 분석 필요 | `browser-automation` |

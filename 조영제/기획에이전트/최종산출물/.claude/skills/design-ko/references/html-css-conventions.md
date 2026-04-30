# HTML + CSS 컨벤션

> Step 4에서 디자인을 제작할 때 참조한다.
> 이 스킬의 모든 출력은 이 컨벤션을 따른다.

---

## 1. 출력 형식: 단일 HTML 파일

모든 디자인은 **하나의 self-contained HTML 파일**로 출력한다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{프로젝트명} — {페이지명}</title>
  <!-- 폰트 CDN (유일한 외부 의존성) -->
  <link rel="stylesheet" href="..." />
  <style>
    /* 모든 CSS가 여기에 포함 */
  </style>
</head>
<body>
  <!-- 시맨틱 HTML -->
  <script>
    /* 인터랙션이 필요한 경우만 최소한의 바닐라 JS */
  </script>
</body>
</html>
```

### 왜 단일 HTML인가?

- 브라우저에서 파일을 더블클릭하면 바로 보인다
- 빌드 도구, 패키지 매니저, 프레임워크 설정이 필요 없다
- 디자인 의도가 코드에 직접 표현된다 (추상화 레이어 없음)
- 스테이크홀더에게 파일 하나만 공유하면 된다

---

## 2. CSS 구조 (파일 내 `<style>`)

```css
/* ========================================
   1. RESET
   ======================================== */

/* ========================================
   2. DESIGN TOKENS (CSS Custom Properties)
   ======================================== */

/* ========================================
   3. BASE (html, body, 시맨틱 요소)
   ======================================== */

/* ========================================
   4. TYPOGRAPHY
   ======================================== */

/* ========================================
   5. LAYOUT (페이지 전체 구조)
   ======================================== */

/* ========================================
   6. COMPONENTS (재사용 가능한 블록)
   ======================================== */

/* ========================================
   7. SECTIONS (페이지별 고유 섹션)
   ======================================== */

/* ========================================
   8. UTILITIES (최소한)
   ======================================== */

/* ========================================
   9. RESPONSIVE (@media)
   ======================================== */

/* ========================================
   10. DARK MODE (선택)
   ======================================== */

/* ========================================
   11. ANIMATIONS / TRANSITIONS
   ======================================== */
```

---

## 3. CSS Reset (최소한)

매 파일에 포함하는 Reset. 용량 최소화를 위해 필요한 것만:

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  scroll-behavior: smooth;
  hanging-punctuation: first last;
}

body {
  min-height: 100dvh;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
  color: inherit;
}

p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  background: none;
  border: none;
}

ul, ol {
  list-style: none;
}
```

---

## 4. Design Tokens (CSS Custom Properties)

docs/DESIGN.md에서 정의한 토큰을 `:root`에 선언한다.

```css
:root {
  /* ── 색상 ── */
  --color-primary: oklch(0.55 0.15 250);
  --color-primary-hover: oklch(0.48 0.17 250);
  --color-primary-light: oklch(0.92 0.04 250);
  --color-accent: oklch(0.58 0.12 180);

  --color-surface-0: oklch(0.99 0.003 250);   /* 배경 */
  --color-surface-1: oklch(0.96 0.005 250);   /* 카드/섹션 */
  --color-surface-2: oklch(0.92 0.008 250);   /* 호버/활성 */

  --color-ink: oklch(0.18 0.02 250);           /* 주 텍스트 */
  --color-ink-secondary: oklch(0.38 0.02 250); /* 보조 텍스트 */
  --color-ink-muted: oklch(0.55 0.015 250);    /* 약한 텍스트 */
  --color-border: oklch(0.88 0.008 250);       /* 구분선 */

  --color-success: oklch(0.62 0.17 145);
  --color-warning: oklch(0.75 0.15 85);
  --color-error: oklch(0.55 0.22 25);
  --color-info: oklch(0.60 0.15 240);

  /* ── 타이포그래피 ── */
  --font-sans: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-serif: var(--font-sans);  /* 페어링에 따라 변경 */
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --font-heading: var(--font-sans);

  --text-hero: clamp(2rem, 5vw + 1rem, 4rem);
  --text-section: clamp(1.5rem, 3vw + 0.5rem, 2.5rem);
  --text-headline: clamp(1.25rem, 2vw + 0.5rem, 1.75rem);
  --text-body: clamp(1rem, 0.5vw + 0.875rem, 1.0625rem);
  --text-caption: clamp(0.8125rem, 0.3vw + 0.75rem, 0.875rem);
  --text-small: clamp(0.6875rem, 0.2vw + 0.625rem, 0.75rem);

  --weight-heading: 700;
  --weight-body: 400;
  --weight-medium: 500;
  --weight-semibold: 600;

  --leading-body: 1.75;
  --leading-heading: 1.25;
  --tracking-ko: -0.01em;
  --tracking-heading: -0.02em;

  /* ── 간격 (4px 그리드) ── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
  --space-32: 128px;

  /* ── 형태 ── */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* ── 그림자 (2단계만) ── */
  --shadow-sm: 0 1px 3px oklch(0.20 0.02 250 / 0.06);
  --shadow-md: 0 4px 16px oklch(0.20 0.02 250 / 0.08);

  /* ── 모션 ── */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --easing: cubic-bezier(0.16, 1, 0.3, 1);

  /* ── 레이아웃 ── */
  --max-width: 1200px;
  --max-width-narrow: 800px;
  --max-width-prose: 40em;
}
```

---

## 5. 네이밍 컨벤션: BEM

```css
/* Block */
.hero { }

/* Element */
.hero__title { }
.hero__subtitle { }
.hero__cta { }

/* Modifier */
.hero--dark { }
.btn--primary { }
.btn--outline { }
```

**규칙**:
- 블록: 컴포넌트 이름 (소문자, 하이픈 구분) — `metric-card`, `nav-bar`
- 엘리먼트: `__` 구분 — `metric-card__value`
- 모디파이어: `--` 구분 — `metric-card--highlighted`
- 네스팅은 1단계까지만. `.a__b__c` 금지 → `.a__c` 또는 새 블록으로

---

## 6. 시맨틱 HTML 규칙

```html
<!-- 페이지 구조 -->
<header>   <!-- 네비게이션 -->
<main>     <!-- 주 콘텐츠 -->
<section>  <!-- 논리적 섹션 -->
<article>  <!-- 독립 콘텐츠 -->
<aside>    <!-- 사이드바/보조 -->
<footer>   <!-- 풋터 -->
<nav>      <!-- 네비게이션 메뉴 -->

<!-- 텍스트 위계 -->
<h1> 페이지당 1개
<h2> 섹션 제목
<h3> 하위 제목
<p>  본문

<!-- 인터랙티브 -->
<button>    행동 (form submit, 토글, 모달 열기)
<a href>    탐색 (다른 페이지/섹션 이동)

<!-- 데이터 -->
<table>     표 형태 데이터
<ul>/<ol>   목록
<figure>    이미지 + 캡션
<time>      날짜/시간
```

**접근성 필수**:
- 모든 인터랙티브 요소에 `focus-visible` 스타일
- 이미지에 `alt` 텍스트
- 아이콘 전용 버튼에 `aria-label`
- 폼 입력에 `<label>` 연결
- 탭 순서 논리적 (`tabindex` 남용 금지)

---

## 7. 반응형 패턴

```css
/* 모바일 퍼스트 */
.grid {
  display: grid;
  gap: var(--space-6);
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* clamp()로 부드러운 반응형 */
.hero__title {
  font-size: var(--text-hero);  /* clamp 값 */
}

/* 컨테이너 */
.container {
  width: 100%;
  max-width: var(--max-width);
  margin-inline: auto;
  padding-inline: var(--space-4);
}

@media (min-width: 768px) {
  .container { padding-inline: var(--space-8); }
}
```

**브레이크포인트** (참고용, clamp 선호):
- 모바일: < 768px
- 태블릿: 768px ~ 1023px
- 데스크톱: >= 1024px

---

## 8. 인터랙션 (바닐라 JS)

JS가 필요한 경우에만 최소한으로 사용한다:

```html
<script>
  // 탭 전환
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      document.querySelectorAll('[data-tab-panel]').forEach(p => {
        p.hidden = p.dataset.tabPanel !== target;
      });
      document.querySelectorAll('[data-tab]').forEach(b => {
        b.classList.toggle('tab--active', b.dataset.tab === target);
      });
    });
  });

  // 모바일 메뉴 토글
  const menuBtn = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  menuBtn?.addEventListener('click', () => {
    const expanded = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', !expanded);
    menu.hidden = expanded;
  });
</script>
```

**JS 규칙**:
- `data-*` 속성으로 타겟팅 (클래스명 의존 금지)
- 이벤트 위임 선호
- DOM 조작 최소화
- CSS로 할 수 있으면 CSS로 (`details/summary`, `:target`, `:checked` 등)

---

## 9. 금지 패턴

```css
/* ❌ 하드코딩 색상 */
color: #6366f1;
background: rgb(99, 102, 241);

/* ✅ CSS Custom Property */
color: var(--color-primary);
background: var(--color-surface-1);

/* ❌ 임의 매직 넘버 */
margin-top: 13px;
padding: 7px 11px;

/* ✅ 토큰 기반 간격 */
margin-top: var(--space-3);
padding: var(--space-2) var(--space-3);

/* ❌ !important */
color: red !important;

/* ❌ transition: all */
transition: all 0.3s;

/* ✅ 개별 속성 지정 */
transition: background-color var(--duration-fast) var(--easing),
            box-shadow var(--duration-fast) var(--easing);

/* ❌ ID 셀렉터 (스타일링 목적) */
#hero-title { }

/* ✅ 클래스 셀렉터 */
.hero__title { }
```

---

## 10. SVG 아이콘

외부 아이콘 라이브러리(Lucide, Heroicons) 대신 인라인 SVG를 사용한다:

```html
<!-- 인라인 SVG (권장) -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M12 5v14M5 12h14"/>
</svg>
```

**규칙**:
- `currentColor`로 부모의 `color` 상속
- `width`/`height` 또는 CSS로 크기 제어
- 장식용 아이콘은 `aria-hidden="true"`
- 의미 있는 아이콘은 `<title>` 또는 `aria-label`

---

## 11. 이미지 플레이스홀더

실제 이미지가 없을 때 CSS로 플레이스홀더를 생성한다:

```css
.placeholder {
  background-color: var(--color-surface-1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-caption);
  color: var(--color-ink-muted);
  border-radius: var(--radius-md);
}
```

```html
<div class="placeholder" style="aspect-ratio: 16/9;">
  제품 스크린샷
</div>
```

---

## 12. 출력 파일 위치

| 파일 | 용도 |
|------|------|
| `docs/DESIGN.md` | 디자인 시스템 문서 |
| `docs/specs/{기능명}/designs/{feature}.html` | 디자인 파일 (기획서 폴더 내) |

# 한국어 타이포그래피 규칙

> Step 3에서 디자인 시스템 생성 시, Step 4에서 디자인 제작 시 참조한다.

---

## 1. 한국어 타이포그래피 원칙

### CJK 특수 규칙

한국어(CJK) 문자는 라틴 문자와 물리적으로 다르다. 같은 font-size에서:
- CJK 글리프는 정사각형 em-box를 거의 꽉 채운다 → 시각적으로 더 무겁다
- 라틴 소문자는 x-height만 차지 → 상대적으로 가벼움
- 따라서 동일 크기에서 한국어는 라틴보다 **더 넓은 행간**이 필요하다

### 필수 CSS 규칙

```css
/* 한국어 텍스트 기본 설정 — 모든 프로젝트에 적용 */
html {
  lang: "ko";
}
body {
  word-break: keep-all;        /* 단어 단위 줄바꿈 (글자 단위 금지) */
  overflow-wrap: break-word;   /* 긴 URL 등은 깨뜨림 */
  line-height: 1.75;           /* 한국어 본문 기본 */
  letter-spacing: -0.01em;     /* 한국어 기본 자간 약간 좁히기 */
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
```

### 줄 길이 (Measure)

| 언어 | 최적 줄당 글자 수 | CSS max-width (본문 16-17px 기준) |
|------|-------------------|----------------------------------|
| 영어 | 65-75자 | 65ch |
| 한국어 | 35-40자 | 40em |

한국어 1글자 ≈ 1em이므로, `max-width: 40em`이 적절하다.

---

## 2. 추천 폰트 페어링 (6종)

### 폰트 로딩 방법

**CDN (권장)**:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
```

---

### 페어링 A: 모던 클린

**톤**: 중립, SaaS, 테크 스타트업
**제목**: Pretendard (600-700)
**본문**: Pretendard (400)
**코드**: JetBrains Mono

```css
:root {
  --font-sans: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-heading: var(--font-sans);
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --weight-heading: 700;
  --weight-body: 400;
}
```

### 페어링 B: 따뜻한 에디토리얼

**톤**: 콘텐츠 플랫폼, 매거진, 블로그
**제목**: Noto Serif KR (700)
**본문**: Noto Sans KR (400)
**코드**: Fira Code

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700&family=Fira+Code:wght@400;500&display=swap&subset=korean" />
```

```css
:root {
  --font-sans: 'Noto Sans KR', -apple-system, system-ui, sans-serif;
  --font-serif: 'Noto Serif KR', Georgia, serif;
  --font-mono: 'Fira Code', ui-monospace, monospace;
  --font-heading: var(--font-serif);
  --weight-heading: 700;
  --weight-body: 400;
}
```

### 페어링 C: 프리미엄

**톤**: 금융, 럭셔리, 고급 서비스
**제목**: Wanted Sans (700)
**본문**: Pretendard (400)
**코드**: IBM Plex Mono

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/wanteddev/wanted-sans@v1.0.3/packages/wanted-sans/fonts/webfonts/variable/split/WantedSansVariable.min.css" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" />
```

```css
:root {
  --font-sans: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-display: 'Wanted Sans Variable', 'Wanted Sans', var(--font-sans);
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
  --font-heading: var(--font-display);
  --weight-heading: 700;
  --weight-body: 400;
}
```

### 페어링 D: 다이내믹

**톤**: 스타트업, 커머스, 에너지
**제목**: Spoqa Han Sans Neo (700)
**본문**: Spoqa Han Sans Neo (400)
**코드**: D2 Coding

```html
<link rel="stylesheet" href="https://spoqa.github.io/spoqa-han-sans/css/SpoqaHanSansNeo.css" />
```

```css
:root {
  --font-sans: 'Spoqa Han Sans Neo', -apple-system, system-ui, sans-serif;
  --font-heading: var(--font-sans);
  --weight-heading: 700;
  --weight-body: 400;
}
```

### 페어링 E: 전통 + 현대

**톤**: 문화, 브랜딩, 출판
**제목**: KoPub Batang (700)
**본문**: Pretendard (400)
**코드**: Fira Mono

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;500&display=swap" />
<style>
  @font-face {
    font-family: 'KoPub Batang';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/KoPubWorldBatangMedium.woff') format('woff');
    font-weight: 500;
    font-display: swap;
  }
  @font-face {
    font-family: 'KoPub Batang';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/KoPubWorldBatangBold.woff') format('woff');
    font-weight: 700;
    font-display: swap;
  }
</style>
```

```css
:root {
  --font-sans: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-serif: 'KoPub Batang', Georgia, serif;
  --font-mono: 'Fira Mono', ui-monospace, monospace;
  --font-heading: var(--font-serif);
  --weight-heading: 700;
  --weight-body: 400;
}
```

### 페어링 F: 공공/정부

**톤**: 공공 서비스, 정부, 비영리
**제목**: Pretendard (700)
**본문**: Pretendard (400)
**코드**: Source Code Pro

Pretendard는 정부24 등 공공 서비스에서도 사용. 중립적이고 접근성이 좋다.

```css
:root {
  --font-sans: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-heading: var(--font-sans);
  --weight-heading: 700;
  --weight-body: 400;
  /* 공공: 더 큰 기본 폰트 크기 */
  --text-body: 17px;
  --line-height-body: 1.8;
}
```

---

## 3. 크기 시스템 (반응형)

모바일 퍼스트 기준. `clamp()`로 부드러운 반응형 적용.

| 토큰 | 모바일 (375px) | 데스크톱 (1440px) | CSS clamp | 용도 |
|------|---------------|-------------------|-----------|------|
| `--text-hero` | 32px | 64px | `clamp(2rem, 5vw + 1rem, 4rem)` | 메인 히어로 |
| `--text-section` | 24px | 40px | `clamp(1.5rem, 3vw + 0.5rem, 2.5rem)` | 섹션 제목 |
| `--text-headline` | 20px | 28px | `clamp(1.25rem, 2vw + 0.5rem, 1.75rem)` | 기능 제목 |
| `--text-body` | 16px | 17px | `clamp(1rem, 0.5vw + 0.875rem, 1.0625rem)` | 본문 |
| `--text-caption` | 13px | 14px | `clamp(0.8125rem, 0.3vw + 0.75rem, 0.875rem)` | 캡션, 보조 |
| `--text-small` | 11px | 12px | `clamp(0.6875rem, 0.2vw + 0.625rem, 0.75rem)` | 라벨, 배지 |

---

## 4. 혼합 언어 규칙 (한국어 + 영어)

한국어 콘텐츠에 영어가 섞일 때:

```css
/* 영어 포함 텍스트에서 폰트 폴백 최적화 */
.mixed-lang {
  font-family: 'Pretendard', -apple-system, 'Helvetica Neue', sans-serif;
  /* Pretendard가 영어 글리프도 포함하므로 일관성 유지 */
}

/* 영어 전용 구간 (브랜드명, 기술 용어 등) */
.en-only {
  letter-spacing: 0;  /* 영어는 자간 조정 불필요 */
  word-break: normal;  /* 영어 줄바꿈은 기본 규칙 */
}
```

### 혼합 시 주의사항
- 한국어 문장 속 영어 단어는 별도 스타일 불필요 (Pretendard가 처리)
- 영어 전용 섹션(브랜드명 등)에서만 `letter-spacing: 0`
- 숫자가 많은 데이터 영역: `font-variant-numeric: tabular-nums` 추가

---

## 5. 인포그래픽용 크기 규칙

인포그래픽에서는 웹 본문보다 약간 큰 크기 권장:

| 용도 | 최소 크기 | 권장 |
|------|----------|------|
| 인포그래픽 제목 | 28px | 36-48px |
| 인포그래픽 본문 | 14px | 16-18px |

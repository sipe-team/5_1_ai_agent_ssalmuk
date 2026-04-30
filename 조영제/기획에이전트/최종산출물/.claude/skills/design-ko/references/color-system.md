# OKLCH 색상 시스템

> Step 3에서 디자인 시스템의 색상 팔레트를 생성할 때 참조한다.

---

## 1. OKLCH를 쓰는 이유

**HSL의 문제**: 같은 Saturation/Lightness에서 색상(Hue)을 바꾸면 **밝기가 달라 보인다**.
노란색(60deg)은 밝아 보이고, 파란색(240deg)은 어두워 보인다. 이것은 HSL이 인간의 지각을 반영하지 않기 때문.

**OKLCH의 해결**: Lightness가 **지각적으로 균일**하다. L=0.5인 모든 색이 비슷한 밝기로 보인다.
→ 보조색을 유도할 때 "빠진" 느낌 없이 조화로운 팔레트가 나온다.

```css
/* OKLCH 형식 */
color: oklch(0.55 0.15 250);
/*            L     C    H
              │     │    └─ Hue (색상, 0-360)
              │     └─ Chroma (채도, 0-0.4)
              └─ Lightness (밝기, 0-1) */
```

---

## 1.5. OKLCH 직접 사용

모든 CSS에서 OKLCH 값을 직접 사용한다. 변환 불필요.

```css
:root {
  --color-primary: oklch(0.55 0.15 250);
}

.btn--primary {
  background: var(--color-primary);
}
```

**브라우저 지원**: OKLCH는 모든 모던 브라우저(Chrome 111+, Safari 15.4+, Firefox 113+)에서 지원된다.
폴백이 필요한 경우 `@supports`를 사용:

```css
.element {
  background: hsl(230, 65%, 55%);  /* 폴백 */
  background: oklch(0.55 0.15 250);
}
```

---

## 2. 팔레트 생성 규칙

### 2.1 브랜드 색상이 있을 때

1. 브랜드 Primary를 OKLCH로 변환
2. 같은 L과 C를 유지하고 H만 변경하여 Accent 생성
   - 보색: H + 180
   - 분할보색: H + 150, H + 210
   - 유사색: H ± 30
3. Neutral은 Primary의 H를 유지하고, C를 0.005-0.02로 낮춤

```css
/* 예: 브랜드 파랑 기반 */
--color-primary:  oklch(0.55 0.15 250);  /* 브랜드 파랑 */
--color-accent:   oklch(0.55 0.15 30);   /* 보색 계열 (따뜻한 주황) */
--neutral-bg:     oklch(0.97 0.005 250); /* 파랑 기운 뉴트럴 */
```

### 2.2 브랜드 색상이 없을 때

아래 5개 프리셋 팔레트 중 톤에 맞는 것을 선택한다.

---

## 3. 프리셋 팔레트 (5종)

### 팔레트 A: Warm Neutral (따뜻한 중립)
**톤**: 따뜻하고 친근, 콘텐츠/커뮤니티

```css
:root {
  --color-primary:       oklch(0.55 0.12 50);   /* 따뜻한 테라코타 */
  --color-primary-light: oklch(0.72 0.08 50);
  --color-primary-dark:  oklch(0.40 0.14 50);
  --color-accent:        oklch(0.60 0.10 160);  /* 세이지 그린 */
  --color-surface-1:     oklch(0.97 0.008 70);  /* 아이보리 */
  --color-surface-2:     oklch(0.94 0.012 70);
  --color-ink:           oklch(0.22 0.02 50);
  --color-ink-secondary: oklch(0.42 0.02 50);
}
```

### 팔레트 B: Cool Professional (차분한 전문)
**톤**: 신뢰감, SaaS/B2B

```css
:root {
  --color-primary:       oklch(0.52 0.14 250);  /* 딥 블루 */
  --color-primary-light: oklch(0.68 0.10 250);
  --color-primary-dark:  oklch(0.38 0.16 250);
  --color-accent:        oklch(0.58 0.12 180);  /* 틸 */
  --color-surface-1:     oklch(0.98 0.003 250);
  --color-surface-2:     oklch(0.95 0.006 250);
  --color-ink:           oklch(0.18 0.02 250);
  --color-ink-secondary: oklch(0.38 0.02 250);
}
```

### 팔레트 C: Nature (자연)
**톤**: 건강, 웰니스, 친환경

```css
:root {
  --color-primary:       oklch(0.52 0.14 155);  /* 포레스트 그린 */
  --color-primary-light: oklch(0.68 0.10 155);
  --color-primary-dark:  oklch(0.38 0.16 155);
  --color-accent:        oklch(0.62 0.10 85);   /* 골든 옐로우 */
  --color-surface-1:     oklch(0.98 0.005 155);
  --color-surface-2:     oklch(0.95 0.010 155);
  --color-ink:           oklch(0.20 0.02 155);
  --color-ink-secondary: oklch(0.40 0.02 155);
}
```

### 팔레트 D: Bold Tech (대담한 테크)
**톤**: 에너지, 스타트업, 혁신

```css
:root {
  --color-primary:       oklch(0.58 0.20 330);  /* 비비드 마젠타 */
  --color-primary-light: oklch(0.72 0.14 330);
  --color-primary-dark:  oklch(0.42 0.22 330);
  --color-accent:        oklch(0.65 0.18 200);  /* 사이안 */
  --color-surface-1:     oklch(0.97 0.004 330);
  --color-surface-2:     oklch(0.94 0.008 330);
  --color-ink:           oklch(0.18 0.02 330);
  --color-ink-secondary: oklch(0.38 0.02 330);
}
```

### 팔레트 E: Elegant Mono (우아한 모노)
**톤**: 럭셔리, 프리미엄, 미니멀

```css
:root {
  --color-primary:       oklch(0.35 0.04 250);  /* 차콜 (거의 무채색) */
  --color-primary-light: oklch(0.50 0.03 250);
  --color-primary-dark:  oklch(0.22 0.04 250);
  --color-accent:        oklch(0.60 0.10 50);   /* 골드 터치 */
  --color-surface-1:     oklch(0.98 0.002 60);  /* 따뜻한 오프화이트 */
  --color-surface-2:     oklch(0.95 0.004 60);
  --color-ink:           oklch(0.15 0.01 250);
  --color-ink-secondary: oklch(0.40 0.01 250);
}
```

---

## 4. 시맨틱 색상 (모든 팔레트 공통)

```css
:root {
  --color-success:       oklch(0.62 0.17 145);  /* 초록 */
  --color-success-light: oklch(0.90 0.06 145);
  --color-warning:       oklch(0.75 0.15 85);   /* 앰버 */
  --color-warning-light: oklch(0.92 0.06 85);
  --color-error:         oklch(0.55 0.22 25);   /* 빨강 */
  --color-error-light:   oklch(0.90 0.08 25);
  --color-info:          oklch(0.60 0.15 240);  /* 파랑 */
  --color-info-light:    oklch(0.92 0.05 240);
}
```

---

## 5. 다크 모드 변환 규칙

다크 모드는 단순히 밝기를 뒤집지 않는다. 규칙:

1. **배경 L**: 0.15-0.22 범위 (순수 검정 금지)
2. **텍스트 L**: 0.88-0.95 범위 (순수 흰색 금지)
3. **Primary C**: 밝은 배경에서보다 약간 낮추기 (눈 피로 방지)
4. **Surface 계층**: 어두운 쪽에서 밝은 쪽으로 (밝은 모드와 반대)
5. **그림자**: 거의 보이지 않음. 대신 보더로 구분

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: oklch(0.65 0.12 250);        /* L 올리고 C 낮추기 */
    --color-surface-1: oklch(0.15 0.008 250);     /* 가장 어두운 배경 */
    --color-surface-2: oklch(0.20 0.010 250);     /* 약간 밝은 배경 */
    --color-surface-3: oklch(0.26 0.012 250);     /* 카드/모달 */
    --color-ink: oklch(0.92 0.01 250);
    --color-ink-secondary: oklch(0.75 0.01 250);
    --color-border: oklch(0.30 0.012 250);
  }
}
```

---

## 6. 대비 검증

모든 텍스트-배경 조합은 WCAG 2.1 AA 기준을 충족해야 한다:

| 조합 | 최소 대비 | 확인 방법 |
|------|----------|----------|
| 본문 텍스트 : 배경 | 4.5:1 | `oklch` L 차이 ≥ 0.4 (근사) |
| 큰 텍스트 (18px+) : 배경 | 3:1 | `oklch` L 차이 ≥ 0.3 (근사) |
| UI 컴포넌트 : 배경 | 3:1 | 버튼, 입력 필드 보더 |
| 포커스 링 : 배경 | 3:1 | `--focus-ring` 색상 |

OKLCH에서 L 차이로 대비를 근사할 수 있지만, 정확한 검증은 WCAG 공식 대비 계산 필요.

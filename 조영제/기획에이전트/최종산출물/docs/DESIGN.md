# 디자인 시스템 — 코인 예측 게임 (Upbit-inspired Dark)

> 업비트 다크 테마 기반. 한국식 시세 색상(상승=빨강 / 하락=파랑) 적용. OKLCH 색공간으로 일관성 확보.

---

## 1. 디자인 원칙

1. **신뢰 우선** — 거래 화면으로 자연스럽게 이어져야 하므로 게임 톤은 "가벼운 카지노"가 아니라 "데이터 대시보드".
2. **시그널 노이즈 분리** — 8개 카드는 한눈에 비교 가능해야 하며 시각적 중요도가 균등.
3. **한국식 시세 컨벤션** — 상승=빨강, 하락=파랑. 글로벌 표준이 아닌 한국 사용자 직관 우선.
4. **여백이 위계** — 카드 남용 대신 여백/타이포로 분리.
5. **숫자는 monospace** — 가격, %, 적중률 등 숫자는 등폭 폰트.

---

## 2. 색상 (OKLCH)

```css
:root {
  /* Surface */
  --c-bg:        oklch(0.13 0.005 270);   /* near-black, 차분한 청흑 */
  --c-surface:   oklch(0.17 0.008 270);   /* card */
  --c-surface-2: oklch(0.21 0.008 270);   /* sub-card */
  --c-surface-3: oklch(0.26 0.010 270);   /* hover */
  --c-border:    oklch(0.30 0.010 270);
  --c-divider:   oklch(0.24 0.008 270);

  /* Text */
  --c-text:        oklch(0.96 0.005 270);
  --c-text-muted:  oklch(0.70 0.010 270);
  --c-text-subtle: oklch(0.55 0.010 270);

  /* Korean market signal */
  --c-up:        oklch(0.66 0.215 27);    /* 상승 빨강 (vivid red) */
  --c-up-bg:     oklch(0.30 0.080 27);    /* 빨강 배경 */
  --c-down:      oklch(0.62 0.180 250);   /* 하락 파랑 (vivid blue) */
  --c-down-bg:   oklch(0.30 0.080 250);   /* 파랑 배경 */
  --c-neutral:   oklch(0.65 0.010 270);

  /* Tier */
  --c-bronze:    oklch(0.62 0.110 50);
  --c-silver:    oklch(0.78 0.005 270);
  --c-gold:      oklch(0.78 0.150 90);
  --c-platinum:  oklch(0.84 0.060 200);
  --c-diamond:   oklch(0.88 0.130 220);

  /* Semantic */
  --c-success:   oklch(0.70 0.170 145);
  --c-warn:      oklch(0.78 0.150 80);
  --c-info:      oklch(0.72 0.130 230);
}
```

---

## 3. 타이포그래피

```css
:root {
  --font-sans: "Spoqa Han Sans Neo", "Pretendard", -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "D2Coding", ui-monospace, monospace;
}
```

| 토큰 | size / line-height / weight | 용도 |
|------|---|---|
| `--t-display` | clamp(28px, 5vw, 36px) / 1.25 / 700 | 결과 시트 헤드라인 |
| `--t-h1` | 22px / 1.4 / 700 | 화면 타이틀 |
| `--t-h2` | 18px / 1.45 / 600 | 섹션 타이틀 |
| `--t-h3` | 15px / 1.5 / 600 | 카드 타이틀 |
| `--t-body` | 14px / 1.6 / 400 | 본문 |
| `--t-caption` | 12px / 1.5 / 400 | 라벨/시간/소스 |
| `--t-mono-lg` | 24px / 1.2 / 600 | 가격/적중률 큰 숫자 |
| `--t-mono-md` | 16px / 1.2 / 600 | 카드 시그널 % |
| `--t-mono-sm` | 12px / 1.3 / 500 | 거래량/소스수 |

규칙:
- `word-break: keep-all` 필수
- `letter-spacing: -0.01em`
- 본문 줄당 35–40자 (앱 컨텍스트라 제한적, 카드 내부에서만 적용)

---

## 4. 간격 (8px scale)

```
4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64
```

---

## 5. 라운드

```css
--r-sm: 6px;    /* 칩, 작은 버튼 */
--r-md: 10px;   /* 카드, 입력 */
--r-lg: 16px;   /* 시트, 대형 카드 */
--r-pill: 999px;
```

---

## 6. 엘리베이션 (다크 모드)

다크 모드에선 그림자 대신 **밝기 단계**로 위계를 표현:
- L0 = `--c-bg`
- L1 = `--c-surface` (카드)
- L2 = `--c-surface-2` (카드 위 카드)
- L3 = `--c-surface-3` (호버)

```css
--shadow-pop: 0 8px 24px rgba(0,0,0,0.4); /* 모달/시트만 */
```

---

## 7. 모션

- ease-out 200ms 기본 (`cubic-bezier(0.2, 0.8, 0.2, 1)`)
- 티어 승급은 600ms 배지 펄스 (`prefers-reduced-motion: reduce` 시 비활성)
- 카드 hover transform 금지 (모바일 환경 우선)

---

## 8. 컴포넌트 규칙

### 시그널 카드
- 사이즈: 모바일 (375px 뷰포트) 1/2 너비, 데스크톱 1/4
- 구성: 채널명 (caption) → 방향+강도 (mono-md, 색상) → 보조 메타 (caption muted)
- 데이터 stale 표시: 우하단 caption muted

### 시세 변화 표시
- 상승: `color: var(--c-up)` + `↑` 또는 `+`
- 하락: `color: var(--c-down)` + `↓` 또는 `-`
- 무효/중립: `color: var(--c-text-muted)`

### 티어 배지
- 5단계 모두 작은 chip 형태
- 그라데이션 금지 (anti-slop: 보라 그라데이션 금지)
- 색은 단색 + outline

---

## 9. 접근성

- 대비 4.5:1 이상 (본문) / 3:1 이상 (큰 텍스트, 14pt+ bold or 18pt+)
- 색상만으로 ↑/↓ 구분 금지 → 화살표 + 텍스트 함께
- focus-visible: 2px outline `oklch(0.78 0.15 90)` (gold)
- 터치 영역 ≥ 44×44

---

## 10. 안티슬롭 가이드

- ❌ 보라-파랑 그라데이션 배경
- ❌ Inter/Roboto 단독
- ❌ 모든 것을 카드로 감싸기 (예: 헤더는 카드 아님)
- ❌ 의미 없는 아이콘 + 라벨 반복
- ❌ "+12.5% 🚀" 같은 이모지 (Anti-slop)
- ✅ 숫자는 mono, 라벨은 sans
- ✅ 카드 색은 단색 + 미세한 border, 그림자 X

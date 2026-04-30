# DESIGN.md 생성 템플릿

> Step 3에서 프로젝트 디자인 시스템을 생성할 때 이 템플릿을 사용한다.
> 생성물: `docs/DESIGN.md`

---

아래는 생성할 `docs/DESIGN.md`의 구조다. `<!-- 지침 -->` 주석은 작성 가이드이며 최종 문서에서 제거한다.

```markdown
# {프로젝트명} 디자인 시스템

> 이 문서는 design-ko 스킬에 의해 생성되었습니다.
> 프로젝트의 시각적 일관성을 유지하기 위한 디자인 토큰과 규칙을 정의합니다.

---

## 1. 브랜드 개요

- **프로젝트명**: {프로젝트명}
- **분류**: {브랜드(마케팅) | 프로덕트(앱/도구)}
- **디자인 철학**: {선택한 디자인 철학, 예: 기능주의 - 미니멀}
- **톤**: {격식체 | 캐주얼 | 럭셔리 | 플레이풀}
- **핵심 가치**: {1-3개 키워드}

<!-- 지침: brand-scout 에이전트가 발견한 브랜드 에셋 정보도 여기에 기록 -->

---

## 2. 색상 팔레트

<!-- 지침: color-system.md의 프리셋 또는 브랜드 기반으로 생성 -->

### Primary
| 토큰 | OKLCH 값 | 용도 |
|------|----------|------|
| `--color-primary` | `oklch(L C H)` | 주 브랜드 색, CTA |
| `--color-primary-hover` | `oklch(L C H)` | 호버 상태 |
| `--color-primary-light` | `oklch(L C H)` | 배경 강조 |

### Accent
| 토큰 | OKLCH 값 | 용도 |
|------|----------|------|
| `--color-accent` | `oklch(L C H)` | 보조 강조 |

### Semantic
| 토큰 | OKLCH 값 | 용도 |
|------|----------|------|
| `--color-success` | `oklch(0.62 0.17 145)` | 성공, 완료 |
| `--color-warning` | `oklch(0.75 0.15 85)` | 경고, 주의 |
| `--color-error` | `oklch(0.55 0.22 25)` | 에러, 삭제 |
| `--color-info` | `oklch(0.60 0.15 240)` | 정보, 도움말 |

### Surface & Ink
| 토큰 | OKLCH 값 | 용도 |
|------|----------|------|
| `--color-surface-0` | `oklch(L C H)` | 기본 배경 |
| `--color-surface-1` | `oklch(L C H)` | 카드/섹션 배경 |
| `--color-surface-2` | `oklch(L C H)` | 호버/활성 배경 |
| `--color-ink` | `oklch(L C H)` | 주 텍스트 |
| `--color-ink-secondary` | `oklch(L C H)` | 보조 텍스트 |
| `--color-ink-muted` | `oklch(L C H)` | 약한 텍스트 |
| `--color-border` | `oklch(L C H)` | 구분선, 보더 |

---

## 3. 타이포그래피

<!-- 지침: typography-ko.md의 페어링 A-F 중 선택 -->

### 폰트 페어링: {페어링 이름}
| 용도 | 폰트 | Weight | CSS 변수 |
|------|-------|--------|----------|
| 제목 | {font-heading} | {weight} | `--font-heading` |
| 본문 | {font-body} | {weight} | `--font-sans` |
| 코드 | {font-mono} | 400 | `--font-mono` |

### 크기 시스템
| 토큰 | 모바일 | 데스크톱 | CSS clamp |
|------|--------|---------|-----------|
| `--text-hero` | 32px | 64px | `clamp(2rem, 5vw + 1rem, 4rem)` |
| `--text-section` | 24px | 40px | `clamp(1.5rem, 3vw + 0.5rem, 2.5rem)` |
| `--text-headline` | 20px | 28px | `clamp(1.25rem, 2vw + 0.5rem, 1.75rem)` |
| `--text-body` | 16px | 17px | `clamp(1rem, 0.5vw + 0.875rem, 1.0625rem)` |
| `--text-caption` | 13px | 14px | `clamp(0.8125rem, 0.3vw + 0.75rem, 0.875rem)` |

### 한국어 규칙
- `word-break: keep-all`
- `line-height: 1.75` (본문), `1.25` (제목)
- `letter-spacing: -0.01em` (한국어), `0` (영어)
- 최대 줄당 글자수: 35-40자 (`max-width: 40em`)

---

## 4. 간격 시스템

4px 그리드 기반.

| 토큰 | 값 | 용도 |
|------|-----|------|
| `--space-1` | 4px | 최소 간격 |
| `--space-2` | 8px | 인라인 요소 간격 |
| `--space-4` | 16px | 컴포넌트 내부 패딩 |
| `--space-6` | 24px | 컴포넌트 간 간격 |
| `--space-8` | 32px | 그룹 간 간격 |
| `--space-16` | 64px | 섹션 간 여백 (모바일) |
| `--space-24` | 96px | 섹션 간 여백 (데스크톱) |

---

## 5. 컴포넌트 토큰

### 버튼
| 상태 | 배경 | 텍스트 | 보더 |
|------|------|--------|------|
| Primary | `--color-primary` | `white` | 없음 |
| Secondary | `transparent` | `--color-ink` | `--color-border` |
| Ghost | `transparent` | `--color-primary` | 없음 |
| Disabled | `--color-surface-2` | `--color-ink-muted` | 없음 |

### 카드
- 배경: `--color-surface-1`
- 보더: `1px solid var(--color-border)`
- 반경: `--radius-lg` (12px)
- 그림자: 호버 시에만 `--shadow-md`

### 입력 필드
- 배경: `--color-surface-0`
- 보더: `1px solid var(--color-border)`
- 포커스: `--color-primary` 보더 + 포커스 링
- 에러: `--color-error` 보더

---

## 6. 레이아웃 그리드

| 속성 | 모바일 (<768px) | 태블릿 (768-1024px) | 데스크톱 (>1024px) |
|------|----------------|--------------------|--------------------|
| 최대 너비 | 100% | 100% | 1200px |
| 컬럼 | 1 | 2 | 3-4 (콘텐츠에 따라) |
| 거터 | 16px | 24px | 24px |
| 마진 | 16px | 32px | auto |

---

## 7. 엘리베이션 (그림자)

<!-- 지침: 그림자는 2단계까지만. 3단계 이상은 WARNING -->

| 토큰 | 값 | 용도 |
|------|-----|------|
| `--shadow-sm` | `0 1px 3px oklch(0.20 0.02 H / 0.06)` | 미세한 구분 |
| `--shadow-md` | `0 4px 16px oklch(0.20 0.02 H / 0.08)` | 호버, 드롭다운 |

---

## 8. 모션

| 토큰 | 값 | 용도 |
|------|-----|------|
| `--duration-fast` | 150ms | 마이크로인터랙션 |
| `--duration-normal` | 250ms | UI 전환 |
| `--easing` | `cubic-bezier(0.16, 1, 0.3, 1)` | expo-out, 기본 |

규칙:
- `transition: all` 금지. 개별 속성 지정
- GPU 가속 우선: `transform`, `opacity`

---

## 9. 접근성

| 항목 | 기준 |
|------|------|
| 텍스트 대비 | 4.5:1 (AA) 이상 |
| 큰 텍스트 대비 | 3:1 이상 (18px+ 또는 14px+ bold) |
| 터치 타겟 | 최소 44x44px |
| 포커스 스타일 | `2px solid var(--color-primary)`, offset 2px |
| 언어 속성 | `<html lang="ko">` |
| 스크린 리더 | ARIA 레이블 필수 (인터랙티브 요소) |
```

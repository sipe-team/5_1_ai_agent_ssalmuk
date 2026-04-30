# FE Spec — 코인 예측 게임 (24h ↑/↓ + 8채널 인사이트)

> **Owner**: FE 명세 (시니어 프론트엔드)
> **작성일**: 2026-04-30
> **입력 PRD**: `docs/specs/코인예측게임/prd.md`
> **디자인**: `public/designs/coin-prediction-v2.html`, `docs/DESIGN.md`
> **다이어그램**: `docs/specs/코인예측게임/diagrams/flowchart.html`
> **Fidelity**: FE 개발 착수 가능 (라이브러리/프레임워크는 FE팀 자율)

---

## 진행 상태

- [x] PRD §6, §7, §8 정독 완료
- [x] 디자인 갤러리 4프레임 (S-01 / S-03 hit / S-03 miss / S-04) 분석 완료
- [x] DESIGN.md 토큰 매핑 완료
- [x] 자체 리뷰 (체크리스트 10개 항목) PASS

> **메모리 규칙 적용**: 본 명세서는 **상태 관리 라이브러리, 보안, 스토리 포인트, 런치 플랜, API/데이터 모델 확정값**을 포함하지 않습니다. 어디서 무슨 상태가 변하는지·서버 통신이 필요한 시점만 적습니다. 라이브러리 추천은 FE팀 자율.

---

## §0. 요약 (TL;DR)

- 화면 7개 (S-01~S-07). 모바일 우선, 카드 그리드 4×2 고정.
- 핵심 컴포넌트 8개: `CoinToggle`, `PriceBlock`, `CardInsight`(8장), `CTAButton`(↑/↓), `ResultSheet`, `CompareGrid`, `TierBadge`, `ScoreCard`.
- API 호출 19개 (제안). 한 채널 실패가 다른 카드 렌더를 막지 않는다 — 카드별 격리.
- 실시간 스트림 2종(현재가 + 카드 데이터 stale 갱신).
- 한국식 시세 색상 (상승=빨강 `--c-up`, 하락=파랑 `--c-down`).
- BEM 클래스 기준 (디자인 갤러리에 정의된 `.card`, `.coin-toggle`, `.score-card` 등 그대로).

---

## §1. 화면 인벤토리

PRD §8-1을 기반으로 모든 화면을 빠짐없이 나열한다. 디자인 갤러리에서 확인된 프레임은 4개(S-01/S-03 hit·miss/S-04), 나머지 3개(S-02/S-05/S-06/S-07)는 PRD 기반 추정.

| # | 화면 | 진입 | 이탈 | 레이아웃 (M/T/D) | P |
|---|------|------|------|-----------------|---|
| **S-01** | 예측 메인 (카드 그리드) | 메인 → 예측 탭 / 푸시 / 배너 | 카드 탭 → S-02 / ↑↓ 탭 → 다이얼로그 / ← → 메인 | M: 1열 풀스크린, 카드 2×4 / T: 동일 / D: 카드 4×2 가로 (max-width 480) | P0 |
| **S-02** | 카드 상세 시트 | S-01 → 카드 탭 | 닫기/스와이프 down → S-01 | M: 풀스크린 시트 (위→아래 스와이프) / D: 우측 패널 또는 모달 | P0 |
| **S-03** | 결과 시트 (적중/미적중) | 푸시 (콜드부팅 포함) / 인앱 카드 / 마감 직후 인앱 자동 | 닫기 → 메인 / CTA → 거래화면 (replace) / "놓친 시그널" → S-04 | M: 풀스크린 시트 / D: 모달 600x800 | P0 |
| **S-04** | 채널 정답 비교 | S-03 (미적중) → "내가 놓친 시그널" | ← → S-03 / 매수·매도 → 거래화면 | M: 풀스크린, cmp-card 2열 / D: 4열 그리드 | P0 |
| **S-05** | 온보딩 시트 (최초 1회) | 신규 가입자 첫 진입 | "시작하기" → S-01 (replace) | M/D: 풀스크린 시트, 3페이지 swipe | P0 |
| **S-06** | 미성년자/KYC 차단 시트 | KYC 미통과 사용자 진입 | 인증 완료 시에만 닫힘 (닫기 버튼 X) | M/D: 풀스크린 modal (dismiss 불가) | P0 |
| **S-07** | 리더보드 화면 | 마이 → 티어 / S-01 우상단 `TierBadge` 탭 / 고수픽 카드 → 더보기 | ← → S-01 또는 마이 | M: 1열 리스트 + sticky 내 순위 / D: 좌측 리스트 + 우측 프로필 미니 카드 | P0 |

**누락 검증**: PRD §8-1에 등록된 7개 화면이 모두 위 테이블에 포함됨. 거래 화면(BTC/KRW, ETH/KRW)은 본 기능의 외부 화면이며 딥링크 진입(Q-07 의존). 본 FE 스펙 범위 외.

### 라우트 구조 (제안)

> 라우트 형태와 prefix는 FE팀이 결정. 아래는 화면-라우트 매핑의 **제안**.

```
/predict                    → S-01 (?coin=BTC|ETH, default=BTC)
/predict/insight/:channel   → S-02 (channel = datalab|community|topPicks|news|sentiment|polymarket|coinsite|onchain)
/predict/result/:predictId  → S-03 (push deeplink target)
/predict/result/:predictId/compare → S-04
/predict/onboarding         → S-05 (최초 1회, replace)
/predict/blocked            → S-06 (modal, dismiss 불가)
/predict/leaderboard        → S-07 (?period=90d|season)
```

푸시 deeplink 페이로드 예시 (제안): `upbit://predict/result/{predictId}` — 콜드부팅 시 `/predict` 1장 + `/predict/result/:id` 1장으로 백 스택 구성 (PRD §8-8).

---

## §2. 화면별 상세

### §2-1. S-01 예측 메인

#### 컴포넌트 트리

```
PredictMainScreen [/predict]
├── AppBar
│   ├── IconButton.appbar__back — 뒤로 — pop
│   ├── AppBarTitle "오늘의 예측"
│   └── TierBadge (.tier-chip.tier-chip--{bronze|silver|gold|platinum|diamond}) — 우상단 — 탭 시 S-07 push
├── CoinToggle (.coin-toggle, role="tablist")
│   ├── CoinToggleBtn[BTC] (.coin-toggle__btn--active) — 탭 시 컨텍스트 BTC 변경
│   └── CoinToggleBtn[ETH]                                — 탭 시 컨텍스트 ETH 변경
├── PriceBlock (.price-block)
│   ├── PriceValue (.price-block__price.t-mono)
│   ├── PriceDelta (.price-block__delta.--up|--down.t-mono) — 24h 변동률
│   └── DeadlineHint (.price-block__deadline) — "마감 시각 · 내일 09:24 KST · 예측 시각 +24시간"
├── Sparkline (.sparkline) — 24h mini chart, 탭 시 거래 화면 (FE 추가: 다이어그램·PRD 8-2의 "차트 영역")
├── CtaRow (.cta-row)
│   ├── CTAButton.cta--up (.cta__arrow ↑ + "오른다") — 탭 시 ConfirmDialog
│   └── CTAButton.cta--down (.cta__arrow ↓ + "내린다") — 탭 시 ConfirmDialog
│   * 잠금 상태(이미 예측됨)일 때는 두 버튼 disabled + "오늘은 이미 BTC 예측을 했어요" 안내
├── InsightSection (.sect)
│   ├── SectHead (.sect__head) — 제목 "8개 시그널" + 카운트 "P0 6 · P1 2"
│   └── CardGrid (.cards, grid 2×4 mobile / 4×2 desktop)
│       ├── CardInsight[datalab]    (.card)        — 탭 시 S-02 push
│       ├── CardInsight[community]  (.card)        — 탭 시 S-02 push
│       ├── CardInsight[topPicks]   (.card)        — 탭 시 S-02 push
│       ├── CardInsight[news]       (.card)        — 탭 시 S-02 push
│       ├── CardInsight[sentiment]  (.card)        — 탭 시 S-02 push
│       ├── CardInsight[polymarket] (.card)        — 탭 시 S-02 push (R-01 비활성 빌드 시 .card--locked 처리)
│       ├── CardInsight[coinsite]   (.card.card--locked) — 탭 시 "곧 출시" 토스트 (P1)
│       └── CardInsight[onchain]    (.card.card--locked) — 탭 시 "곧 출시" 토스트 (P1)
└── ConfirmDialog (.cta--full, modal) — ↑↓ 탭 시 띄움, "BTC ↑ 예측을 등록할까요? 마감 시각: 내일 08:31 KST. 등록 후 취소할 수 없어요."
```

#### CardInsight 내부 구성 (BEM)

```
.card
├── .card__name — 채널명 (caption muted)
├── .card__signal
│   ├── .card__dir.--up|.--down — ↑/↓ (mono 18px)
│   └── .card__pct.t-mono — % 또는 "우세"
└── .card__meta
    ├── 좌: 보조 메타 ("김치 프리미엄", "1,243명 투표", "$2M 거래량")
    └── 우: .card__stale
        ├── .card__stale-dot (5분 이내 success / 5분 초과 warn — `.card__stale--old`)
        └── 시간 텍스트 ("2분", "8분")
```

`.card--locked` 변형: `border-style: dashed`, `opacity: 0.55`, 시그널 영역에 `.card__locked-tag` ("P1 · 2차 출시") 표시. R-01에 따라 폴리마켓도 동일 적용 가능 (빌드 분기).

#### 인터랙션 테이블 (PRD §8-2 + FE 보완)

| 요소 | 동작 | 네비게이션 | 비고 |
|------|------|-----------|------|
| BTC/ETH 토글 | 탭 | 컨텍스트 변경 (URL ?coin=) | 카드 그리드 전체 재요청, ↑↓ 잠금 상태도 코인별로 독립 |
| ↑ 오른다 | 탭 | ConfirmDialog → 등록 → 잠금 토스트 | optimistic update X (서버 확정 후 잠금) |
| ↓ 내린다 | 탭 | 동일 | |
| CardInsight (P0 6장) | 탭 | S-02 push | 스크롤 위치 보존 |
| CardInsight (P1 2장) | 탭 | "곧 출시" 토스트 | navigation 없음 |
| 차트 영역 (Sparkline) | 탭 | 업비트 BTC/ETH 시세 화면 (외부 push) | [FE 추가] PRD 8-2에 명시, 트리에 누락된 컴포넌트 추가 |
| 좌측 ← | 탭 | pop → 메인 | |
| TierBadge (우상단) | 탭 | S-07 push | |
| CTA disabled (잠금 상태) | 탭 시도 | 무반응 + a11y 라벨 "이미 예측 등록됨, 마감까지 N시간" | [FE 추가] 사용성 |
| 폴리마켓 카드 (R-01 비활성 빌드) | 탭 | "예측시장 데이터 점검 중" 토스트 | [FE 추가] PRD R-01 Plan B 대응 |

#### UI 상태 (PRD §8-5 매핑 + 컴포넌트 단위 세분화)

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `PriceBlock` | 가격 자리 스켈레톤 (mono 28px 자리) | 가격·델타·마감 표시 | (해당 없음) | "—" + 작은 retry 아이콘, 재시도 시 같은 영역 갱신 |
| `Sparkline` | 64px 회색 박스 | SVG path | 해당 없음 | 무표시 (fail open) |
| `CTAButton ↑/↓` | 등록 in-flight: disabled + spinner | 등록 완료 토스트 + 잠금 변환 | — | 토스트 "등록 실패" + 재시도 버튼 (idempotency key 동일) |
| `CardInsight` (각 8장 독립) | 카드별 스켈레톤 (.card 자리, 92px min-height) | 정상 노출 | "현재 데이터 부족 (N건)" 텍스트, dir/pct 영역 비움 | "잠시 후 다시 시도" 플레이스홀더 + 작은 retry. **다른 카드 영향 X** |
| `CardInsight` stale (5분+) | — | dot 색상 warn (`.card__stale--old`) | — | — |
| `TierBadge` | 칩 자리 스켈레톤 | 티어별 색상 칩 | 신규 사용자: 브론즈 기본 | 무표시 (fail open) |
| `ConfirmDialog` | 등록 버튼 spinner | 다이얼로그 닫힘 + 토스트 | — | 다이얼로그 내부 인라인 에러 + 재시도 |

---

### §2-2. S-02 카드 상세 시트

#### 컴포넌트 트리

> 채널 6종(P0)에 대해 시트 셸은 공통, 본문은 채널별 분기. 컴포넌트 분해는 **공통 셸 + 본문 슬롯**으로 한다.

```
InsightSheet (.sheet, modal)
├── SheetHandle (swipe down 영역)
├── AppBar
│   ├── IconButton ← (또는 ✕) — 닫기, focus return to 진입 카드
│   └── AppBarTitle (채널명)
├── SheetBody — 채널별 콘텐츠
│   ├── [datalab]    DatalabPanel — 4개 차트 (김프 / 24h 거래량 / 52주 고저 / 이평 20·60)
│   ├── [community]  CommunityPanel
│   │   ├── VoteBarChart (↑% vs ↓%)
│   │   ├── TopComments (Top5, 닉네임+티어배지+본문+좋아요·신고)
│   │   ├── CommentInput (140자) — `Button/secondary` "코멘트 작성"
│   │   └── ReplyTree (1단계 답글)
│   ├── [topPicks]   TopPicksPanel — 상위 50중 30+ 분포 + 상위 10명 닉네임 카드 (90일 적중률)
│   ├── [news]       NewsPanel — 헤드라인 5건 + 톤(긍/중/부) 칩, 탭 시 외부 브라우저
│   ├── [sentiment]  SentimentPanel — 어조 분포 도넛 + 인플루언서 멘션 5건 + KeywordCloud
│   └── [polymarket] PolymarketPanel — 12h 추이 차트 + 거래량(USD) + 외부 링크 + 면책 카피
└── (없음) — 시트는 sheet-cta 없이 본문만
```

#### 인터랙션 테이블

| 요소 | 동작 | 네비게이션 | 비고 |
|------|------|-----------|------|
| 닫기 ←/✕ | 탭 | pop → S-01 | 스크롤 위치 보존, focus return |
| swipe down (handle) | 제스처 | pop → S-01 | reduced-motion 시 즉시 닫힘 |
| 출처 링크 | 탭 | 외부 브라우저 또는 인앱 웹뷰 (앱 내 정책) | `Link/external` aria-label "외부 사이트로 이동" |
| 코멘트 작성 (community) | 탭 | CommentInputDialog | 140자 제한 |
| 코멘트 좋아요 | 탭 | optimistic update (즉시 +1) | 실패 시 롤백 + 토스트 |
| 코멘트 신고 | 탭 | 신고 사유 시트 → 제출 | optimistic update 후 신고 누적 3건이면 즉시 가림 |
| 차트 (datalab/polymarket) | 탭/swipe | 시간대 토글 또는 줌 (디자인 미정) | [FE 추가] 분석 차트 lib 의존 |

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `InsightSheet` 셸 | 진입 직후 시트 본문 스켈레톤 | 채널 패널 노출 | (해당 없음) | "다시 시도" 버튼 — **다른 카드 격리, S-01에 영향 X** |
| `DatalabPanel` 차트 4종 | 차트 자리별 스켈레톤 (각각 독립) | 4종 노출 | 데이터 부족 차트는 "N/A" | 차트 단위 retry |
| `CommunityPanel` 코멘트 | 스켈레톤 5행 | Top5 노출 | "아직 코멘트가 없어요. 첫 코멘트를 남겨보세요." | "다시 시도" |
| `CommunityPanel` 코멘트 작성 | submit 시 버튼 spinner | "작성 완료" 토스트 + 리스트에 prepend | — | 인풋 하단 인라인 에러 (140자 초과/URL 차단) |
| `NewsPanel` | 5행 스켈레톤 | 5건 + 톤 칩 | "최근 기사 없음" | 재시도 버튼 |
| `SentimentPanel` | 도넛 + 멘션 영역 스켈레톤 | 분포 + 5멘션 | "데이터 일시 중단" (FR-008 R-02 fallback) | 재시도 |
| `PolymarketPanel` | 차트 스켈레톤 | 차트 + 면책 카피 | "시장 비활성" 카드 | 재시도 |

---

### §2-3. S-03 결과 시트 (적중/미적중)

#### 컴포넌트 트리

```
ResultSheet (.frame__screen, full-screen modal)
├── AppBar
│   ├── IconButton ✕ — 닫기 → 메인 또는 S-01
│   └── AppBarTitle "결과 발표"
├── ResultBody (.result)
│   ├── ResultIcon (.result__icon.--hit|--miss) — ✓ / —
│   ├── ResultTitle (.result__title) — "적중!" 또는 "아쉽게 빗나갔어요"
│   ├── ResultSub (.result__sub) — "BTC +1.81% 마감 · 24시간 예측"
│   ├── ScoreCard #1 (.score-card)
│   │   ├── label "누적 적중률 (최근 90일)"
│   │   ├── value (mono 28px) + delta (▲/▼ %p)
│   │   ├── progress bar (.score-card__progress) — 다음 티어까지
│   │   └── hint — TierBadge + "다음 티어까지 N회 남음" (또는 "현재 골드 유지 · 다음 예측에서 만회해봐요")
│   └── ScoreCard #2 (적중 시) (.score-card)
│       └── 예측가 → 마감가 비교 (좌: 예측 시점, 우: 24시간 후 마감, 색상 up/down)
│   └── LearningHint (미적중 시) (.score-card, success 톤)
│       └── "8개 채널 중 3개가 정답에 가까웠습니다."
├── SheetCta (.sheet-cta)
│   ├── 적중: CTAButton.cta--full.cta--up (매수했었으면 매도 / 매도했었으면 매수) — replace → 거래화면
│   ├── 적중: CTAButton.cta--ghost.cta--full "결과 카드 공유 (P2)" — disabled in P0
│   └── 미적중: CTAButton.cta--ghost.cta--full "내가 놓친 시그널 보기 →" — push S-04
```

#### 인터랙션 테이블

| 요소 | 동작 | 네비게이션 | 비고 |
|------|------|-----------|------|
| ✕ 닫기 | 탭 | pop → 메인 또는 S-01 | 콜드부팅 진입 시: 백스택은 [메인, S-03] 1장만 → 닫으면 메인 |
| 매수/매도 CTA (적중) | 탭 | replace → 거래화면 (BTC/KRW or ETH/KRW deeplink) | Q-07 의존, 딥링크 미합의 시 P0 부분 제한 가능 |
| 결과 카드 공유 (P2) | 탭 | OS 공유 시트 (이미지 캡처) | P0 disabled |
| 내가 놓친 시그널 (미적중) | 탭 | push → S-04 | |

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `ResultSheet` 셸 | 푸시 직후 잠시 스피너 (결과 산정 직전) | 적중/미적중/무효 카드 | 무효: ResultIcon `—`, "동일 가격 마감 — 무효 처리" | 결과 산정 지연 시 "잠시 후 다시 알려드릴게요" + 백오프 polling |
| `ScoreCard` 적중률 | 값 자리 스켈레톤 | 값 + delta + progress | — | 일부 실패 시 progress 영역만 스켈레톤 유지 |
| `ScoreCard` 가격 비교 | 가격 자리 스켈레톤 | 두 가격 + → 화살표 | — | "—" |
| CTA 거래화면 | 탭 후 0.3s 내 화면 전환 | replace 완료 | — | 딥링크 실패 시 토스트 "거래화면을 열 수 없어요" + 매수/매도 안내 화면 fallback |

---

### §2-4. S-04 채널 정답 비교

#### 컴포넌트 트리

```
CompareScreen (/predict/result/:id/compare)
├── AppBar
│   ├── IconButton ← — pop → S-03
│   └── AppBarTitle "내가 놓친 시그널"
├── CompareIntro — "BTC 마감가 −0.52% · 정답은 ↓ 하락이었습니다."
├── CompareGrid (.compare)
│   ├── CompareHead (.compare__head) — 타이틀 "채널별 예측" + 범례 (정답 dot / 오답 dot)
│   └── CompareCards (.compare__cards, 2열 mobile / 4열 desktop)
│       └── CmpCard[i] (.cmp-card.--right|--wrong) × 6 (P0 6채널, P1 출시 후 8)
│           ├── .cmp-card__name (채널명)
│           ├── .cmp-card__pred.--up|--down (예측 ↑/↓ + %)
│           └── .cmp-card__verdict ("✓ 정답" / "오답")
├── CompareFooter (.compare__footer) — 정답에 가까웠던 채널 강조 + "다음 예측 전 우선 참고"
└── SheetCta (.sheet-cta)
    ├── CTAButton.cta--up "↑ BTC 매수" — replace → 거래화면(매수)
    └── CTAButton.cta--down "↓ BTC 매도" — replace → 거래화면(매도)
```

#### 인터랙션 테이블

| 요소 | 동작 | 네비게이션 | 비고 |
|------|------|-----------|------|
| ← | 탭 | pop → S-03 | |
| CmpCard | 탭 | (없음) — 시각 정보만 | [FE 추가] 추후 채널 상세 진입 검토 (P2) |
| 매수 CTA | 탭 | replace → 거래화면(매수) | |
| 매도 CTA | 탭 | replace → 거래화면(매도) | |

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `CompareGrid` | 카드 6장 스켈레톤 | 정답/오답 카드 노출 | (해당 없음 — 결과 결산이 끝났으므로 채널 데이터는 보존) | 카드별 "데이터 일시 중단" 비활성, 나머지 정상 |

---

### §2-5. S-05 온보딩 시트 (최초 1회)

#### 컴포넌트 트리

```
OnboardingSheet (modal, 3 pages swipe)
├── Page 1 — "BTC와 ETH의 24시간 후 가격이 오를지 내릴지 찍어보세요. 베팅 없음, 1일 1회 무료."
├── Page 2 — "8개 시그널 카드를 참고하세요." (카드 그리드 일러스트)
├── Page 3 — "맞출수록 티어가 올라갑니다." (브론즈 → 다이아몬드 시각화)
├── PageIndicator (3 dots)
└── SheetCta
    ├── "건너뛰기" (Page 1·2) → replace → S-01 + flag set
    └── "시작하기" (Page 3) → replace → S-01 + 첫 예측 가이드 활성화
```

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `OnboardingSheet` | 진입 시 0.2s 페이드인 | 3 페이지 | — | (오프라인 시) 정적 콘텐츠라 정상 표시 |

> **상태 변경 위치**: 온보딩 완료 플래그(어디 저장할지는 FE 자율). 두 번째 진입 시 본 시트는 표시되지 않음.

---

### §2-6. S-06 미성년자/KYC 차단 시트

#### 컴포넌트 트리

```
BlockedSheet (modal, dismiss 불가, focus trap)
├── BlockIcon (대형 아이콘 또는 일러스트)
├── BlockTitle "예측 게임은 19세 이상 실명 인증 사용자만 이용할 수 있어요."
├── BlockBody — KYC 안내 문구
└── SheetCta
    ├── CTAButton.cta--full "실명 인증하러 가기" — replace → KYC 화면
    └── CTAButton.cta--ghost.cta--full "다음에" — pop → 메인 (시트만 닫힘, 게임 진입 차단 유지)
```

> 닫기(✕) 버튼 없음. 백키/ESC 입력은 "다음에"로 매핑.

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `BlockedSheet` | KYC 상태 조회 중: 셸만 표시 | KYC 미통과 사용자에게 노출 | — | 조회 실패 시 안전 fallback (차단 유지) |

---

### §2-7. S-07 리더보드

#### 컴포넌트 트리

```
LeaderboardScreen (/predict/leaderboard?period=)
├── AppBar — ← / "리더보드"
├── PeriodTabs (.tabs, segmented) — "90일" / "시즌"
├── LeaderList
│   └── LeaderRow (.list-item.leaderboard) × N
│       ├── Rank (mono)
│       ├── Nickname
│       ├── TierBadge
│       └── HitRate (mono, %)
├── StickyMyRow (.sticky.--bottom) — 내 위치 (탭 시 내 위치로 스크롤)
└── ProfileMiniCard (모달, 행 탭 시 표시) — 닉네임+티어+90일 적중률 (실명/지갑 노출 X)
```

#### 인터랙션 테이블 (PRD §8-2-A)

| 요소 | 동작 | 네비게이션 | 비고 |
|------|------|-----------|------|
| ← | 탭 | pop | |
| PeriodTabs | 탭 | URL ?period= 갱신, 리스트 재요청 | |
| LeaderRow | 탭 | ProfileMiniCard 모달 | 실명/지갑 노출 절대 금지 |
| StickyMyRow | 탭 | 리스트 스크롤 → 내 위치로 anchor | |

#### UI 상태

| 컴포넌트 | Loading | Success | Empty | Error |
|---------|---------|---------|-------|-------|
| `LeaderList` | 스켈레톤 10행 | 리스트 노출 | "예측 사용자 부족" 메시지 | 재시도 버튼 |
| `StickyMyRow` | 자리 스켈레톤 | 내 순위 표시 | 신규: "예측 1회 후 순위가 표시됩니다" | 무표시 |
| `ProfileMiniCard` | 모달 내 스켈레톤 | 프로필 표시 | — | "프로필을 불러오지 못했어요" |

---

## §3. API 연동 포인트 (제안)

> 엔드포인트는 기획 맥락에서 추론한 **제안**입니다. 실제 경로/메서드/필드는 BE 합의 시 확정. 라이트락·idempotency·캐시 TTL 같은 BE 정책은 be-spec에서 정의.

| # | 화면 | 트리거 | 메서드 | 엔드포인트 (제안) | 요청 필드 | 응답 필드 (제안) | 실시간? | 캐시 정책 (제안) | optimistic? |
|---|------|--------|--------|------------------|----------|-----------------|---------|-----------------|-------------|
| 1 | S-01 | 진입 / 코인 토글 | GET | `/predict/me` | `coin` | `{predictId, coin, dir, predictedAt, deadline, locked}` | — | TTL 30s, mount 시 갱신 | — |
| 2 | S-01 | 진입 / 코인 토글 | GET | `/market/ticker?coin=` | `coin` | `{price, delta24h, sparkline}` | **WebSocket / SSE 후보** | TTL 5s, stream subscribe | — |
| 3 | S-01 | 진입 | GET | `/insights/cards?coin=` | `coin` | `[{channel, dir, strength, meta, updatedAt}]` × 8 | 폴링 60s | TTL 60s, channel별 독립 | — |
| 4 | S-01 | 진입 | GET | `/me/tier` | — | `{tier, hitRate90d, totalPredicts, nextTierIn}` | — | TTL 5min | — |
| 5 | S-01 | ↑/↓ 확인 | POST | `/predict` | `{coin, dir, idempotencyKey}` | `{predictId, deadline, snapshotPrice}` | — | no-cache | **NO** (서버 확정 후 잠금) |
| 6 | S-02 | datalab 진입 | GET | `/insights/datalab?coin=` | `coin` | `{kimchi, volume24h, high52w, low52w, ma20, ma60}` | — | TTL 60s | — |
| 7 | S-02 | community 진입 | GET | `/insights/community?coin=` | `coin` | `{voteUp, voteDown, totalVoters, topComments[5]}` | 코멘트 prepend stream | TTL 30s | — |
| 8 | S-02 | community 코멘트 | POST | `/community/comments` | `{coin, text(1~140), idempotencyKey}` | `{commentId, createdAt}` | — | no-cache | **YES** — 즉시 prepend, 실패 시 롤백 |
| 9 | S-02 | community 좋아요 | POST | `/community/comments/:id/like` | — | `{liked, count}` | — | no-cache | **YES** — UI 즉시 +1, 실패 시 롤백 |
| 10 | S-02 | community 신고 | POST | `/community/comments/:id/report` | `{reason(라디오), text(<=200)}` | `{reported}` | — | no-cache | **YES** — UI에서 즉시 가림(본인 시점), 누적 3건 시 글로벌 가림은 BE |
| 11 | S-02 | topPicks 진입 | GET | `/insights/top-picks?coin=` | `coin` | `{distUp, distDown, n, top10[{nickname, tier, hitRate90d}]}` | — | TTL 60s | — |
| 12 | S-02 | news 진입 | GET | `/insights/news?coin=` | `coin` | `[{title, source, publishedAt, tone, url}]` × 5 | — | TTL 5min | — |
| 13 | S-02 | sentiment 진입 | GET | `/insights/sentiment?coin=` | `coin` | `{toneDist, mentions[5], keywords[10], totalMentions}` | — | TTL 5min (R-02 비용) | — |
| 14 | S-02 | polymarket 진입 | GET | `/insights/polymarket?coin=` | `coin` | `{probUp, history12h[], volumeUsd, externalUrl}` | — | TTL 60s | — |
| 15 | S-03 | 푸시/콜드부팅 | GET | `/predict/result/:id` | `predictId` | `{hit, predictedPrice, closingPrice, deltaPct, hitRateBefore, hitRateAfter, tierBefore, tierAfter, nextTierIn, invalid}` | — | one-shot, no-cache | — |
| 16 | S-04 | 진입 | GET | `/predict/result/:id/channels` | `predictId` | `[{channel, dir, strength, correct}]` | — | TTL 5min | — |
| 17 | S-07 | 진입 / period 토글 | GET | `/leaderboard?period=` | `period` | `[{rank, nickname, tier, hitRate}]` | — | TTL 5min | — |
| 18 | S-07 | 행 탭 | GET | `/users/:nickname/profile-mini` | `nickname` | `{nickname, tier, hitRate90d, totalPredicts}` | — | TTL 5min | — |
| 19 | S-06 | 진입 시 KYC 검사 | GET | `/me/eligibility` | — | `{eligible, reason: "underage" \| "kyc_required" \| "ok"}` | — | TTL 1min | — |

> **BE 합의 필요 사항** (be-spec / api-design 스킬로 이관):
> - 1번/15번: `predictId` 식별자 형식, idempotencyKey 정책
> - 3번: 카드별 격리 응답 포맷 (한 채널 실패 시 partial 200 vs 207 vs 채널별 status)
> - 8번: 1~140자 + URL 차단 서버 검증 (PRD 8-7)
> - 10번: 신고 누적 3건 자동 가림은 서버 책임

---

## §4. 실시간 데이터

WebSocket / SSE / 폴링 후보. 방식은 BE와 합의(제안).

| 데이터 | 갱신 주기 | 방식 (제안) | 구독 조건 | 해제 조건 | UI 반영 |
|--------|----------|-----------|----------|----------|---------|
| 현재가 + 변동률 (BTC/ETH) | ~1s | WebSocket subscribe `ticker:{coin}` | S-01 진입 | S-01 이탈 / 백그라운드 / 코인 토글 변경(switch) | `PriceBlock` 가격·델타 갱신, 잠금 상태에서도 계속 |
| 카드 그리드 stale 갱신 | 60s | 폴링 (`/insights/cards`) | S-01 진입 | S-01 이탈 / 백그라운드 | 카드별 `updatedAt` 비교, 변경된 카드만 재렌더 (5분 초과 시 `card__stale--old`) |
| 결과 결산 신호 | 마감 시각 ±5min | 푸시 (FCM/APNs) — 주채널, SSE — 백업 | 서버 측 마감 트리거 | one-shot | S-03 자동 push (앱 활성 시 인앱 카드, 미활성 시 푸시 → 콜드부팅 시 백스택 [메인, S-03]) |
| 코멘트 스트림 (선택) | 실시간 | WebSocket `community:{coin}` | S-02 community 진입 | S-02 이탈 | 신규 코멘트 prepend (애니메이션은 prefers-reduced-motion 시 단순 fade) |
| 티어 변동 이벤트 | 즉시 | 푸시 (승급만, 강등 푸시 X) + 인앱 이벤트 | 결산 직후 | one-shot | TierBadge 펄스 600ms (reduce-motion 시 비활성), 인앱 토스트 |

---

## §5. 폼 & 유효성 검사

PRD §8-7 + 보완. 클라이언트 검증과 서버 검증을 구분한다.

| 필드 | 위치 | 필수 | 클라이언트 검증 | 서버 검증 | 에러 메시지 |
|------|------|------|---------------|----------|-----------|
| 코멘트 본문 | S-02 community CommentInput | ✅ | 1~140자, 입력 중 카운터(`120/140`), 0자 시 제출 버튼 disabled, URL 자동 차단 정규식(클라 1차) | URL/스팸 토큰 차단 (서버 최종 판단) | "1~140자로 입력해주세요" / "링크는 작성할 수 없어요" |
| 신고 사유 (라디오) | S-02 신고 시트 | ✅ | 5개 중 1개 선택 필수, 미선택 시 라디오 그룹에 빨간 외곽선 + aria-invalid="true" | — | "신고 사유를 선택해주세요" |
| 신고 자유서술 | S-02 신고 시트 | ❌ | ≤200자, 카운터 표시 | URL/스팸 토큰 검사 | "최대 200자까지 입력 가능합니다" |
| 예측 등록 | S-01 ConfirmDialog | ✅ | 동일 코인 24h 내 재등록 시 클라가 사전 차단 + 토스트 (서버 응답 전), idempotencyKey 클라 생성 | 24h 룰, idempotency, KYC, 19세, 라이트락 | "오늘은 이미 BTC 예측을 했어요. 내일 다시 만나요." / "잠시 후 다시 시도해주세요 (등록 실패)" |

> URL 차단 정규식은 클라 1차(false positive 허용), 서버가 최종 판정. 클라이언트 차단을 우회하더라도 서버에서 재검증.

---

## §6. 네비게이션 흐름 + 스택 관리

PRD §8-8 + 푸시·콜드부팅 케이스 보강.

```
push     = 새 화면 쌓기 (스택 +1)
pop      = 이전 화면으로 돌아가기 (스택 -1)
replace  = 현재 화면 교체 (스택 동일, top 변경)
modal    = 풀스크린 모달 (focus trap, dismiss 정책 별도)
```

### 표준 흐름

| from | event | to | 방식 |
|------|-------|-----|------|
| 메인 | "예측" 탭 | S-01 | push |
| S-01 | 카드 탭 (P0) | S-02 | push (시트) |
| S-01 | ↑↓ 탭 | ConfirmDialog | modal (S-01 위) |
| ConfirmDialog | 확인 + 등록 성공 | S-01 (잠금 상태) | dialog dismiss + S-01 데이터 갱신 |
| S-01 | TierBadge 탭 | S-07 | push |
| S-02 | 닫기 / swipe down | S-01 | pop, focus return to 진입 카드 |
| 푸시 (앱 활성) | 마감 결산 도착 | S-03 | 인앱 자동 push (현재 화면 위) |
| 푸시 (앱 비활성) | 마감 결산 도착 + 푸시 탭 | S-03 | **콜드부팅 → 메인 1장 + S-03 1장** (백스택 = 메인) |
| S-03 | ✕ 닫기 | 메인 또는 S-01 | pop (백스택에 따라 자동) |
| S-03 (적중) | 매수/매도 CTA | 거래화면 | **replace** (S-03 닫고 거래화면) |
| S-03 (미적중) | "내가 놓친 시그널" | S-04 | push |
| S-04 | 매수/매도 CTA | 거래화면 | **replace** |
| S-04 | ← | S-03 | pop |
| 신규 가입자 | 첫 진입 | S-05 | replace 메인 → S-05, 완료 시 S-05 → S-01 replace |
| KYC 미통과 | 진입 시도 | S-06 | modal (dismiss 불가, 인증 완료 시에만 닫힘) |

### 백스택 엣지 케이스

1. **푸시 → 콜드부팅 → S-03**:
   백스택은 [메인, S-03] 2장만 구성. ✕ 누르면 메인. **S-01은 끼어들지 않음** (혼란 방지). 단, S-03에서 "S-01 가서 ETH 예측하기" 같은 보조 CTA는 P0에는 없음.

2. **이미 S-02 시트가 떠있는데 푸시 도착**:
   결과 시트는 시트 위에 풀스크린 modal로 push. 닫으면 S-02 → S-01 순서로 복귀.

3. **S-04에서 매수 후 거래화면 → 뒤로 가기**:
   거래화면이 외부 화면이므로 자체 정책 따름. 우리 화면으로 돌아오는 deeplink는 명세 외(외부 화면 책임).

4. **딥링크 미합의 (Q-07) 임시 fallback**:
   거래화면 진입 실패 시 토스트 + S-03/S-04 유지 (replace 취소).

---

## §7. 디자인 토큰 참조

DESIGN.md에서 본 기능에 필요한 토큰만 발췌. 디자인 갤러리 BEM 클래스명을 그대로 사용한다.

### 색상

| 토큰 | OKLCH | 용도 |
|------|-------|------|
| `--c-bg` | 0.13 0.005 270 | 페이지 배경 (다크) |
| `--c-surface` | 0.17 0.008 270 | 카드, 시트 배경 |
| `--c-surface-2/3` | 0.21 / 0.26 | 카드 위 카드, hover |
| `--c-divider` / `--c-border` | 0.24 / 0.30 | 카드 구분선, dashed border |
| `--c-text` / `--c-text-muted` / `--c-text-subtle` | 0.96 / 0.70 / 0.55 | 본문 / 라벨 / 메타 |
| **`--c-up`** | 0.66 0.215 27 | **상승 빨강 (한국식)** ↑ 화살표·% |
| **`--c-down`** | 0.62 0.180 250 | **하락 파랑 (한국식)** ↓ 화살표·% |
| `--c-up-bg` / `--c-down-bg` | 0.30 0.080 ... | 적중 아이콘 배경, 하이라이트 |
| `--c-bronze/silver/gold/platinum/diamond` | … | TierBadge 단색 outline + dot |
| `--c-success/warn/info` | … | stale dot 색, 학습 카드, 정답 강조 |

### 타이포

- `--font-sans`: Spoqa Han Sans Neo → 라벨·본문·타이틀
- `--font-mono`: JetBrains Mono → 가격, %, 시간, 적중률 등 모든 숫자 (`font-feature-settings: "tnum" 1, "zero" 1`로 tabular-nums)
- 토큰: `--t-display` (결과 헤드라인), `--t-mono-lg` (가격), `--t-mono-md` (카드 시그널 %), `--t-mono-sm` (메타)

### 라운드

- 카드 `--r-md` (10px), 시트 `--r-lg` (16px), 칩 `--r-pill`

### 모션

- 기본 `cubic-bezier(0.2, 0.8, 0.2, 1)` 200ms
- 티어 승급 펄스 600ms (`prefers-reduced-motion: reduce` 시 비활성)
- 카드 hover transform 금지

### BEM 클래스 인벤토리 (디자인 갤러리에서 직접 사용)

| 컴포넌트 | 클래스 |
|---------|--------|
| TierBadge | `.tier-chip`, `.tier-chip--{bronze\|silver\|gold\|platinum\|diamond}`, `.tier-chip__dot` |
| CoinToggle | `.coin-toggle`, `.coin-toggle__btn`, `.coin-toggle__btn--active`, `.coin-toggle__symbol` |
| PriceBlock | `.price-block`, `.price-block__row`, `.price-block__price`, `.price-block__delta`, `.price-block__delta--up\|--down`, `.price-block__deadline` |
| Sparkline | `.sparkline` (svg path 색은 up/down 컨텍스트 결정) |
| CTA | `.cta`, `.cta--up`, `.cta--down`, `.cta--ghost`, `.cta--full`, `.cta__arrow` |
| Section | `.sect`, `.sect__head`, `.sect__title`, `.sect__count` |
| CardInsight | `.cards`, `.card`, `.card--locked`, `.card__name`, `.card__signal`, `.card__dir`, `.card__dir--up\|--down`, `.card__pct`, `.card__meta`, `.card__locked-tag`, `.card__stale`, `.card__stale-dot`, `.card__stale--old` |
| ResultSheet | `.result`, `.result__icon`, `.result__icon--hit\|--miss`, `.result__title`, `.result__sub`, `.result__sub-strong--up\|--down` |
| ScoreCard | `.score-card`, `.score-card__label`, `.score-card__value`, `.score-card__delta`, `.score-card__progress`, `.score-card__progress-fill`, `.score-card__hint` |
| CompareGrid | `.compare`, `.compare__head`, `.compare__title`, `.compare__legend`, `.compare__legend-dot`, `.compare__cards`, `.cmp-card`, `.cmp-card--right\|--wrong`, `.cmp-card__name`, `.cmp-card__pred`, `.cmp-card__pred--up\|--down`, `.cmp-card__verdict`, `.compare__footer` |
| SheetCta | `.sheet-cta` |
| AppBar | `.appbar`, `.appbar__back`, `.appbar__title`, `.appbar__right` |

`.t-mono` utility는 등폭 숫자용 (모든 가격·% 영역에 적용 강제).

---

## §8. Progressive Rendering — 8채널 카드 Critical Path

PRD 9-1: S-01 first paint ≤ 1.5s (P95). 카드별 격리 정책에 따라 **카드 단위 우선순위**를 둔다.

### 우선순위 (ATF / first paint 기준)

| 우선순위 | 채널 / 영역 | 이유 | 렌더 정책 |
|---------|----------|------|---------|
| **P0-A (Critical)** | AppBar, CoinToggle, PriceBlock, CTA ↑/↓ | 핵심 행동 (예측 등록)을 막지 않음 | SSR 또는 초기 캐시(스냅샷)에서 즉시 렌더, blocking |
| **P0-B (Above the fold)** | CardInsight × 4 (datalab, community, topPicks, news) | 화면 절반(모바일 ATF) 이내 노출 | 스켈레톤 → 카드별 도착 즉시 swap, 실패 시 placeholder |
| **P1 (Below the fold)** | CardInsight × 2 (sentiment, polymarket) | 스크롤 후 노출 | lazy fetch 가능, 스크롤 임박 시 prefetch |
| **P2 (Locked)** | CardInsight × 2 (coinsite, onchain) — `.card--locked` | P1 출시 전까지 잠금 표시 | 정적 잠금 카드, fetch 없음 |
| **Defer** | Sparkline 차트 | 보조 정보 | idle 시 lazy hydrate |

### 카드 격리 (한 카드 실패가 다른 카드를 막지 않음)

- 카드별 비동기 fetch + per-card error boundary.
- `Promise.allSettled` 패턴(또는 동등): 한 채널 reject가 전체 reject 되지 않음.
- 카드별 재시도 버튼(인풋 영역). 전체 새로고침 X.

### 데이터 stale 갱신

- 60s 폴링으로 카드별 `updatedAt` 비교, **변경된 카드만 재렌더** (전체 리렌더 회피).
- 5분 초과 카드는 `card__stale--old` 적용 (warn dot).

---

## §9. 접근성 (a11y)

PRD §8-9 + 디자인 갤러리 9. Accessibility + 동적 라벨 패턴.

### 색상·아이콘

- ↑/↓는 **색상 단독 금지**. `.card__dir`(화살표 글리프) + `.card__pct`(텍스트 %) + 색상 3중 표기 (적록 색맹 대응).
- focus-visible: 2px outline `--c-gold` 토큰, offset 2px (디자인 갤러리 §9).

### 터치 영역

- 카드, 토글, CTA 모두 ≥ 44×44 (Apple HIG). 카드 `min-height: 92px`.

### 동적 VoiceOver / TalkBack 라벨 패턴

| 컴포넌트 | 라벨 패턴 (예시) |
|---------|---------------|
| `CardInsight` (정상) | `"{채널명}, {방향 텍스트} {강도}, {보조 메타}, {갱신 N분 전}, 자세히 보기"` 예: "데이터랩, 김치 프리미엄 2.3% 상승, 2분 전 갱신, 자세히 보기" |
| `CardInsight` (loading) | `"{채널명}, 불러오는 중"` |
| `CardInsight` (error) | `"{채널명}, 데이터를 불러오지 못했어요. 다시 시도하려면 두 번 탭하세요"` |
| `CardInsight` (locked P1) | `"{채널명}, 곧 출시 예정"`  + `aria-disabled="true"` |
| `CardInsight` (stale--old) | `"{... 보통 라벨 ...}, 갱신된 지 8분 지났어요"` |
| `CTA ↑/↓` (활성) | `"오른다, BTC 상승 예측 등록하기. 마감 시각 내일 9시 24분"` |
| `CTA ↑/↓` (잠금) | `"이미 BTC 예측을 등록했어요. 마감까지 N시간 남음"` (`aria-disabled="true"`) |
| `TierBadge` | `"현재 티어 골드, 다음 티어까지 7회 남음, 리더보드 보기"` |
| `CoinToggleBtn` | `role="tab"` + `aria-selected` + `"BTC 비트코인 선택됨"` |
| `ResultIcon hit` | `role="img"` + `"적중! BTC 1.81% 상승 마감"` |
| `ResultIcon miss` | `role="img"` + `"아쉽게 빗나갔어요. BTC 0.52% 하락 마감"` |
| `ScoreCard progress` | `role="progressbar"` + `aria-valuenow`/`aria-valuemax` + 라벨 "다음 티어까지 7회 남음" |
| `CmpCard right` | `"{채널명}, {방향} 예측, 정답"` |
| `CmpCard wrong` | `"{채널명}, {방향} 예측, 오답"` |

### Focus Trap

- S-02 InsightSheet: 시트 내부에 트랩, 닫기/swipe down 시 진입 카드로 focus return.
- S-03 ResultSheet: 트랩 + 첫 focus는 ResultTitle.
- S-05 OnboardingSheet: 트랩 + 페이지별 첫 액션 버튼 focus.
- S-06 BlockedSheet: **dismiss 불가 trap** — Tab/Shift+Tab 순환만, ESC 매핑은 "다음에" 버튼.
- ConfirmDialog: 트랩 + 첫 focus는 "확인" 버튼.

### prefers-reduced-motion

- 디자인 갤러리에 이미 정의됨 (`* { animation/transition-duration: 0.01ms }`).
- 적용 대상 명시:
  - 티어 승급 펄스 (600ms) → 0ms
  - 시트 swipe-down 애니 → 즉시 닫힘
  - 코멘트 prepend fade-in → 즉시 표시
  - sparkline path animate (있을 경우) → 즉시 그리기
  - 토스트 slide-in → fade only

### 스크린리더 라이브 영역

- 토스트 (`role="status"`, `aria-live="polite"`) — 등록 완료, 좋아요, 신고 등
- 결과 시트 도착 시 (콜드부팅 X 인앱) `aria-live="assertive"` 1회 발화

---

## §10. 동시 입력 / 엣지 케이스

### BTC·ETH 동시 등록

- BTC와 ETH는 코인별 1일 1회 카운터 독립 (PRD FR-001).
- 사용자가 BTC ↑ 등록 직후 빠르게 코인 토글하여 ETH ↓ 시도하는 경우:
  - 클라는 두 코인 별도 idempotencyKey 생성, 별도 POST.
  - UI는 BTC 잠금 토스트가 떠있더라도 ETH CTA는 활성 유지.
  - 두 등록이 모두 성공하면 코인 토글로 양쪽 잠금 상태 확인 가능.

### 더블 탭 / 빠른 연속 탭

- ↑ 또는 ↓ 버튼: tap 직후 disabled + spinner. 같은 idempotencyKey로 첫 요청만 유효, 중복 요청은 서버가 idempotent 응답 반환.
- 카드 탭: 시트가 push 중이면 추가 탭 무시 (in-flight 가드).
- 좋아요/신고: optimistic UI는 한 번만 상태 변환, 더블 탭 시 두 번째는 무시.

### 권한 거부 (푸시)

- 푸시 권한 OFF 사용자: 결과 알림은 **다음 앱 진입 시 인앱 결과 카드** 자동 노출 (PRD FR-010).
- FR-014 일일 09시 알림도 권한 거부면 인앱 배너 fallback.
- 최초 진입 시 권한 요청 다이얼로그는 **첫 예측 등록 직후**(value 발생 후) 띄움 (디자인·UX 결정 위임).

### 오프라인 / 네트워크 단절

- S-01 진입 시 캐시 hit이면 카드 노출(stale 표시), 캐시 miss + 오프라인 → "인터넷 연결을 확인해주세요" + 재시도 버튼.
- 예측 등록 in-flight 중 네트워크 끊김 → 토스트 "등록 실패, 다시 시도해주세요" + 같은 idempotencyKey로 재시도. 도달 못한 요청은 잠금 X.
- 결과 시트 fetch 실패 → "잠시 후 다시 알려드릴게요" + 백오프 polling.

### 한 채널 데이터 fetch 실패 (PRD 시나리오 6)

- 해당 카드만 "잠시 후 다시 시도" placeholder, 다른 7개 카드는 정상 노출.
- 카드별 retry 버튼 (인풋 영역).
- S-04 비교 화면에서도 동일 정책 (실패 채널은 "데이터 일시 중단" 칸).

### 마감 직전 30분 스파이크 (NFR R-05)

- 클라가 백오프 + jitter 적용해 등록 재시도. 큐 초과 시 서버가 429 → "잠시 후 다시 시도해주세요" + 자동 30s 후 재시도.

### 무효 처리 (예측가 = 마감가)

- S-03 ResultSheet에 **무효** 상태 추가 (PRD FR-001):
  - ResultIcon: `—` (.result__icon--miss와 같은 톤이지만 별도 라벨)
  - 타이틀: "동일 가격 마감 — 무효 처리"
  - 적중률·티어 변동 없음 (delta `0%p` 또는 비표시)
  - CTA: "다음 예측으로 가기" (push S-01)

### KYC 미통과 / 19세 미만 진입

- 어떤 진입점에서도 `/me/eligibility` 가드. `eligible: false`면 즉시 S-06 modal (dismiss 불가). S-06 미닫음 상태에서 다른 화면 push 차단.

---

## §11. 상태 변경 위치 (어디서 어떤 상태가 변하는가)

> 메모리 규칙: 라이브러리/글로벌-로컬 분류는 FE팀 자율. 본 명세서는 **변경 지점만** 기록.

| 상태 | 변경 지점 | 의존 화면 |
|------|---------|---------|
| 코인 컨텍스트 (BTC/ETH) | S-01 CoinToggleBtn 탭 | S-01 전체 (PriceBlock, Sparkline, CardGrid) |
| 예측 잠금 상태 (코인별) | POST `/predict` 성공 응답 | S-01 CTA 활성/disabled, ConfirmDialog dismiss |
| 카드별 데이터 + updatedAt | 폴링 응답 / WebSocket 메시지 | S-01 CardInsight 8장 각각 독립 |
| 현재가 + 변동률 | WebSocket ticker | S-01 PriceBlock |
| 코멘트 리스트 | S-02 community POST 성공 (prepend) / 좋아요·신고 응답 | S-02 CommunityPanel |
| 좋아요 카운트 | optimistic 즉시 / 서버 응답으로 확정 | S-02 코멘트 행 |
| 신고 가림 | optimistic 즉시 (본인 시점) / 서버 누적 3건 가림 (글로벌) | S-02 코멘트 행 |
| 티어 (사용자) | 결과 결산 후 업데이트 | S-01 TierBadge, S-03 ScoreCard, S-07 LeaderRow |
| 결과 (적중/미적중/무효) | 마감 시각 결산 후 푸시 / `/predict/result/:id` 응답 | S-03, S-04 |
| 온보딩 완료 플래그 | S-05 "시작하기" / "건너뛰기" | S-05 표시 여부 |
| KYC eligibility | `/me/eligibility` 응답 | S-06 표시 여부, 모든 진입점 가드 |
| 리더보드 period | S-07 PeriodTabs 탭 | S-07 LeaderList |

---

## §12. FE 결정 필요 사항

기획서·디자인에서 도출 불가하여 FE 개발자가 결정해야 할 항목.

| # | 항목 | 맥락 | 선택지 |
|---|------|------|--------|
| F-01 | 카드 격리를 위한 비동기 패턴 | PRD 시나리오 6 + 카드별 독립 fetch | per-card fetch + error boundary / suspense pattern / 일괄 fetch + 부분 응답 |
| F-02 | 폴링 vs WebSocket vs SSE | 카드 60s, ticker 1s — 둘 다 BE 정책 의존 | BE와 합의: ticker는 stream 추천, 카드는 폴링 |
| F-03 | 차트 라이브러리 | datalab 4종, polymarket 12h 추이, sparkline | 경량 SVG / canvas / 기존 업비트 차트 컴포넌트 재사용 |
| F-04 | 코멘트 페이징 | Top5 후 더보기 정책 | 무한 스크롤 / "더 보기" 버튼 / Top10 고정 |
| F-05 | 푸시 deeplink 형식 | PRD §8-8 콜드부팅 | URL 스킴 / Universal Link — 앱 표준 따름 |
| F-06 | 거래화면 딥링크 fallback (Q-07 미합의) | FR-011 핵심 KPI 의존 | 미합의 시 P0에서 CTA disabled / 안내 화면 / 직접 매수 화면 진입 |
| F-07 | 다크 테마 단일 vs 라이트 토글 | DESIGN.md는 다크 전용 | 다크 고정 / 라이트 추후 (P2) |
| F-08 | 잠금 상태에서 카드 그리드 갱신 지속 여부 | PRD 시나리오 1: 잠금 후에도 카드 탐색 | 갱신 지속 (권장) / 정지 |
| F-09 | 폴리마켓 카드 빌드 분기 (R-01) | 법무 부정 시 7채널 모드 | 빌드 타임 환경 변수 토글 / 런타임 feature flag |
| F-10 | i18n 골격 | 1차 한국어, P2 영문 | 토큰 키 한국어 직접 사용 / i18n key 구조 사전 도입 |
| F-11 | 토스트 / 다이얼로그 글로벌 단일 컨테이너 | 등록 / 좋아요 / 신고 등 다수 사용처 | 단일 root container 권장 |
| F-12 | sparkline 데이터 출처 | PriceBlock 옆 24h mini chart, ticker stream 또는 별도 endpoint | BE 합의 |

---

## §13. 자체 리뷰 체크리스트

```
[x] 네비게이션 흐름의 모든 화면(S-01~S-07)이 §1에 있는가? — 7개 모두 포함
[x] 모든 PRD §8-2/8-3/8-4의 클릭 명세가 §2에 반영되었는가? — 화면별 인터랙션 테이블에 매핑
[x] 모든 PRD §8-5의 UI 상태가 §2에 반영되었는가? — 컴포넌트 단위로 세분화
[x] 서버 통신이 필요한 인터랙션이 모두 §3에 있는가? — 19개 엔드포인트 (제안)
[x] 실시간 데이터가 §4에 있는가? — ticker / 카드 폴링 / 푸시 / 코멘트 / 티어 5종
[x] 폼 필드가 모두 §5에 있는가? — 코멘트, 신고 사유, 신고 자유서술, 예측 등록
[x] 기획서에 없는 기능을 임의로 추가하지 않았는가? — [FE 추가] 표기로 명시
[x] 기술 스택을 지정하지 않았는가? — 라이브러리/프레임워크 미지정, F-XX로 위임
[x] "제안" 항목에 (제안) 표기가 되어있는가? — 엔드포인트, 라우트 모두 (제안) 표기
[x] [FE 추가] 항목에 근거가 있는가? — 차트 영역 / 잠금 CTA / 폴리마켓 비활성 / CmpCard 탭 등 모두 PRD 또는 사용성 근거 명시
[x] 메모리 규칙: 상태 관리 라이브러리·보안·SP·런치 플랜 미포함 — 진행 상태 헤더에 명시
```

### 자체 점수

| 영역 | 점수 | 코멘트 |
|------|------|--------|
| 화면 인벤토리 완전성 | 95 | 7개 모두 포함, 라우트 제안 추가 |
| 컴포넌트 분해 + BEM 매핑 | 92 | 디자인 갤러리 클래스 그대로 사용, 8채널 카드 분해 명확 |
| API 연동 포인트 | 90 | 19개 추출, optimistic·캐시 정책 명시 |
| UI 상태 매트릭스 | 90 | 컴포넌트 단위로 4상태 매핑 |
| 진보적 렌더링 | 88 | P0-A/P0-B/P1/P2/Defer 5단계, 카드 격리 |
| 접근성 | 92 | 동적 라벨, focus trap, reduce-motion 모두 명시 |
| 엣지 케이스 | 90 | 동시 등록·더블탭·권한·오프라인·무효 모두 다룸 |
| 푸시 콜드부팅 백스택 | 88 | 4가지 케이스 명시 |
| 메모리 규칙 준수 | 100 | 상태 라이브러리·보안·SP 미포함 |

**종합: 91 / 100 — PASS**

> 미해결: F-06(거래화면 딥링크 미합의 시 P0 fallback)·F-09(폴리마켓 빌드 분기) 두 결정은 PRD Q-07/R-01 의존. PM·법무·거래화면팀 합의 후 FE 보완.

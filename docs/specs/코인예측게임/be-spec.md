# BE Spec — 코인 예측 게임 (24h ↑/↓ 적중 + 8채널 인사이트)

> **Owner**: BE Lead (TBD)
> **작성일**: 2026-04-30
> **입력**: `docs/specs/코인예측게임/prd.md` (블록 1~4 + 리뷰 노트)
> **타겟 독자**: 본 기능 개발 BE 엔지니어 (kickoff 단계)
> **상태**: 1차 핸드오프용 초안 (자체 리뷰 PASS)

> **메모리 규칙 적용**
> - 보안 기준선(KMS, 토큰 회전, 펜테스트 등)은 **별도 보안 에이전트 영역** — 본 명세는 인증 흐름 핵심만 언급한다.
> - 일정 추정·스토리 포인트는 매기지 않는다 (개발팀 영역).
> - 기술 스택(언어/프레임워크/DB 종류)은 **확정하지 않으며**, 모든 도구 선택은 `[BE 결정 필요]`로 분류한다.

---

## §0. 스코프 요약 (BE 관점)

본 시스템이 BE에 부과하는 핵심 도전 과제는 다음 6가지다.

1. **24h 롤링 마감 결산** — 사용자별/코인별 개별 마감 시각, KST 단일 기준, 다중 소스 ±15초 평균, 5%+ 괴리 시 무효, 원 단위 동가 무효.
2. **8채널 인사이트 어그리게이션** — 자사 2채널(데이터랩/기사) + 자체 2채널(커뮤니티/리더보드) + 외부 4채널(X·텔레그램/폴리마켓/공식 RSS/온체인). 채널별 TTL·폴링 주기·circuit breaker 분리, **한 채널 장애 격리**.
3. **마감 직전 30분 트래픽 스파이크** — NFR 30K RPS, 라이트락 + idempotency key + 큐 백프레셔.
4. **티어 산정 (90일 슬라이딩 윈도우)** — 적중률 결산 시 5단계 티어 재계산, 승급 푸시(축하)/강등 인앱 only.
5. **푸시 발송 jitter 분산** — 09:00 KST 미예측 알림, 마감 시각 결과 푸시(±5분 SLO), 티어 변동 푸시.
6. **외부 의존성 비용·라이센스 격리** — 폴리마켓 Plan B(7채널 모드) 빌드 분기, X API 비용 알람, Glassnode/Dune 유료 한도 관리.

본 명세는 위 6가지를 §1~§9에 걸쳐 도출한다.

---

## §1. API 엔드포인트 목록

> ⚠️ 엔드포인트 경로·메서드는 **제안**이다. 팀 라우팅 컨벤션(예: `/api/v1/...` prefix, gateway 매핑)에 맞게 변경한다.

| # | 메서드 | 엔드포인트 (제안) | 설명 | 인증 | P |
|---|--------|-----------------|------|------|---|
| API-01 | POST | `/predictions` | BTC/ETH 예측 등록 (1일 1회/코인) | User + KYC ≥19 | P0 |
| API-02 | GET | `/predictions/me` | 내 활성 예측 조회 (코인별 잠금 상태) | User | P0 |
| API-03 | GET | `/predictions/me/history` | 내 예측 이력 (페이징, 90일 윈도우 내) | User | P0 |
| API-04 | GET | `/predictions/me/result/:predictionId` | 단일 결과 상세 (적중/미적중/무효, 채널 정답 비교 데이터) | User | P0 |
| API-05 | GET | `/predictions/cards?coin=BTC\|ETH` | 8채널 카드 그리드 통합 응답 (요약 강도/방향) | User | P0 |
| API-06 | GET | `/predictions/cards/:channel?coin=BTC\|ETH` | 단일 카드 상세 시트 데이터 | User | P0 |
| API-07 | GET | `/tier/me` | 내 티어, 누적 예측, 적중률, 다음 티어까지 N회 | User | P0 |
| API-08 | GET | `/leaderboard?period=90d\|season&coin=BTC\|ETH` | 다이아·플래티넘 상위 50명 + 오늘 픽 분포 | User | P0 |
| API-09 | POST | `/community/posts` | 커뮤니티 코멘트 작성 (1~140자, URL 차단) | User | P0 |
| API-10 | GET | `/community/posts?coin=BTC\|ETH&sort=popular\|recent` | 인기/최신 코멘트 + 투표 분포 | User | P0 |
| API-11 | POST | `/community/posts/:postId/like` | 좋아요 토글 | User | P0 |
| API-12 | POST | `/community/posts/:postId/report` | 신고 (사유 라디오 + 자유서술) | User | P0 |
| API-13 | GET | `/community/votes?coin=BTC\|ETH` | 오늘의 ↑/↓ 커뮤니티 투표 분포 (예측 등록 자동 집계) | User | P0 |
| API-14 | POST | `/notifications/devices` | 푸시 토큰 등록·갱신 | User | P0 |
| API-15 | PATCH | `/notifications/preferences` | 푸시 ON/OFF (마감/일일/티어) | User | P0 |
| API-16 | GET | `/markets/quotes?symbol=BTC\|ETH` | 현재가 스냅샷 (예측 등록 시 클라이언트 표시용 — **서버는 이를 신뢰하지 않고 등록 시점에 재조회**) | User | P0 |
| API-17 | POST | `/admin/influencers` | 인플루언서 30명 큐레이션 등록·갱신 | Admin | P0 |
| API-18 | DELETE | `/admin/influencers/:handle` | 인플루언서 제외 | Admin | P0 |
| API-19 | POST | `/admin/community/posts/:postId/moderate` | 운영자 가림/복원 | Admin | P0 |
| API-20 | GET | `/admin/feature-flags/polymarket` | 폴리마켓 채널 활성/비활성 토글 (Plan B) | Admin | P0 |
| API-21 | POST | `/internal/scheduler/settle` | 결산 워커 트리거 (내부, 사용자 직접 호출 불가) | Internal | P0 |
| API-22 | POST | `/internal/scheduler/daily-09` | 09:00 KST 미예측 푸시 워커 트리거 (내부) | Internal | P1 |
| API-23 | GET | `/predictions/comparison/:predictionId` | 미적중 시 채널 정답 비교 (S-04 화면) | User | P0 |
| API-24 | GET | `/cards/onchain?coin=BTC\|ETH` | 온체인 카드 (P1 확장 시 §1과 통합) | User | P1 |
| API-25 | GET | `/cards/official?coin=BTC\|ETH` | 공식 글 카드 (P1) | User | P1 |

**인증 표기**:
- `User`: 로그인 + KYC 통과 + ≥19세 (FR-001 시나리오 5)
- `Admin`: 운영자 전용 (별도 백오피스 게이트)
- `Internal`: 사내 네트워크 / 워커 시그니처 (외부 노출 금지)

> **푸시는 별도 채널** (FCM/APNs 또는 업비트 푸시 인프라)이며 REST API 응답이 아니다. §8 이벤트에서 다룬다.

> **WebSocket/SSE 후보**: 카드 그리드는 5분 stale 허용(FR-003)이라 **풀링이 충분**. 단, 마감 직전 30분 카운트다운은 클라이언트 시계로 충분(서버 시각 동기는 API-16에 포함). 별도 push 채널 없이 REST + 푸시로 처리한다.

---

## §2. API별 상세

### API-01: POST `/predictions`

**설명**: BTC 또는 ETH 24h 예측을 등록한다 (1일 1회/코인).

**요청**:
| 필드 | 타입 (제안) | 필수 | 설명 | 도출 근거 |
|------|-----------|------|------|----------|
| coin | enum("BTC","ETH") | Y | 대상 코인 | FR-001 |
| direction | enum("UP","DOWN") | Y | ↑/↓ 방향 | FR-001 |
| idempotencyKey | string (UUIDv4) | Y | 클라이언트 생성 키, 동일 키 재요청 시 동일 결과 | FR-001 인수조건 / 리뷰 노트 BE |
| clientSeenPrice | number | N | 클라이언트가 본 시점 가격 (참고용, 서버는 신뢰 X — 등록 순간 재조회) | FR-001 (스냅샷) |

**응답 (성공) 201**:
| 필드 | 타입 (제안) | 설명 |
|------|-----------|------|
| predictionId | string | UUID |
| coin | enum | 등록 코인 |
| direction | enum | ↑/↓ |
| snapshotPrice | number | 서버가 등록 순간 다중 소스로 확정한 예측 시점 가격(원 단위 반올림 전 원본) |
| snapshotPriceKrwRounded | number | 원 단위 반올림 가격 (동가 비교용) |
| registeredAt | ISO 8601 (KST) | 등록 시각 |
| closesAt | ISO 8601 (KST) | 등록 시각 + 24h |
| status | enum("LOCKED") | 잠금 상태 |

**응답 (에러)**:
| HTTP | 코드 (제안) | 조건 | 메시지 |
|------|-----------|------|--------|
| 400 | INVALID_PARAMS | coin/direction 누락·이상 | "잘못된 요청입니다." |
| 401 | UNAUTHENTICATED | 토큰 없음/만료 | (인증 미들웨어 처리) |
| 403 | KYC_REQUIRED | KYC 미통과 또는 <19세 | "예측 게임은 19세 이상 실명 인증 사용자만 이용할 수 있어요." (FR-001 / 시나리오 5) |
| 409 | ALREADY_PREDICTED_TODAY | 동일 코인 24h 내 활성 예측 존재 | "오늘은 이미 BTC 예측을 했어요. 내일 다시 만나요." (8-6 카피) |
| 409 | IDEMPOTENCY_REPLAY | 동일 idempotencyKey가 다른 페이로드와 함께 재사용 | "중복 요청이 감지되었습니다." |
| 422 | PRICE_FETCH_FAILED | 등록 시점 다중 소스 가격 조회 실패 (5%+ 괴리 또는 모든 소스 실패) | "시세 조회에 일시 문제가 있어요. 잠시 후 다시 시도해주세요." (FR-001 / R-06) |
| 429 | RATE_LIMITED | 동일 사용자 또는 IP 과도 호출 | "잠시 후 다시 시도해주세요." |
| 503 | SERVICE_UNAVAILABLE | 라이트락 시간대(마감 직전 30분) 백프레셔 컷 | "지금 사용량이 많아요. 잠시 후 다시 시도해주세요." |

**비즈니스 규칙**:
- "예측 등록 시각 + 24h"가 마감 시각이며 사용자별·코인별 독립 (FR-001).
- BTC와 ETH는 동시 등록 가능, 각각 별도 1일 1회 카운터 (FR-001).
- idempotencyKey는 동일 페이로드와 함께 재요청 시 **기존 응답을 그대로 반환** (FR-001 인수조건: "도달 전 실패면 롤백, 도달한 등록은 유효").
- 서버는 클라이언트가 보낸 `clientSeenPrice`를 신뢰하지 않고, 등록 순간 다중 소스로 `snapshotPrice`를 재확정한다 (R-06: 시세 데이터 깨짐 방지).
- 등록 즉시 `LOCKED` 상태로 잠긴다 (취소 불가).

**도출 근거**: FR-001 인수 조건 전체, R-06, 리뷰 노트 BE("idempotency key 스펙").

---

### API-02: GET `/predictions/me`

**설명**: 현재 사용자의 활성(미마감) 예측을 코인별로 반환.

**요청**: 없음 (인증 헤더만)

**응답 (성공) 200**:
| 필드 | 타입 (제안) | 설명 |
|------|-----------|------|
| btc | object \| null | BTC 활성 예측 (없으면 null) |
| eth | object \| null | ETH 활성 예측 |
| btc.predictionId | string | UUID |
| btc.direction | enum | ↑/↓ |
| btc.snapshotPriceKrwRounded | number | 등록 시 가격 |
| btc.registeredAt / closesAt | ISO 8601 (KST) | 시각 |
| btc.status | enum("LOCKED","SETTLING","SETTLED","INVALID") | 상태 |

**응답 (에러)**: 401 UNAUTHENTICATED

**비즈니스 규칙**:
- "활성"은 `status IN (LOCKED, SETTLING)`로 정의.
- `SETTLED`/`INVALID`는 본 응답에 포함되지 않으며, 이력은 API-03에서 조회.

**도출 근거**: FR-001 (잠금 표시 시나리오 1, 6번 단계), 시나리오 1.

---

### API-03: GET `/predictions/me/history`

**설명**: 내 예측 이력 (페이징, 최근 90일 윈도우).

**요청**:
| 필드 | 타입 (제안) | 필수 | 설명 |
|------|-----------|------|------|
| coin | enum("BTC","ETH","ALL") | N (default ALL) | 필터 |
| cursor | string | N | 페이징 |
| limit | int (≤50) | N | 기본 20 |

**응답 (성공) 200**:
| 필드 | 타입 (제안) | 설명 |
|------|-----------|------|
| items[] | array | 예측 결과 목록 |
| items[].status | enum("SETTLED","INVALID") | 결산 결과 |
| items[].outcome | enum("HIT","MISS","INVALID_TIE","INVALID_PRICE") | 적중/미적중/동가무효/시세무효 |
| items[].closingPriceKrwRounded | number | 마감가 (원 단위) |
| items[].priceDeltaPct | number | 변동률 (참고) |
| nextCursor | string \| null | — |

**비즈니스 규칙**:
- 90일 이전 데이터는 본 API에서 제외 (티어 윈도우와 일치, FR-002).
- INVALID는 적중·미적중 어느 쪽도 카운트되지 않음을 별도 표기 (FR-001).

**도출 근거**: FR-001, FR-002 (90일 슬라이딩 윈도우).

---

### API-04: GET `/predictions/me/result/:predictionId`

**설명**: 단일 결과 상세 (적중/미적중/무효 + 누적 적중률 변동 + 다음 티어 진행도). S-03 결과 시트.

**응답 (성공) 200**:
| 필드 | 타입 (제안) | 설명 |
|------|-----------|------|
| predictionId | string | — |
| outcome | enum("HIT","MISS","INVALID_TIE","INVALID_PRICE") | 결과 |
| coin / direction | enum | — |
| snapshotPriceKrwRounded | number | 예측가 |
| closingPriceKrwRounded | number | 마감가 (원 단위) |
| priceDeltaPct | number | 변동률 |
| accuracyBefore | number (0~1) | 결산 직전 누적 적중률 |
| accuracyAfter | number (0~1) | 결산 후 누적 적중률 |
| tierBefore / tierAfter | enum | 티어 변동 |
| nextTier.predictionsRemaining | int | 다음 티어 도달까지 N회 |
| ctaTarget | enum("BUY","SELL","COMPARE_CHANNELS") | 결과별 CTA 타겟 |

**응답 (에러)**:
| HTTP | 코드 | 조건 |
|------|-----|------|
| 404 | NOT_FOUND | 본인 소유 아님 또는 미존재 |
| 409 | NOT_SETTLED_YET | 결산 미완료 (마감 시각 +5분 SLO 내) |

**비즈니스 규칙**:
- INVALID는 누적·티어에 영향 없음 (FR-001, FR-002).
- ctaTarget은 적중 시 BUY/SELL(직전 거래 컨텍스트 기반), 미적중 시 COMPARE_CHANNELS (FR-011, 시나리오 3).

**도출 근거**: FR-010, FR-011, 시나리오 2/3.

---

### API-05: GET `/predictions/cards?coin=BTC|ETH`

**설명**: 8채널 카드 그리드 통합 응답. 각 채널은 독립 fetch되며 개별 실패는 다른 채널에 영향 없음.

**요청**:
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| coin | enum("BTC","ETH") | Y | 컨텍스트 코인 |

**응답 (성공) 200**:
| 필드 | 타입 (제안) | 설명 |
|------|-----------|------|
| coin | enum | 요청 코인 |
| serverTimeKst | ISO 8601 | 서버 시각 (클라이언트 시계 동기용) |
| cards[] | array (length=8) | 카드 배열 |
| cards[].channel | enum (datalab,community,leaderboard,news,social,polymarket,official,onchain) | 채널 식별자 |
| cards[].status | enum("OK","STALE","UNAVAILABLE","DISABLED","COMING_SOON") | 카드 상태 |
| cards[].direction | enum("UP","DOWN","NEUTRAL") \| null | 시그널 방향 |
| cards[].strengthPct | number (0~100) \| null | 시그널 강도 |
| cards[].label | string | 카드 표시 텍스트 ("김프 ↑ 2.3%" 등) |
| cards[].lastUpdatedAt | ISO 8601 \| null | 데이터 갱신 시각 |
| cards[].dataAgeSeconds | int \| null | (now - lastUpdatedAt). STALE 임계값 클라가 판단 |
| cards[].error | object \| null | UNAVAILABLE 시 코드/메시지 |

**응답 (에러)**:
| HTTP | 코드 | 조건 |
|------|-----|------|
| 200 | (부분 실패) | 일부 채널이 UNAVAILABLE이어도 전체 200, 카드별 status로 표현 |
| 503 | ALL_CHANNELS_DOWN | 8개 모두 동시 실패 (가능성 매우 낮음, 인프라 장애) |

**비즈니스 규칙**:
- **부분 장애 격리**: 한 카드 실패가 전체 응답 실패가 되지 않는다 (FR-003 인수조건, 시나리오 6, NFR 9-2).
- 폴리마켓 채널이 Plan B(7채널 모드)로 비활성화된 경우 `status="DISABLED"` (R-01).
- P1 채널(공식, 온체인)은 출시 초기 `status="COMING_SOON"`으로 노출 (FR-003 P1 카드 정책, 8-2 클릭 명세).

**도출 근거**: FR-003, FR-004~009, FR-012, FR-013, R-01, 시나리오 6, NFR 9-2.

---

### API-06: GET `/predictions/cards/:channel?coin=BTC|ETH`

**설명**: 단일 카드 상세 시트 데이터 (S-02). 채널별 페이로드 스키마가 다르다.

**요청**: path `channel`, query `coin`

**응답 (성공) 200 — 채널별 페이로드 (모두 제안)**:

- `datalab`:
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | kimchiPremiumPct | number | 김프 |
  | volume24hChangePct | number | 24h 거래량 변화율 |
  | high52w / low52w | number | 52주 고저점 |
  | ma20 / ma60 | number | 이동평균 |
  | rotationKey | enum | 카드 표시 로테이션 (6시간 단위, FR-004) |

- `community`:
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | voteUpPct / voteDownPct | number | 투표 분포 |
  | voteCount | int | 투표자 수 |
  | topPosts[] | array (5건) | 인기 코멘트 |
  | topPosts[].nickname / tier | string / enum | 닉네임 + 티어 (실명 X) |

- `leaderboard`:
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | qualifiedCount | int | 오늘 예측한 다이아·플래티넘 수 (≥30 시 노출) |
  | upPct | number | ↑ 비율 |
  | top10[] | array | 상위 10명 (닉네임 + 티어 + 90일 적중률) |

- `news`:
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | items[] | array (≤5) | 헤드라인 |
  | items[].headline / source / publishedAt / tone | string / string / ISO / enum(POS,NEU,NEG) | — |
  | items[].url | string | 원문 |

- `social` (X+텔레그램):
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | mentionCount24h | int | 24h 멘션 수 (≥100 시 노출) |
  | sentimentDistribution | { pos, neu, neg } pct | — |
  | influencerMentions[] | array (≤5) | 큐레이션 30명 중 최근 멘션 |
  | keywords[] | array (≤10) | 키워드 클라우드 |

- `polymarket`:
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | upProbability | number (0~1) | 24h ↑ 시장 확률 |
  | volumeUsd | number | 시장 거래량 |
  | history12h[] | array | 12h 추이 |
  | externalUrl | string | 폴리마켓 시장 페이지 |
  | disclaimer | string | "미국 예측시장 데이터, 한국 거래/베팅과 무관" (FR-009) |

- `official` (P1):
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | items[] | array (≤5, 7d) | 공식 글 |

- `onchain` (P1):
  | 필드 | 타입 | 설명 |
  |------|------|------|
  | cexNetflow24h | number | CEX 넷플로우 |
  | whaleMoves24h | int | 고래 이동 건수 |
  | sopr / mvrv | number | Glassnode 지표 |
  | sources[] | array | 출처 명시 |

**응답 (에러)**:
| HTTP | 코드 | 조건 |
|------|-----|------|
| 404 | UNKNOWN_CHANNEL | 잘못된 채널명 |
| 503 | CHANNEL_UNAVAILABLE | 해당 채널 circuit breaker OPEN |
| 423 | CHANNEL_DISABLED | feature flag로 비활성 (예: 폴리마켓 Plan B) |

**비즈니스 규칙**:
- 카드 자리에 "데이터 일시 중단" 표시는 FE에서 처리. 서버는 503/423으로 신호.
- `social.influencerMentions`는 운영 큐레이션 30명에 한정 (FR-008, R-02, R-03).
- `polymarket`은 한국어 베팅/참여 유도 텍스트 절대 미포함 (FR-009).
- `community.voteUpPct`는 **예측 등록 데이터에서 자동 집계** (별도 투표 기능 X, FR-005 + 시나리오 1).

**도출 근거**: FR-004~009, FR-012, FR-013, R-01, R-02, R-03.

---

### API-07: GET `/tier/me`

**설명**: 내 티어, 누적 예측, 적중률, 다음 티어까지 N회.

**응답 (성공) 200**:
| 필드 | 타입 | 설명 |
|------|------|------|
| tier | enum (BRONZE,SILVER,GOLD,PLATINUM,DIAMOND) | 현재 티어 |
| accuracy90d | number (0~1) | 90일 적중률 |
| settledCount90d | int | 90일 결산된 예측 수 (INVALID 제외) |
| nextTier | enum \| null | DIAMOND면 null |
| nextTier.predictionsRemaining | int | — |
| nextTier.accuracyRequired | number | — |

**비즈니스 규칙**:
- 윈도우는 **최근 90일** (FR-002).
- 임계값 표는 FR-002 본문 (브론즈/실버/골드/플래티넘/다이아).

**도출 근거**: FR-002.

---

### API-08: GET `/leaderboard?period=90d|season&coin=BTC|ETH`

**설명**: 다이아·플래티넘 상위 50명 리스트 + 오늘 픽 분포 (S-07).

**응답 (성공) 200**:
| 필드 | 타입 | 설명 |
|------|------|------|
| period | enum | 기간 |
| coin | enum | — |
| qualifiedCount | int | 오늘 예측 마친 다이아·플래티넘 수 |
| upPct | number | 30명 이상일 때만 |
| items[] | array (≤50) | 사용자 행 |
| items[].nickname / tier / accuracy90d | — / — / number | 노출 한정 (실명/지갑 X) |
| myRank | object \| null | 내 순위 (sticky bottom) |

**비즈니스 규칙**:
- 30명 미만 시 분포 노출하지 않음 (FR-006).
- 동률(↑=↓) 처리는 운영 정책 (qa-spec 이관 항목, 본 명세는 응답 필드만 정의).
- 닉네임 + 티어 배지 외 정보 노출 금지 (FR-006, 안티골).

**도출 근거**: FR-002, FR-006.

---

### API-09: POST `/community/posts`

**요청**:
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| coin | enum | Y | 대상 코인 |
| content | string (1~140) | Y | 본문 |
| idempotencyKey | string | Y | 중복 게시 방지 |

**응답 (성공) 201**:
| 필드 | 타입 | 설명 |
|------|------|------|
| postId | string | — |
| createdAt | ISO 8601 | — |

**응답 (에러)**:
| HTTP | 코드 | 조건 |
|------|-----|------|
| 400 | INVALID_LENGTH | 0 또는 >140 |
| 400 | URL_BLOCKED | URL 패턴 감지 (8-7) |
| 403 | KYC_REQUIRED | — |
| 429 | RATE_LIMITED | 사용자별 분당 N회 초과 (`[BE 결정 필요]` 임계값) |

**비즈니스 규칙**:
- 신고 누적 3건 이상 시 **자동 가림** (FR-005). 가림은 본 API가 아니라 신고 API의 부수효과.
- 닉네임 + 티어로만 노출 (FR-005).

**도출 근거**: FR-005, 8-7 폼 정책, 리뷰 노트 BE("신고/스팸 봇 레이트리밋").

---

### API-10: GET `/community/posts?coin=BTC|ETH&sort=popular|recent`

**응답**: 코멘트 페이징 (popular = 좋아요·댓글 가중, recent = 최신순). 가림된 글은 본인 외 노출 X.

**도출 근거**: FR-005.

---

### API-11: POST `/community/posts/:postId/like`

**응답**: 토글. 낙관적 업데이트 호환 (8-3).

**도출 근거**: 8-3 클릭 명세.

---

### API-12: POST `/community/posts/:postId/report`

**요청**:
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| reason | enum (5종) | Y | 사유 라디오 |
| detail | string (≤200) | N | 자유서술 |

**응답 (성공) 200**:
| 필드 | 타입 | 설명 |
|------|------|------|
| postId | string | — |
| reportCount | int | 누적 신고 수 |
| autoHidden | boolean | 3건 도달로 가림 처리되었는지 |

**비즈니스 규칙**:
- 동일 사용자 중복 신고는 1건으로 카운트 (`[BE 제안]` — FR-005 본문 명시 없음, 어뷰징 방지).
- 자동 가림 후 운영자 검토 큐에 등재 (R-09).
- autoHidden=true 시 §8 이벤트로 운영팀 알림.

**도출 근거**: FR-005, R-09.

---

### API-13: GET `/community/votes?coin=BTC|ETH`

**응답**: 오늘 ↑/↓ 예측 등록자 수 분포 (예측 등록 시 자동 집계).

**비즈니스 규칙**: API-05 community 카드와 동일 데이터 소스 (캐시 공유).

---

### API-14: POST `/notifications/devices`

**요청**: `deviceId`, `pushToken`, `platform(iOS|AOS|Web)`, `appVersion`. 갱신 가능.

**도출 근거**: FR-010 푸시 발송 전제, NFR 9-2 푸시 99.5%.

---

### API-15: PATCH `/notifications/preferences`

**요청**:
| 필드 | 타입 | 설명 |
|------|------|------|
| settlementPush | boolean | 마감 결과 푸시 |
| dailyMissingPush | boolean | 09:00 미예측 알림 |
| tierPromotionPush | boolean | 티어 승급 푸시 |

**비즈니스 규칙**: 티어 강등은 푸시 없음, 인앱만 (FR-015) — 본 설정에 강등 토글 없음.

**도출 근거**: FR-014, FR-015.

---

### API-16: GET `/markets/quotes?symbol=BTC|ETH`

**응답**:
| 필드 | 타입 | 설명 |
|------|------|------|
| price | number | 다중 소스 평균가 (원 단위 반올림 전) |
| priceKrwRounded | number | 원 단위 |
| sources[] | array | 사용된 소스명·가격 (디버깅용, 운영자만 노출 고려) |
| serverTimeKst | ISO 8601 | — |

**비즈니스 규칙**:
- 표시용. 등록 API-01은 본 응답을 신뢰하지 않고 등록 순간 재조회 (R-06).

**도출 근거**: FR-001, R-06.

---

### API-17 ~ API-20: 운영자 API

- API-17 POST `/admin/influencers`: 인플루언서 30명 큐레이션 등록 (handle, platform, isActive). 출시 전 명단 + 격주 갱신 (10-3 운영 의존).
- API-18 DELETE `/admin/influencers/:handle`: 즉시 제외 + 캐시 무효화.
- API-19 POST `/admin/community/posts/:postId/moderate`: 가림/복원 토글, 사유 기록.
- API-20 GET `/admin/feature-flags/polymarket`: Plan B 토글 상태 조회. 변경은 별도 PATCH (R-01).

**도출 근거**: 10-3 운영 의존, R-01, R-03.

---

### API-21 ~ API-22: 내부 워커 트리거

- API-21 POST `/internal/scheduler/settle`: 결산 워커. 마감 임박 예측을 큐로 가져와 다중 소스 가격 ±15초 평균 → outcome 결정 → 티어 재계산 → 결과 푸시. 외부 호출 차단.
- API-22 POST `/internal/scheduler/daily-09`: 09:00 KST 미예측 사용자 푸시. jitter 09:00~10:00 분산.

**도출 근거**: FR-001 (마감 결산), FR-010 (결과 알림), FR-014 (09:00 알림), 리뷰 노트 BE.

---

### API-23: GET `/predictions/comparison/:predictionId`

**설명**: 미적중 예측에 대해 6채널이 정답을 어떻게 가리켰는지 비교 (S-04, 시나리오 3).

**응답**:
| 필드 | 타입 | 설명 |
|------|------|------|
| myDirection | enum | 내 예측 |
| actualDirection | enum | 실제 결과 |
| channels[] | array | 채널별 |
| channels[].channel | enum | datalab/community/... |
| channels[].directionAtPredictionTime | enum | 예측 등록 시점 채널 시그널 방향 |
| channels[].correct | boolean | 정답 여부 |
| highlightTopN | int | 정답 가까운 채널 강조 (3) |

**비즈니스 규칙**:
- "예측 등록 시점 채널 시그널"을 결정하기 위해 등록 시점 카드 데이터를 **이력 저장** 필요 (§3 PredictionChannelSnapshot).

**도출 근거**: 시나리오 3, FR-011 ("내가 놓친 시그널").

---

## §3. 데이터 모델 (제안)

> ⚠️ 타입, 제약, 인덱스, DB 종류는 모두 제안이다. **실제 스키마·DB 선택은 BE팀이 확정**한다 (`[BE 결정 필요]` §9).

### User (참조 — 업비트 기존 사용자 시스템 사용)

본 기능은 자체 사용자 테이블을 만들지 않고 업비트 인증/KYC를 신뢰한다 (10-1). 외래 키 후보:
| 필드 | 설명 |
|------|------|
| userId | PK (외부) |
| nickname | 닉네임 (실명 노출 금지) |
| ageVerified | KYC ≥19 (시나리오 5) |
| kycPassed | 실명 인증 통과 |

### Prediction (예측)

| 필드 | 타입 (제안) | 제약 (제안) | 설명 | 도출 근거 |
|------|-----------|-----------|------|----------|
| predictionId | string (UUID) | PK | 예측 ID | FR-001 |
| userId | string | FK, idx | 사용자 | FR-001 |
| coin | enum("BTC","ETH") | NN, idx | 대상 | FR-001 |
| direction | enum("UP","DOWN") | NN | ↑/↓ | FR-001 |
| snapshotPrice | decimal | NN | 등록 시 다중 소스 평균 (원본) | FR-001, R-06 |
| snapshotPriceKrwRounded | bigint | NN | 원 단위 반올림 (동가 비교용) | FR-001 |
| registeredAt | timestamp (KST) | NN, idx | 등록 시각 | FR-001 |
| closesAt | timestamp (KST) | NN, idx | registeredAt + 24h | FR-001 |
| closingPrice | decimal | nullable | 마감 시 다중 소스 평균 | FR-001 |
| closingPriceKrwRounded | bigint | nullable | 원 단위 | FR-001 |
| status | enum("LOCKED","SETTLING","SETTLED","INVALID") | NN, idx | 상태 | API-02 |
| outcome | enum("HIT","MISS","INVALID_TIE","INVALID_PRICE") \| null | — | 결산 결과 | FR-001 |
| invalidReason | string \| null | — | 무효 사유 (TIE / PRICE_DIVERGENCE / SOURCE_FAILURE) | FR-001, R-06 |
| idempotencyKey | string | UNIQUE(userId, idempotencyKey) | 중복 차단 | API-01 |
| createdAt / updatedAt | timestamp | NN | — | — |

**복합 유니크 제약 (1일 1회 보장)**:
- `(userId, coin)` 중 `status IN (LOCKED, SETTLING)`인 행은 최대 1개. (`[BE 제안]`: 부분 인덱스 또는 애플리케이션 락 + DB 트랜잭션)

**핵심 인덱스 후보**:
- `(closesAt) WHERE status='LOCKED'` — 결산 워커 스캔
- `(userId, registeredAt DESC)` — 이력 페이징
- `(userId, coin, registeredAt DESC)` — 90일 윈도우 집계

**도출 근거**: FR-001 인수 조건, R-06.

### PredictionChannelSnapshot (예측 시점 채널 시그널 이력)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| predictionId | FK | NN | API-23 비교용 |
| channel | enum | NN | datalab/community/leaderboard/news/social/polymarket/official/onchain |
| direction | enum("UP","DOWN","NEUTRAL") | nullable | 등록 시점 채널 시그널 |
| strengthPct | number | nullable | 강도 |
| capturedAt | timestamp | NN | — |

**도출 근거**: API-23, 시나리오 3.

### TierAssignment (티어 부여 이력)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| userId | FK | idx | — |
| tier | enum (BRONZE..DIAMOND) | NN | — |
| accuracy90d | number | NN | 산정 시 적중률 |
| settledCount90d | int | NN | 산정 시 누적 |
| assignedAt | timestamp | NN | — |
| changeType | enum("INITIAL","PROMOTION","DEMOTION") | NN | 푸시/배지 트리거 |

**도출 근거**: FR-002, FR-015.

### CardCache (8채널 카드 응답 캐시)

> 영구 저장이 아닌 캐시 (Redis 등). DB 엔티티가 아니라 **논리적 키 구조**.

| 키 (제안) | 값 | TTL |
|----------|-----|-----|
| `card:datalab:{coin}` | API-06 datalab 페이로드 | 60s |
| `card:community:{coin}` | community 페이로드 | 30s |
| `card:leaderboard:{coin}` | leaderboard 페이로드 | 60s |
| `card:news:{coin}` | news 페이로드 | 5m |
| `card:social:{coin}` | social 페이로드 (X+Telegram) | 5m |
| `card:polymarket:{coin}` | polymarket 페이로드 | 60s |
| `card:official:{coin}` | official RSS 페이로드 | 30m |
| `card:onchain:{coin}` | onchain 페이로드 | 15m |
| `card:summary:{coin}` | API-05 통합 응답 (8장 요약) | 30s |

**TTL 근거**: FR-003 인수조건("5분 이상 stale 시 갱신 시각 표기") + 채널별 외부 API 한도 + 비용 (§5). NFR 9-2 카드 99.0%.

### CommunityPost (커뮤니티 코멘트)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| postId | UUID | PK | — |
| userId | FK | idx | — |
| coin | enum | idx | — |
| content | string (≤140) | NN | URL 차단 |
| likeCount | int | default 0 | — |
| reportCount | int | default 0 | — |
| status | enum("VISIBLE","AUTO_HIDDEN","ADMIN_HIDDEN") | idx | — |
| createdAt | timestamp | NN, idx | — |

**도출 근거**: FR-005, 8-7.

### CommunityReport (신고 이력)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| postId | FK | (postId, reporterId) UNIQUE | 중복 신고 차단 |
| reporterId | FK | — | — |
| reason | enum (5종) | NN | — |
| detail | string (≤200) | nullable | — |
| createdAt | timestamp | — | — |

**도출 근거**: FR-005, 8-7, R-09.

### Influencer (인플루언서 큐레이션)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| handle | string | PK | X/Telegram 핸들 |
| platform | enum("X","TELEGRAM") | NN | — |
| displayName | string | — | — |
| isActive | boolean | NN | — |
| addedBy | FK (admin) | — | — |
| reviewedAt | timestamp | — | 격주 갱신 트래킹 |

**제약**: `isActive=true` 행 수 ≤ 30 (FR-008, 운영 정책).

**도출 근거**: FR-008, 10-3.

### NotificationLog (푸시 발송 이력)

| 필드 | 타입 | 제약 | 설명 |
|------|------|-----|------|
| notificationId | UUID | PK | — |
| userId | FK | idx | — |
| type | enum("SETTLEMENT","DAILY_09","TIER_PROMOTION") | NN | — |
| sentAt | timestamp | — | 실제 발송 시각 (jitter 적용 후) |
| scheduledAt | timestamp | — | 원래 의도 시각 |
| status | enum("SENT","FAILED","FALLBACK_INAPP") | — | 권한 거부 시 인앱 fallback (FR-014) |
| relatedId | string | — | predictionId 등 |

**도출 근거**: FR-010, FR-014, FR-015, NFR 9-2 푸시 99.5%.

### FeatureFlag (운영 토글)

| 필드 | 값 | 설명 |
|------|-----|------|
| `polymarket.enabled` | boolean | Plan B 토글 (R-01) |
| `social.enabled` | boolean | X API 비용 폭주 시 비상 차단 (R-02) |
| `dailyPush.enabled` | boolean | 푸시 프리퀀시 운영 |

**도출 근거**: R-01, R-02, Q-05.

### 관계 다이어그램 (텍스트)

```
User 1──N Prediction
Prediction 1──N PredictionChannelSnapshot
User 1──N TierAssignment
User 1──N CommunityPost
CommunityPost 1──N CommunityReport
User 1──N CommunityReport (reporter)
User 1──N NotificationLog
Influencer ── (운영 큐레이션, X·텔레그램 수집 입력)
CardCache ── (Redis 등, 영구 저장 X)
FeatureFlag ── (운영 콘솔)
```

---

## §4. 비즈니스 로직

### 로직-01: 예측 등록 (POST `/predictions`)

**도출 근거**: FR-001 인수 조건, R-06, 리뷰 노트 BE("idempotency, 라이트락").

**입력**: `userId`, `coin`, `direction`, `idempotencyKey`

**처리**:
1. 인증 미들웨어로 `userId`, `kycPassed`, `ageVerified` 확인. 둘 중 하나라도 false면 403 KYC_REQUIRED. — 시나리오 5, FR-001.
2. **마감 직전 30분 라이트락 확인** — 현재 시각이 다른 사용자들의 마감 클러스터(±30분)에 위치하면 백프레셔 큐 사용. 큐 길이 임계 초과 시 503 SERVICE_UNAVAILABLE 반환. — R-05, NFR 9-1 30K RPS, 리뷰 노트 BE.
3. `idempotencyKey` 조회. 존재하면 기존 응답 반환 (재요청 멱등성). — FR-001 인수조건.
4. `(userId, coin)` 활성(`LOCKED`/`SETTLING`) 행 존재 여부를 **DB 트랜잭션 + 부분 유니크 인덱스**로 확인. 존재 시 409 ALREADY_PREDICTED_TODAY. — FR-001 ("같은 코인을 24시간 이내에 다시 예측할 수 없다").
5. 다중 소스(시세 API ≥3개) 동시 조회 → 평균. 모든 소스 실패 또는 5%+ 괴리 시 422 PRICE_FETCH_FAILED. — R-06, FR-001 5%+ 괴리.
6. 평균가를 원 단위 반올림 → `snapshotPriceKrwRounded`. `closesAt = registeredAt + 24h` (KST). — FR-001.
7. Prediction 행 INSERT (status=LOCKED) + PredictionChannelSnapshot INSERT (현재 8채널 시그널 캡처). — FR-001, API-23.
8. 응답 + 커뮤니티 투표 카운터 증분 이벤트 발행 (FR-005 / API-13). — FR-005 "오늘의 투표 결과 = 예측 등록 자동 집계".

**출력**: 201 + Prediction 객체.

**엣지 케이스**:
| 조건 | 처리 |
|------|------|
| idempotencyKey 동일 + 페이로드 다름 | 409 IDEMPOTENCY_REPLAY |
| 다중 소스 1개 실패, 나머지 평균 가능 | 평균 계속 진행 (degrade 허용) |
| 다중 소스 ≥2개 실패 또는 5%+ 괴리 | 422 PRICE_FETCH_FAILED |
| KYC 미통과 | 403 KYC_REQUIRED |
| 마감 클러스터 라이트락 + 큐 임계 초과 | 503 SERVICE_UNAVAILABLE |

---

### 로직-02: 결과 결산 (마감 시각 도래)

**도출 근거**: FR-001 (마감가, 동가 무효, 5%+ 괴리), FR-010, NFR 9-1 (마감 +5분 푸시), R-06.

**입력**: 결산 대상 Prediction (`status=LOCKED` AND `closesAt ≤ now`)

**처리**:
1. 워커가 `closesAt ≤ now AND status=LOCKED`인 행을 **시간 윈도우 단위로 배치 추출**, 각 행을 `status=SETTLING`로 전이 (낙관적 락). — NFR 9-1.
2. 마감 시각 `closesAt ±15초` 윈도우 내 다중 소스 시세 수집 (≥3개). — FR-001 "마감 시각 ±15초 다중 소스 평균".
3. 5%+ 괴리 검증:
   - 소스 간 최대-최소 차이 / 평균 > 5% → `outcome=INVALID_PRICE`, `invalidReason=PRICE_DIVERGENCE` (재계산 X). — FR-001.
4. 모든 소스 실패 시 → `INVALID_PRICE`, `invalidReason=SOURCE_FAILURE`. — R-06.
5. 정상이면 평균 → 원 단위 반올림 → `closingPriceKrwRounded`.
6. **동가 비교**: `snapshotPriceKrwRounded == closingPriceKrwRounded` → `INVALID_TIE`. — FR-001 ("원 단위 반올림 후 동일이면 무효").
7. 정상이면 방향 비교:
   - `UP` 예측 + closing > snapshot → `HIT`
   - `UP` 예측 + closing < snapshot → `MISS`
   - DOWN 대칭
8. `status=SETTLED`, outcome 저장.
9. **티어 재계산** (로직-03 호출).
10. 결과 푸시 발송 큐에 등재 (jitter 적용, 로직-04). — FR-010, FR-015.

**출력**: 결산 완료 + 푸시 발송.

**엣지 케이스**:
| 조건 | 처리 |
|------|------|
| 동가 (원 단위 동일) | INVALID_TIE, 적중·미적중 모두 카운트 X (FR-001) |
| 5%+ 괴리 | INVALID_PRICE (재계산 X) |
| 모든 시세 소스 실패 | INVALID_PRICE, 운영 알람 (NFR 9-3) |
| `closesAt`이 5분 지나도 미결산 | 모니터링 알람 + 사용자 결과 화면 "잠시 후 다시 알려드릴게요" (8-5) |
| 사용자가 마감 직후 API-04 호출 | 409 NOT_SETTLED_YET 반환 |

---

### 로직-03: 티어 재계산 (90일 슬라이딩 윈도우)

**도출 근거**: FR-002.

**입력**: `userId`

**처리**:
1. 최근 90일 SETTLED 예측 집계 (INVALID 제외). — FR-002.
2. `accuracy90d = HIT 수 / SETTLED 수`, `settledCount90d`.
3. 임계값 표(FR-002)와 비교 → 새 티어 결정. 동일하면 종료.
4. 변경 시 TierAssignment INSERT, `changeType=PROMOTION/DEMOTION`.
5. PROMOTION이면 푸시 큐 등재 (FR-015 축하 애니메이션). DEMOTION은 푸시 X, 인앱 카드만. — FR-015.

**엣지 케이스**:
| 조건 | 처리 |
|------|------|
| settledCount90d=0 | 티어=BRONZE, 변동 없음 |
| 임계 경계값 진동 (예: 적중률 54.9%↔55.1%) | `[BE 결정 필요]` 히스테리시스 (예: ±1%p 버퍼) — qa-spec 이관 항목과 연계 |

---

### 로직-04: 푸시 발송 (jitter 분산)

**도출 근거**: FR-010, FR-014, FR-015, R-05 (스파이크), NFR 9-1 (마감 +5분 SLO).

**입력**: 푸시 발송 요청 (type, userId, scheduledAt, payload)

**처리**:
1. 사용자별 NotificationPreferences 확인. 거부 시 인앱 fallback (NotificationLog status=FALLBACK_INAPP). — FR-014, FR-015.
2. 다음 jitter 적용:
   - **SETTLEMENT**: 마감 시각 도래 후 0~120초 균등 분포 (NFR 9-1 +5분 SLO 내).
   - **DAILY_09**: 09:00~10:00 균등 분포 (FR-014 명시).
   - **TIER_PROMOTION**: 결산 직후 0~30초.
3. `sentAt = scheduledAt + jitter` 큐 등재.
4. 발송 실패 시 재시도 (지수 백오프). 최종 실패 시 인앱 fallback.

**엣지 케이스**:
| 조건 | 처리 |
|------|------|
| 푸시 권한 거부 / DND | FALLBACK_INAPP, 다음 앱 진입 시 인앱 카드 (8-5) |
| 동일 사용자 마감+티어 동시 발생 | 티어 푸시는 결과 푸시 본문에 병합 (`[BE 제안]`, FR-015 정신) |
| 일일 푸시 프리퀀시 한도 | Q-05 결정 필요 — `[BE 결정 필요]` |

---

### 로직-05: 8채널 카드 어그리게이션

**도출 근거**: FR-003 (격리), FR-004~009, FR-012, FR-013, NFR 9-2 카드 99.0%, R-01, R-02, 시나리오 6, 리뷰 노트 BE("채널별 캐시 TTL").

**입력**: `coin`

**처리**:
1. `card:summary:{coin}` 캐시 조회 (TTL 30s). 히트 시 즉시 반환.
2. 미스 시 8채널 캐시(`card:{channel}:{coin}`)를 **병렬 조회**. 각 채널 응답:
   - 히트 → OK + 데이터.
   - 미스 → 백그라운드 fetcher 트리거 + STALE 또는 UNAVAILABLE 반환 (마지막 성공 데이터가 있으면 STALE, 없으면 UNAVAILABLE).
3. 각 채널 fetcher는 **circuit breaker** 보호:
   - CLOSED → 외부 API 호출.
   - HALF_OPEN → 일부 트래픽 시도.
   - OPEN → 즉시 UNAVAILABLE 반환 (다음 재시도 시각까지).
4. 채널별 폴링 주기는 별도 워커가 처리 (§5 표). 본 API는 캐시만 읽는 read-through 패턴.
5. 폴리마켓 채널이 FeatureFlag로 비활성이면 DISABLED. — R-01.
6. P1 채널이 비활성이면 COMING_SOON. — FR-003 인수조건 8-2.
7. 8장 응답 조립 후 `card:summary:{coin}`에 캐시.

**엣지 케이스**:
| 조건 | 처리 |
|------|------|
| 1개 채널 fetch 실패 | 해당 카드만 UNAVAILABLE, 나머지 정상 (FR-003, 시나리오 6) |
| 8개 모두 실패 | 503 ALL_CHANNELS_DOWN (인프라 알람) |
| social 채널 데이터 < 100 멘션 | "현재 데이터 부족" status 노출 (FR-008 인수조건) |
| leaderboard 다이아·플래티넘 < 30명 | "데이터 부족 (현재 N명)" (FR-006 인수조건) |
| news 24h 0건 | "최근 기사 없음" (FR-007) |

**Circuit Breaker 정책 (제안)**:
| 채널 | 실패 임계 | OPEN 시간 | 백오프 |
|------|----------|----------|--------|
| social (X) | 연속 5회 또는 5분 내 50% 실패율 | 60s | 지수 |
| polymarket | 동일 | 60s | 지수 |
| onchain | 연속 3회 | 120s | 지수 |
| 기타 | 연속 5회 | 60s | 지수 |

> 임계값은 출시 후 데이터로 튜닝. `[BE 결정 필요]`.

---

### 로직-06: 커뮤니티 자동 가림

**도출 근거**: FR-005, R-09.

**처리**:
1. `/community/posts/:postId/report` 수신.
2. `(postId, reporterId)` UNIQUE → 중복 신고는 1건으로.
3. `reportCount += 1`. ≥3이면 `status=AUTO_HIDDEN` + 운영 큐 알림 이벤트 발행. — FR-005.
4. 운영자가 API-19로 검토 후 복원/유지.

---

## §5. 외부 연동

> ⚠️ TTL·폴링 주기·백오프는 **기획서 명시값 + 비용·라이센스 고려한 BE 제안**. 실제 값은 출시 전 부하·비용 테스트로 확정.

| 서비스 | 용도 | 갱신 주기 (제안) | 캐시 TTL (제안) | 장애 시 대응 | 비용/라이센스 | 도출 근거 |
|--------|------|------|------|----------|--------------|----------|
| **업비트 시세 API** (KRW BTC/ETH) | 예측 등록 시 스냅샷, 마감가 평균 (다중 소스 1개) | 등록·마감 이벤트 시 즉시 + 마감 ±15초 윈도우 | 5s | 다른 소스로 평균 가능. 모든 소스 실패 시 INVALID_PRICE | 무료 (자사) | FR-001, R-06 |
| **외부 시세 소스 #1** (예: CoinGecko, Binance KRW pair 환산) | 다중 소스 평균 (≥3개 소스) | 위와 동일 | 5s | circuit breaker, 격리 | 무료 또는 저비용 | FR-001 R-06 (다중 소스) |
| **외부 시세 소스 #2** (예: 또 다른 CEX) | 동일 | 동일 | 5s | 동일 | — | 동일 |
| **업비트 데이터랩 API** | FR-004 카드 (김프, 거래량, 52w, MA) | 폴링 60s | 60s | 카드 UNAVAILABLE, 다른 카드 정상 | 무료 (자사) | FR-004 |
| **업비트 기사 피드** | FR-007 (24h 헤드라인 5건) | 폴링 5m | 5m | 0건이면 "최근 기사 없음" | 무료 (자사) | FR-007 |
| **업비트 푸시 인프라** | 결과/일일/티어 푸시 | 이벤트 트리거 | — | 실패 시 인앱 fallback | 무료 (자사), 99.5% NFR | FR-010, FR-014, FR-015 |
| **업비트 KYC/인증** | ≥19세 게이트 | 등록 시 1회 | 세션 캐시 | 인증 실패 → 403 | 무료 (자사) | 시나리오 5 |
| **X API (Tier Pro 이상)** | FR-008 멘션·센티먼트 | 폴링 5m + 인플루언서 멘션 5m | 5m | circuit breaker, 카드 UNAVAILABLE, 비용 폭주 시 FeatureFlag로 차단 | ≈ $5K/월 (Q-03), 약관 검토 | FR-008, R-02, 10-2, Q-03 |
| **Telegram Channel API** | FR-008 채널 멘션 (공개 채널 한정) | 폴링 5m | 5m | 동일 | 운영자 동의 필요 | FR-008, 10-2 |
| **Polymarket API** | FR-009 시장 확률 + 거래량 | 폴링 60s | 60s | circuit breaker; **Plan B**: FeatureFlag로 즉시 7채널 모드, 카드 자리 자리표시자 | **법무 검토 필수**, 비용 미정 | FR-009, R-01, 10-2 |
| **Bitcoin.org / Ethereum.org RSS** | FR-012 공식 글 (P1) | 폴링 30m | 30m | 카드 UNAVAILABLE | 무료 (공개 RSS) | FR-012, 10-2 |
| **Dune Analytics API** | FR-013 CEX 넷플로우, 고래 이동 (P1) | 폴링 15m | 15m | UNAVAILABLE; 비용 한도 초과 시 차단 | 유료 ($X/월, Q-03 동시 결정) | FR-013, 10-2 |
| **Glassnode API** | FR-013 SOPR/MVRV (P1) | 폴링 15m | 15m | 동일 | 유료 | FR-013, 10-2 |
| **자동 번역 (Papago/DeepL)** | 외부 데이터 한글 요약 (FR-007 영문 기사 등) | 데이터 수집 시 1회 + 결과 캐시 | 24h | 번역 실패 시 원문만 노출 | 비용 모니터, 출시 전 품질 검증 | 10-2, NFR 9-4 |

**`[BE 제안]`**:
- 시세 다중 소스는 **최소 3개**를 권장 (1개 장애 + 1개 outlier 제외 후에도 평균 가능).
- 외부 API 키·비밀은 별도 보안 에이전트 영역. 본 명세는 **사용처와 폴백만 정의**한다.
- 라이센스/비용 알람: X API 월 예산 초과 70% 시 운영 알림, 95% 시 자동 폴링 주기 2배 증가, 100% 시 FeatureFlag로 채널 차단 (R-02).

---

## §6. 비기능 요구사항

> PRD §9 NFR을 그대로 가져오고, 리뷰 노트 BE 항목("P95/P99 분리, 백프레셔 임계, 30K RPS 산출")을 BE 제안으로 보강.

### 6-1. 성능 SLO

| 항목 | 목표 (P95) | 목표 (P99) `[BE 제안]` | 측정 | BE 관점 영향 |
|------|----------|----------|------|-------------|
| S-01 진입 카드 그리드 first paint | ≤ 1.5s (KT 4G) | ≤ 3.0s | RUM | API-05 캐시 히트 비율 ≥ 95% 필요 |
| 카드 데이터 fetch (캐시 hit) | ≤ 200ms | ≤ 400ms | 서버 메트릭 | 인메모리/Redis 응답 시간 모니터 |
| 카드 데이터 fetch (캐시 miss) | ≤ 1.5s | ≤ 3.0s | 서버 메트릭 | 채널별 fetcher SLO, circuit breaker |
| 예측 등록 (API-01) | ≤ 800ms | ≤ 1.5s | 서버 메트릭 | 다중 소스 평균 + DB INSERT 합산 |
| 결과 결산 지연 | 마감 +5분 푸시 100% (가용성) | — | 워커 메트릭 | 결산 워커 동시성 + 푸시 큐 처리량 |
| 동시 예측자 처리 | 30,000 RPS | — | 부하 테스트 | **산출 근거** `[BE 제안]`: DAU 1M × 참여율 15% × 마감 클러스터링 (가정 — 리뷰 노트 BE 이관 항목, 출시 전 검증) |

### 6-2. 가용성 SLO

| 항목 | 목표 | BE 관점 영향 |
|------|------|-------------|
| 예측 등록 / 결과 결산 | 99.9% (월 ~43분) | 다중 AZ, DB 페일오버 (`[BE 결정 필요]`) |
| 카드 인사이트 (전체) | 99.0% | **채널별 독립** — 한 채널 다운이 다른 채널 안 막음 |
| 푸시 알림 | 99.5%, 실패 시 인앱 fallback | NotificationLog로 감사 |

### 6-3. 백프레셔 / 큐 정책 `[BE 제안]`

리뷰 노트 BE 이관 항목.

| 큐 | 트리거 | 정책 |
|-----|--------|------|
| 예측 등록 큐 | 라이트락 시간대 (마감 클러스터 ±30분) | 큐 길이 임계(예: 10K) 초과 시 503 + Retry-After 헤더 |
| 결산 큐 | 마감 시각 도달 | 시간 윈도우 단위 배치, 워커 N개 병렬 (수평 확장) |
| 푸시 큐 | 결산/티어/일일 | jitter 분산, 발송 실패 시 지수 백오프 + 인앱 fallback |
| 카드 fetch 큐 | 폴링 주기 | 폴링 워커 분리, circuit breaker |

> 큐 임계값·동시성은 부하 테스트 후 확정 (`[BE 결정 필요]`).

### 6-4. 모니터링 / 알림

| 메트릭 | 위치 (제안) | 알람 임계 (제안) |
|--------|-----------|---------------|
| 8채널 카드별 응답 지연 / 실패율 | 그라파나 대시보드 (NFR 9-3) | 채널별 실패율 5% 초과 시 알람 |
| 일일 예측 등록 수 / 코인별 / 시간대 분포 | 동일 | 평소 대비 -50% 시 알람 |
| 마감 직전 30분 RPS | 동일 (NFR 9-3) | 30K RPS 임계 90% 초과 시 알람 |
| 티어 변동 이벤트 (승급/강등 횟수) | 동일 | 일일 합계, 비정상 스파이크 감지 |
| 결산 워커 lag | 새로 추가 | `closesAt - settledAt > 5min` 1건이라도 발생 시 알람 (NFR 9-1) |
| INVALID_PRICE 발생률 | 새로 추가 | 시간당 5건 초과 시 R-06 알람 |
| 외부 API 비용 누적 (X/Glassnode/Dune) | 별도 비용 대시보드 | 월 예산 70% / 95% / 100% 단계 알람 (R-02) |
| 커뮤니티 자동 가림 발생 | 모더레이션 대시보드 | 시간당 N건 초과 시 운영자 호출 (R-09) |
| 폴리마켓 FeatureFlag 토글 이력 | 운영 로그 | 토글 시 즉시 알림 (R-01) |

---

## §7. 동시성 & 정합성

PRD R-05·R-06·R-07 + 리뷰 노트 BE를 가져오고 BE 제안 추가.

| 시나리오 | 위험 | 기획서 기대 | 해결 방향 (제안) |
|---------|------|-----------|----------------|
| 동일 사용자 동일 코인 동시 2회 탭 (네트워크 지연) | 1일 1회 위반 | FR-001 "같은 코인 24h 내 재예측 불가" | `(userId, coin) WHERE status IN (LOCKED,SETTLING)` 부분 유니크 + 트랜잭션. 추가로 idempotencyKey로 클라 재시도 멱등 |
| 등록 진행 중 화면 이탈 | 등록 손실/중복 | FR-001 "도달한 등록은 유효, 도달 전 실패는 롤백" | idempotencyKey 기반 재시도. 서버 응답 도달 전 클라 재요청 시 동일 결과 반환 |
| 마감 직전 30분 트래픽 스파이크 | 장애 | NFR 30K RPS 대응 (R-05) | 라이트락(읽기 전용 시간대 큐) + 백프레셔 503 + 수평 확장 |
| 결산 워커 중복 처리 (재시작·이중 트리거) | 결과 이중 결산 | — | `status=LOCKED → SETTLING` 전이를 낙관적 락(version) 또는 SELECT FOR UPDATE로 보호 |
| 시세 데이터 깨짐 (소스 단일 장애) | 잘못된 결산 | FR-001 "5%+ 괴리 무효" / R-06 "다중 소스 평균 + 무효 처리" | 다중 소스 ≥3, 5% 괴리 검증, INVALID 처리 |
| 다중 계정 어뷰징 (티어 게이밍) | 리더보드 오염 | R-07 "1계정 1티어, KYC 식별" | KYC 기반 userId 1:1, 의심 계정 모니터 (보안 에이전트와 협업) |
| 커뮤니티 동일 사용자 같은 글 다중 신고 | 자동 가림 우회 | — | `(postId, reporterId)` UNIQUE |
| 카드 캐시 thundering herd (TTL 만료 동시 fetch) | 외부 API 한도 초과 | — | single-flight / coalescing + 갱신 락 |
| 푸시 발송 동시 스파이크 | 인프라 부하 | FR-014 "jitter 분산" | jitter 0~120s (마감) / 0~3600s (09:00) |
| 9시 미예측 알림 + 티어 알림 + 마감 알림 동시 | 사용자 푸시 폭격 | Q-05 미정 | 사용자별 일일 푸시 한도 + 우선순위 (`[BE 결정 필요]`) |

---

## §8. 이벤트 & 알림

| 이벤트 | 트리거 | 처리 | 대상 | 도출 근거 |
|--------|--------|------|------|----------|
| `prediction.registered` | API-01 성공 | 커뮤니티 투표 카운터 증분, PredictionChannelSnapshot 생성 | 내부 | FR-005, API-23 |
| `prediction.settled` | 로직-02 완료 | 결과 푸시 큐 + 티어 재계산 트리거 | 사용자 + 내부 | FR-010, FR-002 |
| `prediction.invalid` | 로직-02 INVALID 결정 | 결과 푸시 + 운영 알람(IF=PRICE_DIVERGENCE/SOURCE_FAILURE) | 사용자 + 운영 | FR-001, R-06 |
| `tier.promoted` | 로직-03 승급 | 푸시 + 인앱 배지 애니메이션 | 사용자 | FR-015 |
| `tier.demoted` | 로직-03 강등 | **인앱 카드만**, 푸시 X | 사용자 | FR-015 (부정 알림 회피) |
| `daily.09kst.tick` | 09:00 KST 스케줄러 (API-22) | 직전 24h 미예측 사용자 조회 → 푸시 jitter 큐 | 사용자 | FR-014 |
| `community.post.auto_hidden` | reportCount ≥ 3 | 운영자 검토 큐 + 모더레이션 알림 | 운영 | FR-005, R-09 |
| `card.channel.unhealthy` | circuit breaker OPEN | 그라파나 알람 | 운영 | NFR 9-3 |
| `featureflag.changed` | 운영자 토글 | 캐시 무효화 + 감사 로그 | 운영 | R-01, R-02 |
| `external.budget.threshold` | X/Glassnode/Dune 비용 임계 | 운영 알림 + 정책 적용 (폴링 감속, 차단) | 운영 | R-02 |

---

## §9. BE 결정 필요 사항

| # | 항목 | 맥락 (기획서 근거) | 선택지 |
|---|------|-----------------|--------|
| D-01 | 데이터베이스 종류 (Prediction, TierAssignment 등) | NFR 30K RPS, 90일 윈도우 집계, 트랜잭션 (FR-001) | RDB(PostgreSQL/MySQL) vs RDB+읽기 전용 복제, 집계만 OLAP |
| D-02 | 카드 캐시 저장소 | 8채널 TTL, single-flight, NFR 카드 99.0% (NFR 9-2) | Redis vs Memcached vs 인메모리+Redis 2티어 |
| D-03 | 메시지 큐 (예측·결산·푸시) | 30K RPS, 백프레셔, 결산 워커 동시성 (NFR 9-1, R-05) | Kafka vs SQS vs Redis Stream |
| D-04 | 결산 스케줄러 | 사용자별·코인별 롤링 마감 (FR-001), +5분 SLO | Cron + 워커 / Quartz / 자체 시간 휠 |
| D-05 | 라이트락 / 백프레셔 임계값 | 30K RPS 산출 검증 (리뷰 노트 BE) | 부하 테스트 결과로 확정 |
| D-06 | 다중 시세 소스 선택 (3개) | FR-001 다중 소스, R-06 | 업비트 + CoinGecko + Binance(KRW 환산) 등 |
| D-07 | 티어 임계 히스테리시스 | FR-002 임계 진동 (리뷰 노트 QA) | ±1%p 버퍼 / 일 1회 평가 / 무 히스테리시스 |
| D-08 | 푸시 일일 한도 | Q-05 (FR-014) | 사용자당 일 N회 + 우선순위 |
| D-09 | 신고/스팸 봇 레이트리밋 임계 | 리뷰 노트 BE | API별 분당 N회 |
| D-10 | 동률(↑=↓=15) 처리 (리더보드) | qa-spec 이관 (FR-006) | UP 우선 표기 / NEUTRAL 표기 |
| D-11 | INVALID 케이스 결과 화면 카피 | FR-001 동가/괴리 무효 (8-6 카피 일부만 정의) | "무효 처리됨" 텍스트 + 사유 노출 |
| D-12 | X API Tier 선택 | Q-03 | Pro($5K) vs Enterprise |
| D-13 | 자체 커뮤니티 신규 vs 기존 모듈 통합 | Q-08 | 신규 / 통합 / P1 강등 |
| D-14 | 외부 API 부분 장애 시 폴리마켓 Plan B 자동/수동 토글 | R-01 | 자동 (실패율 임계 자동 OFF) / 수동 |
| D-15 | 다중 코인 동시 등록 동시성 보장 방식 | qa-spec 이관 | 별도 트랜잭션 / 단일 트랜잭션 |

---

## §10. 자체 리뷰 (Phase 3)

스킬 가이드의 체크리스트 11개 항목으로 자체 검증.

| # | 체크 | 결과 | 비고 |
|---|------|------|------|
| 1 | PRD의 모든 FR이 최소 1개 API에 매핑되는가? | PASS | FR-001→API-01~04, FR-002→API-07/08, FR-003→API-05/06, FR-004~009→API-06 채널별, FR-010→API-04 + 푸시, FR-011→API-04/23, FR-012/013→API-25/24/06, FR-014→API-22, FR-015→§8 이벤트 |
| 2 | 모든 비즈니스 규칙이 §2 또는 §4에 반영? | PASS | 24h 롤링/원 단위 동가/5%+ 괴리/다중 소스/idempotency/jitter/30명 임계/100 멘션 임계/3건 자동 가림/30분 라이트락 모두 포함 |
| 3 | 모든 엣지 케이스가 에러 응답 또는 로직 예외에 반영? | PASS | KYC 미통과(403), 중복 예측(409), idempotency(409), 시세 실패(422), 라이트락(503), 시나리오 6 카드 격리, INVALID_TIE/INVALID_PRICE 모두 포함 |
| 4 | 동시성 시나리오가 §7에 있는가? | PASS | R-05/R-06/R-07 + 리뷰 노트 BE 9건 모두 반영 |
| 5 | 외부 연동의 장애 대응이 §5에 있는가? | PASS | 채널별 폴백 + circuit breaker + Plan B + 비용 임계 알람 |
| 6 | 비기능 요구사항이 §6에 그대로 있는가? | PASS | NFR 9-1~9-4 + 백프레셔/모니터링 보강 |
| 7 | 데이터 모델이 API 요청/응답과 일관성? | PASS | Prediction.snapshotPriceKrwRounded ↔ API-01 응답, PredictionChannelSnapshot ↔ API-23, TierAssignment ↔ API-07 등 정합 |
| 8 | 기획서에 없는 기능을 임의로 추가하지 않았는가? | PASS | 추가 항목은 모두 `[BE 제안]` 또는 `[BE 결정 필요]` 표기 |
| 9 | 기술 스택을 확정하지 않았는가? | PASS | DB/큐/캐시 선택은 §9 D-01~D-04로 분리 |
| 10 | 모든 "제안" 항목에 (제안) 또는 [BE 제안] 표기? | PASS | 엔드포인트/타입/제약/TTL/임계값 모두 표기 |
| 11 | 모든 도출 항목에 근거(FR/PRD 참조) 있는가? | PASS | API별, 데이터 모델별, 로직별 "도출 근거" 명시 |

**메모리 규칙 준수 체크**:
- [x] 보안 기준선(KMS·펜테스트·토큰 회전 디테일) 미포함 — 인증 흐름은 KYC/≥19 게이트 + idempotency만 명시.
- [x] 일정/스토리 포인트 미포함.
- [x] 기술 스택 확정 안 함.

**리뷰 노트 BE 이관 항목 처리**:
- [x] P95/P99 분리 → §6-1
- [x] 채널별 캐시 TTL 표 → §3 CardCache + §5
- [x] 라이트락 윈도우, idempotency key 스펙 → API-01 + 로직-01
- [x] 채널 비용 산정 → §5 비고 + R-02 알람
- [x] 신고/스팸 봇 레이트리밋 → API-09/12 + D-09
- [x] 30K RPS 산출 근거 → §6-1 비고

**자체 평가**: **PASS** (체크리스트 11/11 + 메모리 규칙 + 이관 항목 모두 충족).

---

## 변경 로그

| 날짜 | 유형 | 대상 | 변경 내용 | 사유 |
|------|------|------|----------|------|
| 2026-04-30 | ADD | 전체 | 신규 작성 (PRD 블록 1~4 + 리뷰 노트 BE 이관 항목 반영) | be-spec 스킬 1차 핸드오프 |

# 다이어그램 연동 가이드 (Diagram Integration Guide)

SKILL.md의 Step 5에서 참조됩니다.
다이어그램 생성은 `diagram-design` 스킬에 위임합니다.

## 연동 방식

product-spec 스킬은 다이어그램을 직접 생성하지 않습니다.
대신 `diagram-design` 스킬(cathrynlavery/diagram-design)을 호출하여 생성합니다.

### 호출 규칙

1. 다이어그램이 필요한 시점에 diagram-design 스킬의 규칙에 따라 HTML+SVG를 생성
2. **모든 레이블과 텍스트는 한국어**로 작성 (기술 용어만 영문 허용)
3. 파일명은 `{spec-name}-{diagram-type}.html` 형식으로 기획서와 같은 디렉토리에 저장

### 한국어 변환 규칙

diagram-design 스킬 사용 시 다음을 적용:
- 노드 레이블: 한국어 기본 (예: "결제 서비스", "사용자 인증")
- 축 레이블: 한국어 (예: "영향도", "구현 난이도")
- 범례: 한국어 (예: "동기 호출", "비동기 응답")
- 기술 용어: 영문 유지 가능 (예: "API Gateway", "Redis", "PostgreSQL")
- 상태명: 한국어 (예: "대기중", "처리중", "완료", "실패")

## 기획서 타입별 자동 선택 매트릭스

| 기획서 타입 | 자동 생성 다이어그램 |
|------------|-------------------|
| PRD | architecture + flowchart + timeline |
| 기능 명세서 | sequence + state + flowchart |
| 유저 스토리 | swimlane + flowchart |
| 기술 명세서 | architecture + er + sequence + layers |

## 다이어그램 삽입 위치

### PRD
- **시스템 개요** 직후 → architecture 다이어그램
- **사용자 시나리오** 직후 → flowchart 다이어그램
- **일정 및 마일스톤** 직후 → timeline 다이어그램

### 기능 명세서
- **기능 흐름** 설명 직후 → flowchart 다이어그램
- **시스템 상호작용** 설명 직후 → sequence 다이어그램
- **상태 관리** 설명 직후 → state 다이어그램

### 유저 스토리
- **전체 흐름** 설명 직후 → swimlane 다이어그램
- **개별 스토리 흐름** → flowchart 다이어그램

### 기술 명세서
- **아키텍처 설계** 직후 → architecture 다이어그램
- **데이터 모델** 직후 → er 다이어그램
- **API 호출 흐름** 직후 → sequence 다이어그램
- **기술 스택** 설명 직후 → layers 다이어그램

## 추가 다이어그램 요청 시

사용자가 매트릭스 외 다이어그램을 요청할 수 있습니다:
- "우선순위 매트릭스 그려줘" → quadrant (사분면)
- "사용자 퍼널 보여줘" → pyramid (피라미드/퍼널)
- "팀 간 역할 분담 보여줘" → swimlane (스윔레인)
- "모듈 구조 보여줘" → nested (중첩)
- "기능 겹침 보여줘" → venn (벤 다이어그램)
- "경쟁사 비교" → consultant 2×2 (컨설턴트 2x2)

이 경우 diagram-design 스킬의 해당 타입 규칙에 따라 생성합니다.

---
name: preview
description: >
  프로젝트의 디자인(.html)과 다이어그램을 갤러리 형태로 브라우저에서 미리보기.
  자체 내장 서버로 외부 의존성 없이 실행됩니다.
  "프리뷰", "디자인 보여줘", "서버 띄워", "갤러리" 등의 요청에 반응합니다.
argument-hint: "[--stop]"
best_for:
  - 디자인 HTML 미리보기
  - 다이어그램 브라우징
  - 디자인 리뷰
scenarios:
  - "프리뷰"
  - "디자인 보여줘"
  - "서버 띄워"
  - "--stop"
estimated_time: "10초"
---

# Preview (디자인 갤러리 서버)

프로젝트의 HTML 디자인 파일과 다이어그램을 갤러리 형태로 볼 수 있는 서버를 띄웁니다.

## 핵심 원칙

- **외부 의존성 없음**: Vite, npm install 불필요. Node.js만 있으면 동작.
- **프로젝트 오염 없음**: package.json, vite.config.js를 건드리지 않음.
- **자체 내장 서버**: `scripts/server.cjs`가 HTTP + WebSocket 서버를 직접 구동.
- **자동 새로고침**: 파일 변경 시 WebSocket으로 브라우저 자동 리로드.

## 파일 구조

서버가 스캔하는 산출물 위치:
```
docs/specs/{기능명}/
├── designs/*.html      ← design-ko 산출물
└── diagrams/*.html     ← diagram-design 산출물
```

서버 상태 파일 (자동 생성, `.gitignore` 추가 필요):
```
.preview-server/
├── server.pid
├── server.log
├── server-info          ← JSON (port, url 등)
└── server-stopped       ← 종료 시 생성
```

## 실행 순서

### 서버 시작 (`--stop`이 아닌 경우)

1. **서버 시작**:
   ```bash
   skills/preview/scripts/start-server.sh --project-dir $PROJECT_DIR
   ```
   반환 JSON:
   ```json
   {"type":"server-started","port":52341,"url":"http://localhost:52341","project_dir":"/path","file_count":5}
   ```

2. **URL 안내**: 사용자에게 반환된 URL을 안내한다.

3. **`.gitignore` 확인**: `.preview-server/`가 `.gitignore`에 없으면 추가한다.

갤러리 페이지 기능:
- **다크 테마** 기본
- **카드 그리드**: 각 HTML 파일을 카드로 표시 (파일명, 기능명, 카테고리 배지, 수정 시각)
- **카테고리 필터**: 전체 / Design / Diagram / 기능별
- **클릭** → 해당 HTML을 새 탭으로 열기
- **자동 새로고침**: 파일 추가/수정 시 WebSocket으로 갤러리 자동 갱신

### 서버 중지 (`--stop`)

```bash
skills/preview/scripts/stop-server.sh $PROJECT_DIR
```

## 서버 이미 실행 중일 때

`.preview-server/server-info` 파일이 있고, 해당 PID가 살아있으면:
- 재시작하지 않고 기존 URL만 읽어서 안내한다.
- 파일에서 URL을 읽는 방법: `cat $PROJECT_DIR/.preview-server/server-info`

## 규칙

- `docs/specs/` 디렉토리가 없으면 빈 갤러리를 표시한다 (에러 아님).
- 서버는 1시간 비활성 시 자동 종료된다.
- 프로젝트 루트의 `package.json`, `vite.config.js` 등을 절대 수정하지 않는다.

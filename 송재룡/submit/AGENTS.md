# Agent Rules

## 먼저 볼 것
- 제품 의도와 사용자-facing 동작은 `docs/project-brief.md`, `docs/product-spec.md`를 먼저 확인한다.
- 모듈 경계와 실행 흐름은 `docs/architecture.md`와 실제 진입점 `src/market_agent/main.py`를 기준으로 맞춘다.
- 시장/뉴스 연동 변경 전 `docs/data-sources.md`, 리포트 변경 전 `docs/report-contract.md`, scoring 변경 전 `docs/scoring-policy.md`를 확인한다.

## 실행 명령
- Setup: `uv sync`.
- 전체 테스트: `uv run pytest`.
- 단일 테스트 파일/케이스: `uv run pytest tests/test_reports.py` 또는 `uv run pytest tests/test_reports.py::test_premarket_report_includes_required_metadata`.
- 로컬 CLI: `uv run market-agent premarket`, `uv run market-agent hourly`, `uv run market-agent closing`, `uv run market-agent scheduler`.

## 구조와 상태
- Package는 `src/market_agent`, 테스트는 `tests`; `pyproject.toml`의 `pythonpath = ["src"]` 설정에 의존한다.
- CLI는 기본적으로 `MockMarketDataClient`를 쓰며, `MARKET_AGENT_MARKET_DATA_PROVIDER=finance-data-reader`일 때 국내 전일 지수 context만 `FinanceDataReaderKoreaMarketDataClient`로 가져온다.
- News는 기본적으로 `MockNewsClient`를 쓰며, `MARKET_AGENT_NEWS_PROVIDER=naver`일 때 `NaverNewsClient`를 사용한다.
- 기본 DB는 `.data/market_agent.sqlite3`; `Repository`가 SQLite schema를 직접 생성한다.
- 설정은 `MARKET_AGENT_` prefix와 `.env`를 사용하며, secret은 읽거나 commit하지 않는다.

## 제품 제약
- 실제 거래, broker 주문, 계좌 변경 기능은 구현하지 않는다.
- 출력은 투자 조언이 아니라 참고용 관찰 후보/리서치 정보로 표현한다.
- Live data를 지어내지 말고 mock/live label, source name, data timestamp를 유지한다.
- Schedule과 report 시간 의미는 `Asia/Seoul`; 정규장 tracking은 09:00-15:30 KST, closing summary는 15:35 KST다.
- Telegram은 기본 `dry_run=True`; dry-run 해제 시 token/chat id가 없으면 실패해야 한다.

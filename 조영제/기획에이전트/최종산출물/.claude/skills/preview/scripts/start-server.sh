#!/usr/bin/env bash
# Start the preview gallery server
# Usage: start-server.sh --project-dir <path> [--host <bind-host>] [--url-host <display-host>] [--foreground]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PROJECT_DIR=""
FOREGROUND="false"
FORCE_BACKGROUND="false"
BIND_HOST="127.0.0.1"
URL_HOST=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --host)
      BIND_HOST="$2"
      shift 2
      ;;
    --url-host)
      URL_HOST="$2"
      shift 2
      ;;
    --foreground|--no-daemon)
      FOREGROUND="true"
      shift
      ;;
    --background|--daemon)
      FORCE_BACKGROUND="true"
      shift
      ;;
    *)
      echo "{\"error\": \"Unknown argument: $1\"}"
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_DIR" ]]; then
  echo '{"error": "Usage: start-server.sh --project-dir <path>"}'
  exit 1
fi

if [[ -z "$URL_HOST" ]]; then
  if [[ "$BIND_HOST" == "127.0.0.1" || "$BIND_HOST" == "localhost" ]]; then
    URL_HOST="localhost"
  else
    URL_HOST="$BIND_HOST"
  fi
fi

# Auto-foreground for environments that reap background processes
if [[ -n "${CODEX_CI:-}" && "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  FOREGROUND="true"
fi
if [[ "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  case "${OSTYPE:-}" in
    msys*|cygwin*|mingw*) FOREGROUND="true" ;;
  esac
  if [[ -n "${MSYSTEM:-}" ]]; then
    FOREGROUND="true"
  fi
fi

STATE_DIR="${PROJECT_DIR}/.preview-server"
PID_FILE="${STATE_DIR}/server.pid"
LOG_FILE="${STATE_DIR}/server.log"

mkdir -p "$STATE_DIR"

# Kill existing server
if [[ -f "$PID_FILE" ]]; then
  old_pid=$(cat "$PID_FILE")
  kill "$old_pid" 2>/dev/null
  rm -f "$PID_FILE"
fi

cd "$SCRIPT_DIR"

# Resolve owner PID
OWNER_PID="$(ps -o ppid= -p "$PPID" 2>/dev/null | tr -d ' ')"
if [[ -z "$OWNER_PID" || "$OWNER_PID" == "1" ]]; then
  OWNER_PID="$PPID"
fi

if [[ "$FOREGROUND" == "true" ]]; then
  echo "$$" > "$PID_FILE"
  env PREVIEW_PROJECT_DIR="$PROJECT_DIR" PREVIEW_STATE_DIR="$STATE_DIR" \
      PREVIEW_HOST="$BIND_HOST" PREVIEW_URL_HOST="$URL_HOST" \
      PREVIEW_OWNER_PID="$OWNER_PID" \
      node server.cjs
  exit $?
fi

nohup env PREVIEW_PROJECT_DIR="$PROJECT_DIR" PREVIEW_STATE_DIR="$STATE_DIR" \
    PREVIEW_HOST="$BIND_HOST" PREVIEW_URL_HOST="$URL_HOST" \
    PREVIEW_OWNER_PID="$OWNER_PID" \
    node server.cjs > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
disown "$SERVER_PID" 2>/dev/null
echo "$SERVER_PID" > "$PID_FILE"

# Wait for startup
for i in {1..50}; do
  if grep -q "server-started" "$LOG_FILE" 2>/dev/null; then
    alive="true"
    for _ in {1..20}; do
      if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        alive="false"
        break
      fi
      sleep 0.1
    done
    if [[ "$alive" != "true" ]]; then
      echo "{\"error\": \"Server started but was killed. Retry with --foreground\"}"
      exit 1
    fi
    grep "server-started" "$LOG_FILE" | head -1
    exit 0
  fi
  sleep 0.1
done

echo '{"error": "Server failed to start within 5 seconds"}'
exit 1

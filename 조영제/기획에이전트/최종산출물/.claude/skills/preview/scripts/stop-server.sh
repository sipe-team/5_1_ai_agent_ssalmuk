#!/usr/bin/env bash
# Stop the preview gallery server
# Usage: stop-server.sh <project-dir>

PROJECT_DIR="$1"

if [[ -z "$PROJECT_DIR" ]]; then
  echo '{"error": "Usage: stop-server.sh <project-dir>"}'
  exit 1
fi

STATE_DIR="${PROJECT_DIR}/.preview-server"
PID_FILE="${STATE_DIR}/server.pid"

if [[ -f "$PID_FILE" ]]; then
  pid=$(cat "$PID_FILE")
  kill "$pid" 2>/dev/null || true

  for i in {1..20}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.1
  done

  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
    sleep 0.1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    echo '{"status": "failed", "error": "process still running"}'
    exit 1
  fi

  rm -f "$PID_FILE" "${STATE_DIR}/server.log"
  echo '{"status": "stopped"}'
else
  echo '{"status": "not_running"}'
fi

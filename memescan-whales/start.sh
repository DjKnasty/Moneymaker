#!/bin/bash
# Start the 60-second whale watcher if it is not already running.
# Inherits HELIUS_API_KEY from the environment; does not write or echo it.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$DIR/watch_whales.pid"
LOG="$DIR/watch.log"
PY="${PYTHON:-/usr/bin/python3}"

mkdir -p "$DIR"
cd "$DIR"

if [[ -z "${HELIUS_API_KEY:-}" ]]; then
  echo "HELIUS_API_KEY is not set in the environment; refusing to start" >&2
  exit 1
fi

if [[ -f "$PIDFILE" ]]; then
  PID="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "whale watcher already running (pid $PID)"
    exit 0
  fi
  rm -f "$PIDFILE"
fi

# Export only for the child; do not print the value.
export HELIUS_API_KEY
unset WHALE_LOG_STDOUT || true
nohup bash -c "
  while true; do
    $PY -u '$DIR/watch_whales.py' --loop >> '$LOG' 2>&1
    code=\$?
    if [[ -f '$DIR/STOP' ]]; then
      rm -f '$DIR/STOP'
      exit 0
    fi
    echo \"\$(date -Iseconds) wrapper: loop exited \$code, restarting in 10s\" >> '$LOG'
    sleep 10
  done
" >> "$LOG" 2>&1 &
echo $! > "$DIR/wrapper.pid"
sleep 0.4
echo "started whale-watcher wrapper pid $(cat "$DIR/wrapper.pid") log $LOG"

#!/bin/bash
# Start the 15-minute memescan-lite loop if it is not already running.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$DIR/scan_lite.pid"
LOG="$DIR/scan.log"
PY="${PYTHON:-/usr/bin/python3}"

mkdir -p "$DIR"
cd "$DIR"

if [[ -f "$PIDFILE" ]]; then
  PID="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "memescan-lite already running (pid $PID)"
    exit 0
  fi
  rm -f "$PIDFILE"
fi

nohup bash -c "
  while true; do
    $PY -u '$DIR/run_loop.py' >> '$LOG' 2>&1
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
echo "started memescan-lite wrapper pid $(cat "$DIR/wrapper.pid") log $LOG"

#!/bin/bash
# Stop the 15-minute memescan-lite loop.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
touch "$DIR/STOP"
for f in wrapper.pid scan_lite.pid; do
  if [[ -f "$DIR/$f" ]]; then
    PID="$(cat "$DIR/$f" 2>/dev/null || true)"
    if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
      kill "$PID" 2>/dev/null || true
      for i in 1 2 3 4 5; do
        kill -0 "$PID" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$PID" 2>/dev/null || true
      echo "stopped $f pid $PID"
    fi
    rm -f "$DIR/$f"
  fi
done
pkill -f "$DIR/run_loop.py" 2>/dev/null || true
rm -f "$DIR/STOP"
echo "memescan-lite stopped"

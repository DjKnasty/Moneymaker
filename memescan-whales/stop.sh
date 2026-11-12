#!/bin/bash
# Stop the 60-second whale watcher.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
touch "$DIR/STOP"
for f in wrapper.pid watch_whales.pid; do
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
pkill -f "$DIR/watch_whales.py" 2>/dev/null || true
rm -f "$DIR/STOP"
echo "whale watcher stopped"

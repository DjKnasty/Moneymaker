#!/usr/bin/env python3
"""Resilient 15-minute scheduler for scan_lite.py.

Runs every 15 minutes, 24/7, America/New_York clock times.
No crontab required. Restarted by start.sh if the process dies.
Read-only: never trades or touches a wallet.
"""
from __future__ import annotations

import os
import sys
import time
import signal
import datetime as dt
import traceback
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ET = ZoneInfo("America/New_York")
PID_FILE = BASE / "scan_lite.pid"
LOG = BASE / "scan.log"
INTERVAL_MIN = 15

sys.path.insert(0, str(BASE))
import scan_lite  # noqa: E402

_stop = False


def log(msg):
    # start.sh redirects stdout/stderr to scan.log; print only so lines are not doubled.
    print(msg, flush=True)


def now_et():
    return dt.datetime.now(ET)


def next_slot(t):
    """Next 15-minute clock time (00/15/30/45), 24/7, possibly tomorrow."""
    raw = t.replace(second=0, microsecond=0)
    remainder = raw.minute % INTERVAL_MIN
    if remainder or t.second or t.microsecond:
        add = INTERVAL_MIN - remainder if remainder else INTERVAL_MIN
        raw = raw + dt.timedelta(minutes=add)
        raw = raw.replace(second=0, microsecond=0)
    return raw


def handle_stop(signum, frame):
    global _stop
    _stop = True
    log(f"{now_et().isoformat(timespec='seconds')} loop received signal {signum}, stopping")


def write_pid():
    PID_FILE.write_text(str(os.getpid()))


def clear_pid():
    try:
        if PID_FILE.exists() and PID_FILE.read_text().strip() == str(os.getpid()):
            PID_FILE.unlink()
    except Exception:
        pass


def main():
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    write_pid()
    log(f"{now_et().isoformat(timespec='seconds')} loop started pid={os.getpid()}")
    try:
        while not _stop:
            t = now_et()
            nxt = next_slot(t)
            wait = max(0.0, (nxt - t).total_seconds())
            end = time.time() + wait
            while not _stop and time.time() < end:
                time.sleep(min(5.0, max(0.1, end - time.time())))
            if _stop:
                break
            try:
                scan_lite.load_dotenv()
                scan_lite.run(post=True)
            except Exception:
                log(f"{now_et().isoformat(timespec='seconds')} loop run error:\n{traceback.format_exc()}")
                time.sleep(5)
    finally:
        clear_pid()
        log(f"{now_et().isoformat(timespec='seconds')} loop stopped")


if __name__ == "__main__":
    sys.exit(main() or 0)

# memescan-lite

Lightweight Solana meme-coin scanner. It uses no LLM calls and no bot usage.
Read-only: it never signs a transaction, never touches a wallet, and never trades.

Live path on the box: `/workspace/memescan/lite/`.

This copy also lives in `DjKnasty/Moneymaker` under `memescan-lite/`.

## Change log

- 2026-11-11: market cap gate removed (no lower or upper bound). All other gates unchanged.

## What it does

Every 15 minutes, 24/7 (America/New_York clock), a free local script:

1. Pulls high-volume Solana pools from GeckoTerminal and overlays DexScreener mcap, liquidity, volume, and price.
2. Applies cheap gates first (screener data, then candles, then adjusted top-10):
   - liquidity $150K–$1M
   - 24-hour volume at least $1.5M and 7–20x liquidity
   - at least 12 hourly candles (skips tokens younger than 12 hours without a candle fetch)
   - adjusted top-10 holders at or under 30%, excluding pool and AMM vaults
3. Only coins that pass every cheap gate get anti-rug and hidden-fee checks, using the public RugCheck API (api.rugcheck.xyz token report) plus a read-only Solana RPC mint read:
   - mint and freeze authority revoked
   - LP locked or burned (at least 90% on the primary pool)
   - no honeypot
   - trading not paused
   - tax under 5% (pool-reported and on-chain Token-2022)
   - no proxy or live fee authority
   - no RugCheck danger-level risks or rugged=true
4. If `/workspace/memescan/lite/POSITION_OPEN` exists, the run is skipped (the one-minute open-trade watcher is in charge).
5. Coins already alerted in the last 6 hours are deduped (`alerted.json`).
6. Only when at least one new coin passes everything does the script POST a compact JSON payload to `WEALTH_WEBHOOK_URL`, with `WEALTH_WEBHOOK_KEY` sent as an `Authorization: Bearer` header and also as `x-webhook-key`. If those env vars are missing, it logs and skips the POST. Values are read from `/workspace/memescan/lite/.env` when that file is present.
7. Each run appends one line to `scan.log` with counts at each stage and the runtime.

## Schedule

`cron` is not available on this box, so a resilient `nohup` loop is used:

- `start.sh` starts a wrapper (pid in `wrapper.pid`) that keeps `run_loop.py` alive (`scan_lite.pid`).
- `stop.sh` stops both.
- The loop sleeps until the next :00 / :15 / :30 / :45 America/New_York clock time, every hour of every day.

Start and stop:

    /workspace/memescan/lite/start.sh
    /workspace/memescan/lite/stop.sh

## Manual run

One scan. POST is skipped automatically if `.env` / webhook env is unset, or when `--no-post` is passed:

    /usr/bin/python3 /workspace/memescan/lite/scan_lite.py --once --no-post

## Webhook env

Copy `.env.example` to `.env` and set `WEALTH_WEBHOOK_URL` and `WEALTH_WEBHOOK_KEY`.
`.env` is gitignored. Do not put secrets in the repo or print the key into `scan.log`.

Payload shape: a JSON object with `timestamp` and `passers`. Each passer has `mint`, `symbol`, `price`, `mcap`, `liq`, `vol`, `checks` (mint/freeze/lp_pct/honeypot/paused/tax_pct/fee_authority/adj10/rugcheck_dangers), and `timestamp`.

## Pause while a position is open

    touch /workspace/memescan/lite/POSITION_OPEN
    rm /workspace/memescan/lite/POSITION_OPEN

# memescan-lite

Lightweight Solana meme-coin scanner. It uses no LLM calls and no bot usage.
Read-only: it never signs a transaction, never touches a wallet, and never trades.

Live path on the box: `/workspace/memescan/lite/`.

This copy also lives in `DjKnasty/Moneymaker` under `memescan-lite/`.

## Change log

- 2026-11-11: social-presence gate added after the liquidity/volume gates and before candles/anti-rug. A coin needs at least one X/Twitter or Telegram link (website is a bonus). `social_score` is 0–3 (X, Telegram, website). Generic or status X URLs, and X links reused across mints in the same scan, are flagged but not gated. If DexScreener and Pump.fun both error, the coin is logged as `social_unknown` and fails closed. Socials are cached per mint per run and written to the webhook payload and `shadow_log.jsonl`.
- 2026-11-11: two-lane cheap filters approved and shipped. Lane 1 (aged) and Lane 2 (fresh) replace the single-lane $150K–$1M / $1.5M vol / 7–20x vol-liq / 12-candle / adj-top-10 gate set. Market cap stays info-only. Adj top-10 is shadow-logged, not a gate. New-pools feed added. Shadow log and risk rules added.
- 2026-11-11: market cap gate removed (no lower or upper bound).

## What it does

Every 15 minutes, 24/7 (America/New_York clock), a free local script:

1. Pulls high-volume and trending Solana pools from GeckoTerminal, plus a new-pools feed (GeckoTerminal `/networks/solana/new_pools` and DexScreener latest token profiles), and overlays DexScreener mcap, liquidity, volume, price, and pair age.
2. Assigns each coin to a lane and applies cheap gates (screener data, then social presence, then candles). Market cap is recorded but is not a gate. The old 7–20x volume/liquidity gate is gone.
   - Lane 1 (aged): at least 12 hourly candles, 24-hour volume at least $250K, volume/mcap at least 0.4, liquidity $50K–$2.0M.
   - Lane 2 (fresh): pool age 15 minutes to 12 hours, at least 1 hourly candle, 24-hour volume at least $100K, volume/mcap at least 0.5, liquidity at least $50K (no upper bound).
   - Social gate (after liquidity/volume, before candles and anti-rug): at least one X/Twitter or Telegram link, using DexScreener `info.socials` / `info.websites` (already fetched in the overlay) with Pump.fun coin metadata as a fallback. Website is a bonus and is not enough on its own. `social_score` is 0–3 (X, Telegram, website). A generic or status X URL, or an X link reused by more than one mint in the same scan, is flagged but still allowed. If the social APIs error and presence cannot be determined, the coin is logged as `social_unknown` and fails the gate.
   - Adjusted top-10 holders is computed and shadow-logged only (not a gate). A value over 30% is flagged in the log, then the coin still goes to anti-rug.
3. Only coins that pass the cheap lane gates and the social gate get anti-rug and hidden-fee checks, using the public RugCheck API (api.rugcheck.xyz token report) plus a read-only Solana RPC mint read:
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
7. Each run appends one line to `scan.log` with counts at each stage (including a `social` stage in the per-lane funnel: candidates/liq/vol/social/candles/antirug) and the runtime.
8. Each run appends one record per collected candidate to `shadow_log.jsonl` (liquidity, holders, top-10, socials, social_score, lane, pass/fail reasons) so the liquidity band can be re-derived in 2–3 weeks.

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

Payload shape: a JSON object with `timestamp` and `passers`. Each passer has `mint`, `symbol`, `price`, `mcap`, `liq`, `vol`, `lane` (`l1` or `l2`), `socials` (`twitter`, `telegram`, `website`), `social_score` (0–3), `checks` (mint/freeze/lp_pct/honeypot/paused/tax_pct/fee_authority/adj10/rugcheck_dangers), and `timestamp`.

## Shadow log

`shadow_log.jsonl` is gitignored runtime data. One JSON object per collected coin per run, with `liq`, `holders`, `raw10`, `adj10`, `socials`, `social_score`, `social_flags`, `lane`, `passed`, `status`, and `reasons`. A social miss is `status=social_fail` or `social_unknown`. Use it after 2–3 weeks to re-derive the liquidity band and to review the 30% top-10 flag. Do not treat current holders or top-10 as pre-breakout values.

## Risk rules

See `risk_rules.json` for the canonical copy. Summary:

- **Sizing:** risk per trade is 10% of current closed-trade equity, capped at $40. Size only from closed equity, never after a win streak.
- **Drawdown:** track high-water mark (HWM) of wallet equity. 20% below HWM: halve risk per trade. 35% below HWM: pause new entries and ask Thomas. 3 straight stops, or $40 lost in a calendar day (America/New_York): stop entering for the rest of that day.
- **Filters:** re-check monthly (rerun the breakout study on the latest 30 days). Volume, turnover, candle/age, and the liquidity band are the gates most likely to decay.

If `trades.jsonl` is present, compute the current risk state with:

    /usr/bin/python3 /workspace/memescan/lite/risk_state.py

Expected `trades.jsonl` fields (one closed trade per line): `pnl` or `pnl_usd`, optional `equity` / `equity_after` / `closed_equity`, `result` or `outcome` (`stop`, `tp`, `win`, `loss`), and `ts` / `timestamp` / `closed_at` (ISO). The helper writes `risk_state.json` (gitignored) and prints a summary. If `trades.jsonl` does not exist yet, it reports the rules and "no trades yet".

This helper only reads logs. It does not place trades or touch a wallet.

## Pause while a position is open

    touch /workspace/memescan/lite/POSITION_OPEN
    rm /workspace/memescan/lite/POSITION_OPEN

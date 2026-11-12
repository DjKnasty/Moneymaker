# memescan-whales

Read-only Solana whale-wallet watcher. It never signs a transaction, never touches a wallet, and never trades.

Live path on the box: `/workspace/memescan/whales/`.

This copy also lives in `DjKnasty/Moneymaker` under `memescan-whales/`.

When a tracked wallet buys a still-early meme coin, the script POSTs a `source: "whale"` payload to the same Wealth Creation webhook used by memescan-lite (`Solana scanner passer alert`). That routine runs the live entry, safety and social checks, and is the only thing that may trade.

## Wallets

See `wallets.json` for the 7 tracked addresses, why each was chosen, all-time / 30-day PnL evidence, and typical buy size.

Selection (2026-11-12):

- Public GMGN smart-money / KOL leaderboards, then verified on-chain with Helius.
- Profitable meme-coin trading over roughly the last year (all-time realized profit well above the last 30 days, plus Helius activity in a window 10–13 months ago and a mid-year window).
- Real traders: not tagged `snipe_bot`, `fresh_wallet`, `top_dev`, or `wash_trader`; not contracts / CEX / AMM vaults; not hundreds of trades per day; not one-hit wonders.

## Loop

A single 60-second loop (no extra watchers):

1. `getSignaturesForAddress` for each wallet (until the last-seen cursor). Only new signatures are parsed, in batches, via the Helius enhanced transactions API.
2. Detect SWAP (and SWAP-like) buys of non-major SPL tokens, paid in SOL or USDC, of at least about 1 SOL. The wallet must be the fee payer or have a real token/SOL balance change (referral / incidental appearances are ignored).
3. Enrich new candidate mints with DexScreener (market cap, liquidity, pool age, 1h and 24h change) — only for those buys.
4. "Good price" filter: market cap under $5M, liquidity at least $50K, liquidity ÷ market cap at least 0.03, 1h change under +30%, 24h change under +150%. SOL, stables and majors are skipped.
5. Priority is raised when 2 or more tracked wallets buy the same token within 2 hours.
6. Quick RugCheck pre-check for mint and freeze authority (attached to the payload; the trading routine still runs the full anti-rug stack).
7. Deduped: one webhook alert per token per 6 hours, unless a new tracked wallet joins.
8. If `/workspace/memescan/lite/POSITION_OPEN` exists, the buy is still logged but the webhook is not POSTed.
9. Every detection, filter miss, dedupe and alert is appended to `alerts.jsonl`. Cycle summaries go to `watch.log`. Neither file is committed. The Helius key is never logged.

## Start and stop

`cron` is not available on this box, so a resilient `nohup` wrapper is used, the same pattern as memescan-lite.

`HELIUS_API_KEY` must already be in the process environment. It is not stored in a file.

    /workspace/memescan/whales/start.sh
    /workspace/memescan/whales/stop.sh

Manual one-shot and 24-hour backfill (never POSTs the backfill):

    /usr/bin/python3 /workspace/memescan/whales/watch_whales.py --backfill-hours 24 --no-post
    /usr/bin/python3 /workspace/memescan/whales/watch_whales.py --once --no-post

## Webhook

The watcher reads `WEALTH_WEBHOOK_URL` and `WEALTH_WEBHOOK_KEY` from the environment, or from `/workspace/memescan/lite/.env` (same as the lite scanner). Values are not printed.

Payload shape: a JSON object with `timestamp` and `passers`. Each passer reuses the lite fields (`mint`, `symbol`, `price`, `mcap`, `liq`, `vol`, `checks`, `timestamp`) and adds `source: "whale"`, `wallets` (address, buy size in SOL, tx signature, price paid), `tx_signature`, `buy_size_sol`, `priority` (`normal` or `multi`), `change_1h`, `change_24h`, `pool_age_hours`, and `liq_over_mcap`.

## Rate limits

Free Helius usage is kept to one `getSignaturesForAddress` per wallet per minute, plus parse / DexScreener / RugCheck only when there is a new candidate buy. The loop backs off on HTTP 429. Request and 429 counts are stored in `state.json` (gitignored). See the run report for credit-headroom notes.

## Safety

This process has no trading authority. It must never call Phantom buy or send tools and must never touch a wallet.

# Callout tracking (OnlyBands pinned channels)

`track.py` produces the running record. Two inputs:

1. `raw/*.jsonl` — long history already harvested (Jaycee, Hipp's QQQ, Teej, Bucky).
2. `inbox/*.jsonl` — drop new messages here, named `<channel-name>.jsonl` (anything starting with the
   channel slug works, e.g. `odte-iwm-jaycee-trades-2026-11-05.jsonl`). `track.py` merges them into
   `raw/` (deduped by ts + text prefix) and deletes the inbox file.

Each message object: `{"ts": "<ISO8601 UTC>", "author": "<display name>", "text": "<verbatim>"}`.
`ts` must be the Discord message timestamp in UTC (what the message's own timestamp is based on);
`text` must be verbatim, newlines as `\n`.

Run:
    /usr/bin/python3 /workspace/onlybands/track.py --today-only     # today's callouts + record
    /usr/bin/python3 /workspace/onlybands/track.py --days 7         # last week's callouts
Writes /workspace/onlybands/tracking/latest.md and prints the same markdown.

## What it reports
- **Stated record** — the trader's own posted percentages (only plays where they stated a result).
- **Underlying hit rate** — independent: for each call with a call/put direction, did the underlying
  close the session on the right side of where it was when the call posted. Verified from Yahoo
  1-minute bars. Direction only, not option P&L.

## Channels
| channel | slug | file |
|---|---|---|
| Jaycee (IWM) | odte-iwm-jaycee-trades | iwm-jaycee.jsonl |
| Hipp (QQQ) | odte-qqq-hipp-trades | qqq-hipp.jsonl |
| Bucky (swings) | bucky-budget-swings | bucky-budget.jsonl |
| Teej (breakout) | teej-breakout-trades | teej-breakout.jsonl |

Discord channel URLs (server 1273646245092790282):
Jaycee https://discord.com/channels/1273646245092790282/1332098987343478946
Hipp   https://discord.com/channels/1273646245092790282/1362462137062002869
Bucky  https://discord.com/channels/1273646245092790282/1564668305304723537
Teej   https://discord.com/channels/1273646245092790282/1564667898738245692

State of the newest message already harvested: `tracking/last-harvest.json`.
Nothing is ever posted, reacted to, or changed in Discord — read only.

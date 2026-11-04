# OnlyBands two-month Discord play backtest — 2026-11-04

Source: pinned call channels in the OnlyBands Discord (`odte-qqq-hipp-trades`, `odte-iwm-jaycee-trades`, `teej-breakout-trades`, `bucky-budget-swings`). Everything below comes only from what the traders themselves wrote; no option prices were modelled and no fills were guessed.

Workbook: `OnlyBands_2month_play_backtest.xlsx` (sheets: Summary, Plays, By month, Method, Raw counts). Rebuild with `python3 build_backtest.py && python3 verify.py`.

## Summary

| trader | date range covered (ET) | messages | plays | scored | unscored | W/L/BE | win rate | avg ROI | median | best win | worst loss |
|---|---|---|---|---|---|---|---|---|---|---|---|
| JAYCEE$IWMGUWOP | 2026-09-02 to 2026-11-04 (64d) | 588 | 61 | 29 | 32 | 20/1/0 | 20/21 = 95.2% | 46.9% | 45.0% | 78% SPY 771p Oct 8 | -16% INTC 100c Oct 30 |
| HippTooHipp | 2026-09-02 to 2026-11-04 (64d) | 770 | 53 | 44 | 9 | 25/1/1 | 25/27 = 92.6% | 103.1% | 91.0% | 255% QQQ 740p Sep 23 | -20% QQQ 610p Oct 27 |
| Bucky Dolla | 2026-10-27 to 2026-11-04 (9d) | 11 | 4 | 0 | 4 | 0/0/0 | n/a | - | - | none stated | none stated |
| Teej | 2026-10-28 to 2026-11-04 (8d) | 93 | 17 | 6 | 11 | 3/2/0 | 3/5 = 60.0% | 31.0% | 45.0% | 59% IWM 280c Nov 3 | -25% IWM 280c Nov 3 |
| **TOTAL** | 2026-09-02 to 2026-11-04 | 1462 | 135 | 79 | 56 | 48/4/1 | 48/53 = 90.6% | 73.8% | 57.6% | | |

Sum of per-play stated ROI: 3,688%. That is a sum of percents across separate plays, not a portfolio return. 29 scored plays had exit language but no number and carry no ROI.

## What this does and does not say

- The win rates are high because these traders post their winners. Only 4 stated losses exist in 1,462 messages, so treat the win rate as a reporting artifact, not as edge.
- ROI is the trader-stated percent on an exit, sell, target or stop message. Running marks like "60% here" are not counted as results.
- Only Jaycee and Hipp cover roughly two months. Teej has 8 days of history and Bucky 9 days, so their numbers cannot stand in for a two-month record.
- Classification is rule-based, not hand-labelled. Expect some misgrouped plays; spot-check through the message ids in the Plays sheet.

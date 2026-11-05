# Celestial Prints — Shopify store `bhaeqw-9z`

Second, clean storefront for the astronomy print-on-demand line. Distinct from the
Nightlens telescope store (`duv5f8-wt`, on hold) and from the accidental duplicate
`4exkcb-uk` created by the Shopify signup flow (builder filler products, $75/$48/$62 —
not used, nothing deleted).

- Public: https://bhaeqw-9z.myshopify.com
- Admin: https://admin.shopify.com/store/bhaeqw-9z
- Plan: Trial (must be upgraded before selling)

## Products

Live Printify posters are 18x24 at **$39.99** (cheaper on purpose than the earlier $44.99 plan). No 24x36 yet. The Solar System kiss-cut sticker stays live at 2/3/4/6 inch, $3.99-$7.99.

| Product | Size | Price | Shopify product id | Handle |
| --- | --- | --- | --- | --- |
| Ursa Major Constellation Print | 18x24 | $39.99 | 15489780810043 | `ursa-major-constellation-print` |
| Moon Phase | 18x24 | $39.99 | 15489780777275 | `moon-phase-print` |
| Solar System Chart Print | 18x24 | $39.99 | 15489779761467 | `solar-system-chart-print` |
| Kiss-Cut Stickers (Solar System) | 2/3/4/6 in | $3.99-$7.99 | 15489779794235 | unchanged |

### Hidden DRAFT originals (set to DRAFT on Nov 4, 2026)

These are the earlier unlinked products. Their $44.99 / $64.99 prices are the retired plan. Handles were moved to `*-original` so the live listings could take the public URLs.

| Product | 18x24 | 24x36 | Shopify product id | Handle |
| --- | --- | --- | --- | --- |
| Ursa Major Constellation Print | $44.99 | $64.99 | 15489621721403 | `ursa-major-constellation-print-original` |
| Moon Phase Print | $44.99 | $64.99 | 15489621754171 | `moon-phase-print-original` |
| Solar System Chart Print | $44.99 | $64.99 | 15489621852475 | `solar-system-chart-print-original` |

SKUs on the drafts: `CP-URSA-1824`, `CP-URSA-2436`, `CP-MOON-1824`, `CP-MOON-2436`,
`CP-SOLAR-1824`, `CP-SOLAR-2436`. Vendor `Printify`, product type `Poster`.
Theme: Horizon (default).

## Artwork

All three plates are public domain:
- Ursa Major — Sidney Hall, *Urania's Mirror*, 1825 (Plate IX).
- Moon phases — drawn programmatically (astronomically correct illuminated limb).
- Solar System — Andreas Cellarius, *Harmonia Macrocosmica*, "Scenographia Systematis
  Copernicani", Amsterdam 1660.

No NASA or ESA imagery: NASA requires written merchandise approval and ESO is the only
sellable alternative. Canva templates are a licensing conflict for POD posters.

Print-ready masters are 4500x6000 PNG on the box at `/workspace/starart/art/`. The
2400x3200 JPEGs uploaded to Shopify are not committed here to keep the repo light.

## Still open

1. **No 24x36 on the live posters yet.** Printify is connected. The three poster
   listings are renamed, carry the original descriptions, and are $39.99 for 18x24.
   See **Nov 4, 2026: Printify cleanup**.
2. **Trial plan.** `Plan: trial — you'll need to upgrade before you can start selling and
   unlock full features`.
3. **Storefront password is still on.** The public URL redirects to /password ("Opening soon"). Shopify does not let a trial store drop password protection, and the toggle (Settings > Online Store > Store access > Password protection) is reachable only from the Shopify admin signed in as the store owner account, karonrobbkk@gmail.com; the browser session this bot can drive is signed in as a different Shopify account with no staff access to bhaeqw-9z.
4. **`4exkcb-uk`** duplicate store needs Thomas's decision before anything is deleted.

## Nov 4, 2026: Printify cleanup

Printify is connected as the fulfillment service. Printify first published four new listings under placeholder names (the posters were 18x24 matte at $21.99):

- **Matte Vertical Posters** — Solar System art, gid `15489779761467`, 18x24 matte at $21.99.
- **Copy of Matte Vertical Posters** — Moon Phases, gid `15489780777275`, 18x24 matte at $21.99.
- **Copy of Matte Vertical Posters** — Ursa Major, gid `15489780810043`, 18x24 matte at $21.99.
- **Kiss-Cut Stickers** — Solar System, gid `15489779794235`.

Earlier decision: keep the Printify listings and fix them in Printify (rename to the original titles, paste the original descriptions, add 24x36, set prices to $44.99 for 18x24 and $64.99 for 24x36, republish).

Thomas renamed the Printify poster listings to **Ursa Major Constellation Print**, **Moon Phase**, and **Solar System Chart Print**, with the original descriptions. He chose **$39.99 for 18x24**, cheaper on purpose, replacing the $44.99 plan. There is no 24x36 yet.

URL handles changed, with redirects:

- `15489780810043` → `ursa-major-constellation-print` (Ursa Major Constellation Print)
- `15489780777275` → `moon-phase-print` (Moon Phase)
- `15489779761467` → `solar-system-chart-print` (Solar System Chart Print)

The sticker product (`15489779794235`) stays live, with 2/3/4/6 inch sizes at $3.99-$7.99.

The original three unlinked products were set to DRAFT (hidden) on Nov 4, 2026, then moved to `*-original` handles:

- Ursa Major Constellation Print `15489621721403` → `ursa-major-constellation-print-original`
- Moon Phase Print `15489621754171` → `moon-phase-print-original`
- Solar System Chart Print `15489621852475` → `solar-system-chart-print-original`

The homepage **The prints** grid showed Shopify placeholder (blank shirt) images because the All Prints collection (gid `512813596987`) only held the hidden drafts. The three live Printify posters (`15489780810043`, `15489780777275`, `15489779761467`) were added to All Prints.

The **About the art** homepage section's "View print" links still point at the hidden `*-original` drafts. The live theme cannot be edited via the API, so URL redirects were created. Each of these 301s to the matching live handle without `-original`:

- `/products/ursa-major-constellation-print-original` → `/products/ursa-major-constellation-print`
- `/products/moon-phase-print-original` → `/products/moon-phase-print`
- `/products/solar-system-chart-print-original` → `/products/solar-system-chart-print`

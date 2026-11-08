# Celestial Prints — Shopify store `bhaeqw-9z`

Second, clean storefront for the astronomy print-on-demand line. Distinct from the
Nightlens telescope store (`duv5f8-wt`, on hold) and from the accidental duplicate
`4exkcb-uk` created by the Shopify signup flow (builder filler products, $75/$48/$62 —
not used, nothing deleted).

- Public: https://bhaeqw-9z.myshopify.com
- Admin: https://admin.shopify.com/store/bhaeqw-9z
- Plan: Trial, as last recorded. Not rechecked on 2026-11-07.

## Celestial paintings page

Star-map and celestial wall-art page for this store only. No inventory. See [PAINTINGS.md](./PAINTINGS.md).

The page, the collection, and a main-menu link are live from 2026-11-05. On 2026-11-08 the public shop name is Vintage Plate Co., and the storefront theme is "Dawn - Vintage Plate Co. Draft" (`188621029691`). The page body already names four paintings in this order: Moon Phase, Ursa Major, Orion, Solar System. The collection still lists the solar system before Orion. The page still has no banner and no product grid. A page draft, a size strip on the Dawn template, a collection-order proposal, and a homepage size-and-tile proposal are in the repo and were not uploaded. This run did not change a price. Every public product read that morning was one 18×24 matte variant at $31.99, compare-at $39.99.

## Products

Public price read on 2026-11-07 for each poster below: **$31.99**, compare-at **$39.99**, one 18x24 matte variant. Do not write a price from this file. The $39.99 figure is the earlier price Thomas set and is now the compare-at amount. No 24x36 variant is on these listings. The Solar System kiss-cut sticker (`15489779794235`) is not in the 24 public products. This run did not unpublish, delete, or restore it.

| Product | Size | Price observed 2026-11-07 | Shopify product id | Handle |
| --- | --- | --- | --- | --- |
| Ursa Major Constellation Print | 18x24 | $31.99 (compare-at $39.99) | 15489780810043 | `ursa-major-constellation-print` |
| Moon Phase | 18x24 | $31.99 (compare-at $39.99) | 15489780777275 | `moon-phase-print` |
| Solar System Chart Print | 18x24 | $31.99 (compare-at $39.99) | 15489779761467 | `solar-system-chart-print` |
| Orion Constellation Print | 18x24 | $31.99 (compare-at $39.99) | 15490090008891 | `orion-constellation-print` |

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

Source plates:
- Ursa Major — Sidney Hall, *Urania's Mirror*, 1825 (Plate IX). Public domain.
- Orion — John Flamsteed, *Atlas Céleste*, Plate 24, 1776. Public domain. On the public page and in the collection as of 2026-11-07.
- Moon phases — drawn programmatically (astronomically correct illuminated limb). Original artwork.
- Solar System — Andreas Cellarius, *Harmonia Macrocosmica*, "Scenographia Systematis
  Copernicani", Amsterdam 1660. Public domain.

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
3. **Storefront password.** On 2026-11-04 a bot recorded that the public URL redirected to /password ("Opening soon") and that a trial store cannot drop that protection. On 2026-11-07 a request to `/password` ended on the storefront, and the paintings page returned the page itself. The trial plan was not rechecked on 2026-11-07.
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

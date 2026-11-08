# Celestial paintings page

Print-on-demand store `bhaeqw-9z.myshopify.com` only. The public shop name on 2026-11-08 is Vintage Plate Co. The telescope shop was not edited. Nothing on this page is held in inventory. Printify prints each order.

## 2026-11-08 draft (not sent to Shopify)

A read of the public storefront found the same theme and the same text-only page as on Nov 7. Theme id `188621029691`, name "Dawn - Vintage Plate Co. Draft", role main, Dawn 16.1.1. The page body still names Moon Phase, Ursa Major, Orion, then the solar system. It still has no collection link and no line that other sizes are absent. `?view=celestial-paintings` still renders the default page section. Dawn prints `template.name` into `data-template`, which stays `page` with or without a suffix, so this read does not show whether the page resource's template suffix is still `celestial-paintings`. Admin was not opened.

All 24 public products have one variant, `18″ x 24″ / Matte`, price $31.99, compare-at $39.99. The four celestial posters share `updated_at` `2026-11-08T08:38:28-05:00`. This run did not change them. The Ursa Major body still says 1824. The collection order is still solar system third, Orion fourth.

The homepage size strip still says `12 × 16 in · 18 × 24 in · 24 × 36 in` and that larger and smaller sizes will roll out. No public variant is 12×16 or 24×36. The National Parks tile uses `solar-system.jpg` and says "coming soon" while linking to All Prints. The Botanical tile uses `moon-phases.jpg` and says "planned next" while linking to All Prints. Both of those collections are already public: `vintage-national-parks` and `vintage-botanical-plates`. The celestial tile still links to `/collections/celestial-paintings` and was left as it is.

Shopify admin was not authenticated, so no theme duplicate was created and nothing was uploaded.

The page HTML now says a 12 by 16 inch size is also absent. The Dawn template adds a rich-text size section after the four-product grid and says 18 by 24 inches in the grid description. It still points only at `celestial-paintings`, four products, two desktop columns. A homepage edit proposal is in `theme-draft/homepage-size-and-tiles.proposed.json`. It is not a replacement for `templates/index.json`. Product-description drafts, including the Ursa year 1825, are in `celestial-paintings.apply.json` under `pending_revision_2026_11_08`. They were not sent. Do not paste both the Nov 7 Ursa paragraph and the Nov 8 Ursa paragraph.

## 2026-11-07 draft (not sent to Shopify)

A read of the public storefront found the page already naming four paintings. The page was updated `2026-11-06T13:07:09-05:00`. Its order is Moon Phase, Ursa Major, Orion, Solar System. The collection `celestial-paintings` (id `512824901947`) still lists the solar system before Orion. The 2026-11-06 HTML in this repo would have reversed that page order, so it must not be pasted over the live page. On 2026-11-07 the file `pages/celestial-paintings.html` was the smaller revision: the live sentences, the live order, a link to the collection, and a line that 24 by 36 inches is not on these listings. It did not state a price. The 2026-11-08 edit of that same file also says a 12 by 16 inch size is not on these listings.

The rendered page is the announcement bar, the header, the default page body, and the footer. Theme id served on the page: `188621029691`, name "Dawn - Vintage Plate Co. Draft", role main, Dawn 16.1.1. `?view=celestial-paintings` renders the same default page section, so `templates/page.celestial-paintings.json` is not on this theme. That template file was not changed today. It still points at collection `celestial-paintings` only, four products, two desktop columns. It must not be pointed at All Prints. All Prints now has 24 products, including botanical plates and national-park posters, and those do not belong on this page.

The template belongs on an unpublished duplicate of theme `188621029691`. The Nov 5 duplicate `188599370043` was copied from the older main theme `188589113659`, which is not the theme the storefront is serving. Do not write the live theme. Do not publish.

Shopify admin was not authenticated in this session, so no theme, page, product, or collection write was possible.

Public variant price on each of the four posters, read 2026-11-07: $31.99, compare-at $39.99, 18×24 matte, one variant each. This run did not change a price. Do not write a price from these notes.

The Ursa Major product body still says the plate was published in 1824. The page, `SPECS.md`, and `sources.json` say 1825. A replacement paragraph is in `celestial-paintings.apply.json` under `ursa_year_proposed` and was not sent.

The Solar System sticker (`15489779794235`) is not among the 24 public products. This run did not unpublish, delete, or restore it. The three hidden `*-original` drafts are also absent from the public list. Admin was not opened, so their draft status was not rechecked.

## 2026-11-06 record

That morning the page body still named three paintings and the collection already included Orion. A four-painting HTML file and the Dawn template were written here and were not uploaded. Later the same day the live page was edited and Orion was added in the third slot. Treat that later page as the current body. Do not re-apply the 2026-11-06 revision.

## What the page is

A collection and a content page for the four wall-art paintings that are already public Printify posters. The page order below is the order a buyer reads. The collection order is still solar system third, Orion fourth, until Thomas says yes to a reorder.

| Order on the live page | Painting | Handle | Product id | Collection position on 2026-11-07 |
| --- | --- | --- | --- | --- |
| 1 | Moon Phase | `moon-phase-print` | 15489780777275 | 1 |
| 2 | Ursa Major Constellation Print | `ursa-major-constellation-print` | 15489780810043 | 2 |
| 3 | Orion Constellation Print | `orion-constellation-print` | 15490090008891 | 4 |
| 4 | Solar System Chart Print | `solar-system-chart-print` | 15489779761467 | 3 |

Left off the page: botanical plates, national-park and WPA posters, the Solar System sticker, and the three hidden `*-original` drafts. There is still no 24×36 variant on the four posters.

A custom date-and-place star map, a moon tied to one date, and a twelve-sign series stay off this page. A static poster cannot take a date and a place, and those plates are not drawn. The Nov 6 demand note is `morning-reports/precheck-2026-11-06-trending-researcher.md`.

## Files

- `pages/celestial-paintings.html` — proposed page body. The 2026-11-08 edit adds that 12 by 16 inches is not on these listings. Not uploaded.
- `templates/page.celestial-paintings.json` — Dawn 16.1.1 layout: dark banner, the page copy, a two-column portrait grid of four products from collection `celestial-paintings`, then a cream size strip that names 18×24 only. Not on the live theme.
- `theme-draft/homepage-size-and-tiles.proposed.json` — proposed homepage size-strip and tile edits for an unpublished duplicate. Not a full `index.json`. Not uploaded.
- `celestial-paintings.apply.json` — Nov 5 record has `"applied": true`. The 2026-11-06 block is `superseded_revision` with `"do_not_apply": true`. The 2026-11-07 block is `pending_revision` with `"applied": false`. The 2026-11-08 block is `pending_revision_2026_11_08` with `"applied": false`.

## Apply only after a yes

1. Confirm the domain is `bhaeqw-9z.myshopify.com`. Stop if it is anything else, including `duv5f8-wt.myshopify.com`.
2. Do not apply `2026-11-06-orion-on-page`. The live page already names Orion.
3. Re-read the four product ids. Use them only if the handles still match the table above.
4. Do not recreate the collection, the page, or the menu item.
5. Do not add botanical plates, park posters, the sticker, or the draft originals. Do not change any price.
6. Replace the page body from the HTML file only if Thomas has said yes. Leave the page published state as it already is unless he says otherwise.
7. Reorder the collection to Moon Phase, Ursa Major, Orion, Solar System only if he has said yes. Only then add the extra description sentence stored on `collection_reorder_proposed`.
8. Change the Ursa Major year from 1824 to 1825 only if he has said yes. If the Nov 8 product bodies are also approved, use `pending_revision_2026_11_08` once and skip `ursa_year_proposed.proposed_body_html`. If only the year is approved, use `ursa_year_proposed.proposed_body_html`. Do not change that product's price.
9. Copy the template onto an unpublished duplicate of theme `188621029691` only. Do not write the live theme. Do not publish the duplicate. Do not upload it to NightLens. Use the 2026-11-08 template, which includes the size strip.
10. Edit the homepage size strip and the National Parks and Botanical tiles only from `theme-draft/homepage-size-and-tiles.proposed.json`, and only on that unpublished duplicate. Do not paste that file over `templates/index.json`.
11. If product descriptions are approved, apply `pending_revision_2026_11_08.product_bodies_proposed` once. Do not also paste the 2026-11-07 Ursa paragraph. Do not change any price.

## Still needs Thomas

- Say yes before the live page body is replaced with the HTML file.
- Say yes before the collection order changes. Until then, a product grid would show the solar system before Orion while the page text does the opposite.
- Say yes before the Ursa Major description year changes.
- Say yes before the Dawn template is uploaded, and only to an unpublished duplicate of the theme the storefront is serving now.
- Say yes before the homepage size strip and the two mislabeled tiles are edited, and only on that unpublished duplicate.
- Say yes before any product description is replaced. The Nov 8 drafts add the 18×24-only line and, for Ursa Major, the year 1825.
- Leave prices, NightLens, the sticker, and the hidden drafts alone. Do not add botanical plates or park posters to the Celestial Paintings collection.
- A custom date-and-place star map, and a twelve-sign series, are separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-08)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-08)
- [Vintage Plate Co. homepage](https://bhaeqw-9z.myshopify.com/) (read 2026-11-08)
- `sources.json` date for the Ursa Major file: 1825
- Dawn 16.1.1, confirmed by `Shopify.theme.schema_version` on the live page

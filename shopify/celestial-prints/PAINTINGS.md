# Celestial paintings page

Print-on-demand store `bhaeqw-9z.myshopify.com` only. The public shop name on 2026-11-07 is Vintage Plate Co. The telescope shop was not edited. Nothing on this page is held in inventory. Printify prints each order.

## 2026-11-07 draft (not sent to Shopify)

A read of the public storefront found the page already naming four paintings. The page was updated `2026-11-06T13:07:09-05:00`. Its order is Moon Phase, Ursa Major, Orion, Solar System. The collection `celestial-paintings` (id `512824901947`) still lists the solar system before Orion. The 2026-11-06 HTML in this repo would have reversed that page order, so it must not be pasted over the live page. The file `pages/celestial-paintings.html` is now the smaller revision: the live sentences, the live order, a link to the collection, and a line that 24 by 36 inches is not on these listings. It does not state a price.

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

- `pages/celestial-paintings.html` — proposed page body for the 2026-11-07 revision. Not uploaded. Do not paste it over the live page without a yes.
- `templates/page.celestial-paintings.json` — Dawn 16.1.1 layout from 2026-11-06: dark banner, the page copy, then a two-column portrait grid of four products from collection `celestial-paintings`. Not on the live theme. Not changed on 2026-11-07.
- `celestial-paintings.apply.json` — Nov 5 record has `"applied": true`. The 2026-11-06 block is `superseded_revision` with `"do_not_apply": true`. The 2026-11-07 block is `pending_revision` with `"applied": false`.

## Apply the 2026-11-07 revision only after a yes

1. Confirm the domain is `bhaeqw-9z.myshopify.com`. Stop if it is anything else, including `duv5f8-wt.myshopify.com`.
2. Do not apply `2026-11-06-orion-on-page`. The live page already names Orion.
3. Re-read the four product ids. Use them only if the handles still match the table above.
4. Do not recreate the collection, the page, or the menu item.
5. Do not add botanical plates, park posters, the sticker, or the draft originals. Do not change any price.
6. Replace the page body from the HTML file only if Thomas has said yes. Leave the page published state as it already is unless he says otherwise.
7. Reorder the collection to Moon Phase, Ursa Major, Orion, Solar System only if he has said yes. Only then add the extra description sentence stored on `collection_reorder_proposed`.
8. Change the Ursa Major year from 1824 to 1825 only if he has said yes. Use `ursa_year_proposed.proposed_body_html`. Do not change that product's price.
9. Copy the template onto an unpublished duplicate of theme `188621029691` only. Do not write the live theme. Do not publish the duplicate. Do not upload it to NightLens.

## Still needs Thomas

- Say yes before the live page body is replaced with the HTML file.
- Say yes before the collection order changes. Until then, a product grid would show the solar system before Orion while the page text does the opposite.
- Say yes before the Ursa Major description year changes.
- Say yes before the Dawn template is uploaded, and only to an unpublished duplicate of the theme the storefront is serving now.
- Leave prices, NightLens, the sticker, the hidden drafts, and the botanical and park collections alone.
- A custom date-and-place star map, and a twelve-sign series, are separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-07)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-07)
- `sources.json` date for the Ursa Major file: 1825
- Dawn 16.1.1, confirmed by `Shopify.theme.schema_version` on the live page

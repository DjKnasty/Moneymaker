# Celestial paintings page

Print-on-demand store `bhaeqw-9z.myshopify.com` only. The public shop name on 2026-11-11 is Vintage Plate Co. The telescope shop was not edited. Nothing on this page is held in inventory. Printify prints each order.

## 2026-11-11 draft (unpublished)

The live theme is still "Dawn - Celestial paintings draft" (`188676014395`), role MAIN. Buyers still see Dawn's placeholder in the banner, then the page title a second time. This run did not write that theme. Its page template is still the Nov 9 file: `updatedAt` `2026-11-09T13:39:12Z`, size 2411.

Unpublished theme "Dawn - Celestial page draft" (`188699902267`) is still UNPUBLISHED. On that copy only, the banner now uses two existing shop files: `shopify://shop_images/moon-phases-mockup.jpg` on the left and `shopify://shop_images/solar-system-mockup.jpg` on the right. They stack on a phone. The banner line is "Four unframed 18 by 24 inch charts, printed when you order them." There is still no second "Celestial paintings" heading. The file was written `2026-11-11T13:42:11Z`, size 2370. No new image was uploaded. The theme was not published. A public `preview_theme_id=188699902267` request still served the live theme. Preview it in Admin.

The page body was not written. `updatedAt` is still `2026-11-09T14:06:35Z`. The collection was not written. Order is still Moon Phase, Ursa Major, Orion, Solar System, and the description is still two sentences. Each of the four variants is still 18″×24″ matte at $31.99, compare-at $39.99. This run did not change a price.

The Moon Phase product body still does not say the chart is original artwork or that it is not a photograph. The page does. A longer paragraph that adds those two sentences, and keeps the rest, is in `celestial-paintings.apply.json` under `moon_original_artwork_proposed` with `apply: false`. It was not sent.

The homepage size line still reads "12 × 16 in · 18 × 24 in · 24 × 36 in" on the live theme and on this unpublished copy. This run did not edit `templates/index.json`. A read of the 25 active products found 24 posters at 18×24 and the kiss-cut sticker. No active poster is 12×16 or 24×36.

## 2026-11-10 draft (unpublished)

The Nov 9 copy "Dawn - Celestial paintings draft" (`188676014395`) is now the live theme, role MAIN. This run did not publish it. Its page template is still the Nov 9 file, updated `2026-11-09T13:39:12Z`. Buyers see Dawn's placeholder drawing in the banner, then the page title "Celestial paintings" again as the page `h1`.

This run duplicated that live theme to unpublished theme "Dawn - Celestial page draft", id `188699902267`, role UNPUBLISHED. On that copy only, `templates/page.celestial-paintings.json` now points the banner at the existing shop file `shopify://shop_images/solar-system-mockup.jpg` and drops the banner heading so the page `h1` is the only "Celestial paintings" title. The file on the copy was written `2026-11-10T13:50:18Z`. The live theme file was read back at the old timestamp and the old size. The theme was not published. A public `preview_theme_id=188699902267` request still served the live theme. Preview it in Admin.

The page body already matches `pages/celestial-paintings.html`, including the collection link, the 1825 Ursa line, and the line that 24 by 36 inches is not on these listings. Admin `updatedAt` is `2026-11-09T14:06:35Z`. This run did not write the page.

Collection `celestial-paintings` (`512824901947`) is manual and now lists Moon Phase, Ursa Major, Orion, then the solar system. `updatedAt` is `2026-11-09T14:06:38Z`. The description is still the two sentences. The extra order sentence was not added.

The Ursa Major product body already says 1825. It was updated `2026-11-10T02:09:12Z` and is longer than `ursa_year_proposed.proposed_body_html`. Do not paste that short paragraph over it. The variant is still $31.99, compare-at $39.99. This run did not change a price.

## 2026-11-09 draft theme (now the live theme)

Historical record from that morning. The 2026-11-10 section above is the current state.

The live page and the collection were read again and left as they were. Page order is still Moon Phase, Ursa Major, Orion, Solar System. Collection `celestial-paintings` (id `512824901947`) still lists the solar system before Orion. Its `updatedAt` is `2026-11-08T23:12:46Z`. The description is still the two sentences from Nov 7.

The storefront theme is still "Dawn - Vintage Plate Co. Draft", id `188621029691`, role main, Dawn 16.1.1. That theme does not contain `templates/page.celestial-paintings.json`. The page's `templateSuffix` is already `celestial-paintings`, so the storefront falls back to the default page section.

This run duplicated theme `188621029691` to unpublished theme "Dawn - Celestial paintings draft", id `188676014395`, role UNPUBLISHED, and wrote the repo template onto that copy only. The file's `updatedAt` on the copy is `2026-11-09T13:39:12Z`. A later read of the live theme still returns NOT_FOUND for that filename. The theme was not published. The Nov 5 duplicate `188599370043` was not written.

The template's featured-collection setting `show_description` is now false, and the grid sentence is a richtext paragraph. On this Dawn file, `show_description: true` prints the collection description and does not print the custom sentence. The grid still uses collection `celestial-paintings` only, four products, two desktop columns. It must not be pointed at All Prints.

`pages/celestial-paintings.html` was not uploaded. The draft theme's page section renders the body that is already on the published page. A preview of the draft therefore shows the current text, the new banner, and a grid that still places the solar system before Orion.

Public and admin price on each of the four posters, read 2026-11-09: $31.99, compare-at $39.99, 18×24 matte, one variant each. This run did not change a price. Do not write a price from these notes. The shop plan read Advanced. This run did not change the plan.

The Ursa Major product body still says the plate was published in 1824. The replacement paragraph in `celestial-paintings.apply.json` under `ursa_year_proposed` was not sent.

## 2026-11-07 draft (page body still not sent)

Historical record from that morning. The 2026-11-10 section above is the current state.

A read of the public storefront found the page already naming four paintings. The page was updated `2026-11-06T13:07:09-05:00`. Its order is Moon Phase, Ursa Major, Orion, Solar System. The 2026-11-06 HTML in this repo would have reversed that page order, so it must not be pasted over the live page. The file `pages/celestial-paintings.html` is the smaller revision: the live sentences, the live order, a link to the collection, and a line that 24 by 36 inches is not on these listings. It does not state a price. That file was still not sent on 2026-11-09.

On 2026-11-07 the rendered page was the announcement bar, the header, the default page body, and the footer. That is still what buyers see. All Prints is not the collection for this template. It mixes in botanical plates and national-park posters, and those do not belong on this page.

The Ursa Major product body still says 1824. The page, `SPECS.md`, and `sources.json` say 1825.

The Solar System sticker (`15489779794235`) was not among the public products on the Nov 7 read. This run did not open that product, and did not unpublish, delete, or restore it. The three hidden `*-original` drafts were not opened either.

## 2026-11-06 record

That morning the page body still named three paintings and the collection already included Orion. A four-painting HTML file and the Dawn template were written here and were not uploaded. Later the same day the live page was edited and Orion was added in the third slot. Treat that later page as the current body. Do not re-apply the 2026-11-06 revision.

## What the page is

A collection and a content page for the four wall-art paintings that are already public Printify posters. The page order below is the order a buyer reads. On 2026-11-10 the collection order matches that page. Do not reorder it again.

| Order on the live page | Painting | Handle | Product id | Collection position on 2026-11-09 |
| --- | --- | --- | --- | --- |
| 1 | Moon Phase | `moon-phase-print` | 15489780777275 | 1 |
| 2 | Ursa Major Constellation Print | `ursa-major-constellation-print` | 15489780810043 | 2 |
| 3 | Orion Constellation Print | `orion-constellation-print` | 15490090008891 | 3 |
| 4 | Solar System Chart Print | `solar-system-chart-print` | 15489779761467 | 4 |

Left off the page: botanical plates, national-park and WPA posters, the Solar System sticker, and the three hidden `*-original` drafts. There is still no 24×36 variant on the four posters.

A custom date-and-place star map, a moon tied to one date, and a twelve-sign series stay off this page. A static poster cannot take a date and a place, and those plates are not drawn. The Nov 9 demand note is `morning-reports/precheck-2026-11-09-trending-researcher.md`. It reaches the same conclusion.

## Files

- `pages/celestial-paintings.html` — proposed page body for the 2026-11-07 revision. Not uploaded. Do not paste it over the live page without a yes.
- `templates/page.celestial-paintings.json` — Dawn layout: banner, the page copy, then a two-column portrait grid of four products from collection `celestial-paintings`. On 2026-11-11 the banner on unpublished theme `188699902267` uses the existing moon mockup and the existing solar-system mockup, and the line names 18 by 24 inches. There is still no second title. The live theme `188676014395` still has the Nov 9 file, with a placeholder banner and a repeated title.
- `celestial-paintings.apply.json` — Nov 5 record has `"applied": true`. The 2026-11-06 block is `superseded_revision` with `"do_not_apply": true`. The 2026-11-07 block is `pending_revision` with `"applied": false` for the live page, the collection, and the Ursa year. The unpublished theme write is recorded on that block and is not a publish.

## Apply the 2026-11-07 revision only after a yes

1. Confirm the domain is `bhaeqw-9z.myshopify.com`. Stop if it is anything else, including `duv5f8-wt.myshopify.com`.
2. Do not apply `2026-11-06-orion-on-page`. The live page already names Orion.
3. Re-read the four product ids. Use them only if the handles still match the table above.
4. Do not recreate the collection, the page, or the menu item.
5. Do not add botanical plates, park posters, the sticker, or the draft originals. Do not change any price.
6. The live page body already matches the HTML file, read `2026-11-10`. Do not send it again. Leave the page published.
7. The collection order already matches the page, read `2026-11-10`. Do not reorder it. Add the extra description sentence on `collection_reorder_proposed` only if Thomas has said yes.
8. Do not change the Ursa Major description. It already says 1825. Do not change that product's price.
9. The current unpublished draft is theme `188699902267`. On 2026-11-11 the banner on that copy uses the moon mockup and the solar-system mockup. Do not write the live theme `188676014395`. Do not publish the copy. Do not upload it to NightLens. Do not treat `188676014395` as unpublished. Do not treat the Nov 5 theme `188599370043` as the current draft.
10. Do not paste `ursa_year_proposed.proposed_body_html` over the live Ursa Major description. The live text already says 1825 and is longer than that paragraph.

## Still needs Thomas

- Preview unpublished theme `188699902267` in Admin before anyone publishes it. Publishing would replace the placeholder banner with the moon mockup beside the solar-system mockup, name 18 by 24 inches in the banner line, and remove the repeated banner title. It was not published.
- Say yes before the Moon Phase product gains the two sentences that call the chart original artwork and not a photograph. The rest of that description stays. Do not change its price.
- Say yes before the collection description gains the extra sentence that names the four charts in order. The order itself already matches the page.
- Leave the Ursa Major description as it is. Do not replace it with the shorter 1825 paragraph.
- Leave prices, the live page body, NightLens, the sticker, the hidden drafts, and the botanical and park collections alone.
- The live homepage size line still names 12 × 16 and 24 × 36. This run did not change it. The paintings page still says 24 by 36 is not on these four listings.
- A custom date-and-place star map, and a twelve-sign series, are separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-11)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-11)
- `sources.json` date for the Ursa Major file: 1825
- Dawn 16.1.1, confirmed by `Shopify.theme.schema_version` on the live page

# Store builder pre-check — 2026-11-10

The celestial paintings page on bhaeqw-9z is live on theme Dawn - Celestial paintings draft (188676014395), with the four paintings in the order Moon Phase, Ursa Major, Orion, then the solar system, and the collection is now in that same order. The banner buyers see is still Dawn's placeholder drawing, and the banner heading repeats the page title. This run copied that live theme into unpublished theme Dawn - Celestial page draft (188699902267) and, on that copy only, pointed the banner at the existing solar-system mockup and removed the repeated heading. The live theme file was not written, nothing was published, no price was changed, and NightLens was not touched. Thomas still needs to preview that unpublished theme before anyone publishes it, and he still needs to decide whether the collection description should name the four charts.

## Prepared

- Unpublished theme `gid://shopify/OnlineStoreTheme/188699902267`, name "Dawn - Celestial page draft", role UNPUBLISHED, duplicated from the current main theme `188676014395`. It was not published. The live theme is still main. Its page-template `updatedAt` is still `2026-11-09T13:39:12Z` and its size is still 2411.
- `templates/page.celestial-paintings.json` on that unpublished theme only, written `2026-11-10T13:50:18Z`, size 2290. The banner image is the existing shop file `shopify://shop_images/solar-system-mockup.jpg` (MediaImage `49553951490363`, already READY). The banner heading block is gone, so the page `h1` is the only "Celestial paintings" title. The grid is unchanged: collection `celestial-paintings`, four products, two desktop columns, `show_description` false. A public request with `preview_theme_id=188699902267` still served the live theme. Buyers do not see the draft.
- Repo copies of that template, `PAINTINGS.md`, the store README, `STATUS.md`, and `celestial-paintings.apply.json`. The 2026-11-07 revision is marked `do_not_apply`. The short Ursa Major paragraph is marked `do_not_apply` because the live description already says 1825 and is longer. The collection's extra sentence is still stored with `apply: false`.

The same-day demand note (`morning-reports/precheck-2026-11-10-trending-research.md`) did not open the shop. It still ranks a custom date-and-place star map ahead of these static plates. That map is not on this page. A static poster cannot take a date and a place.

## What the store showed, and was left as it was

- Shop `bhaeqw-9z`, public name Vintage Plate Co., plan Advanced. This run did not change the plan.
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings), id `166674628923`, still published. Body `updatedAt` `2026-11-09T14:06:35Z`. The body matches `pages/celestial-paintings.html`: the collection link, Ursa Major in 1825, Orion before the solar system, and the line that 24 by 36 inches is not on these listings. This run did not write the page.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, four products, manual, `updatedAt` `2026-11-09T14:06:38Z`. Order is Moon Phase, Ursa Major, Orion, Solar System. The description is still the two sentences and does not name the four titles. This run did not write the collection.
- Each of the four variants is still 18″×24″ matte, price $31.99, compare-at $39.99. The Ursa Major variant `updatedAt` is `2026-11-09T04:18:43Z`. The Ursa Major product body, updated `2026-11-10T02:09:12Z`, already says 1825. This run did not write a product or a price.
- The live page renders the announcement bar, a placeholder banner, the page body, the four-product grid in page order, and the footer. The grid sentence "Four paintings, printed on demand. No stock held." is on the page.
- The live homepage size line still reads "12 × 16 in · 18 × 24 in · 24 × 36 in". This run did not edit the homepage.
- The main menu still links "Celestial paintings" to the page. NightLens (`duv5f8-wt`) was not edited. Its homepage still responds on the NightLens theme.

## Needs his yes

- Preview "Dawn - Celestial page draft" (`188699902267`) in Admin, then decide whether that banner should ever be published. Do not publish it from this note. Do not write live theme `188676014395`.
- Add the third collection sentence, the one that names the moon phases, Ursa Major, Orion, and the Copernican solar system, only if he wants it. The collection order already matches the page, so do not reorder it.
- Leave the Ursa Major description as it is. Do not replace it with the shorter paragraph in the old proposal, and do not change its price.
- Leave every price as it is, including the $31.99 / compare-at $39.99 on the four posters.
- Leave the homepage size line alone unless he wants that copy changed. It still names sizes the four paintings do not sell.
- Leave NightLens alone.
- A custom date-and-place star map, and a twelve-sign series, remain separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-10)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-10)
- Admin read of themes `188676014395` and `188699902267`, page `166674628923`, collection `512824901947`, and the Ursa Major variant (read 2026-11-10)
- Existing shop file `solar-system-mockup.jpg` (read 2026-11-10, not uploaded)

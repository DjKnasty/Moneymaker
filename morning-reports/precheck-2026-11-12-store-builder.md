# Store builder pre-check — 2026-11-12

The celestial paintings page on bhaeqw-9z is still live on theme Dawn - Celestial paintings draft (188676014395), with the four paintings in the order Moon Phase, Ursa Major, Orion, then the solar system, and the collection in that same order. Buyers still see Dawn's placeholder drawing in the banner, and the banner heading still repeats the page title. This run did not copy a theme. On the unpublished theme Dawn - Celestial page draft (188699902267) only, yesterday's banner is unchanged, and a new section places the existing Ursa Major mockup beside the existing Orion framed photo, stacked on a phone. The live theme file was not written, nothing was published, no price was changed, and NightLens was not touched. Thomas still needs to preview that unpublished theme before anyone publishes it. He also still needs to decide on a Moon Phase sentence, a public-domain sentence on Orion and on the solar system, the collection's extra sentence, and the homepage size line.

## Prepared

- `templates/page.celestial-paintings.json` on unpublished theme `gid://shopify/OnlineStoreTheme/188699902267` only, written `2026-11-12T13:41:36Z`, size 4343. The role is still UNPUBLISHED. The banner is still the existing shop files `shopify://shop_images/moon-phases-mockup.jpg` and `shopify://shop_images/solar-system-mockup.jpg`, with the line "Four unframed 18 by 24 inch charts, printed when you order them." There is still no banner heading. Under that banner, section `pair` is a two-column multicolumn. The left image is the existing shop file `shopify://shop_images/ursa-major-mockup.jpg` (MediaImage `49553950146875`, already READY). The right image is the existing shop file `shopify://shop_images/orion-constellation-print-framed.jpg` (MediaImage `49632362463547`, already READY). Files has no Orion image in the mockup series, so this draft uses that framed wall photo. No file was uploaded. The two columns use one column on a phone. The grid is unchanged: collection `celestial-paintings`, four products, two desktop columns, `show_description` false. A public request with `preview_theme_id=188699902267` still served the live theme. Buyers do not see the draft.
- The same file in the repo, plus `PAINTINGS.md`, the store README, `STATUS.md`, and `celestial-paintings.apply.json`. The new block is `pending_revision_2026_11_12`, and it is not a publish.
- An Orion description and a solar-system description, both stored with `apply: false`. Each keeps the current second paragraph and the details list, and adds "The plate is public domain." to the first paragraph. Neither was sent. Orion `updatedAt` is still `2026-11-09T10:00:34Z`. The solar-system product `updatedAt` is still `2026-11-09T16:16:13Z`.
- The Moon Phase description from yesterday, still stored with `apply: false` and still not sent. Its `updatedAt` is still `2026-11-09T10:00:32Z`.
- The collection's third sentence, still stored with `apply: false` and still not sent. The collection `updatedAt` is still `2026-11-09T14:06:38Z`.
- The homepage size replacement, still stored with `apply: false` and not written. The heading would become "18 × 24 in". The paragraph would say every poster on sale is 18 by 24 inches and that 12 by 16 and 24 by 36 are not on these listings.

## What the store showed, and was left as it was

- Shop `bhaeqw-9z`, public name Vintage Plate Co., plan Advanced. This run did not change the plan.
- Live theme `188676014395`, role MAIN. Its page template `updatedAt` is still `2026-11-09T13:39:12Z` and its size is still 2411. The placeholder banner and the repeated heading are still what buyers see. A read of the public page still shows the placeholder drawing and the main-menu link to the page.
- Unpublished theme `188699902267` homepage `templates/index.json` was not written. Size 6891, `updatedAt` `2026-11-10T13:49:48Z`. The live homepage was not written either. Size 6891, `updatedAt` `2026-11-09T13:38:18Z`. The size line on both copies still reads "12 × 16 in · 18 × 24 in · 24 × 36 in".
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings), id `166674628923`, still published. Body `updatedAt` `2026-11-09T14:06:35Z`. This run did not write the page.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, four products, manual, `updatedAt` `2026-11-09T14:06:38Z`. Order is Moon Phase, Ursa Major, Orion, Solar System. The description is still the two sentences. This run did not write the collection.
- Each of the four variants is still 18″×24″ matte, price $31.99, compare-at $39.99. This run did not write a product or a price. A read of the 25 active products found those four posters, twenty other posters at the same 18×24 price, and the kiss-cut sticker. No active poster is 12×16 or 24×36. The hidden `*-original` drafts were not opened.
- The Ursa Major product body still says 1825 and is longer than the old short paragraph. Do not paste that paragraph over it. This run also did not add a public-domain sentence to it.
- NightLens (`duv5f8-wt`) was not edited. Its homepage still responds.

The same-day demand note was not in the repo when this run started. The Nov 11 demand note (`morning-reports/precheck-2026-11-11-trending-research.md`) did not open the shop. It still ranks a custom date-and-place star map ahead of these static plates. That map is not on this page. A static poster cannot take a date and a place.

## Needs his yes

- Preview "Dawn - Celestial page draft" (`188699902267`) in Admin, then decide whether that page should ever be published. Publishing would replace the placeholder with the moon mockup beside the solar-system mockup, put "18 by 24 inch" in the banner line, remove the repeated title, and show the Ursa Major mockup beside the Orion framed photo. Do not publish it from this note. Do not write live theme `188676014395`.
- Add the two Moon Phase sentences only if he wants the product page to say the chart is original artwork and not a photograph. Do not change its price.
- Add "The plate is public domain." to the Orion product, and the same sentence to the solar-system product, only if he wants those product pages to match the page. Do not change a price.
- Add the third collection sentence, the one that names the moon phases, Ursa Major, Orion, and the Copernican solar system, only if he wants it. Do not reorder the collection.
- Leave the Ursa Major description as it is. Do not change any price, including the $31.99 / compare-at $39.99 on the four posters.
- Leave the homepage size line alone unless he wants that copy changed. The replacement text is in the repo and was not written.
- Leave NightLens alone.
- A custom date-and-place star map, and a twelve-sign series, remain separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-12)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-12)
- Admin read of themes `188676014395` and `188699902267`, page `166674628923`, collection `512824901947`, and the four poster variants (read 2026-11-12)
- Existing shop files `ursa-major-mockup.jpg`, `orion-constellation-print-framed.jpg`, `moon-phases-mockup.jpg`, and `solar-system-mockup.jpg` (read 2026-11-12, not uploaded)

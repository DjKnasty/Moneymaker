# Store builder pre-check — 2026-11-09

The celestial paintings page on bhaeqw-9z still names four prints, in the order Moon Phase, Ursa Major, Orion, then the solar system, and the Celestial Paintings collection still lists the solar system before Orion. This run copied the live theme Dawn - Vintage Plate Co. Draft (188621029691) into an unpublished theme, Dawn - Celestial paintings draft (188676014395), and wrote `templates/page.celestial-paintings.json` on that copy only. The live theme still has no such file, the published page body was not changed, no price was changed, and NightLens was not touched. Thomas still needs to approve the extra page sentences, the collection reorder, the Ursa Major year correction from 1824 to 1825, and any preview or publish of that unpublished theme.

## What the storefront showed

Read first. The only Shopify writes were the unpublished theme copy and the one template file on that copy. Nothing was published.

- Shop `bhaeqw-9z`. Public name Vintage Plate Co. The connected admin shop is that store. Plan now reads Advanced. The Nov 7 note still said the trial plan had not been rechecked. This run did not change the plan.
- Theme served on the page: `188621029691`, name "Dawn - Vintage Plate Co. Draft", role main, Dawn 16.1.1. Its `config/settings_data.json` was already updated at `2026-11-09T04:17:18Z`, before this run, and already includes the Vintage Plate Co. wordmark and an OptiMonk app embed. This run did not edit that file. The unpublished copy inherited it.
- Page [Celestial paintings](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings), id `166674628923`, still published, body updated `2026-11-06T13:07:09-05:00`. The body is the same four-painting text as the Nov 7 read. It does not link to the collection, and it does not say that 24×36 is absent. Admin `templateSuffix` is already `celestial-paintings`. The live theme has no `templates/page.celestial-paintings.json`, so the storefront still renders the announcement bar, header, the default page body, and the footer. A request with `preview_theme_id=188676014395` was redirected back to that live theme. Buyers do not see the draft.
- Collection [Celestial Paintings](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings), id `512824901947`, four products, updated `2026-11-08T18:12:46-05:00`. Order is still Moon Phase, Ursa Major, Solar System, Orion. The description is still the two sentences from Nov 7. It does not list the four titles.
- Each of the four variants is still 18″×24″ matte, price $31.99, compare-at $39.99. Admin variant `updatedAt` is `2026-11-09T04:18:43Z` for Moon Phase, Ursa Major, and the solar system, and `2026-11-09T04:18:42Z` for Orion. This run did not write a price.
- The Ursa Major product text still says the plate was published in 1824. The page, `SPECS.md`, and `sources.json` say 1825.
- The main menu still has "Celestial paintings" pointing at the page.
- NightLens (`duv5f8-wt`) was not edited. Its homepage still responds.

## Prepared

- Unpublished theme `gid://shopify/OnlineStoreTheme/188676014395`, name "Dawn - Celestial paintings draft", role UNPUBLISHED, duplicated from the current main theme `188621029691`. It was not published. The live theme is still main.
- `templates/page.celestial-paintings.json` on that unpublished theme only, written `2026-11-09T13:39:12Z`. A read-back of the live theme still returns NOT_FOUND for that filename. The Nov 5 duplicate `188599370043` was not written. It still holds the older three-product template.
- The repo template now sets `show_description` to false and puts the grid sentence in a richtext paragraph. On this Dawn theme, `show_description: true` prints the collection description and ignores the custom sentence. The grid still reads collection `celestial-paintings`, four products, two desktop columns. It must stay off All Prints.
- `pages/celestial-paintings.html` is unchanged. It is still the proposed page body: the live sentences, the live order, a collection link, and a line that 24 by 36 inches is not on these listings. No price in the copy. It was not sent to the page.
- `celestial-paintings.apply.json` still has the collection reorder and the Ursa Major 1825 paragraph marked `apply: false`.

The draft theme's page section renders whatever body is already on the published page. Until Thomas approves the HTML, a preview of the draft shows the current four-painting text, plus the new banner and the four-product grid. The grid follows the collection, so the solar system still appears before Orion there.

The same-day demand note (`morning-reports/precheck-2026-11-09-trending-researcher.md`) did not open the shop. It still ranks a custom date-and-place star map ahead of these static plates. That map is not on this page. A static poster cannot take a date and a place.

## Not done

- The live page body was not replaced. The page's published state was not changed. `updatedAt` is still `2026-11-06T18:07:09Z`.
- The collection was not reordered, and its description was not edited.
- The Ursa Major year was not changed. No price was changed.
- The live theme file was not written. No theme was published.
- NightLens was not edited. Botanical plates, park posters, the sticker, and the hidden drafts were not edited.

## Needs his yes

- Preview "Dawn - Celestial paintings draft" in Admin, then decide whether that template should ever be published. Do not publish it from this note.
- Replace the live page body with `pages/celestial-paintings.html` only if he wants the collection link and the 24×36 line.
- Reorder the Celestial Paintings collection so it matches the page: Moon Phase, Ursa Major, Orion, Solar System. Only then add the extra description sentence. Until then, the draft grid and the page text disagree. Leave botanical plates, park posters, the sticker, and the hidden drafts out of that collection.
- Change the Ursa Major description year from 1824 to 1825, using the paragraph in `ursa_year_proposed`. Do not change its price.
- Leave every price as it is, including the $31.99 / compare-at $39.99 now on the four posters.
- Leave NightLens alone.
- A custom date-and-place star map, and a twelve-sign series, remain separate jobs.

## Sources

- [Celestial paintings page](https://bhaeqw-9z.myshopify.com/pages/celestial-paintings) (read 2026-11-09)
- [Celestial Paintings collection](https://bhaeqw-9z.myshopify.com/collections/celestial-paintings) (read 2026-11-09)
- Admin read of themes `188621029691` and `188676014395`, page `166674628923`, and the four poster variants (read 2026-11-09)
- Live theme `sections/featured-collection.liquid` and `sections/image-banner.liquid` (read 2026-11-09, not written)

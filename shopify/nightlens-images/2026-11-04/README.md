# NightLens — Scenario MCP test run (2026-11-04)

Test of the Scenario MCP connector (scenario-labs/skills) on the **free tier** using a real NightLens product photo. **Nothing was published.** The live Shopify store and the draft theme were not touched. No paid plan, card, or credit beyond the free 50 CU/day was used.

## Input

Real store photo, downloaded from duv5f8-wt.myshopify.com:

- `NightLens Pro` (product 15467531960688, handle `precision-reflector-telescope`)
- Original file `nightlens-pro-front.png` (768x1344 PNG), kept locally at `/workspace/nb/scenario/test-input/`
- Uploaded to Scenario as `asset_JStD641v9yT2v3r7ja7AnmrB`

## Skills exercised

| Skill | Result |
|---|---|
| `scenario-asset-analysis` | Built the fidelity checklist before any generation |
| `scenario-product-shots` | White packshot + two lifestyle scenes, each gated against the checklist |
| `scenario-brand-kit` | Palette-derived provisional logo in real SVG |
| `scenario-formats` | 1:1, 4:5 and 16:9 crops all derived from ONE approved master |

## Fidelity checklist (gate)

The source photo has **no printed text, labels, or logos anywhere** — so the label-fidelity check had nothing to compare against. The gate ran on shape, finish, and optic coating instead:

- ~2:1 truncated cylinder tube, four-vane spider with central secondary at the front
- Finderscope on top, right-angle eyepiece at the rear
- Articulated mount with large knobs on a flat circular base
- Satin-to-matte brushed metal; **dark gunmetal body**; purple/blue coated optics
- 9:16 three-quarter rear view angled up-left on dark navy bokeh

This is the caveat on the whole run: any real branded product shot in future should use a photo that actually shows the label, or the check is only structural.

## Outputs and gate results

| File | Model | CU | Gate |
|---|---|---|---|
| `packshot-white.png` | `model_photoroom-background-removal` (bg FFFFFF, soft shadow) | 3 | **PASS** — clean high-key cutout, product pixels preserved, soft contact shadow |
| `scene-desert.png` | `model_openai-gpt-image-2-5-flare` (reference img, 1088x1344, medium) | 4 | **PASS** — campsite, Milky Way, glowing tent, correct gunmetal finish |
| `scene-rooftop-FAILED-gate.png` | same model/params | 4 | **FAIL** — tube rendered silver instead of gunmetal. Kept for the record; needs a re-run |
| `crop-1x1-1080x1080.png` | `model_scenario-resize-image` (fit cover) | 2 | from desert master |
| `crop-4x5-1080x1350.png` | same | 2 | from desert master |
| `crop-16x9-1920x1080.png` | same | 2 | from desert master |
| `nightlens-logo-provisional.svg` | `model_recraft-v4-1-svg` | 16 | spells NIGHTLENS correctly; orange vanes bleed slightly outside the aperture ring |

Notes:

- `model_scenario-smart-reframe` quoted **45 CU** for a single 16:9 reframe and was rejected as too expensive; plain resize-cover was used instead. A free-tier budget cannot absorb smart-reframe.
- There was **no NightLens logo file in the store**, so the logo was generated from the palette (background `rgb(11,13,18)`, navy `rgb(16,32,74)`, orange `rgb(240,106,27)`). It is a real editable SVG (19 paths, viewBox 2048x1509) and is provisional, not the brand's real mark.
- `model_recraft-v4-styles-svg` refuses without a style ID or style reference images, so the plain `model_recraft-v4-1-svg` was used.

## Credit ledger — 35.25 of 50 free CU/day

- `model_recraft-v4-1-svg` (logo): **16**
- `model_openai-gpt-image-2-5-flare` (2 lifestyle scenes): **8**
- `model_scenario-resize-image` (3 crops): **6**
- `model_photoroom-background-removal` (packshot): **3**
- `model_scenario-llm` (fidelity checklist, gate checks, prompt refinement): **2.25**

About 14.75 CU remain today. Note: `consumption_limit_get` reports "unlimited / 0" on the free tier and does not reflect the daily cap. Track spend with the `usage` tool for the current day.

## Store usability

- **Usable now:** the white packshot (clean PDP-ready cutout) and the desert night scene (hero/collection imagery, passes the gate).
- **Usable with a caveat:** the three crops, if you accept resize-cover cropping of the master.
- **Not usable:** the rooftop scene (wrong finish) and the provisional logo (vanes bleed, and it is not the real brand mark).
- None of this replaces real photography of the actual product for a live PDP.

## Reproduce / where things live

- Scenario collection: `col_mUavV4326vjKgtZAVAYboSML` — "NightLens Scenario Test 2026-11-04"
- Local working files: `/workspace/nb/scenario/` (`gate-verdict.txt`, `gate-lines.txt`, `logo-gate.txt`, `out/`)
- This folder in the repo holds the deliverables committed today.

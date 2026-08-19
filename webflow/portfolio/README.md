# Spotlight Media — Portfolio page build

Rebuild of the design handoff (`Spotlight_Homepage_Redesign_6.zip`, the Portfolio
bundle). Reuses the Header/Footer components and `../homepage/global.css` tokens
already built for the homepage — this page only adds new component classes for
its own content (site cards, model cards, analytics cards).

## Files

| File | What it is |
|---|---|
| `portfolio-body.html` | Portfolio page content only (hero → analytics), no header/footer — this is what goes in the Embed |
| `index.html` | Full page: header + body + footer stitched together, for browser preview |
| `uploads/` | The three site icons this page uses |

New CSS was appended to `../homepage/global.css` (not a separate stylesheet) —
see the "Portfolio page" section near the bottom of that file. Since the site's
Head Code is one shared stylesheet, just add that section to what's already
pasted in Site Settings → Custom Code → Head Code; no need to touch the rest.

## What's reused vs new

- **Header/footer**: identical to the homepage — same Embeds/Components, no changes.
- **Hero**: reuses `.header-band` + `.hero` classes from the homepage, with this
  page's own padding/max-width as inline overrides (92px/1180px vs the homepage's
  100px/1000px) — same pattern used throughout for page-specific padding.
- **New classes**: `.sites-grid`/`.scard` (site cards with fact list + progress
  bar), `.model-grid`/`.model-card` (the three navy-section cards), `.analytics-grid`/
  `.acard` (the three stat cards with the mint rounded-corner icon tile — the only
  rounded element on the site, per the handoff).

## Responsive behaviour authored

Per the handoff's own guidance: all three grids on this page (sites, model,
analytics) collapse from 3 columns to 1 at ≤900px, keeping source order. No
other breakpoint changes were needed — the hero/section-heading responsive
rules already exist from the homepage build and apply here automatically.

## Icons — need uploading

Three brand icons need uploading to Webflow's Asset Manager, same process as
the homepage images:

| File | Note |
|---|---|
| `uploads/aquaswitch-icon.svg` | Safe to use as-is — uses inline `fill` attributes, not a `<style>` block, so it won't hit the black-icon bug flagged in the homepage handoff |
| `uploads/business-energy-deals-icon.png` | Renamed from the original `BED_Icon_Color...` filename per the handoff's own note |
| `uploads/business-broadband-hub-icon.png` | Different icon from the homepage's Business Broadband Hub icon — this one is a signal/wifi mark, not the "eye" mark used on the homepage. Both are real, just for different contexts; don't assume they're interchangeable |

Note the AquaSwitch icon here is a different file (SVG, diagonal-line mark) from
the homepage's AquaSwitch icon (PNG) — visually the same brand mark, different
export. Reuse the homepage's already-uploaded AquaSwitch asset if you'd rather
not upload a duplicate; otherwise upload this SVG version.

## Data note (from the handoff)

The progress bars (site completion %) and analytics breakdown bars are static
widths in this build, matching the handoff exactly. If this data updates
regularly, the handoff recommends making these CMS fields (a percentage
driving `width`) rather than hand-edited values — worth a follow-up if so.

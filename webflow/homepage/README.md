# Spotlight Media — Homepage build

Rebuild of the design handoff (`Spotlight_Homepage_Redesign_5.zip`), split into
global components and a page-specific body, with the responsive behaviour the
original prototype didn't include.

## Files

| File | What it is |
|---|---|
| `global.css` | Design tokens (CSS variables) + every shared/component class, including all responsive media queries |
| `header.html` | Header component in isolation — nav, logo, dropdown, mobile burger |
| `footer.html` | Footer component in isolation — CTA band + legal bar |
| `homepage-body.html` | Homepage content only (hero → team), no header/footer |
| `index.html` | Full page: header + body + footer stitched together, for browser preview |
| `uploads/`, `assets/` | Images and favicons, carried over from the source handoff (renamed — see below) |

Open `index.html` directly in a browser to preview the whole page; no build step.

## Why it's split this way

- **`header.html` / `footer.html`** are the two pieces that repeat on every page.
  In Webflow, build each once as a **Component** and drop it onto every page —
  edit once, it updates everywhere.
- **`homepage-body.html`** is everything unique to this page. Other pages
  (Portfolio, Process, the two service pages) get their own body file, reusing
  the same header/footer components and `global.css` tokens.
- **`global.css`** is the shared source of truth for colour, type, spacing, and
  component styling — pull it in via Project Settings → Custom Code → Head Code
  in Webflow (wrapped in `<style>` tags), or use it as the reference when
  setting up Webflow's own Variables/Style Guide, so header, footer, and every
  page body stay in sync instead of drifting apart.

## What changed from the design handoff

The handoff was intentionally high-fidelity but desktop-only, inline-styled,
and not meant to ship as-is (see its own README). To make it Webflow-ready:

1. **Inline styles → classes.** Webflow styles through classes, not inline
   attributes, and inline styles can't be overridden by media queries without
   `!important` hacks. Every layout/colour/spacing value from the original is
   preserved, just moved into named classes in `global.css`.
2. **Responsive behaviour authored**, per the handoff's own guidance:
   - Gutter: 72px desktop → 40px ≤1100px → 24px ≤760px.
   - Team grid: 4 → 2 columns at ≤1100px → 1 column at ≤760px.
   - "Why we're different", services intro, service tiles, and portfolio grid:
     all collapse to 1 column at ≤900px (portfolio's 2-column text indent
     resets to full width at the same point).
   - Hero H1 and section H2s scale down at ≤760px; the footer CTA band stacks
     vertically and its button goes full-width.
   - **Nav**: collapses to a burger menu below 900px. The "Our Services"
     dropdown and the burger both use a hidden-checkbox + `<label>` CSS
     pattern, so tapping to open works with **zero JavaScript** — consistent
     with the original prototype's no-JS approach. Desktop keeps the original
     hover behaviour, plus `:focus-within` for keyboard users.
3. **Filename fix**: `BBH_Icon_Light Blue.png` (space in the name, flagged in
   the handoff README) is renamed `business-broadband-hub-icon.png`. All
   `uploads/` and `assets/` files were renamed to short, descriptive,
   space-free names.
4. **Placeholder links preserved as-is**: service tiles 03/04 and the
   portfolio card links still point to `#`, matching the handoff — those
   destination pages don't exist yet.

## One design decision worth flagging

The header's navy gradient is deliberately meant to "bleed into" the hero
directly below it (per the handoff notes) so they read as one band. Here,
the header component carries its own gradient (self-contained, so it looks
correct on any page), and the homepage hero continues the same gradient
colours immediately below it. Because they're two separate elements, there's
a theoretical seam — in practice, at the header's actual height, it isn't
visible, but if you want the two guaranteed pixel-identical, the alternative
is dropping the header markup *inside* the hero's gradient wrapper on the
homepage only, transparent, and letting the page section supply the colour.
Worth deciding once you know whether other pages reuse this same "gradient
band" treatment.

## Not yet built

The header's dropdown links, "Our Services"/"Our Portfolio"/"Our Process"
nav items, and hero CTA all point to sibling pages (Portfolio, Process, the
two service pages) that don't exist in this bundle yet — same as the
original handoff. Say if you want those built next; the component split
here means header/footer are already done for them.

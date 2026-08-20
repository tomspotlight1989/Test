# Spotlight Media — Key Page Content Optimisation page build

Rebuild of the design handoff's `design_handoff_key-page-content` bundle
(from `Key_Page.zip`). Reuses most of the Header component and
`../homepage/global.css` tokens already built, but with two deliberate
exceptions — see below.

## Files

| File | What it is |
|---|---|
| `key-page-content-body.html` | Page content, **including its own footer** (see "Light CTA" below) — this is what goes in the Embed |
| `index.html` | Full page: header + body (with its own footer) stitched together, for browser preview |

New CSS was appended to `../homepage/global.css` — see the "Key Page Content
Optimisation page" section near the bottom of that file.

## Two deliberate exceptions to the shared components

1. **Light CTA — this page does NOT use the shared Footer component.**
   Every other page's CTA band is dark navy. This page's section immediately
   above the CTA is already dark ("We set your team up for the future"), so
   the handoff specifies a **light** CTA band here instead — otherwise the
   two dark sections would visually merge into one. Rather than adding a
   light/dark toggle to the shared Footer component for a variant only one
   page uses, this page carries its own CTA + legal bar markup at the end of
   `key-page-content-body.html`. **Don't drop the shared Footer
   Embed/Component on this page** — this page's body Embed already includes
   it, with the light variant (`.cta-band--light`, `.cta-band__heading--on-light`,
   `.cta-band__content`, `.cta-band__body`) and different button copy
   ("Request pricing →" vs "Get in touch →").
2. **Header's "Our Services" nav item is active on this page** (mint text +
   mint underline, via the new `.nav-link--active` class) — matches the
   handoff exactly. This is a one-line difference from the standard header
   snippet (add `nav-link--active` alongside `nav-link` on that one item);
   the Tune-Up page will need the same treatment.

## What's new

- **`.herogrid` / `.herocol` / `.sublab`**: the three-column hero framing
  block ("The challenge" / "Our approach" / "The difference") — an eyebrow
  label over a paragraph, repeated three times. `.sublab` is flagged in the
  handoff as a reusable eyebrow-label component worth keeping.
- **`.hero__standfirst`**: the large (26px/600) white lead paragraph unique
  to this page's hero — heavier than the standard `.hero__lead` used
  elsewhere.
- **`.subheader-band` (+ `--mint` / `--navy` modifiers)**: the small banner
  introducing the rule table ("Our experts use the following data led
  approach"). Mint-on-navy here; the handoff notes the Tune-Up page uses the
  navy-on-white version of the same component — both modifiers are included
  now so that page can reuse this without another CSS pass.
- **`.diff-card__title`**: an optional title between the number and body on
  `.diff-card` (used in "How does it work?"), with colour set correctly for
  both the navy and white card variants — the "Who's it for?" cards reuse
  the existing `.diff-card` as-is, no title.
- **`--row-label-width`**: `.prow`/`.drow` now read this CSS variable (falling
  back to `250px`) for their label-column width, since this page's rule
  table uses `280px` where the Process page used `250px`. Set via an inline
  `style="--row-label-width:280px"` on the wrapping div — no class
  duplication needed.

## Responsive behaviour authored

- `.herogrid` collapses to 1 column at ≤900px (this was the *only* responsive
  rule in the original prototype — everything else here follows the same
  breakpoints already established for the rest of the site).
- Rule table and card-grid collapse rules are unchanged/reused from the
  Process and Portfolio builds.

## No images

Entirely type and rules, by design — same as the Process page.

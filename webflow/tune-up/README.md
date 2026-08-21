# Spotlight Media — Hands-On SEO Tune-Up page build

Rebuilt per the revised handoff (`Spotlight_Homepage_Redesign_7.zip`), which
supersedes the first Tune-Up build in full. This version brings the page's
visual pattern in line with Key Page Content Optimisation, and — unlike the
first build — **does** need its own header/footer treatment.

## Files

| File | What it is |
|---|---|
| `tune-up-body.html` | Page content, **including its own footer** (light CTA + legal bar) — this is what goes in the Embed |
| `index.html` | Full page: header (with active nav state) + body + own footer, for browser preview |

## What changed from the first build

1. **Hero** replaced entirely — now the `.herogrid`/`.sublab`/`.hero__standfirst`
   pattern (The challenge / Our approach / The difference), same shape as Key
   Page Content's hero, instead of three plain paragraphs.
2. **"Who is it for?" and "How does it work?" cards** now alternate
   navy/white/navy (`.diff-card--navy`/`.diff-card--white`) instead of being
   uniformly white.
3. **"How does it work?"'s card grid uses a mint hairline** (`background:
   var(--mint);border-color:var(--mint)` inline override on `.diff-grid`)
   instead of navy — deliberate, per the handoff, to visually separate it
   from "Who is it for?"'s navy hairline grid.
4. **"What's included?" moved onto the full navy gradient** (`.site-header`),
   with **mint** sub-header bands (`.subheader-band--mint`) and `.drow` rows
   instead of a flat ground with navy bands and `.prow` rows.
5. **"We set your team up for the future"** now uses the standard light
   gradient (`--grey-1` → `--page`) instead of the mint-wash gradient.
6. **A mint rule was added** between "We set your team up for the future"
   and "How does it work?" — the first build had a deliberate gap here;
   this revision closes it.
7. **The page now ends with its own light CTA + legal bar**
   (`.cta-band--light`), not the shared dark Footer — reintroduces the
   `.cta-band--light`/`.cta-band__content`/`.cta-band__heading--on-light`/
   `.cta-band__body` classes that were removed from `global.css` when Key
   Page Content was simplified to the standard footer. **Do not drop the
   shared Footer component on this page** — the body Embed already includes
   its own footer at the end.
8. **Header now needs "Our Services" marked active** (`nav-link--active`
   alongside `nav-link`), matching Key Page Content.
9. Minor copy fixes: "Hands-On" hyphenated throughout (previously "Hands
   On" in some places), "of our established website" → "of your
   established website", a few de-hyphenations ("clean-up" → "clean up",
   "one-off" → "one off", etc. — matched exactly as given).

## No new CSS beyond what already existed

Every class this page needs (`.herogrid`, `.subheader-band--mint`, `.drow`,
`--row-label-width`, `.diff-card--navy`/`--white`, `.nav-link--active`) was
already built for Key Page Content or earlier pages. The only additions to
`global.css` were re-adding the light-CTA classes that had been removed.

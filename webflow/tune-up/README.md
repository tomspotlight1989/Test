# Spotlight Media — Hands On SEO Tune-Up page build

Rebuild of the design handoff's `design_handoff_tune-up` bundle (from
`Tune_Up.zip`). By request, this page skips two things the original handoff
specifies, for consistency with the Key Page Content page's build:

- **No active nav state.** The handoff has "Our Services" showing the mint
  active state on this page (same as Key Page Content). Not built here —
  the standard header is used unchanged.
- **No page-specific CTA.** The handoff specifies a two-part "Request
  pricing for your site." CTA (heading + supporting paragraph + "Request
  pricing →" button), same pattern as Key Page Content originally had. Not
  built here — the standard shared Footer component ("Let's talk about your
  organic visibility." + "Get in touch →") is used instead.

## Files

| File | What it is |
|---|---|
| `tune-up-body.html` | Page content only (hero → how it works), no header/footer — this is what goes in the Embed |
| `index.html` | Full page: standard header + body + standard footer, for browser preview |

## No new global CSS needed

Every component on this page reuses classes already built for earlier
pages — nothing was added to `global.css`:

- **Hero**: standard `.header-band`/`.hero`/`.hero__title`, with the three
  lead paragraphs as plain inline-styled `<p>` tags in a flex column (same
  pattern as the Process page's hero) — smaller (18px) than the standard
  `.hero__lead` since there are three of them, per the handoff.
- **"Who is it for?" / "How does it work?" cards**: reuse `.diff-grid` +
  `.diff-card diff-card--white` applied to *all three* cards (no
  navy/white alternation on this page — every card is white with hairline
  navy divider lines). `.diff-card__title` (added for the Key Page Content
  page) is reused for "How does it work?"'s titled cards.
- **"What's included?" rule tables**: reuse `.prow-table`/`.prow`/`.prow-t`/
  `.prow-b`, with `--row-label-width:280px` (same override technique as Key
  Page Content) and `.subheader-band subheader-band--navy` for the two
  "Here's what..." banners — the navy variant of the component that was
  built mint for Key Page Content, exactly as that page's README
  anticipated.
- **"We set your team up for the future"**: no cards, just heading +
  paragraphs in a flex column — identical pattern to the same-titled
  section on Key Page Content.

## Minor fidelity note

The handoff's "How does it work?" card body copy is 18px/1.55 while "Who is
it for?"'s is 19px/1.5 — both reuse `.diff-card__text`, so the 18/1.55
variant is applied via an inline style override on those three paragraphs
rather than a new class, consistent with how other small per-instance
differences have been handled throughout this build.

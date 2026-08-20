# Spotlight Media — Process page build

Rebuild of the design handoff's `03-process` bundle (from `Spotlight_Our_Process_Hand_Off.zip`,
which turned out to contain all five pages' handoffs — only the Process folder
was used here). Reuses the Header/Footer components and `../homepage/global.css`
tokens already built. No images on this page at all — it's entirely type and
rule tables.

## Files

| File | What it is |
|---|---|
| `process-body.html` | Process page content only (hero → authority), no header/footer — this is what goes in the Embed |
| `index.html` | Full page: header + body + footer stitched together, for browser preview |

New CSS was appended to `../homepage/global.css` — see the "Process page"
section near the bottom of that file. Add it to the same Head Code block
already in place; nothing else needs to change.

## What's new

- **`.prow` / `.prow-table`**: the light rule-table row (label + body, 250px/1fr
  grid) used in "The basics", "Page architecture", and "Authority and
  reputation". Hover opens the row slightly (background tint + horizontal
  padding) — matches the handoff exactly.
- **`.drow` / `.drow-table`**: the on-navy variant of the same row. Not used on
  this page, but the handoff explicitly calls out keeping it in the shared
  layer since the two service pages (Tune-Up, Key Page Content) use it.
- **`.dnum-grid` / `.dnum`**: the numbered-criteria card, used twice — once as
  a 4-column grid ("Criteria for new content") and once as 3-column with an
  added title ("Data-led optimisation"). Two modifier classes
  (`.dnum-grid--four` / `.dnum-grid--three`) share the same card styling and
  only differ in column count and responsive collapse point.

## Responsive behaviour authored

Per the handoff's guidance:
- `.dnum-grid--four` (4→2 columns at ≤1100px, →1 at ≤900px)
- `.dnum-grid--three` (stays 3 columns until ≤900px, then →1)
- `.prow` / `.drow` rows stack (label above body) at ≤900px, replacing the
  `250px 1fr` grid with a single column
- Hero H1 and section H2 scaling reuses the rules already added for the
  homepage — no page-specific overrides needed here

## Note on the shared footer

The handoff's CTA band on this page uses a slightly different gradient stop
(`50%` vs the `55%` used elsewhere) and wraps its content in an extra inner
div. Since the Footer is a shared global Component, this page reuses it
as-is rather than introducing a one-off variant for a difference this
small — consistent with the whole point of building header/footer once.

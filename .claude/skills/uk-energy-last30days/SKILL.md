---
name: uk-energy-last30days
description: Research a UK energy-industry topic using real signals from the last 30 days — Reddit, Hacker News, GitHub, arXiv, Polymarket, Bluesky, GOV.UK/Ofgem, and UK trade press out of the box, plus optional X, YouTube, TikTok, Instagram, Threads, LinkedIn, Pinterest, Perplexity, and Brave Search — and write a markdown research guide.
---

# UK Energy /last30days

A UK-energy-focused adaptation of [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill):
instead of relying on editorial curation, it aggregates what Reddit, Hacker
News, GOV.UK, UK trade press, prediction markets, and (optionally) social
platforms have actually said about a topic in the last 30 days, ranks it by
real engagement and freshness, and turns it into a saved markdown guide.

The Python script under `scripts/` only fetches, dedupes, and ranks data —
it deliberately does not generate prose. **You (the invoking agent) are the
synthesis step**: read its structured output and write the actual guide.

## When to use this skill

Invoke it when the user asks to research, track, or write a guide about
anything in the UK energy industry — e.g. `/uk-energy-last30days offshore
wind CfD auction`, or "what's the latest on the price cap", "build me a
guide on SMRs", "what's happening with the grid connection queue".

## Steps

1. **Parse the topic** from the user's request or slash-command arguments.
   If it's ambiguous or very broad (e.g. just "energy"), ask a brief
   clarifying question before running — a focused topic produces a much
   better guide than a generic one.

2. **Run the pipeline** from this skill's directory:

   ```bash
   python3 scripts/uk_energy_search.py "<topic>" --emit json
   ```

   First time in a fresh environment, install dependencies:
   `pip install -r requirements.txt` (or use the checked-in `.venv` if one
   exists). If the user has set up any optional credentials (see
   `docs/SOURCES.md`), they'll be picked up automatically from `.env` or the
   shell environment — no flag needed.

   Useful flags:
   - `--since-days N` — change the lookback window (default 30).
   - `--as-of YYYY-MM-DD` — treat a past date as "today", for a historical run.
   - `--only source1,source2` — restrict to specific sources (names from `docs/SOURCES.md`).
   - `--diagnose` — report which sources are configured, instead of researching a topic.

3. **Read the JSON output.** Its shape:

   ```json
   {
     "topic": "...", "generated_at": "...", "window_days": 30,
     "source_status": {"reddit": {"ok": true, "count": 4}, "x": {"ok": false, "reason": "not_configured", ...}},
     "total_raw_items": 37, "total_clusters": 21,
     "ranked": [
       {"score": 12.4, "sources": ["reddit", "govuk"], "representative": {"title": "...", "url": "...", "snippet": "...", "engagement_label": "..."}, "items": [...] }
     ]
   }
   ```

   `ranked` is already sorted best-first by a blend of engagement, freshness,
   and topic/UK-energy relevance, with cross-source duplicates merged into a
   single cluster (`sources` shows which platforms covered it).

4. **Write the guide** as markdown and save it to `guides/<topic-slug>.md`
   (slug = lowercase, non-alphanumerics replaced with `-`, matching what the
   script itself would use for `--save-dir`). Use this structure:

   ```markdown
   # <Topic> — UK Energy Guide
   _Generated <date> · last <window_days> days · <total_clusters> stories from <N> sources_

   ## Summary
   2-4 sentences on what's actually going on, grounded only in the ranked items below.

   ## Key developments
   Group the top-ranked clusters into 2-5 natural themes (e.g. regulatory,
   commercial, community reaction, market signal). Under each theme, a few
   bullets citing specific items — what happened, who said it, and the
   engagement signal (e.g. "420 upvotes on r/unitedkingdom", "$40k traded on
   Polymarket") so the reader can judge how strong the signal is.

   ## Regulatory & policy signals
   Anything sourced from GOV.UK, Ofgem, or NSTA — call these out separately
   since they're authoritative rather than just "buzz".

   ## Sources
   A table or list of every URL cited above, with source platform and date.
   ```

   Do not invent facts beyond what's in the ranked items — if coverage is
   thin, say so plainly rather than padding the guide.

5. **Report back to the user**: a short summary (not the whole guide) plus
   the saved file path. Mention any source that failed with `reason:
   "not_configured"` only if it's plausibly relevant (e.g. X/YouTube missing
   on a topic that's clearly trending on social) — don't list every unset
   credential every time.

## Building a series of guides

If the user wants ongoing coverage of a topic area (not just one run), treat
each invocation as independent — save a new dated guide, or ask whether they
want the existing `guides/<topic>.md` updated in place instead of a new file.

## Notes

- This intentionally mirrors the original last30days' "zero-config sources
  work immediately, others degrade gracefully" design — see `docs/SOURCES.md`
  for exactly which sources need which credential, and `docs/SETUP.md` for
  how to get them.
- `guides/` is checked into this repo so research builds into a durable,
  browsable library over time.

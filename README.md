# UK Energy /last30days

A Claude Code skill for researching the UK energy industry using real
signals from the last 30 days, adapted from
[mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill).

Instead of relying on editorial curation, it aggregates what Reddit, Hacker
News, GOV.UK/Ofgem, UK trade press, prediction markets, and (optionally)
social platforms have actually said about a topic recently, ranks it by
engagement and freshness, and turns it into a saved markdown guide under
[`guides/`](guides/).

## Quick start

```bash
cd .claude/skills/uk-energy-last30days
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/uk_energy_search.py "offshore wind CfD auction" --emit summary
```

No API keys are required for Reddit, Hacker News, GitHub, arXiv, Polymarket,
Bluesky, GOV.UK, UK trade press, Techmeme, or StockTwits. X, YouTube,
TikTok, Instagram, Threads, LinkedIn, Pinterest, Perplexity, and Brave
Search are supported too, but need credentials — see
[`docs/SOURCES.md`](.claude/skills/uk-energy-last30days/docs/SOURCES.md) and
[`docs/SETUP.md`](.claude/skills/uk-energy-last30days/docs/SETUP.md).

## Using it inside Claude Code

Open this repo in Claude Code and invoke the skill directly:

```
/uk-energy-last30days offshore wind CfD auction
```

Claude runs the pipeline, reads its ranked/structured output, writes the
narrative guide, and saves it to `guides/<topic-slug>.md`. The full
step-by-step contract is in
[`.claude/skills/uk-energy-last30days/SKILL.md`](.claude/skills/uk-energy-last30days/SKILL.md).

## Repo layout

```
.claude/skills/uk-energy-last30days/
  SKILL.md              Instructions Claude follows when the skill runs
  scripts/               The research pipeline (fetch → dedupe → score)
  docs/                  Source list and credential setup
  tests/                 pytest suite (mocked HTTP, no live network needed)
guides/                  Generated research guides land here
```

## Running the tests

```bash
cd .claude/skills/uk-energy-last30days
source .venv/bin/activate  # after the quick-start setup above
python -m pytest tests/ -v
```

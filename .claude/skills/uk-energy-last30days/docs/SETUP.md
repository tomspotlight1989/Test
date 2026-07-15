# Setup

## Zero-config sources

Reddit, Hacker News, GitHub, arXiv, Polymarket, Bluesky, GOV.UK, UK trade
press, Techmeme, and StockTwits all work with no setup. Install the Python
dependencies and you can run a real research query immediately:

```bash
cd .claude/skills/uk-energy-last30days
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/uk_energy_search.py "offshore wind CfD auction" --emit summary
```

## Adding credentialed sources

Copy `.env.example` to `.env` in this directory and fill in whichever of
these you have. Every one is optional — the pipeline just skips a source it
isn't configured for.

| Variable | Where to get it |
|---|---|
| `GITHUB_TOKEN` | github.com/settings/tokens — a classic PAT with no scopes is enough, it's only used to raise the search rate limit. |
| `X_BEARER_TOKEN` | developer.x.com — create a project/app, needs at least Basic API access for recent search. |
| `YOUTUBE_API_KEY` | console.cloud.google.com — enable the "YouTube Data API v3", create an API key. |
| `PERPLEXITY_API_KEY` | perplexity.ai/settings/api |
| `BRAVE_API_KEY` | brave.com/search/api |
| `SCRAPECREATORS_API_KEY` | scrapecreators.com — a single key unlocks TikTok, Instagram, Threads, Pinterest, LinkedIn, and Xiaohongshu. |

After adding any of these, run:

```bash
python3 scripts/uk_energy_search.py --diagnose
```

to confirm what's active.

## Running as a Claude Code skill

This directory is a project skill (`.claude/skills/uk-energy-last30days/SKILL.md`).
Once this repo is open in Claude Code, invoke it as:

```
/uk-energy-last30days offshore wind CfD auction
```

Claude runs the script, reads the ranked/structured JSON it prints, writes
the narrative guide, and saves it to `guides/<topic-slug>.md`. See SKILL.md
for the exact contract Claude follows.

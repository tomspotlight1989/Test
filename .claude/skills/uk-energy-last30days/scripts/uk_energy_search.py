#!/usr/bin/env python3
"""CLI entry point for the UK Energy /last30days research skill.

Fetches, dedupes, and ranks UK energy-industry signals from the last 30
days (or a custom window) across 15+ zero-config and credentialed sources,
then prints structured JSON. This script deliberately does NOT write prose
itself — see SKILL.md for how the invoking agent should read this output
and author the actual narrative guide.

Examples:
    python3 uk_energy_search.py "offshore wind CfD auction"
    python3 uk_energy_search.py "hydrogen strategy" --since-days 14 --emit summary
    python3 uk_energy_search.py --diagnose
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import diagnose as diagnose_mod
from pipeline import WINDOW_DAYS, build_brief_data
from sources import SOURCE_REGISTRY


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="uk_energy_search.py", description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("topic", nargs="*", help="Topic to research, e.g. 'offshore wind CfD auction'")
    parser.add_argument("--since-days", type=int, default=WINDOW_DAYS,
                         help="Lookback window in days (default 30)")
    parser.add_argument("--as-of", type=str, default=None,
                         help="ISO date to treat as 'today', e.g. 2026-03-01 (for historical runs)")
    parser.add_argument("--only", type=str, default=None,
                         help="Comma-separated list of source names to restrict to")
    parser.add_argument("--emit", choices=["json", "summary"], default="json")
    parser.add_argument("--save-dir", type=str, default=None,
                         help="Directory to write a raw JSON snapshot to (optional)")
    parser.add_argument("--diagnose", action="store_true",
                         help="Report source availability/configuration and exit")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    config.load_env()

    if args.diagnose:
        diagnose_mod.run()
        return 0

    topic = " ".join(args.topic).strip()
    if not topic:
        print("error: a topic is required (or pass --diagnose)", file=sys.stderr)
        return 2

    as_of = datetime.now(timezone.utc)
    if args.as_of:
        as_of = datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc)
    since = as_of - timedelta(days=args.since_days)

    only = [s.strip() for s in args.only.split(",")] if args.only else None
    if only:
        unknown = set(only) - set(SOURCE_REGISTRY)
        if unknown:
            print(f"error: unknown source(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            print(f"available: {', '.join(sorted(SOURCE_REGISTRY))}", file=sys.stderr)
            return 2

    data = build_brief_data(topic, since, only=only)

    if args.save_dir:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        slug = "".join(c if c.isalnum() else "-" for c in topic.lower()).strip("-")
        snapshot_path = save_dir / f"{slug}.raw.json"
        snapshot_path.write_text(json.dumps(data, indent=2))
        data["_snapshot_path"] = str(snapshot_path)

    if args.emit == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_summary(data)
    return 0


def _print_summary(data):
    print(f"Topic: {data['topic']}")
    print(f"Window: last {data['window_days']} days (since {data['since']})")
    print(f"{data['total_clusters']} clustered stories from {data['total_raw_items']} raw items\n")
    for i, cluster in enumerate(data["ranked"][:15], 1):
        rep = cluster["representative"]
        print(f"{i}. [{cluster['score']}] {rep['title']}  ({', '.join(cluster['sources'])})")
        print(f"   {rep['url']}")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Watch the Google Search Status Dashboard feed for core updates.

One GitHub issue per core update (incident). Each new status entry
(announcement, release, rollout complete...) is posted as a comment, and the
issue is closed when Google marks the update RESOLVED. Issues are the state:
markers in issue bodies/comments record which entries were already posted.

Env:
  FEED_URL       feed to read (default: Google's Atom feed)
  FEED_FILE      read the feed from a local file instead (for testing)
  MATCH          regex matched against entry titles (default: "core update")
  MAX_AGE_DAYS   ignore entries older than this (default: 14)
  ASSIGNEE       GitHub user to assign new issues to (triggers a notification)
  LABEL          issue label (default: core-update)
  DRY_RUN=1      print what would happen, change nothing
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
FEED_URL = os.environ.get("FEED_URL", "https://status.search.google.com/en/feed.atom")
MATCH = re.compile(os.environ.get("MATCH", r"core update"), re.I)
MAX_AGE = timedelta(days=int(os.environ.get("MAX_AGE_DAYS", "14")))
ASSIGNEE = os.environ.get("ASSIGNEE", "").strip()
LABEL = os.environ.get("LABEL", "core-update")
DRY_RUN = os.environ.get("DRY_RUN") == "1"


def load_feed():
    if os.environ.get("FEED_FILE"):
        with open(os.environ["FEED_FILE"], "rb") as f:
            return f.read()
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "core-update-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def html_to_text(s):
    s = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", s, flags=re.S)
    s = re.sub(r"<strong>(.*?)</strong>", r"**\1**", s, flags=re.S)
    s = re.sub(r"<hr\s*/?>", "\n\n---\n\n", s)
    s = re.sub(r"</p>|<br\s*/?>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(l.strip() for l in s.splitlines())).strip()


def parse(feed_bytes):
    root = ET.fromstring(feed_bytes)
    out = []
    for e in root.findall("a:entry", NS):
        title = (e.findtext("a:title", "", NS) or "").strip()
        if not MATCH.search(title):
            continue
        link_el = e.find("a:link", NS)
        link = link_el.get("href") if link_el is not None else ""
        out.append({
            "title": title,
            "status": title.split(":", 1)[0].strip().upper() if ":" in title else "",
            "name": title.split(":", 1)[-1].strip(),
            "link": link,
            "incident": link.rstrip("/").rsplit("/", 1)[-1],
            "id": e.findtext("a:id", "", NS).strip(),
            "updated": datetime.fromisoformat(e.findtext("a:updated", "", NS).strip()),
            "text": html_to_text(e.findtext("a:summary", "", NS) or ""),
        })
    return sorted(out, key=lambda x: x["updated"])


def gh(*args, input=None):
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=True, input=input).stdout


def existing_issues():
    if DRY_RUN and not os.environ.get("GH_TOKEN"):
        return []
    data = gh("issue", "list", "--label", LABEL, "--state", "all", "--limit", "200",
              "--json", "number,state,body,comments")
    return json.loads(data)


def entry_body(e, heading):
    return (f"{heading}\n\n{e['text']}\n\n"
            f"Updated: {e['updated'].isoformat()} · [View on the status dashboard]({e['link']})\n\n"
            f"<!-- entry:{e['id']} -->")


def main():
    entries = parse(load_feed())
    issues = existing_issues()
    cutoff = datetime.now(timezone.utc) - MAX_AGE
    posted = 0

    for e in entries:
        if e["updated"] < cutoff:
            continue
        inc_marker = f"<!-- incident:{e['incident']} -->"
        entry_marker = f"<!-- entry:{e['id']} -->"
        issue = next((i for i in issues if inc_marker in (i.get("body") or "")), None)

        if issue:
            texts = [issue.get("body") or ""] + [c.get("body") or "" for c in issue.get("comments", [])]
            if any(entry_marker in t for t in texts):
                continue
            print(f"comment #{issue['number']}: {e['title']}")
            if not DRY_RUN:
                gh("issue", "comment", str(issue["number"]), "--body-file", "-",
                   input=entry_body(e, f"### {e['title']}"))
                if issue["state"] == "CLOSED" and e["status"] != "RESOLVED":
                    gh("issue", "reopen", str(issue["number"]))
                    issue["state"] = "OPEN"
            issue.setdefault("comments", []).append({"body": entry_marker})
        else:
            print(f"open issue: Google {e['name']} ({e['status'] or 'NEW'})")
            body = entry_body(e, f"Google posted a **{e['status'] or 'new'}** status for the **{e['name']}**.") \
                + f"\n{inc_marker}"
            issue = {"number": None, "state": "OPEN", "body": body, "comments": []}
            if not DRY_RUN:
                args = ["issue", "create", "--title", f"Google {e['name']}", "--label", LABEL,
                        "--body-file", "-"]
                if ASSIGNEE:
                    args += ["--assignee", ASSIGNEE]
                url = gh(*args, input=body).strip()
                issue["number"] = int(url.rsplit("/", 1)[-1])
            issues.append(issue)
        posted += 1

        if e["status"] == "RESOLVED" and issue["state"] == "OPEN":
            print(f"close issue for {e['name']}")
            if not DRY_RUN and issue["number"]:
                gh("issue", "close", str(issue["number"]), "--reason", "completed")
            issue["state"] = "CLOSED"

    print(f"done: {posted} new core-update entr{'y' if posted == 1 else 'ies'}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as err:
        sys.stderr.write(err.stderr or "")
        raise

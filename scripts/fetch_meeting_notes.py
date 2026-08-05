#!/usr/bin/env python3
"""
Fetch and parse weekly meeting notes from a Google Doc.

Uses the gws CLI to export the doc as plain text, then parses
date-headed entries and returns recent ones as JSON.

Adapted from the weekly-jira-report skill's fetch_notes.py pattern.

Usage: python3 fetch_meeting_notes.py <GOOGLE_DOC_ID> [--days 14]
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from shutil import which

MONTH_NAMES = (
    "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
)
DATE_HEADER_RE = re.compile(
    rf"^({MONTH_NAMES})\s+(\d{{1,2}}),\s+(\d{{4}})\s*\|(.+)$",
    re.MULTILINE,
)
ATTENDEES_RE = re.compile(r"Attendees:\s*(.+?)(?:\n|$)")


def check_gws():
    """Check gws CLI is installed and authenticated."""
    if which("gws") is None:
        return False, "gws CLI not found. Install with: npm install -g @googleworkspace/cli"
    try:
        result = subprocess.run(
            ["gws", "auth", "status"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0 or "not logged in" in result.stdout.lower():
            return False, "gws not authenticated. Run: gws auth login"
        return True, None
    except subprocess.TimeoutExpired:
        return False, "gws auth check timed out"
    except Exception as e:
        return False, f"Error checking gws: {e}"


def export_doc(doc_id):
    """Export a Google Doc as plain text via gws CLI."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    tmp_path = os.path.join(repo_dir, f".tmp_notes_{doc_id[:12]}.txt")

    try:
        params = json.dumps({
            "fileId": doc_id,
            "mimeType": "text/plain",
        })
        result = subprocess.run(
            ["gws", "drive", "files", "export", "--params", params, "-o", tmp_path],
            capture_output=True, text=True, timeout=30, cwd=repo_dir,
        )
        if result.returncode != 0:
            return None, f"Export failed: {result.stderr}"

        with open(tmp_path) as f:
            content = f.read()
        return content, None
    except subprocess.TimeoutExpired:
        return None, "Export timed out"
    except Exception as e:
        return None, f"Error exporting doc: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def parse_entries(text):
    """Split document text into date-headed entries."""
    matches = list(DATE_HEADER_RE.finditer(text))
    if not matches:
        return []

    entries = []
    for i, m in enumerate(matches):
        month_str, day_str, year_str, title = (
            m.group(1), m.group(2), m.group(3), m.group(4).strip()
        )
        try:
            date = datetime.strptime(f"{month_str} {day_str}, {year_str}", "%b %d, %Y")
        except ValueError:
            continue

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        attendees_match = ATTENDEES_RE.search(body)
        attendees = attendees_match.group(1).strip() if attendees_match else ""

        wins = ""
        wins_match = re.search(r"Win Celebration[:\s]*\n(.*?)(?=\n\s*(?:Notes|Action items|$))", body, re.DOTALL)
        if wins_match:
            wins = wins_match.group(1).strip()

        action_items = ""
        actions_match = re.search(r"Action items[:\s]*\n(.*?)$", body, re.DOTALL)
        if actions_match:
            action_items = actions_match.group(1).strip()

        notes_start = body.find("Notes")
        if notes_start == -1:
            notes_text = body
        else:
            notes_end = body.find("Action items")
            if notes_end == -1:
                notes_text = body[notes_start:].strip()
            else:
                notes_text = body[notes_start:notes_end].strip()

        entries.append({
            "date": date.strftime("%Y-%m-%d"),
            "date_display": f"{month_str} {day_str}, {year_str}",
            "title": title,
            "attendees": attendees,
            "wins": wins,
            "notes": notes_text,
            "action_items": action_items,
        })

    return entries


def filter_recent(entries, days=14):
    """Keep only entries within the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    return [e for e in entries if datetime.strptime(e["date"], "%Y-%m-%d") >= cutoff]


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_meeting_notes.py <GOOGLE_DOC_ID> [--days 14]"}))
        sys.exit(1)

    doc_id = sys.argv[1]
    days = 14
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])

    ok, error = check_gws()
    if not ok:
        print(json.dumps({"warning": error, "entries": [], "count": 0}))
        sys.exit(0)

    text, error = export_doc(doc_id)
    if error:
        print(json.dumps({"error": error, "entries": [], "count": 0}))
        sys.exit(1)

    all_entries = parse_entries(text)
    recent = filter_recent(all_entries, days=days)

    result = {
        "entries": recent,
        "count": len(recent),
        "total_entries_in_doc": len(all_entries),
        "filter_days": days,
    }

    if not recent and all_entries:
        result["warning"] = (
            f"No entries in the last {days} days. "
            f"Most recent: {all_entries[0]['date_display']}"
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

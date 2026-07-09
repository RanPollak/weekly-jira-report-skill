#!/usr/bin/env python3
"""
Fetch and parse weekly meeting notes from a Google Doc.

Uses the gws CLI to export the doc as plain text, then parses
date-headed entries and returns recent ones as JSON.

Usage: python3 fetch_notes.py <GOOGLE_DOC_ID> [--days 14]
"""

import json
import os
import re
import subprocess
import sys
import tempfile
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


def check_gws_installed():
    if which("gws") is None:
        return False, "gws CLI not found. Install with: npm install -g @googleworkspace/cli"
    return True, None


def check_gws_auth():
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
        return False, f"Error checking gws auth: {e}"


def export_doc(doc_id):
    """Export a Google Doc as plain text via gws CLI."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    tmp_path = os.path.join(skill_dir, f".tmp_notes_{doc_id[:12]}.txt")

    try:
        params = json.dumps({
            "fileId": doc_id,
            "mimeType": "text/plain",
        })
        result = subprocess.run(
            ["gws", "drive", "files", "export", "--params", params, "-o", tmp_path],
            capture_output=True, text=True, timeout=30, cwd=skill_dir,
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
        month_str, day_str, year_str, title = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        try:
            date = datetime.strptime(f"{month_str} {day_str}, {year_str}", "%b %d, %Y")
        except ValueError:
            continue

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        attendees_match = ATTENDEES_RE.search(body)
        attendees = attendees_match.group(1).strip() if attendees_match else ""

        notes_start = body.find("Notes:")
        if notes_start == -1:
            notes_start = body.find("Topics")
        if notes_start == -1:
            notes_text = body
        else:
            notes_text = body[notes_start:].strip()

        entries.append({
            "date": date.strftime("%Y-%m-%d"),
            "date_display": f"{month_str} {day_str}, {year_str}",
            "title": title,
            "attendees": attendees,
            "notes": notes_text,
        })

    return entries


def filter_recent(entries, days=14):
    """Keep only entries within the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    return [e for e in entries if datetime.strptime(e["date"], "%Y-%m-%d") >= cutoff]


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_notes.py <GOOGLE_DOC_ID> [--days 14]"}))
        sys.exit(1)

    doc_id = sys.argv[1]
    days = 14
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])

    installed, error = check_gws_installed()
    if not installed:
        print(json.dumps({"warning": error, "entries": [], "count": 0}))
        sys.exit(0)

    authed, error = check_gws_auth()
    if not authed:
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
        result["warning"] = f"No entries in the last {days} days. Most recent: {all_entries[0]['date_display']}"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

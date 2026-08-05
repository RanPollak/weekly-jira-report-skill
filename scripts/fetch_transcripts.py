#!/usr/bin/env python3
"""
Fetch meeting notes from this week's AI First Steering Committee meeting.

Uses the gws CLI to:
1. Find the steering committee calendar event for the current week
2. Pull attached Google Docs (Gemini notes + human notes)
3. Export them as plain text

Outputs JSON to stdout.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from shutil import which


def check_gws_installed():
    """Check if gws CLI is installed."""
    if which("gws") is None:
        return False, "gws CLI not found. Install with: npm install -g @googleworkspace/cli"
    return True, None


def check_gws_auth():
    """Check if gws is authenticated."""
    try:
        result = subprocess.run(
            ["gws", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0 or "not logged in" in result.stdout.lower():
            return False, "gws not authenticated. Run: gws auth login"
        return True, None
    except subprocess.TimeoutExpired:
        return False, "gws auth check timed out"
    except Exception as e:
        return False, f"Error checking gws auth: {e}"


def get_current_week_bounds():
    """Get Monday 00:00 and Sunday 23:59 of the current week in ISO format."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    time_min = monday.strftime("%Y-%m-%dT00:00:00Z")
    time_max = sunday.strftime("%Y-%m-%dT23:59:59Z")
    return time_min, time_max


def export_doc_as_text(file_id):
    """Export a Google Docs file as plain text via gws."""
    # gws restricts -o to the current directory, so use a temp file here
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    tmp_path = os.path.join(repo_dir, f".tmp_export_{file_id}.txt")

    try:
        params = json.dumps({
            "fileId": file_id,
            "mimeType": "text/plain",
        })

        result = subprocess.run(
            ["gws", "drive", "files", "export", "--params", params, "-o", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_dir,
        )

        if result.returncode != 0:
            return None, f"Export failed: {result.stderr}"

        with open(tmp_path, "r") as f:
            content = f.read()

        return content, None

    except subprocess.TimeoutExpired:
        return None, "Export timed out"
    except Exception as e:
        return None, f"Error exporting file: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def find_calendar_event(search_query):
    """Find a calendar event matching the search query for the current week."""
    time_min, time_max = get_current_week_bounds()

    params = json.dumps({
        "calendarId": "primary",
        "q": search_query,
        "timeMin": time_min,
        "timeMax": time_max,
        "singleEvents": True,
    })

    try:
        result = subprocess.run(
            ["gws", "calendar", "events", "list", "--params", params],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None, f"Calendar search failed: {result.stderr}"

        data = json.loads(result.stdout)
        items = data.get("items", [])

        if not items:
            return None, f"No '{search_query}' event found this week"

        return items[0], None

    except subprocess.TimeoutExpired:
        return None, "Calendar search timed out"
    except json.JSONDecodeError:
        return None, f"Failed to parse calendar response: {result.stdout}"
    except Exception as e:
        return None, f"Error searching calendar: {e}"


def fetch_transcripts_for_event(search_query):
    """Fetch transcripts for a single calendar event. Returns (transcripts, warnings, event_date)."""
    event, error = find_calendar_event(search_query)
    if error:
        return [], [error], None

    event_date = event.get("start", {}).get("dateTime", "unknown")
    event_summary = event.get("summary", search_query)
    attachments = event.get("attachments", [])

    if not attachments:
        return [], [f"'{event_summary}' event found but has no attachments"], event_date

    # Filter to Google Docs attachments only
    doc_mime = "application/vnd.google-apps.document"
    docs = [a for a in attachments if a.get("mimeType") == doc_mime]

    if not docs:
        return [], [f"'{event_summary}' event has attachments but none are Google Docs"], event_date

    transcripts = []
    warnings = []

    for doc in docs:
        file_id = doc.get("fileId")
        title = doc.get("title", "Unknown")

        content, error = export_doc_as_text(file_id)
        if error:
            warnings.append(f"{title}: {error}")
            continue

        source = "ai-generated" if "Gemini" in title else "human"
        transcripts.append({
            "title": title,
            "source": source,
            "meeting": event_summary,
            "content": content,
        })

    return transcripts, warnings, event_date


def main():
    # Check prerequisites - but don't fail hard, transcripts are optional
    installed, error = check_gws_installed()
    if not installed:
        print(json.dumps({
            "warning": error,
            "transcripts": [],
            "setup_instructions": "For Red Hat users: npm install -g @googleworkspace/cli && gws auth login"
        }))
        sys.exit(0)

    authed, error = check_gws_auth()
    if not authed:
        print(json.dumps({
            "warning": error,
            "transcripts": [],
            "setup_instructions": "For Red Hat users: Run 'gws auth login' and sign in with your @redhat.com Google account"
        }))
        sys.exit(0)

    # Default search query, plus any additional ones passed as arguments
    search_queries = ["AI First Steering Committee"] + sys.argv[1:]

    all_transcripts = []
    all_warnings = []
    event_dates = []

    for query in search_queries:
        transcripts, warnings, event_date = fetch_transcripts_for_event(query)
        all_transcripts.extend(transcripts)
        all_warnings.extend(warnings)
        if event_date:
            event_dates.append(event_date)

    result = {
        "transcripts": all_transcripts,
        "count": len(all_transcripts),
    }

    if event_dates:
        result["event_dates"] = event_dates

    if all_warnings:
        result["warnings"] = all_warnings

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

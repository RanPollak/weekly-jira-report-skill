#!/usr/bin/env python3
"""
Fetch recent demo videos and blog posts from a Google Drive folder.

Scans the folder and one level of subfolders for files modified within
the reporting window. Returns JSON with links for the WIN section.

Usage: python3 fetch_demos.py <FOLDER_ID> [--days 14]
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from shutil import which


def check_gws():
    if which("gws") is None:
        return False, "gws CLI not found"
    return True, None


def list_folder(folder_id):
    """List files in a Drive folder via gws."""
    params = {
        "q": f'"{folder_id}" in parents and trashed=false',
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
        "fields": "files(id,name,mimeType,webViewLink,modifiedTime,createdTime)",
        "orderBy": "modifiedTime desc",
        "pageSize": 50,
    }
    result = subprocess.run(
        ["gws", "drive", "files", "list", "--params", json.dumps(params)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return [], f"List failed: {result.stderr}"

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [], f"Parse error: {result.stdout[:200]}"

    return data.get("files", []), None


def is_content_file(mime):
    """Check if a file is a demo video, blog post, or presentation."""
    content_types = [
        "video/",
        "text/markdown",
        "text/html",
        "application/pdf",
        "application/vnd.google-apps.document",
        "application/vnd.google-apps.presentation",
        "application/vnd.google-apps.shortcut",
    ]
    return any(mime.startswith(t) for t in content_types)


def categorize(name, mime):
    """Categorize a file as demo, blog, or other."""
    name_lower = name.lower()
    if "blog" in name_lower:
        return "blog"
    if mime.startswith("video/") or "demo" in name_lower:
        return "demo"
    if mime == "application/vnd.google-apps.presentation":
        return "presentation"
    if mime == "application/vnd.google-apps.shortcut":
        if "blog" in name_lower:
            return "blog"
        if "demo" in name_lower:
            return "demo"
        return "artifact"
    return "artifact"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_demos.py <FOLDER_ID> [--days 14]"}))
        sys.exit(1)

    folder_id = sys.argv[1]
    days = 14
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])

    ok, err = check_gws()
    if not ok:
        print(json.dumps({"warning": err, "items": [], "count": 0}))
        sys.exit(0)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    top_files, err = list_folder(folder_id)
    if err:
        print(json.dumps({"error": err, "items": [], "count": 0}))
        sys.exit(1)

    items = []
    subfolder_ids = []

    for f in top_files:
        if f["mimeType"] == "application/vnd.google-apps.folder":
            subfolder_ids.append((f["id"], f["name"]))
            continue
        if not is_content_file(f["mimeType"]):
            continue
        mod = f.get("modifiedTime", f.get("createdTime", ""))
        if mod >= cutoff_str:
            items.append({
                "name": f["name"],
                "category": categorize(f["name"], f["mimeType"]),
                "link": f["webViewLink"],
                "modified": mod[:10],
                "folder": "",
            })

    for sf_id, sf_name in subfolder_ids:
        sub_files, _ = list_folder(sf_id)
        for f in sub_files:
            if not is_content_file(f.get("mimeType", "")):
                continue
            mod = f.get("modifiedTime", f.get("createdTime", ""))
            if mod >= cutoff_str:
                items.append({
                    "name": f["name"],
                    "category": categorize(f["name"], f["mimeType"]),
                    "link": f["webViewLink"],
                    "modified": mod[:10],
                    "folder": sf_name,
                })

    items.sort(key=lambda x: x["modified"], reverse=True)

    print(json.dumps({
        "items": items,
        "count": len(items),
        "filter_days": days,
        "folder_id": folder_id,
    }, indent=2))


if __name__ == "__main__":
    main()

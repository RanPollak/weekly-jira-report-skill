#!/usr/bin/env python3
"""
Create a Google Doc directly from a markdown report using gws CLI.

Replaces the old HTML conversion + rclone upload flow.
Uploads markdown to Google Drive with auto-conversion to native Google Docs.

Usage: python3 create_gdoc.py <markdown_file> [--folder-id FOLDER_ID]
"""

import json
import os
import subprocess
import sys
from datetime import date
from shutil import which


def check_gws():
    if which("gws") is None:
        print("Error: gws CLI not found. Install with: npm install -g @googleworkspace/cli", file=sys.stderr)
        sys.exit(1)


def create_gdoc(md_path, folder_id=None):
    """Upload markdown file to Drive as a Google Doc.

    gws restricts --upload to files under cwd, so we copy the file
    into a temp location in the same directory as this script and
    run gws from there.
    """
    import shutil

    basename = os.path.splitext(os.path.basename(md_path))[0]
    abs_md = os.path.abspath(md_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    tmp_name = f".tmp_upload_{os.path.basename(md_path)}"
    tmp_path = os.path.join(skill_dir, tmp_name)

    try:
        shutil.copy2(abs_md, tmp_path)

        params = {
            "uploadType": "multipart",
            "supportsAllDrives": True,
        }

        metadata = {
            "name": basename,
            "mimeType": "application/vnd.google-apps.document",
        }
        if folder_id:
            metadata["parents"] = [folder_id]

        cmd = [
            "gws", "drive", "files", "create",
            "--params", json.dumps(params),
            "--json", json.dumps(metadata),
            "--upload", tmp_name,
            "--upload-content-type", "text/markdown",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=skill_dir,
        )

        if result.returncode != 0:
            print(f"Error creating Google Doc: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Unexpected response: {result.stdout}", file=sys.stderr)
            sys.exit(1)

        doc_id = response.get("id", "")
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "id": doc_id,
            "name": response.get("name", basename),
            "url": doc_url,
            "mimeType": response.get("mimeType", ""),
        }
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main():
    if len(sys.argv) < 2:
        print("Usage: create_gdoc.py <markdown_file> [--folder-id FOLDER_ID]")
        sys.exit(1)

    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Error: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    folder_id = None
    if "--folder-id" in sys.argv:
        idx = sys.argv.index("--folder-id")
        if idx + 1 < len(sys.argv):
            folder_id = sys.argv[idx + 1]

    check_gws()
    result = create_gdoc(md_path, folder_id)

    print(f"\nGoogle Doc created:")
    print(f"  Name: {result['name']}")
    print(f"  URL:  {result['url']}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

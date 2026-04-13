# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "markdown2",
# ]
# ///
"""Convert a weekly update markdown report to styled HTML and upload to Google Drive via rclone."""

import argparse
import os
import subprocess
import sys
from datetime import datetime

import markdown2


def upload_to_drive(file_path: str, drive_path: str, drive_url: str, shared_drive: bool) -> bool:
    """Upload file to Google Drive using rclone."""
    try:
        result = subprocess.run(
            ["rclone", "listremotes"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            print("\nrclone not available", file=sys.stderr)
            return False

        remotes = result.stdout.strip().split("\n")
        gdrive_remote = None
        for remote in remotes:
            name = remote.strip().rstrip(":")
            if name and name.lower() in ("gdrive", "drive", "google"):
                gdrive_remote = name
                break

        if not gdrive_remote:
            print("\nNo Google Drive remote configured in rclone", file=sys.stderr)
            print("   Run: rclone config", file=sys.stderr)
            print("   Create a remote named 'gdrive' for Google Drive", file=sys.stderr)
            return False

        upload_cmd = ["rclone", "copy", file_path, f"{gdrive_remote}:{drive_path}"]
        if shared_drive:
            upload_cmd.append("--drive-shared-with-me")
            print(f"\nUploading to Shared Drive via rclone ({gdrive_remote})...")
        else:
            print(f"\nUploading to Google Drive via rclone ({gdrive_remote})...")
        upload_cmd.append("-v")

        upload_result = subprocess.run(
            upload_cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if upload_result.returncode == 0:
            print(f"Successfully uploaded to Google Drive!")
            print(f"View at: {drive_url}")
            return True
        else:
            print(f"\nUpload failed: {upload_result.stderr}", file=sys.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("\nUpload timed out", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("\nrclone not installed", file=sys.stderr)
        return False


def convert_to_html(report_file: str, output_file: str, team_name: str) -> str:
    """Convert markdown report to styled HTML."""
    if not os.path.exists(report_file):
        print(f"Report file not found: {report_file}", file=sys.stderr)
        print("  Generate the markdown report first using the weekly-jira-report skill.", file=sys.stderr)
        sys.exit(1)

    with open(report_file, "r") as f:
        markdown_content = f.read()

    html_content = markdown2.markdown(
        markdown_content,
        extras=["tables", "fenced-code-blocks", "strike", "target-blank-links"],
    )

    today = datetime.now().strftime("%B %d, %Y")
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team_name} Weekly Update - {today}</title>
    <style>
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #000;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            background-color: #fff;
        }}
        h1 {{
            font-size: 24pt;
            font-weight: bold;
            color: #000;
            margin-top: 0;
            margin-bottom: 12pt;
        }}
        h2 {{
            font-size: 16pt;
            font-weight: bold;
            color: #000;
            margin-top: 18pt;
            margin-bottom: 6pt;
            background-color: #f3f3f3;
            padding: 6pt;
        }}
        h3 {{
            font-size: 14pt;
            font-weight: bold;
            color: #1155cc;
            margin-top: 14pt;
            margin-bottom: 4pt;
        }}
        p {{ margin: 6pt 0; }}
        a {{ color: #1155cc; text-decoration: underline; }}
        ul {{ margin: 6pt 0; padding-left: 36pt; }}
        li {{ margin: 4pt 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }}
        table, th, td {{ border: 1px solid #000; }}
        th {{
            background-color: #f3f3f3;
            padding: 6pt;
            text-align: left;
            font-weight: bold;
        }}
        td {{ padding: 6pt; }}
        strong {{ font-weight: bold; }}
        em {{ font-style: italic; color: #000; }}
        hr {{ border: none; border-top: 1px solid #ccc; margin: 18pt 0; }}
        .status-on-track {{ color: #0f9d58; }}
        .status-at-risk {{ color: #f4b400; }}
        .status-off-track {{ color: #db4437; }}
        @media print {{
            body {{ margin: 0; padding: 0.5in; }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    with open(output_file, "w") as f:
        f.write(html_template)

    print(f"HTML file created: {output_file}")
    print(f"File size: {len(html_template)} bytes")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Convert weekly update markdown to HTML and upload to Google Drive."
    )
    parser.add_argument("--output-dir", required=True, help="Directory containing the markdown report")
    parser.add_argument("--team", required=True, help="Team name (must match the generated report)")
    parser.add_argument("--drive-path", required=True, help="rclone destination path on Google Drive")
    parser.add_argument("--drive-url", required=True, help="Google Drive folder URL for sharing")
    parser.add_argument("--shared-drive", action="store_true", help="Upload to a Shared Drive")
    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output_dir)
    date_str = datetime.now().strftime("%Y-%m-%d")
    team_slug = args.team.replace(" ", "_")
    report_file = os.path.join(output_dir, f"{team_slug}_Weekly_Update_{date_str}.md")
    html_file = os.path.join(output_dir, f"{team_slug}_Weekly_Update_{date_str}.html")

    html_path = convert_to_html(report_file, html_file, args.team)

    upload_success = upload_to_drive(html_path, args.drive_path, args.drive_url, args.shared_drive)
    if not upload_success:
        print(f"\nManual upload required:", file=sys.stderr)
        print(f"   Visit: {args.drive_url}", file=sys.stderr)
        print(f"   Drag and drop: {html_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Convert Weekly Update markdown to HTML and upload to Google Drive
"""
import markdown2
import subprocess
import sys
import os
from datetime import datetime

# Configuration - UPDATE THESE VALUES
OUTPUT_DIR = "~/weekly-reports"  # Directory containing markdown files
TEAM_NAME = "Your_Team_Name"  # Must match the name used in generate_weekly_update.py
DRIVE_FOLDER_PATH = "Your Folder Path"  # e.g., "Team Drive/Reports/Weekly" or "My Drive/Reports"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR-FOLDER-ID"
USE_SHARED_DRIVE = True  # Set to True if uploading to Shared Drive (Team Drive)

# Expand paths
OUTPUT_DIR = os.path.expanduser(OUTPUT_DIR)
DATE = datetime.now().strftime('%Y-%m-%d')
REPORT_FILE = os.path.join(OUTPUT_DIR, f'{TEAM_NAME}_Weekly_Update_{DATE}.md')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'{TEAM_NAME}_Weekly_Update_{DATE}.html')

def upload_to_drive(file_path):
    """Upload file to Google Drive using rclone"""
    try:
        # Check if rclone is configured with a gdrive remote
        result = subprocess.run(
            ['rclone', 'listremotes'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print("\n⚠️  rclone not available")
            return False

        # Check for any Google Drive remote (gdrive, drive, or google)
        remotes = result.stdout.strip().split('\n')
        gdrive_remote = None
        for remote in remotes:
            remote = remote.strip().rstrip(':')
            if remote and remote.lower() in ['gdrive', 'drive', 'google']:
                gdrive_remote = remote
                break

        if not gdrive_remote:
            print("\n⚠️  No Google Drive remote configured in rclone")
            print("   Run: rclone config")
            print("   Then create a remote named 'gdrive' for Google Drive")
            return False

        # Upload the file
        upload_cmd = ['rclone', 'copy', file_path, f'{gdrive_remote}:{DRIVE_FOLDER_PATH}']

        # Add --drive-shared-with-me flag for Shared Drives
        if USE_SHARED_DRIVE:
            upload_cmd.append('--drive-shared-with-me')
            print(f"\nUploading to Shared Drive via rclone ({gdrive_remote})...")
        else:
            print(f"\nUploading to Google Drive via rclone ({gdrive_remote})...")

        upload_cmd.append('-v')

        upload_result = subprocess.run(
            upload_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if upload_result.returncode == 0:
            print(f"✓ Successfully uploaded to Google Drive!")
            print(f"✓ View at: {DRIVE_FOLDER_URL}")
            return True
        else:
            print(f"\n✗ Upload failed: {upload_result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("\n✗ Upload timed out")
        return False
    except FileNotFoundError:
        print("\n⚠️  rclone not installed")
        return False
    except Exception as e:
        print(f"\n✗ Upload error: {e}")
        return False

def convert_to_html():
    """Convert markdown report to HTML"""
    # Read the markdown content
    if not os.path.exists(REPORT_FILE):
        print(f"✗ Report file not found: {REPORT_FILE}")
        print("  Run generate_weekly_update.py first to create the markdown file.")
        sys.exit(1)

    with open(REPORT_FILE, 'r') as f:
        markdown_content = f.read()

    # Convert markdown to HTML with tables support
    html_content = markdown2.markdown(
        markdown_content,
        extras=['tables', 'fenced-code-blocks', 'strike', 'target-blank-links']
    )

    # Create a styled HTML document matching Google Docs style
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TEAM_NAME} Weekly Update - {datetime.now().strftime('%B %d, %Y')}</title>
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
            border-bottom: none;
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

        p {{
            margin: 6pt 0;
        }}

        a {{
            color: #1155cc;
            text-decoration: underline;
        }}

        ul {{
            margin: 6pt 0;
            padding-left: 36pt;
        }}

        li {{
            margin: 4pt 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }}

        table, th, td {{
            border: 1px solid #000;
        }}

        th {{
            background-color: #f3f3f3;
            padding: 6pt;
            text-align: left;
            font-weight: bold;
        }}

        td {{
            padding: 6pt;
        }}

        strong {{
            font-weight: bold;
        }}

        em {{
            font-style: italic;
            color: #000;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 18pt 0;
        }}

        .status-on-track {{ color: #0f9d58; }}
        .status-at-risk {{ color: #f4b400; }}
        .status-off-track {{ color: #db4437; }}

        @media print {{
            body {{
                margin: 0;
                padding: 0.5in;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    # Write the HTML file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_template)

    print(f"✓ HTML file created: {OUTPUT_FILE}")
    print(f"✓ File size: {len(html_template)} bytes")

    return OUTPUT_FILE

# Main execution
if __name__ == "__main__":
    # Convert to HTML
    html_file = convert_to_html()

    # Upload to Google Drive
    upload_success = upload_to_drive(html_file)

    if not upload_success:
        print(f"\n⚠️  Manual upload required:")
        print(f"   Visit: {DRIVE_FOLDER_URL}")
        print(f"   Drag and drop: {html_file}")

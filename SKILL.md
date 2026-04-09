---
name: weekly-jira-report
description: Use when generating weekly team status reports from Jira with automatic Google Drive upload via rclone
---

# Weekly Jira Report Generator

Automates weekly team update reports by fetching Jira data, generating formatted markdown/HTML, and uploading to Google Drive (including Shared Drives).

## When to Use

Use this skill when:
- The user asks for a weekly report, weekly update, or team status report
- The user mentions "Catalyst report" or references the team update
- The user wants to generate a report from Jira issues

## Configuration

**Jira Details:**
- Site: redhat.atlassian.net
- Email: rpollak@redhat.com
- API Token: (stored in script)
- Root Issue: AIPCC-5516 (Catalyst Platform)

**Output Location:**
- Local folder: `/home/rpollak/catalyst weekly/`
- Files: `Catalyst_Weekly_Update_YYYY-MM-DD.{md,html}`
- Google Drive Folder: https://drive.google.com/drive/folders/11iPCk23YY02-3XmtfPrOWLwxGR-b1Ylk

## Report Format

The report follows this structure:

1. **Sprint Info** - Sprint number and ID
2. **Overall Status** - Shows status legend (🟢 On Track / 🟠 At Risk / 🔴 Off Track) followed by current status and progress percentages
3. **This Week** - Completed items only
4. **Next Week** - Planned & in-progress, prioritized
5. **What Is Blocked** - Current blockers with owners
6. **Risks** - Forward-looking risks
7. **Decisions Needed** - Specific decisions required
8. **Team Health / Notes** - Team health assessment
9. **Deep Dive** - Major initiatives with:
   - Target delivery dates
   - Priority indicators
   - Progress tracking (Completed/In Progress/Planned)
   - Change tracking table
   - Sub-task breakdowns

## Overall Status Format

The Overall Status section includes a legend at the top:
```
## Overall Status
🟢 On Track
🟠 At Risk / Delay
🔴 Off Track

**Current Status:** [Automatically determined status]
*X% Completed, Y% In Progress, Z% Planned*
```

## Execution Steps

1. **Fetch Jira Data**
   ```bash
   python3 /home/rpollak/generate_weekly_update.py
   ```

2. **Convert to HTML and Upload to Google Drive**
   ```bash
   python3 /home/rpollak/convert_update_to_html.py
   ```
   - Automatically converts markdown to HTML
   - Automatically uploads to Google Drive folder via rclone
   - Displays upload confirmation with Drive link

3. **Preview in Browser (Optional)**
   ```bash
   xdg-open /home/rpollak/Catalyst_Weekly_Update_YYYY-MM-DD.html
   ```

## Google Drive Upload

**Automatic Upload:**
- Conversion script automatically uploads HTML to Google Drive (personal or Shared Drive)
- Uses rclone with `gdrive` remote
- For Shared Drives: requires `--drive-shared-with-me` flag
- Upload path: Full path from Drive root (e.g., `AIPCC Shared Drive/AI Catalyst Platform/AI CAtalyst Weekly Report`)

**One-Time Setup:**
1. Install rclone: `sudo dnf install rclone` (Fedora) or equivalent
2. Configure: `rclone config`
   - Create new remote named `gdrive`
   - Type: Google Drive
   - Scope: Full access (option 1)
   - Use auto config: yes (opens browser for OAuth)
3. Test: `rclone lsd gdrive:` should list your drives

**For Shared Drives:**
- Use full path including Shared Drive name
- Add `--drive-shared-with-me` flag to rclone commands
- Example: `rclone copy file.html "gdrive:TeamDrive/Folder" --drive-shared-with-me`

**Common Upload Issues:**
- Files not appearing: Check if using Shared Drive (need `--drive-shared-with-me`)
- Permission denied: Verify rclone OAuth token is valid
- Wrong folder: Use full path from Drive root, not folder ID

## Important Notes

- Always generate both markdown and HTML versions
- HTML automatically uploads to Google Drive (no manual drag-and-drop needed)
- The HTML file is optimized for Google Docs import
- Sprint info, risks, decisions, and team health need manual completion
- If upload fails, manual upload instructions are displayed

## Scripts Location

- Generator: `/home/rpollak/generate_weekly_update.py`
- Converter (with auto-upload): `/home/rpollak/convert_update_to_html.py`
- Upload setup: `/home/rpollak/setup_gdrive_upload.sh`
- Manual upload: `/home/rpollak/upload_weekly_report.sh`
- Jira Credentials: Embedded in generator script

## Implementation Notes

**Key Libraries:**
- `requests` - Jira REST API calls
- `markdown2` - Markdown to HTML conversion (with tables support)
- `rclone` - Google Drive uploads (system command via subprocess)

**Upload Function Pattern:**
```python
def upload_to_drive(file_path):
    drive_path = "Shared Drive Name/Folder/Subfolder"
    result = subprocess.run(
        ['rclone', 'copy', file_path, f'gdrive:{drive_path}',
         '--drive-shared-with-me', '-v'],
        capture_output=True, text=True, timeout=60
    )
    return result.returncode == 0
```

**Critical for Shared Drives:**
- Always use `--drive-shared-with-me` flag
- Use full path, not folder IDs
- Folder IDs work for personal Drive but fail silently for Shared Drives

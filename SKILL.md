---
name: weekly-jira-report
description: Use when generating weekly team status reports from Jira with automatic Google Drive upload via rclone
---

# Weekly Jira Report Generator

Automates weekly team update reports by fetching Jira data, generating formatted markdown/HTML, and uploading to Google Drive (including Shared Drives).

## When to Use

Use this skill when:
- The user asks for a weekly report, weekly update, or team status report
- The user wants to generate a report from Jira issues
- The user needs automated report generation and Google Drive upload

## Prerequisites

Before using this skill, complete the following one-time setup:

### 1. Install Python Dependencies

```bash
pip install requests markdown2
```

### 2. Install rclone

**Fedora/RHEL:**
```bash
sudo dnf install rclone
```

**Ubuntu/Debian:**
```bash
sudo apt install rclone
```

**macOS:**
```bash
brew install rclone
```

**Verify installation:**
```bash
rclone version
```

### 3. Generate Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Weekly Reports")
4. Copy the token (you won't be able to see it again)

### 4. Configure rclone for Google Drive

```bash
rclone config
```

Follow these steps in the wizard:
1. Type `n` (new remote)
2. Name: `gdrive`
3. Storage type: Find "Google Drive" and enter its number (usually 15 or 18)
4. client_id: Press **Enter** (leave blank)
5. client_secret: Press **Enter** (leave blank)
6. Scope: Enter `1` (Full access)
7. root_folder_id: Press **Enter**
8. service_account_file: Press **Enter**
9. Advanced config: Type `n`
10. Auto config: Type `y` (browser will open for OAuth authentication)
11. Authenticate in browser with your Google account
12. Team Drive: Type `n` (unless using Team Drive exclusively)
13. Confirm: Type `y`
14. Quit: Type `q`

**Test the connection:**
```bash
rclone lsd gdrive:
```

This should list your Google Drive folders.

### 5. Install Scripts

Download or clone the scripts:

```bash
# If using as Claude Code skill
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-jira-report

# Copy scripts to working location
cp ~/.claude/skills/weekly-jira-report/*.py ~/
```

Or download directly:
```bash
cd ~
wget https://raw.githubusercontent.com/RanPollak/weekly-jira-report-skill/main/generate_weekly_update.py
wget https://raw.githubusercontent.com/RanPollak/weekly-jira-report-skill/main/convert_update_to_html.py
chmod +x *.py
```

### 6. Configure Scripts

**Edit `generate_weekly_update.py`:**

```python
JIRA_URL = "https://your-company.atlassian.net"
EMAIL = "your-email@company.com"
API_TOKEN = "paste-your-jira-api-token-here"
START_ISSUE = "PROJECT-123"  # Your root epic/issue key
TEAM_NAME = "Your Team Name"
OUTPUT_DIR = "~/weekly-reports"
```

**Edit `convert_update_to_html.py`:**

```python
OUTPUT_DIR = "~/weekly-reports"  # Match the above
TEAM_NAME = "Your_Team_Name"  # Underscores, match the above
DRIVE_FOLDER_PATH = "Your Folder/Path"  # Or "Shared Drive Name/Folder/Path"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR-FOLDER-ID"
USE_SHARED_DRIVE = True  # Set to False if using personal Drive
```

**Create output directory:**
```bash
mkdir -p ~/weekly-reports
```

### 7. Verify Setup

Test the complete workflow:

```bash
# Test Jira connection
python3 generate_weekly_update.py

# Should create: ~/weekly-reports/YourTeam_Weekly_Update_YYYY-MM-DD.md

# Test HTML conversion and upload
python3 convert_update_to_html.py

# Should create HTML and upload to Google Drive
```

## Configuration

**Jira Details:**
- Site: your-company.atlassian.net
- Email: your-email@company.com
- API Token: (configured in generate_weekly_update.py)
- Root Issue: PROJECT-XXX (your root epic/issue)

**Output Location:**
- Local folder: `~/weekly-reports/`
- Files: `TeamName_Weekly_Update_YYYY-MM-DD.{md,html}`
- Google Drive Folder: (configured in convert_update_to_html.py)

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
   python3 generate_weekly_update.py
   ```

2. **Convert to HTML and Upload to Google Drive**
   ```bash
   python3 convert_update_to_html.py
   ```
   - Automatically converts markdown to HTML
   - Automatically uploads to Google Drive folder via rclone
   - Displays upload confirmation with Drive link

3. **Preview in Browser (Optional)**
   ```bash
   xdg-open ~/weekly-reports/TeamName_Weekly_Update_YYYY-MM-DD.html
   ```

## Google Drive Upload

**Automatic Upload:**
- Conversion script automatically uploads HTML to Google Drive (personal or Shared Drive)
- Uses rclone with `gdrive` remote
- For Shared Drives: requires `--drive-shared-with-me` flag
- Upload path: Full path from Drive root (e.g., `Team Drive Name/Department/Weekly Reports`)

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

- Generator: `generate_weekly_update.py`
- Converter (with auto-upload): `convert_update_to_html.py`
- Jira Credentials: Configured at top of generator script

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

# Weekly Jira Report - Claude Code Skill

Automates weekly team status reports from Jira with automatic Google Drive uploads (including Shared Drives).

**One-time setup (15 minutes) → Weekly reports in 1 command!**

## Features

- 📊 Fetches Jira issues hierarchically from a root epic
- 📝 Generates formatted Markdown and HTML reports
- ☁️ Automatically uploads to Google Drive (personal or Shared Drives)
- 🎨 HTML optimized for Google Docs import
- 📈 Progress tracking (Completed/In Progress/Planned percentages)
- 🚦 Status indicators (🟢 On Track / 🟠 At Risk / 🔴 Off Track)
- 🤖 Works with Claude Code or standalone

## Table of Contents

- [Prerequisites & Installation](#prerequisites--installation)
- [Usage](#usage)
- [Report Format](#report-format)
- [Google Drive Upload](#google-drive-upload)
- [Troubleshooting](#troubleshooting-upload-issues)
- [Customization](#customization)
- [FAQ](#faq)
- [Contributing](#contributing)

## Quick Start

Complete these 9 steps once, then generate reports with a single command!

## Prerequisites & Installation

### Step 1: Install Python Dependencies

```bash
pip install requests markdown2
```

### Step 2: Install rclone

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

**Windows:**
Download from https://rclone.org/downloads/

**Verify installation:**
```bash
rclone version
```

### Step 3: Generate Jira API Token

1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it: `Weekly Reports`
4. **Copy the token** (you won't see it again!)
5. Save it temporarily - you'll need it in Step 6

### Step 4: Install the Skill

**Option A: As Claude Code Skill (Recommended)**

```bash
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-jira-report
```

Claude Code will automatically discover this skill.

**Option B: Standalone Scripts**

```bash
cd ~
git clone https://github.com/RanPollak/weekly-jira-report-skill.git
cd weekly-jira-report-skill
chmod +x *.py
```

Or download directly:
```bash
wget https://raw.githubusercontent.com/RanPollak/weekly-jira-report-skill/main/generate_weekly_update.py
wget https://raw.githubusercontent.com/RanPollak/weekly-jira-report-skill/main/convert_update_to_html.py
chmod +x *.py
```

### Step 5: Configure rclone for Google Drive

```bash
rclone config
```

**Follow the wizard carefully:**

1. Type **`n`** (new remote)
2. Name: **`gdrive`**
3. Storage type: Find **"Google Drive"** and enter its number (usually **15** or **18**)
4. client_id: Press **Enter** (leave blank)
5. client_secret: Press **Enter** (leave blank)
6. Scope: Enter **`1`** (Full access to all files)
7. root_folder_id: Press **Enter**
8. service_account_file: Press **Enter**
9. Edit advanced config: Type **`n`**
10. Use auto config: Type **`y`** (browser will open)
11. **Sign in with your Google account** in the browser window
12. Grant permissions to rclone
13. Configure as Team Drive: Type **`n`** (unless using Team Drive exclusively)
14. Confirm settings: Type **`y`**
15. Quit config: Type **`q`**

**Test the connection:**
```bash
rclone lsd gdrive:
```

You should see your Google Drive folders listed.

### Step 6: Configure Your Jira Settings

Edit `generate_weekly_update.py` (line 10-15):

```python
JIRA_URL = "https://your-company.atlassian.net"  # Your Jira site
EMAIL = "your-email@company.com"                # Your Jira email
API_TOKEN = "paste-your-api-token-here"         # From Step 3
START_ISSUE = "PROJECT-123"                     # Your root epic/issue key
TEAM_NAME = "Your Team Name"                    # Your team's name
OUTPUT_DIR = "~/weekly-reports"                 # Where to save reports
```

**How to find your root issue key:**
- Open your main epic/issue in Jira
- Look at the URL or the issue key at the top (e.g., `AIPCC-5516`)

### Step 7: Configure Google Drive Settings

Edit `convert_update_to_html.py` (line 11-15):

```python
OUTPUT_DIR = "~/weekly-reports"                              # Match Step 6
TEAM_NAME = "Your_Team_Name"                                 # Underscores, match Step 6
DRIVE_FOLDER_PATH = "Your Folder/Path"                       # See below
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR-FOLDER-ID"
USE_SHARED_DRIVE = True                                      # True for Shared Drive, False for personal
```

**For Personal Drive:**
```python
DRIVE_FOLDER_PATH = "My Reports/Weekly"
USE_SHARED_DRIVE = False
```

**For Shared Drive:**
```python
DRIVE_FOLDER_PATH = "Team Drive Name/Department/Weekly Reports"
USE_SHARED_DRIVE = True
```

**To get your folder URL:**
1. Open the folder in Google Drive in your browser
2. Copy the URL (it contains the folder ID)

### Step 8: Create Output Directory

```bash
mkdir -p ~/weekly-reports
```

### Step 9: Verify Setup

**Test Jira connection:**
```bash
python3 generate_weekly_update.py
```

✅ Should create: `~/weekly-reports/YourTeam_Weekly_Update_YYYY-MM-DD.md`

**Test Google Drive upload:**
```bash
python3 convert_update_to_html.py
```

✅ Should create HTML file and upload to Google Drive  
✅ Check your Drive folder - the file should appear!

## Setup Complete! 🎉

## Usage

### Using Claude Code Skill (Easiest!)

If you installed as a Claude Code skill, just ask Claude:

```
Generate my weekly report
```

or

```
Create this week's status update
```

Claude will automatically:
1. Run the Jira data fetch
2. Convert to HTML
3. Upload to Google Drive
4. Show you the results

### Manual Usage

**Quick command (runs both scripts):**
```bash
python3 generate_weekly_update.py && python3 convert_update_to_html.py
```

**Or step-by-step:**

1. **Fetch data from Jira:**
   ```bash
   python3 generate_weekly_update.py
   ```
   Creates: `~/weekly-reports/YourTeam_Weekly_Update_2026-04-09.md`

2. **Convert to HTML and upload:**
   ```bash
   python3 convert_update_to_html.py
   ```
   Creates: `~/weekly-reports/YourTeam_Weekly_Update_2026-04-09.html`  
   Uploads: Automatically to your configured Google Drive folder

3. **Preview locally (optional):**
   ```bash
   xdg-open ~/weekly-reports/*.html
   ```

### Viewing in Google Drive

After upload, the HTML file appears in your Drive folder. To convert to Google Docs:

1. Open the HTML file in Google Drive
2. Right-click → **"Open with Google Docs"**
3. Edit and share as needed!

### Weekly Workflow

**Every week, just run:**
```bash
python3 generate_weekly_update.py && python3 convert_update_to_html.py
```

The report automatically includes:
- ✅ All completed work this week (from Jira)
- 📅 Planned work for next week
- 🚧 Current blockers
- 📊 Progress percentages
- 🎯 Status indicators

## Report Format

The generated report includes:

1. **Overall Status** - Status legend and current status with progress percentages
2. **This Week** - Completed items only
3. **Next Week** - Planned & in-progress items, prioritized
4. **What Is Blocked** - Current blockers with owners
5. **Risks** - Forward-looking risks
6. **Decisions Needed** - Specific decisions required
7. **Team Health / Notes** - Team health assessment
8. **Deep Dive** - Major initiatives with:
   - Target delivery dates
   - Priority indicators (🔴 High / 🟠 Medium / 🟢 Low)
   - Progress tracking
   - Change tracking table
   - Sub-task breakdowns

## Google Drive Upload

### Personal Drive

Default configuration works out of the box. Files upload to the specified folder.

### Shared Drives (Team Drives)

**Important:** Shared Drives require special handling:

1. Use the full path from Drive root:
   ```python
   DRIVE_FOLDER_PATH = "Team Drive Name/Folder/Subfolder"
   ```

2. The upload function includes `--drive-shared-with-me` flag automatically

3. **Do NOT use folder IDs** - they work for personal Drive but fail silently for Shared Drives

### Troubleshooting Upload Issues

**Files not appearing in Drive:**
1. **Refresh your browser** (Ctrl+F5 or Cmd+Shift+R)
2. **Check if using Shared Drive:**
   - Shared Drives require `USE_SHARED_DRIVE = True` in config
   - Path must include the Shared Drive name
3. **Verify rclone can access the folder:**
   ```bash
   # For Personal Drive:
   rclone lsd "gdrive:Your Folder/Path"
   
   # For Shared Drive:
   rclone lsd "gdrive:Shared Drive Name/Folder" --drive-shared-with-me
   ```
4. **Check upload logs** - the script shows success/failure messages

**Permission errors:**
- Re-authenticate rclone: `rclone config reconnect gdrive:`
- Verify you have **edit access** to the target folder in Google Drive
- For Shared Drives, ensure you're a member of the Shared Drive

**Upload succeeds but file in wrong location:**
- Don't use folder IDs - they work for personal Drive but fail silently for Shared Drives
- Use the full path from Drive root
- Example: `"My Team Shared Drive/Projects/Weekly Reports"` not just `"Weekly Reports"`

**"No Google Drive remote configured" error:**
- Run `rclone config` and verify remote name is exactly `gdrive`
- Check: `rclone listremotes` should show `gdrive:`

**Jira connection errors:**
- Verify your API token is valid (tokens don't expire but can be revoked)
- Check your Jira URL format: `https://company.atlassian.net` (no trailing slash)
- Ensure your email matches your Jira account
- Test: `curl -u your-email@company.com:YOUR_API_TOKEN https://company.atlassian.net/rest/api/3/myself`

**Python errors:**
- Missing libraries: `pip install requests markdown2`
- Permission denied: `chmod +x *.py`

## Customization

### Modify Report Sections

Edit `generate_weekly_update.py` to:
- Change categorization logic (lines 65-84)
- Modify report structure (lines 311-370)
- Adjust status calculation (lines 304-309)

### HTML Styling

Edit `convert_update_to_html.py` to customize:
- Colors and fonts
- Table formatting
- Page layout
- Header/footer content

### Status Mapping

Customize how Jira statuses map to report categories in `categorize_issues()`:

```python
if status in ['done', 'closed']:
    completed.append(issue)
elif status in ['in progress', 'review', 'testing']:  # Add your statuses
    in_progress.append(issue)
elif status in ['blocked', 'on hold']:
    blocked.append(issue)
```

## FAQ

**Q: Do I need Claude Code to use this?**  
A: No! It works standalone. Claude Code integration is optional but convenient.

**Q: Can I run this on a schedule (cron)?**  
A: Yes! Add to crontab:
```bash
# Every Friday at 4 PM
0 16 * * 5 cd ~ && python3 generate_weekly_update.py && python3 convert_update_to_html.py
```

**Q: Will this work with Jira Cloud and Jira Server?**  
A: Yes for Jira Cloud. Jira Server/Data Center may need API endpoint adjustments.

**Q: Can I track multiple projects?**  
A: Yes - create separate config files or modify the script to loop through multiple `START_ISSUE` values.

**Q: Does this modify my Jira data?**  
A: No, it's read-only. It only fetches data, never writes to Jira.

**Q: What if my team doesn't use sprints?**  
A: Works fine! It tracks all child issues under your root epic, sprint-based or not.

**Q: Can I customize the report sections?**  
A: Absolutely! Edit `generate_weekly_update.py` - it's just Python template strings.

**Q: How do I handle multiple Google accounts?**  
A: Create multiple rclone remotes (`gdrive-work`, `gdrive-personal`) and specify in config.

**Q: My Shared Drive files aren't appearing!**  
A: Ensure `USE_SHARED_DRIVE = True` and use full path with Shared Drive name. See [Troubleshooting](#troubleshooting-upload-issues).

**Q: Can I email the report instead of uploading to Drive?**  
A: Not built-in, but you can add email functionality using Python's `smtplib` after HTML generation.

**Q: How do I update the scripts?**  
A: `cd ~/.claude/skills/weekly-jira-report && git pull origin main`

## Contributing

Contributions welcome! Please:
1. Fork this repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - Feel free to use and adapt for your team's needs!

## Author

Created by Ran Pollak ([@RanPollak](https://github.com/RanPollak))

## Acknowledgments

Built with Claude Code using the Superpowers skill framework.

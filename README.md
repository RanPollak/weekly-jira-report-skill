# Weekly Jira Report - Claude Code Skill

Automates weekly team status reports from Jira with automatic Google Drive uploads (including Shared Drives).

## Features

- 📊 Fetches Jira issues hierarchically from a root epic
- 📝 Generates formatted Markdown and HTML reports
- ☁️ Automatically uploads to Google Drive (personal or Shared Drives)
- 🎨 HTML optimized for Google Docs import
- 📈 Progress tracking (Completed/In Progress/Planned percentages)
- 🚦 Status indicators (🟢 On Track / 🟠 At Risk / 🔴 Off Track)

## Prerequisites

- Python 3.x
- `requests` library: `pip install requests`
- `markdown2` library: `pip install markdown2`
- `rclone` configured for Google Drive
- Jira API token

## Installation

### 1. Install as Claude Code Skill

```bash
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-jira-report
```

Claude Code will automatically discover this skill.

### 2. Install Scripts

Copy the Python scripts to your preferred location:

```bash
cp generate_weekly_update.py ~/generate_weekly_update.py
cp convert_update_to_html.py ~/convert_update_to_html.py
chmod +x ~/*.py
```

### 3. Configure Jira Credentials

Edit `generate_weekly_update.py` and update:

```python
JIRA_URL = "https://your-company.atlassian.net"
EMAIL = "your-email@company.com"
API_TOKEN = "your-jira-api-token"  # Generate at: https://id.atlassian.com/manage-profile/security/api-tokens
START_ISSUE = "PROJECT-123"  # Your root epic/issue
TEAM_NAME = "Your Team Name"
```

### 4. Configure Google Drive Upload

Edit `convert_update_to_html.py` and update:

```python
DRIVE_FOLDER_PATH = "Your Folder Path"  # e.g., "Team Drive/Reports/Weekly"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/YOUR-FOLDER-ID"
```

### 5. Set Up rclone for Google Drive

First time setup:

```bash
rclone config
```

Follow these steps:
1. Type `n` (new remote)
2. Name: `gdrive`
3. Storage type: Find "Google Drive" and enter its number
4. client_id: Press Enter (leave blank)
5. client_secret: Press Enter (leave blank)
6. Scope: Enter `1` (Full access)
7. root_folder_id: Press Enter
8. service_account_file: Press Enter
9. Advanced config: `n`
10. Auto config: `y` (browser will open for OAuth)
11. Team Drive: `n`
12. Confirm: `y`
13. Quit: `q`

Test the connection:
```bash
rclone lsd gdrive:
```

## Usage

### Using Claude Code Skill

Simply ask Claude:
```
Generate my weekly report
```

Claude will use the `weekly-jira-report` skill and run both scripts automatically.

### Manual Usage

1. **Generate report from Jira:**
   ```bash
   python3 ~/generate_weekly_update.py
   ```

2. **Convert to HTML and upload to Google Drive:**
   ```bash
   python3 ~/convert_update_to_html.py
   ```

3. **Optional - Preview locally:**
   ```bash
   xdg-open ~/catalyst\ weekly/Catalyst_Weekly_Update_*.html
   ```

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
- Refresh your browser (Ctrl+F5)
- Check if you're using a Shared Drive (verify path includes Shared Drive name)
- Verify rclone can list the folder: `rclone lsd "gdrive:Path/To/Folder" --drive-shared-with-me`

**Permission errors:**
- Re-authenticate rclone: `rclone config reconnect gdrive:`
- Verify you have write access to the target folder

## Customization

### Modify Report Sections

Edit `generate_weekly_update.py` to:
- Change categorization logic (lines 65-84)
- Modify report structure (lines 311-370)
- Adjust status calculation (lines 304-309)

### HTML Styling

Edit `convert_update_to_html.py` (lines 30-133) to customize:
- Colors and fonts
- Table formatting
- Page layout

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

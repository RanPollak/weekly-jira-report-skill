# Weekly Jira Report - Claude Code Skill

An AI-native Claude Code skill that generates weekly team status reports from Jira, team meeting notes, and demo/blog artifacts. Claude fetches the data, correlates across sources, and writes the report using its own judgment -- not rigid templates.

## What Makes This AI-Native

Traditional report scripts mechanically dump Jira data into a template. This skill has Claude:

- **Correlate multiple sources** -- Jira data, meeting notes (Google Doc), and demo/blog artifacts (Google Drive) feed into one coherent report
- **Write the WIN section from real conversations** -- meeting notes are the primary source for celebrations, not Jira status fields
- **Enrich with links** -- demo videos and blog posts from Google Drive are attached to WIN entries when they match what the team discussed
- **Analyze patterns** -- identify risk clusters, workload imbalances, stalled items
- **Write with judgment** -- summarize completed work as a narrative, not a raw list
- **Track changes** -- compare against last week's report to highlight what changed

## Prerequisites

- [jira-cli](https://github.com/ankitpokhrel/jira-cli) -- Modern Jira CLI tool
- [gws](https://github.com/nicholasgasior/gws) -- Google Workspace CLI (for meeting notes, demo folder scanning, and Google Doc creation)

## Installation

### As a Claude Code Skill

```bash
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-jira-report
```

Claude Code will automatically discover the skill.

### Setup

#### 1. Configure jira-cli

```bash
jira init
```

Follow the interactive prompts to configure your Jira instance, authentication, and default project.

#### 2. Configure gws

```bash
npm install -g @googleworkspace/cli
gws auth login
```

#### 3. Create local config

Create `weekly_report.local.json` in the skill directory:

```json
{
  "START_ISSUE": "PROJECT-123",
  "TEAM_NAME": "Your Team",
  "OUTPUT_DIR": "~/weekly-reports",
  "DRIVE_FOLDER_URL": "https://drive.google.com/drive/folders/YOUR-FOLDER-ID",
  "NOTES_DOC_ID": "GOOGLE_DOC_ID_FOR_MEETING_NOTES",
  "DEMOS_FOLDER_ID": "GOOGLE_DRIVE_FOLDER_ID_FOR_DEMOS"
}
```

## Usage

Ask Claude:

```
Generate my weekly report
```

Claude will:
1. Fetch data from Jira using `jira-cli`
2. Fetch meeting notes from the Google Doc via `gws`
3. Scan the demos/blog folder for recent artifacts via `gws`
4. Correlate notes and demos to build the WIN section
5. Analyze the data and write the full report
6. Present the draft for your review
7. Create a native Google Doc in the target Drive folder

## Data Sources

| Source | Script | Purpose |
|--------|--------|---------|
| Jira | `jira-cli` | Issue status, completions, initiatives |
| Meeting notes | `scripts/fetch_notes.py` | WIN section (primary), team discussions |
| Demos & blogs | `scripts/fetch_demos.py` | Links for WIN entries that match notes |
| Google Doc output | `scripts/create_gdoc.py` | Upload report as native Google Doc |

## Project Structure

```
weekly-jira-report/
├── SKILL.md                      # Skill manifest and workflow instructions
├── weekly_report.local.json      # Configuration (create this, gitignored)
├── scripts/
│   ├── fetch_notes.py            # Fetch & parse meeting notes from Google Doc
│   ├── fetch_demos.py            # Scan Drive folder for recent demos/blogs
│   ├── create_gdoc.py            # Upload markdown as native Google Doc
│   └── convert_and_upload.py     # Legacy HTML conversion (deprecated)
└── references/
    └── report-format.md          # Report template and format reference
```

## Report Sections

1. **Summary** -- status emoji, one sentence, progress percentages
2. **Team Celebrations / WIN** -- achievements from meeting notes, enriched with demo/blog links
3. **Completed This Week** -- only current-period completions from Jira
4. **Shipping Next Week** -- max 5 items that will actually ship
5. **Appendix -- Initiative Deep Dives** -- optional, 3-4 sentences each

See `references/report-format.md` for the full specification.

## FAQ

**Q: Do I need Claude Code to use this?**
A: The skill is designed for Claude Code. The scripts can be run standalone, but the report generation relies on Claude's analysis.

**Q: Will this work with Jira Cloud and Jira Server?**
A: Yes for both via jira-cli. Configure the appropriate instance during `jira init`.

**Q: Does this modify my Jira data?**
A: No, it's read-only. It only fetches data, never writes to Jira.

**Q: What if I don't have meeting notes or a demos folder?**
A: Both are optional. The skill falls back to Jira-only mode if `NOTES_DOC_ID` or `DEMOS_FOLDER_ID` are not set.

## License

Apache License 2.0

## Author

Created by Ran Pollak ([@RanPollak](https://github.com/RanPollak))

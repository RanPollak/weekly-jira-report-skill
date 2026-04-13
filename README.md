# Weekly Jira Report - Claude Code Skill

An AI-native Claude Code skill that generates weekly team status reports from Jira. Claude fetches the data via `jira-cli`, analyzes it, and writes the report using its own judgment -- not rigid templates.

## What Makes This AI-Native

Traditional report scripts mechanically dump Jira data into a template. This skill has Claude:

- **Analyze patterns** -- identify risk clusters, workload imbalances, stalled items
- **Write with judgment** -- summarize completed work as a narrative, not a raw list
- **Infer blockers and risks** -- suggest causes and owners based on issue context
- **Track changes** -- compare against last week's report to highlight what changed
- **Fill manual sections** -- draft Risks, Decisions Needed, and Team Health instead of leaving "TBD"

The only script left is `convert_and_upload.py` for mechanical HTML conversion and rclone upload.

## Prerequisites

- [jira-cli](https://github.com/ankitpokhrel/jira-cli) -- Modern Jira CLI tool
- [rclone](https://rclone.org/) -- for Google Drive uploads
- [uv](https://docs.astral.sh/uv/) -- Python package manager (for HTML conversion)

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

#### 2. Configure rclone for Google Drive

```bash
rclone config
```

1. Type `n` (new remote)
2. Name: `gdrive`
3. Storage type: Find "Google Drive" and enter its number
4. client_id / client_secret: Press Enter (leave blank)
5. Scope: Enter `1` (Full access)
6. Auto config: Type `y` (browser will open for OAuth)
7. Confirm and quit

Test the connection:

```bash
rclone lsd gdrive:
```

## Usage

Ask Claude:

```
Generate my weekly report
```

Claude will:
1. Ask you for the Jira issue key, team name, output directory, and Drive folder
2. Fetch data from Jira using `jira-cli`
3. Analyze the data and write a report with insights
4. Present the draft for your review
5. Convert to HTML and upload to Google Drive

## Project Structure

```
weekly-jira-report-skill/
├── SKILL.md                      # Skill manifest and workflow instructions
├── scripts/
│   └── convert_and_upload.py    # HTML conversion + rclone upload (uses inline deps via PEP 723)
└── references/
    └── report-format.md         # Report template and format reference
```

## Report Sections

1. **Overall Status** -- progress percentages and assessed status
2. **This Week** -- completed work, grouped and summarized
3. **Next Week** -- upcoming work prioritized by impact
4. **What Is Blocked** -- blockers with inferred causes and owners
5. **Risks** -- pattern-based risk identification
6. **Decisions Needed** -- inferred from blockers and risks
7. **Team Health** -- workload and velocity observations
8. **Deep Dive** -- initiative narratives with sub-task breakdowns

See `references/report-format.md` for the full specification.

## Google Drive Upload

### Shared Drives

Use the `--shared-drive` flag. Important:
- Use the full path from Drive root (e.g., `Team Drive Name/Folder/Subfolder`)
- Do **not** use folder IDs -- they fail silently for Shared Drives

### Troubleshooting

- **Files not appearing**: Check if using a Shared Drive (needs `--shared-drive` flag)
- **Permission errors**: Re-authenticate with `rclone config reconnect gdrive:`
- **Wrong folder**: Verify path with `rclone lsd "gdrive:Path/To/Folder" --drive-shared-with-me`

## FAQ

**Q: Do I need Claude Code to use this?**
A: The skill is designed for Claude Code. The `convert_and_upload.py` script can be run standalone, but the report generation relies on Claude's analysis.

**Q: Will this work with Jira Cloud and Jira Server?**
A: Yes for both Jira Cloud and Jira Server/Data Center via jira-cli. Configure the appropriate instance during `jira init`.

**Q: Does this modify my Jira data?**
A: No, it's read-only. It only fetches data, never writes to Jira.

## License

Apache License 2.0

## Author

Created by Ran Pollak ([@RanPollak](https://github.com/RanPollak))

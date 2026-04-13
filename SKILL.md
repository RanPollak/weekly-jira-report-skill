---
name: weekly-jira-report
description: >-
  AI-native weekly team status report generator from Jira. Claude fetches data via Jira REST API,
  analyzes it with judgment, and writes meaningful reports. Use when the user asks to 'generate
  a weekly report', 'create a team status update', or 'make my weekly update'.
---

# Weekly Jira Report Generator (AI-Native)

## Step 1: Load Configuration

Check for configuration file at `~/.claude/skills/weekly-jira-report/weekly_report.local.json`:

```json
{
  "START_ISSUE": "PROJECT-123",
  "TEAM_NAME": "Your Team",
  "OUTPUT_DIR": "~/weekly-reports",
  "DRIVE_FOLDER_PATH": "Shared Drive/Team/Reports",
  "DRIVE_FOLDER_URL": "https://drive.google.com/drive/folders/YOUR-ID",
  "USE_SHARED_DRIVE": true
}
```

**Note:** Jira authentication is handled separately via `jira init` (run once during setup).

If values are missing or placeholders, ask the user.

## Step 2: Fetch Jira Data via jira-cli

Use jira-cli to fetch data from Jira. Authentication is handled automatically via `jira init`.

**Fetch root issue:**
```bash
jira issue view "$ISSUE_KEY" --plain --comments 0
```

**Fetch child issues (initiatives):**
```bash
jira issue list --parent "$ISSUE_KEY" --plain --columns KEY,SUMMARY,STATUS,ASSIGNEE,TYPE,PRIORITY
```

**For each initiative, fetch sub-tasks:**
```bash
jira issue list --parent "$INITIATIVE_KEY" --plain --columns KEY,SUMMARY,STATUS,ASSIGNEE,TYPE,PRIORITY
```

**For deeper analysis**, fetch individual issues:
```bash
jira issue view "$ISSUE_KEY" --plain --comments 0
```

**Note:** jira-cli automatically handles pagination, so you don't need to worry about maxResults limits.

## Step 3: Analyze and Write the Report

**This is where you add real AI value.** Do NOT just template data mechanically. Use your judgment:

### Categorize Issues by Status

- `Done` / `Closed` → Completed
- `In Progress` / `In Review` → In Progress  
- `Blocked` → Blocked
- Everything else → Planned

### Calculate Progress

Compute percentages: completed / in-progress / planned

### Determine Overall Status

- Any blocked items → consider Off Track (🔴)
- >60% in progress with low completion → At Risk (🟠)
- Otherwise → On Track (🟢)
- **Use judgment** - minor blockers may not mean Off Track

### Write Report Following `references/report-format.md`

**Target audience:** Managers who need to make decisions in 2 minutes.

**Structure:** Actions first, context second. The format prioritizes:
1. **Status Line** - One sentence summary
2. **Decisions Needed** - Max 3, one line each
3. **Risks & Actions** - Table format for quick scanning
4. **Completed This Week** - Only this week's completions (not old ones!)
5. **Shipping Next Week** - Max 5 items that will actually ship
6. **Blocked** - Specific blockers with owners to unblock
7. **Appendix** - Initiative deep dives (optional reading)

**Key sections where you reason, not just copy:**

- **Status Line**: One clear sentence explaining the overall state. Not generic.
- **Decisions Needed**: Frame as questions. Max 3. Only include if leadership genuinely needs to decide something.
- **Risks & Actions**: Use table format. Be specific with data ("Nati owns 38%" not "uneven workload"). Include recommended action.
- **Completed This Week**: ONLY items completed during this reporting period. If nothing, write "No completions this week." Never pad with old completions.
- **Shipping Next Week**: Max 5 items. What will actually ship, not everything in-progress. If you have 14 items, you're dumping the backlog.
- **Blocked**: Specific blocker + who can unblock. Omit section if nothing blocked.
- **Appendix**: 3-4 sentences per initiative. Skip sub-task lists unless critical.

**Identify risks by analyzing patterns:**
- Workload concentration (one person owns >30% of items)
- No completions in several days
- Multiple blockers in same area
- Items with no assignee
- Overdue dates or stalled in-progress items

### Compare with Previous Report

If a previous report exists in the output directory, read it to inform your analysis:
- Identify new completions vs. what was completed before
- Note new blockers or resolved blockers
- Track whether status improved or degraded
- **Do NOT create a "Changes from Last Week" section** - readers can see changes by reading the structured sections

**Save report as:** `TEAM_NAME_Weekly_Update_YYYY-MM-DD.md` in output directory.

## Step 4: Review with the User

Present the generated report to the user. Ask them to review and refine:
- Are the risk assessments accurate?
- Any blockers or decisions to add/remove?
- Team health notes?

Make edits based on their feedback.

## Step 5: Convert to HTML and Upload

Once the user approves the report:

```bash
cd ~/.claude/skills/weekly-jira-report
uv run scripts/convert_and_upload.py \
  --output-dir "$OUTPUT_DIR" \
  --team "$TEAM_NAME" \
  --drive-path "$DRIVE_FOLDER_PATH" \
  --drive-url "$DRIVE_FOLDER_URL" \
  $([ "$USE_SHARED_DRIVE" = "true" ] && echo "--shared-drive")
```

## Prerequisites

- [`jira-cli`](https://github.com/ankitpokhrel/jira-cli) - Modern Jira CLI tool
  - Install: `brew install ankitpokhrel/jira-cli/jira-cli` (macOS) or see installation docs for other platforms
  - Configure: `jira init` (interactive setup with your Jira instance)
- `uv` - Python package manager (for HTML conversion)
- `rclone` - configured with Google Drive remote (`gdrive:`)

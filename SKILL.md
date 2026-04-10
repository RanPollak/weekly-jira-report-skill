---
name: weekly-jira-report
description: >-
  Generates weekly team status reports from Jira data with HTML conversion
  and Google Drive upload. Use when the user asks to 'generate a weekly report',
  'create a team status update', 'build the weekly Jira report', 'make my
  weekly update', or mentions 'Catalyst report'.
---

# Weekly Jira Report Generator

## Step 1: Interview the User

Before doing anything, ask the user for:

1. **Root Jira issue key** (e.g., `AIPCC-5516`) -- the parent epic to report on
2. **Team name** (e.g., `Catalyst`) -- used in report title and filename
3. **Output directory** (e.g., `~/weekly-reports`) -- where to save generated files
4. **Google Drive upload?** -- ask if they want to upload to Google Drive. If yes, ask:
   a. **Google Drive folder path** (e.g., `Shared Drive/Team/Reports`) -- rclone destination
   b. **Google Drive folder URL** -- link to share after upload
   c. **Shared Drive?** -- yes/no, affects rclone flags
   If no, skip the Drive sub-questions and proceed to Step 2.

## Step 2: Fetch Jira Data

Run these acli commands to gather data. Use `--csv` for search commands (compact output) and `--json` only for individual issue views when you need full descriptions.

**Fetch the root issue:**
```bash
acli jira workitem view ISSUE_KEY --json --fields "*all"
```

**Fetch all child issues (initiatives):**
```bash
acli jira workitem search --jql "parent = ISSUE_KEY" --csv --fields "key,summary,status,assignee,issuetype,priority" --limit 100
```

**For each initiative, fetch its sub-tasks:**
```bash
acli jira workitem search --jql "parent = INITIATIVE_KEY" --csv --fields "key,summary,status,assignee,issuetype,priority" --limit 100
```

**For issues that need deeper analysis** (e.g., to understand blockers or risks), fetch individual issues:
```bash
acli jira workitem view ISSUE_KEY --json --fields "summary,status,description"
```

If there are many initiatives, fetch sub-tasks only for the top 10 by priority.

**Note:** The `duedate` field is not available in acli search. Due dates can be checked via individual issue views if needed.

## Step 3: Analyze and Write the Report

This is where you add real value. Do NOT just template the data mechanically. Use your judgment:

**Categorize issues by status:**
- Done / Closed → Completed
- In Progress / Review → In Progress
- Blocked → Blocked
- Everything else → Planned

**Calculate progress** as percentages of completed / in-progress / planned.

**Determine overall status:**
- Any blocked items → consider Off Track (🔴)
- More in-progress than completed, or >60% in progress → consider At Risk (🟠)
- Otherwise → On Track (🟢)
- Use your judgment -- if blockers are minor, the project may still be On Track.

**Write the report in markdown** following the format in `references/report-format.md`. Key sections where you should reason, not just copy:

- **This Week**: Summarize completed work in a way that tells a story, not just a list. Group related completions.
- **Next Week**: Prioritize by impact, not just Jira priority field.
- **What Is Blocked**: For each blocker, infer the likely cause from the issue description and suggest who might unblock it.
- **Risks**: Identify risks by analyzing patterns -- e.g., multiple blocked items in one area, items with no assignee, overdue dates, stalled in-progress items.
- **Decisions Needed**: Infer from blockers and risks what decisions leadership needs to make.
- **Team Health**: Note if workload looks uneven (one person assigned too many items), if velocity seems low, or if blocked items are piling up. Ask the user to confirm or adjust.
- **Deep Dive**: For each major initiative, provide a meaningful status narrative, not just percentages.

**If a previous report exists** in the output directory, read it and note:
- What changed since last week (new completions, new blockers, resolved blockers)
- Whether status improved or degraded
- Include a brief "Changes from Last Week" note where relevant

Save the report as `TEAM_NAME_Weekly_Update_YYYY-MM-DD.md` in the output directory.

## Step 4: Review with the User

Present the generated report to the user. Ask them to review and refine:
- Are the risk assessments accurate?
- Any blockers or decisions to add/remove?
- Team health notes?

Make edits based on their feedback.

## Step 5: Convert to HTML and Upload

Once the user approves the report:

```bash
uv run scripts/convert_and_upload.py \
  --output-dir "OUTPUT_DIR" \
  --team "TEAM_NAME" \
  --drive-path "DRIVE_FOLDER_PATH" \
  --drive-url "DRIVE_FOLDER_URL" \
  [--shared-drive]
```

Skip this step if the user declined Google Drive upload in Step 1.

## Prerequisites

- `acli` -- authenticated (`acli jira auth`)
- `rclone` -- configured with a Google Drive remote (`rclone config`)
- `uv` -- Python package manager (for the HTML conversion script)

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
  "JIRA_URL": "https://your-company.atlassian.net",
  "EMAIL": "your@email.com",
  "API_TOKEN": "your-jira-api-token",
  "START_ISSUE": "PROJECT-123",
  "TEAM_NAME": "Your Team",
  "OUTPUT_DIR": "~/weekly-reports",
  "DRIVE_FOLDER_PATH": "Shared Drive/Team/Reports",
  "DRIVE_FOLDER_URL": "https://drive.google.com/drive/folders/YOUR-ID",
  "USE_SHARED_DRIVE": true
}
```

If values are missing or placeholders, ask the user.

## Step 2: Fetch Jira Data via REST API

Use curl to fetch data directly from Jira. Authenticate with Basic Auth (email:api_token in base64).

**Fetch root issue:**
```bash
curl -s -u "$EMAIL:$API_TOKEN" \
  "$JIRA_URL/rest/api/3/issue/$ISSUE_KEY" | jq .
```

**Fetch child issues (initiatives):**
```bash
curl -s -u "$EMAIL:$API_TOKEN" \
  "$JIRA_URL/rest/api/3/search?jql=parent=$ISSUE_KEY&maxResults=100&fields=key,summary,status,assignee,issuetype,priority" | jq .
```

**For each initiative, fetch sub-tasks:**
```bash
curl -s -u "$EMAIL:$API_TOKEN" \
  "$JIRA_URL/rest/api/3/search?jql=parent=$INITIATIVE_KEY&maxResults=100&fields=key,summary,status,assignee,issuetype,priority" | jq .
```

**For deeper analysis**, fetch individual issues:
```bash
curl -s -u "$EMAIL:$API_TOKEN" \
  "$JIRA_URL/rest/api/3/issue/$ISSUE_KEY?fields=summary,status,description" | jq .
```

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

**Key sections where you reason, not just copy:**

- **This Week**: Summarize completed work as a story, not a list. Group related completions.
- **Next Week**: Prioritize by impact, not just Jira priority field.
- **What Is Blocked**: For each blocker, infer the likely cause from description and suggest who might unblock it.
- **Risks**: Identify risks by analyzing patterns:
  - Multiple blocked items in one area
  - Items with no assignee
  - Overdue dates
  - Stalled in-progress items
- **Decisions Needed**: Infer from blockers and risks what decisions leadership needs.
- **Team Health**: Note if:
  - Workload looks uneven (one person assigned too many items)
  - Velocity seems low
  - Blocked items are piling up
  - Ask the user to confirm or adjust
- **Deep Dive**: For each major initiative, provide meaningful status narrative, not just percentages.

### Compare with Previous Report

If a previous report exists in the output directory, read it and note:
- What changed since last week (new completions, new blockers, resolved blockers)
- Whether status improved or degraded
- Include a brief "Changes from Last Week" note where relevant

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

- `jq` - JSON processor for parsing Jira responses
- `uv` - Python package manager (for HTML conversion)
- `rclone` - configured with Google Drive remote (`gdrive:`)
- Jira API token (create at: https://id.atlassian.com/manage-profile/security/api-tokens)

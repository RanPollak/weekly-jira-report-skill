---
name: weekly-jira-report-skill
description: >-
  Use when the user asks to 'generate a weekly report', 'create a team status update',
  'make my weekly update', or 'write a Jira status report'. Fetches Jira data via jira-cli,
  analyzes with AI judgment, and produces meaningful narrative reports (not mechanical templates).
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

**Security: Validate configuration values before use**
- Ensure paths contain no shell metacharacters (`;`, `|`, `&`, `$()`, etc.)
- Quote all variables in shell commands: `"$VAR"` not `$VAR`
- If any value looks suspicious, reject and ask user to fix config file

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

### Write Report Following Standard Format

**Report structure** (also in `references/report-format.md` if available):

```markdown
# Weekly TEAM_NAME Update – Month DD, YYYY

## Overall Status
🟢 On Track | 🟠 At Risk | 🔴 Off Track

**Current Status:** [One sentence explaining state]
*X% Completed, Y% In Progress, Z% Planned*

## Decisions Needed From Me
[Max 3, framed as questions. Omit if none.]

## Risks & Actions
| Risk | Data | Recommended Action |
|------|------|-------------------|
| [Specific risk] | [Evidence] | [Action] |

## Completed This Week (🟢)
[ONLY items completed during this reporting period]

## Shipping Next Week (⚪)
[Max 5 items that will actually ship]

## Blocked (if any)
[Specific blocker + who can unblock]

## Appendix – Initiative Deep Dives
[3-4 sentences per initiative, skip sub-task lists unless critical]
```

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

## Error Handling

**When jira-cli fails:**
- Authentication errors: Re-run `jira init` to reconfigure credentials
- Network errors: Check VPN connection, verify Jira URL is reachable
- Issue not found: Verify START_ISSUE key is correct and you have access
- Rate limiting: jira-cli handles this automatically with retries

**When config file issues occur:**
- File missing: Create template and ask user to fill values
- Malformed JSON: Show parsing error, ask user to fix syntax
- Missing required fields: List which fields are missing

**When convert_and_upload.py fails:**
- `uv` not installed: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `rclone` not configured: Run `rclone config` and create `gdrive` remote
- Upload timeout: File may have uploaded successfully - check Drive folder
- Permission denied: Verify user has write access to Shared Drive

**General approach:**
- Always check command exit codes before proceeding
- Show the actual error message to user, don't just say "failed"
- Provide actionable next steps for each failure mode

## Common Mistakes / Gotchas

**DON'T mechanically template the data** - this is the #1 mistake
- ❌ Bad: Copy-paste each Jira summary into bullet points
- ✅ Good: Group related work, write narrative, add context

**DON'T use Jira priority field blindly**
- ❌ Bad: Sort "Next Week" by Jira priority (may be outdated)
- ✅ Good: Use judgment - what matters most RIGHT NOW for delivery?

**DON'T skip comparison with previous report**
- ❌ Bad: Generate fresh report ignoring what happened since last week
- ✅ Good: Read previous report, note what changed (progress or regression)

**DON'T pad "Completed This Week" with old completions**
- ❌ Bad: Include items completed weeks ago to make section look full
- ✅ Good: ONLY include items completed during this reporting period

**DON'T dump the backlog into "Shipping Next Week"**
- ❌ Bad: List all 14 in-progress items
- ✅ Good: Max 5 items that will actually ship next week

**DON'T infer risks from single data points**
- ❌ Bad: One blocked item → "We're off track"
- ✅ Good: Look for patterns - clusters, trends, accumulation over time

**DON'T forget to validate shell variables**
- ❌ Bad: Use `$OUTPUT_DIR` directly in commands
- ✅ Good: Quote variables: `"$OUTPUT_DIR"` and validate no metacharacters

**DO expand ~ in paths** before using in shell commands
- ❌ Bad: Pass `~/weekly-reports` to Python script (some tools don't expand ~)
- ✅ Good: Use `os.path.expanduser()` or `${HOME}/weekly-reports`

**DO check prerequisites before running** - saves time vs debugging failures
- Verify `jira-cli`, `uv`, `rclone` are installed
- Test `jira-cli` with simple command: `jira issue list --limit 1`
- Test `rclone listremotes` shows configured remote

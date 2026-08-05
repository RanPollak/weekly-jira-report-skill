---
name: weekly-ai-catalyst-status
description: Generate weekly AI Catalyst team status report from Jira (AIPCC), meeting notes, and Gemini transcripts
---

# AI Catalyst Team Weekly Status Report

A skill for generating the weekly status report for the AI Catalyst team, led by Ran Pollak.

## What It Does

This skill gathers data from multiple sources and synthesizes a weekly team status report for the AI Catalyst group:

1. **Pulls Jira data** - Fetches AIPCC project issues assigned to team members, updated in the last 14 days
2. **Fetches team meeting notes** - Exports the team's running Google Doc via `gws` CLI, parses date-headed entries for wins, notes, and action items
3. **Gathers Gemini transcripts** - Searches Google Calendar for "AI Catalyst" events and exports attached "Notes by Gemini" docs via `gws` CLI
4. **Synthesizes the report** - Analyzes all data sources and produces a team-level weekly status report
5. **Uploads to Google Drive** - Saves locally and uploads as a Google Doc to the Catalyst weekly reports folder

## Team

| Member | Focus Areas |
|--------|-------------|
| Ran Pollak | Team Lead |
| Sergey Bekkerman | Vllm + KServe + llm-d Day 2 Operations |
| Sean Condon | GPU as a Service |
| Avi Avraham | Observability Org Pulse |
| Roy Belio | Catalyst Lab E2E |
| Eitan Geiger | Llama Stack, ACP Maintainer |
| Nati Fridman | Vllm + KServe + llm-d Day 2 Operations, ACP |
| Gerald Trotman | Agentic AI, Llama Stack, Observability, Org Pulse Dashboard, Catalyst POCs, Lab E2E, Dev Preview Pipeline |

## Google Workspace Access

**IMPORTANT: Always use the `gws` CLI for all Google interactions.** Do NOT use the Google Workspace MCP tools (they require browser OAuth each session and fail). Do NOT use rclone for Google Docs by ID.

`gws` is already authenticated via `~/.config/gws/client_secret.json` and supports all Google Workspace APIs natively.

## Trigger

When the user asks to:
- Generate the AI Catalyst weekly status
- Create the Catalyst team status report
- Write the AI Catalyst weekly update

Do NOT trigger for:
- AI First steering committee updates (that is a different skill: `weekly-ai-first-status`)
- Anything referencing RHAISTRAT-1401

## Instructions

**Working Directory:** `/home/rpollak/ai-first-status`

**Error Handling:** Complete end-to-end without stopping for user input. If any step fails partially, continue with available data.

### Step 1: Prerequisites Check

Verify `.env` exists and load `NOTES_DOC_ID`:

```bash
cd /home/rpollak/ai-first-status && source .env && echo "NOTES_DOC_ID=$NOTES_DOC_ID"
```

### Step 2: Fetch Jira Data (AIPCC Project)

```bash
acli jira workitem search \
  --jql 'project = AIPCC AND assignee IN ("sbekkerm@redhat.com", "scondon@redhat.com", "aavraham@redhat.com", "rbelio@redhat.com", "eigeiger@redhat.com", "nfridman@redhat.com", "gtrotman@redhat.com") AND updated >= -14d ORDER BY assignee, updated DESC' \
  --fields "key,summary,status,issuetype,assignee,description,updated" \
  --limit 100 \
  --json
```

Save as `jira_data`. For key issues, also fetch latest comment via `acli jira workitem comment list --key <KEY> --limit 1 --json`.

### Step 3: Fetch Team Meeting Notes (via gws)

```bash
cd /home/rpollak/ai-first-status && python3 scripts/fetch_meeting_notes.py "$NOTES_DOC_ID"
```

Save as `meeting_notes_data`. Primary source for wins, discussion topics, action items.

### Step 4: Fetch Gemini Transcripts (via gws, Optional)

```bash
cd /home/rpollak/ai-first-status && python3 scripts/fetch_transcripts.py "AI Catalyst"
```

Save as `transcript_data`. Supplementary source for meeting context.

### Step 5: Synthesize the Status Report

Using all available data, synthesize the report following this **exact structure**:

```markdown
# Weekly AI Catalyst Platform Update – [Mon DD, YYYY]

## 1. Team Celebrations / WIN
- **[Team Member Name]** – [Achievement with specifics and impact. Primary source: meeting notes wins field. Enrich with Jira completions.]
- **[Team Member Name]** – [Achievement]

---

## 2. Summary
🟢 On Track | 🟠 At Risk / Delay | 🔴 Off Track

**Current Status:** [One paragraph synthesizing the week: who delivered what, key new initiatives launched, notable progress, items stuck in review. Be specific — name people and issue keys. Include meeting context (wins, discussions, decisions) woven into the narrative naturally.]

*X% Completed • Y% In Progress • Z% Planned*

---

## 3. Completed This Week
1. **[AIPCC-XXXXX](https://redhat.atlassian.net/browse/AIPCC-XXXXX)** – [Title] ([Owner]) — Closed [date]. [Brief description of what was delivered.]

[ONLY items with status Closed that were updated this reporting period. If nothing, write "No completions this week."]

---

## 4. Shipping Next Week
[Max 5 items. What will actually ship — items In Progress or In Review closest to completion.]

1. **[AIPCC-XXXXX](https://redhat.atlassian.net/browse/AIPCC-XXXXX)** – [Title] ([Owner] — status, how long in review if applicable)

---

## Appendix – Initiative Deep Dives

### [Initiative Name] ([AIPCC-XXXXX](https://redhat.atlassian.net/browse/AIPCC-XXXXX))
**Owner:** [Name] • **Priority:** [Priority] • **Status:** [emoji] [Status]

[3-5 sentences: what this initiative is, current state, what happened this week, what's next. Weave in context from meeting notes where relevant — e.g., if the initiative was discussed in the weekly sync, include that discussion context. Reference sub-tasks by key.]

---

[Repeat for each major initiative. Group related issues under their parent initiative. An "initiative" is a Feature-type issue or a significant Epic with children.]
```

**Writing guidelines (same as weekly-jira-report):**
- **Target audience:** Managers who need to make decisions in 2 minutes.
- **Team Celebrations / WIN**: ALWAYS the FIRST section. Primary source is meeting notes `wins` field. Enrich with Jira completions. Bold the names.
- **Summary**: Comes AFTER wins. Executive overview paragraph with progress percentages.
- **Completed This Week**: ONLY items completed this reporting period. Never pad with old completions.
- **Shipping Next Week**: Max 5 items that will actually ship. Not a backlog dump.
- **Deep Dives**: 3-5 sentences per initiative. Weave in meeting discussion context where applicable. Skip sub-task lists unless critical.
- **Meeting context integration**: Don't create a separate "Discussion Highlights" section. Instead, weave meeting notes context (wins, discussions, action items, decisions) into the relevant sections: wins go into Team Celebrations, discussion topics go into the relevant Initiative Deep Dive, action items go into Summary or Shipping Next Week as appropriate.

### Step 6: Save and Upload to Google Drive

1. Format the date: `TITLE="Weekly AI Catalyst Platform Update – $(date +'%b %-d, %Y')"`

2. Save the report as markdown to: `~/catalyst weekly/$TITLE.md`

3. Upload to Google Drive — the filename becomes the Google Doc title:

```bash
TITLE="Weekly AI Catalyst Platform Update – $(date +'%b %-d, %Y')"
python3 ~/.claude/skills/weekly-jira-report/scripts/create_gdoc.py \
  "$HOME/catalyst weekly/$TITLE.md" \
  --folder-id "11iPCk23YY02-3XmtfPrOWLwxGR-b1Ylk"
```

The resulting Google Doc will be named **"Weekly AI Catalyst Platform Update – Aug 5, 2026"** (with the actual date).

**Drive folder:** https://drive.google.com/drive/folders/11iPCk23YY02-3XmtfPrOWLwxGR-b1Ylk

### Step 7: Report Success

Print:
1. The Google Doc URL
2. The Drive folder link
3. Brief summary of data sources used
4. Any warnings

**Do NOT ask the user if they want to continue.** The skill is complete.

## Credentials

Credentials stored in `.env` in `/home/rpollak/ai-first-status/`:
- `JIRA_EMAIL` - Red Hat email address
- `JIRA_TOKEN` - Jira/Confluence API token
- `NOTES_DOC_ID` - Google Doc ID for team meeting notes (`1AONqVzC8DtCVufAnMmyi0ARKRebvl3SSkqFVhWPFpSs`)

Google auth handled by `gws` CLI separately (`gws auth login`).

## Scope Boundaries

This skill is strictly for the **AI Catalyst team**. It does NOT:
- Fetch or reference AI First steering committee data
- Query RHAISTRAT issues
- Publish to Confluence
- Overlap with `weekly-ai-first-status`

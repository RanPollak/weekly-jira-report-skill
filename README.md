# Weekly AI Catalyst Status - Claude Code Skill

A Claude Code skill that generates weekly status reports for the AI Catalyst Platform team. It pulls data from three sources — Jira, a shared Google Doc with meeting notes, and Google Calendar Gemini transcripts — then has Claude synthesize everything into a single structured report and upload it as a Google Doc.

## How It Works

1. **Fetches Jira issues** from the AIPCC project for each team member (last 14 days) via `acli`
2. **Exports the team's meeting notes** from a shared Google Doc via `gws` CLI — parses date-headed weekly entries to extract wins, discussion topics, and action items
3. **Pulls Gemini transcripts** from the "Weekly AI Catalyst Group Sync" Google Calendar event via `gws` CLI
4. **Synthesizes the report** — Claude correlates all three sources, writes the narrative, calculates progress percentages, and produces the report in the established Catalyst weekly format
5. **Saves locally** to `~/catalyst weekly/` and **uploads as a native Google Doc** to the team's shared Drive folder

## Report Format

The output follows this structure (see a [live example](https://docs.google.com/document/d/1_OKqWW5Is3E-Lfocl_g-cvEukPUbltjEAWtRwtjezOY/edit)):

| Section | What goes in it |
|---------|----------------|
| **1. Team Celebrations / WIN** | 2-4 achievements — primary source is meeting notes, enriched with Jira completions |
| **2. Summary** | Status emoji, one-paragraph narrative naming people and issue keys, progress percentages |
| **3. Completed This Week** | Only issues closed this reporting period, with links, owners, and one-line descriptions |
| **4. Shipping Next Week** | Max 5 items closest to completion — In Progress or In Review |
| **Appendix — Initiative Deep Dives** | 3-5 sentences per initiative with meeting discussion context woven in |

Meeting context (wins, discussions, decisions, action items) is woven into the relevant sections — not dumped into a separate "Discussion Highlights" block.

## Quick Start

### 1. Install prerequisites

```bash
# Atlassian CLI for Jira
pip install acli

# Google Workspace CLI for Docs, Calendar, Drive
npm install -g @googleworkspace/cli
```

### 2. Authenticate

```bash
acli auth login
gws auth login
```

### 3. Clone the skill

```bash
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-ai-catalyst-status
```

### 4. Configure credentials

Create `.env` in your working directory:

```env
JIRA_EMAIL=you@redhat.com
JIRA_TOKEN=your-jira-api-token
NOTES_DOC_ID=your-google-doc-id
```

- **JIRA_TOKEN**: Get one at https://id.atlassian.com/manage-profile/security/api-tokens
- **NOTES_DOC_ID**: The ID from your team's meeting notes Google Doc URL (`https://docs.google.com/document/d/<THIS_ID>/edit`)

### 5. Generate a report

```
Generate the AI Catalyst weekly status
```

## Data Sources

| Source | Tool | Script | What it provides |
|--------|------|--------|------------------|
| Jira (AIPCC project) | `acli` | direct CLI call | Issue status, completions, assignees, descriptions |
| Team meeting notes | `gws` | `scripts/fetch_meeting_notes.py` | Wins, discussion topics, action items, attendees |
| Gemini transcripts | `gws` | `scripts/fetch_transcripts.py` | AI-generated meeting summaries from Google Calendar |
| Google Drive upload | `gws` | `scripts/create_gdoc.py` | Uploads markdown as a native Google Doc |

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
| Gerald Trotman | Agentic AI, Llama Stack, Observability, Org Pulse, Catalyst POCs, Dev Preview Pipeline |

## Project Structure

```
weekly-ai-catalyst-status/
├── SKILL.md                        # Skill definition — workflow steps, report format, writing guidelines
├── scripts/
│   ├── fetch_meeting_notes.py      # Export & parse Google Doc meeting notes (gws)
│   ├── fetch_transcripts.py        # Fetch Gemini transcripts from Calendar events (gws)
│   ├── create_gdoc.py              # Upload markdown as native Google Doc (gws)
│   ├── fetch_notes.py              # Older meeting notes fetcher (still works, different parsing)
│   └── fetch_demos.py              # Scan Drive folder for demo videos / blog posts
└── references/
    └── report-format.md            # Report template reference
```

## FAQ

**How is this different from the `weekly-ai-first-status` skill?**

They cover different teams. This skill reports on the AI Catalyst team (Ran's group, AIPCC Jira project, team sync meeting notes) and uploads to Google Drive. The AI First skill reports on the org-wide AI First initiative (RHAISTRAT-1401, steering committee) and publishes to Confluence.

**Does this modify Jira data?**

No. Read-only — it fetches issues and comments but never writes.

**What if the meeting notes or transcripts are unavailable?**

Both are optional. The skill continues with Jira data only and notes the gap in the output.

**Can I use this for a different team?**

Yes. Update the team member email list in SKILL.md (Step 2 JQL query), the AIPCC project key if different, and the `NOTES_DOC_ID` in `.env` to point to your team's meeting notes doc.

## License

Apache License 2.0

## Author

Created by Ran Pollak ([@RanPollak](https://github.com/RanPollak))

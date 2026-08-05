# Weekly AI Catalyst Status - Claude Code Skill

An AI-native Claude Code skill that generates weekly status reports for the AI Catalyst team. Pulls Jira data (AIPCC project), team meeting notes (Google Doc), and Gemini transcripts (Google Calendar), then synthesizes everything into a structured report uploaded to Google Drive.

## What Makes This AI-Native

Traditional report scripts mechanically dump Jira data into a template. This skill has Claude:

- **Correlate multiple sources** -- Jira data, meeting notes (Google Doc), and Gemini transcripts feed into one coherent report
- **Write the WIN section from real conversations** -- meeting notes are the primary source for celebrations, not Jira status fields
- **Weave meeting context into deep dives** -- discussions, decisions, and action items appear in the relevant initiative section
- **Analyze patterns** -- identify risk clusters, stalled items, review queue friction
- **Write with judgment** -- summarize completed work as a narrative, not a raw list
- **Track changes** -- compare against last week's report to highlight what changed

## Prerequisites

- [acli](https://github.com/redhat-et/acli) -- Atlassian CLI for Jira Cloud
- [gws](https://github.com/nicholasgasior/gws) -- Google Workspace CLI (for meeting notes, transcripts, and Google Doc creation)

## Installation

### As a Claude Code Skill

```bash
cd ~/.claude/skills
git clone https://github.com/RanPollak/weekly-jira-report-skill.git weekly-ai-catalyst-status
```

Claude Code will automatically discover the skill.

### Setup

#### 1. Configure acli

```bash
acli auth login
```

#### 2. Configure gws

```bash
npm install -g @googleworkspace/cli
gws auth login
```

#### 3. Create .env file

Create `.env` in your working directory (e.g., `/home/rpollak/ai-first-status/`):

```env
JIRA_EMAIL=you@redhat.com
JIRA_TOKEN=your-api-token-here
NOTES_DOC_ID=your-google-doc-id-here
```

Get your Jira API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

Ask Claude:

```
Generate the AI Catalyst weekly status
```

Claude will:
1. Fetch AIPCC Jira data for team members via `acli`
2. Fetch meeting notes from the Google Doc via `gws`
3. Fetch Gemini transcripts from Google Calendar via `gws`
4. Synthesize the report using the established Catalyst weekly format
5. Save locally and upload as a native Google Doc to the team Drive folder

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

## Data Sources

| Source | Tool | Purpose |
|--------|------|---------|
| Jira (AIPCC) | `acli` | Issue status, completions, initiatives |
| Meeting notes | `scripts/fetch_meeting_notes.py` | WIN section (primary), team discussions |
| Gemini transcripts | `scripts/fetch_transcripts.py` | Calendar event transcripts |
| Google Doc output | `scripts/create_gdoc.py` | Upload report as native Google Doc |

## Project Structure

```
weekly-ai-catalyst-status/
├── SKILL.md                        # Skill manifest and workflow instructions
├── scripts/
│   ├── fetch_meeting_notes.py      # Fetch & parse meeting notes from Google Doc via gws
│   ├── fetch_transcripts.py        # Fetch Gemini transcripts from Google Calendar via gws
│   ├── fetch_notes.py              # Legacy: fetch notes (older format)
│   ├── fetch_demos.py              # Scan Drive folder for recent demos/blogs
│   ├── create_gdoc.py              # Upload markdown as native Google Doc
│   └── convert_and_upload.py       # Legacy HTML conversion (deprecated)
└── references/
    └── report-format.md            # Report template and format reference
```

## Report Sections

1. **Summary** -- status emoji, one paragraph narrative, progress percentages
2. **Team Celebrations / WIN** -- achievements from meeting notes, enriched with Jira completions
3. **Completed This Week** -- only current-period completions from Jira
4. **Shipping Next Week** -- max 5 items that will actually ship
5. **Appendix -- Initiative Deep Dives** -- 3-5 sentences each, meeting context woven in

## FAQ

**Q: How is this different from the weekly-ai-first-status skill?**
A: This skill covers the AI Catalyst team (Ran's group, AIPCC project). The AI First skill covers the org-wide AI First initiative (RHAISTRAT-1401, steering committee) and publishes to Confluence.

**Q: Does this modify my Jira data?**
A: No, it's read-only. It only fetches data, never writes to Jira.

**Q: What if meeting notes or transcripts are unavailable?**
A: Both are optional. The skill falls back to Jira-only mode and notes the gap in the report.

## License

Apache License 2.0

## Author

Created by Ran Pollak ([@RanPollak](https://github.com/RanPollak))

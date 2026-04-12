# Weekly Report Format Reference

Use this as the template structure when writing the report. Adapt section content using your judgment -- don't fill sections mechanically.

## Report Template

```markdown
# Weekly TEAM_NAME Update – Month DD, YYYY

## Overall Status
🟢 On Track
🟠 At Risk / Delay
🔴 Off Track

**Current Status:** [Your assessed status with emoji]
*X% Completed, Y% In Progress, Z% Planned*

## This Week – What Actually Happened (🟢 Completed only)

[Summarize completed work. Group related items. Tell the story of what got done, not just a raw list.]

- [KEY](link) - Summary (Assignee: Name)
  *Brief context on why this matters*

## Next Week – What Will Be Delivered (Planned & In Progress ⚪)

**Priority Order (Highest to Lowest):**

[Prioritize by actual impact, not just Jira priority field.]

- [KEY](link) - Summary (Assignee: Name)

## What Is Blocked

[For each blocker, explain the likely cause and suggest who might unblock it.]

- [KEY](link) - Summary (Assignee: Name)
  - **Blocker:** [Inferred from issue data]
  - **Owner to unblock:** [Best guess based on context]

## Risks

[Identify from patterns: clusters of blocked items, missing assignees, overdue dates, stalled work.]

- Risk 1: [Specific, actionable risk with evidence]
- Risk 2: [Specific, actionable risk with evidence]

## Decisions Needed From Me

[Infer from blockers and risks what leadership needs to decide.]

- Decision 1: [Specific decision with context]

## Team Health / Notes

[Note workload distribution, velocity trends, blocked item accumulation. Ask user to confirm.]

- Overall team health: [Your assessment]
- Key notes: [Observations]

---

## Deep Dive – Major Work & End Goals

### Initiative Name ([KEY](link))
**Target Delivery Date:** YYYY-MM-DD
**Priority:** [emoji] Priority
**Status:** [emoji] Status

🟢 X% Completed  🔄 Y% In progress  ⚪ Z% Planned

[Write a brief narrative about where this initiative stands, not just numbers.]

| Date | Original Target | Updated Target | Change Summary | Impact | Owner |
|------|----------------|----------------|----------------|---------|-------|
| TBD | TBD | TBD | TBD | TBD | TBD |

**Sub-tasks (N total):**

*Completed (X):*
- [KEY](link) - Summary (Assignee: Name)

*In Progress (Y):*
- [KEY](link) - Summary (Assignee: Name)

*Blocked (Z):*
- [KEY](link) - Summary (Assignee: Name)

---
```

## Issue Categorization

| Jira Status | Category |
|-------------|----------|
| Done, Closed | Completed |
| In Progress, Review | In Progress |
| Blocked | Blocked |
| Everything else | Planned |

## Priority Emoji Mapping

| Priority | Emoji |
|----------|-------|
| Highest / High | 🔴 |
| Medium | 🟠 |
| Low / Lowest | 🟢 |

## Status Emoji Mapping

| Condition | Status | Emoji |
|-----------|--------|-------|
| Blocked items exist | Off Track | 🔴 |
| >60% in progress or more in-progress than completed | At Risk | 🟠 |
| Default | On Track | 🟢 |

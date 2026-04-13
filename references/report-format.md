# Weekly Report Format Reference

**Target Audience:** Managers who need to make decisions in 2 minutes.

**Design Principle:** Actions first, context second. Front-load what the reader needs to *do*, then provide supporting detail.

## Report Template

```markdown
# Weekly TEAM_NAME Update – Month DD, YYYY

## 1. Status Line
🟢 On Track | 🟠 At Risk | 🔴 Off Track

**Status:** [emoji] [One sentence: what's the overall state and why]

*Progress: X% Completed • Y% In Progress • Z% Planned*

---

## 2. Decisions Needed

[Max 3 decisions. One line each. These should be yes/no or choice questions.]

1. **[Decision topic]** – [Brief context, 1-2 sentences max]
2. **[Decision topic]** – [Brief context]

If no decisions needed, write "None at this time."

---

## 3. Risks & Actions

[Table format for quick scanning. Max 5 risks.]

| Risk | Impact | Recommended Action |
|------|--------|-------------------|
| [Specific risk with data] | [What breaks if unfixed] | [Who does what] |
| Nati owns 38% of initiatives | Bottleneck, delays if unavailable | Redistribute 2-3 items to others |
| No completions in 3 days | Possible blockers or scope issues | Sprint review to identify blockers |

**Team Health Note:** [1-2 sentences on workload distribution, velocity trends, or morale. Skip if nothing notable.]

---

## 4. Completed This Week

[Only items completed during this reporting period. If none, write "No completions this week." Do NOT list old completions.]

- **[KEY](link)** – Summary (Owner: Name)  
  *[One line: why this matters or what it unblocks]*

---

## 5. Shipping Next Week

[Max 5 items. What will *actually* ship, not everything in the backlog. Prioritize by impact.]

1. **[KEY](link)** – Summary (Owner: Name)
2. **[KEY](link)** – Summary (Owner: Name)

---

## 6. Blocked

[Only if blockers exist. For each, state the blocker and who can unblock.]

- **[KEY](link)** – Summary (Owner: Name)  
  **Blocker:** [Specific reason]  
  **Action:** [Who needs to do what]

If nothing blocked, omit this section entirely.

---

## Appendix: Initiative Details

[Collapsible/optional reading. Deep dive on major initiatives. Keep each to 3-4 sentences max.]

### [Initiative Name] ([KEY](link))
**Target:** YYYY-MM-DD • **Priority:** [emoji] • **Status:** [emoji] [Brief status phrase]

*Progress: X% done, Y% in progress, Z% planned*

[2-3 sentences on current state, next milestone, any concerns. Skip sub-task lists unless critical to understanding.]

---
```

---

## Reference: Issue Categorization

| Jira Status | Category |
|-------------|----------|
| Done, Closed | Completed |
| In Progress, In Review | In Progress |
| Blocked | Blocked |
| Everything else | Planned |

## Reference: Priority Emoji Mapping

| Priority | Emoji |
|----------|-------|
| Highest / High | 🔴 |
| Medium | 🟠 |
| Low / Lowest | 🟢 |

## Reference: Overall Status Logic

| Condition | Status | Emoji |
|-----------|--------|-------|
| Multiple blockers OR critical blocker | Off Track | 🔴 |
| >60% in progress with low completion OR workload imbalance | At Risk | 🟠 |
| Making steady progress, no major concerns | On Track | 🟢 |

**Use judgment:** A minor blocker doesn't automatically mean Off Track. Context matters.

---

## Writing Guidelines

### Section 1: Status Line
- **One sentence** summarizing the current state
- Good: "On track - 3 initiatives shipping this week, Dev Preview pipeline staffing in progress"
- Bad: "Overall status is good. We have made progress on several items."

### Section 2: Decisions Needed
- Frame as **questions requiring a yes/no or choice**
- Include just enough context to make the decision (1-2 sentences)
- If a decision was already covered in Risks, don't repeat it here

### Section 3: Risks & Actions
- **Be specific:** "Nati owns 38% of initiatives" not "workload imbalance"
- **Quantify impact:** "Delays if unavailable" not "might cause issues"
- **Actionable:** "Redistribute 2-3 items" not "monitor situation"
- **Table format** for fast scanning - keep cells concise

### Section 4: Completed This Week
- **Only items completed during this reporting period**
- If nothing completed, write "No completions this week" and move on
- **Never** list items completed in previous weeks under "This Week"

### Section 5: Shipping Next Week
- **Max 5 items** - if you have 14 items, you're listing the entire backlog
- What will **actually ship**, not what's theoretically in progress
- Prioritize by business impact, not Jira priority field

### Section 6: Blocked
- Omit entirely if nothing is blocked (don't write "None")
- For each blocker: specific reason + who can unblock
- Group related blockers to reduce line count

### Appendix: Initiative Details
- This is **optional reading** - most managers will skip it
- 3-4 sentences max per initiative
- Skip sub-task lists unless critical to understanding
- Focus on: where we are, what's next, any concerns

---

## What NOT to Include

❌ **"Changes from Last Week"** - readers can see what's new by reading the sections  
❌ **Summary section at the bottom** - redundant, readers already know the status  
❌ **Sub-task breakdowns in the main body** - move to appendix  
❌ **Old completions under "This Week"** - misleading  
❌ **Every open item under "Next Week"** - that's a backlog dump, not a plan  
❌ **Generic risks** - "timeline may slip" is not a risk without specifics  
❌ **Process notes** - "we had a meeting" doesn't belong unless it yielded a decision

# Weekly Report Format Reference

**Target Audience:** Managers who need to make decisions in 2 minutes.

**Design Principle:** Actions first, context second. Front-load what the reader needs to *do*, then provide supporting detail.

## Report Template

```markdown
# Weekly TEAM_NAME Update – Month DD, YYYY

## 1. Summary
🟢 On Track | 🟠 At Risk | 🔴 Off Track

**Current Status:** [One sentence with key highlights, workload distribution notes]

*X% Completed • Y% In Progress • Z% Planned*

---

## 2. Team Celebrations / WIN

- **[Team Member Name]** – [Achievement with specifics]. [Impact or key details]. [Issue key if applicable].
- **[Team Member Name]** – [Achievement with specifics]. [Impact or key details]. [Issue key if applicable].
- **[Team Member Name]** – [Achievement with specifics]. [Impact or key details]. [Issue key if applicable].

---

## 3. Risks & Actions

[Table format for quick scanning. Max 5 risks.]

| Risk | Data | Recommended Action |
|------|------|-------------------|
| [Specific risk] | [Evidence with numbers] | [Who does what] |
| Workload concentration | Nati owns 38% of initiatives | Redistribute 2-3 items to others by mid-May |
| Forecast slippage | 3 of 4 forecasted items didn't ship | Review estimation - are we over-committing? |

**Team Health Note:** [Workload distribution metrics, velocity trends, completion momentum. 2-3 sentences.]

---

## 4. Completed This Week

[Only items completed during this reporting period. If none, write "No completions this week." Do NOT list old completions.]

1. **[KEY](link)** – [Title] ([Owner]) - [Brief description with key details]

---

## 5. Shipping Next Week

[Max 5 items. What will *actually* ship, not everything in the backlog. Prioritize by impact.]

1. **[KEY](link)** – [Title] ([Owner, deadline if applicable])

---

## Appendix – Initiative Deep Dives

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

### Section 1: Summary
- **One sentence** with key highlights and positive framing when appropriate
- Include workload distribution improvements if notable
- Good: "Strong completions this week - POCExplorer video demo shipped, OpenShift deployment plan delivered. Workload distribution excellent: Gerald 27%, Nati 27%"
- Bad: "Overall status is good. We have made progress on several items."

### Section 2: Team Celebrations / WIN
- **ALWAYS include** - recognize 2-4 team members for achievements this week
- Use **bold for names** to make them stand out
- Be **specific with details**: issue keys, completion dates, technical achievements, impact
- **Celebrate wins, not just completions** - what was hard about this? What did it enable?
- Good: "**Roy Belio** – POCExplorer Video Demo shipped! 3-minute showcase complete, closed May 6, meeting EOW May 8 deadline early."
- Bad: "Roy completed his task."

### Section 3: Risks & Actions
- **Be specific:** "Nati owns 38% of initiatives" not "workload imbalance"
- **Quantify with data:** Use percentages, counts, dates
- **Actionable:** "Redistribute 2-3 items by mid-May" not "monitor situation"
- **Table format** for fast scanning - keep cells concise
- End with **Team Health Note**: workload distribution, velocity trends, team observations (2-3 sentences)
- **Blockers go in this table**, not a separate section

### Section 4: Completed This Week
- **Only items completed during this reporting period**
- If nothing completed, write "No completions this week" and move on
- **Never** list items completed in previous weeks under "This Week"
- Format: `1. **[KEY](link)** – [Title] ([Owner]) - [Brief description]`

### Section 5: Shipping Next Week
- **Max 5 items** - if you have 14 items, you're listing the entire backlog
- What will **actually ship**, not what's theoretically in progress
- Prioritize by business impact, not Jira priority field
- Include owner and deadline if known

### Appendix: Initiative Deep Dives
- This is **optional reading** - most managers will skip it
- 3-4 sentences max per initiative
- Skip sub-task lists unless critical to understanding
- Focus on: where we are, what's next, any concerns
- Use emoji indicators (🟢/🟡/🔴) for visual status

---

## What NOT to Include

❌ **"Decisions Needed From Me"** - removed from standard format, handle through other channels  
❌ **Separate "Blocked" section** - blockers go in the Risks & Actions table  
❌ **"Changes from Last Week"** - readers can see what's new by reading the sections  
❌ **Summary section at the bottom** - redundant, readers already know the status  
❌ **Sub-task breakdowns in the main body** - move to appendix  
❌ **Old completions under "This Week"** - misleading  
❌ **Every open item under "Next Week"** - that's a backlog dump, not a plan  
❌ **Generic risks** - "timeline may slip" is not a risk without specifics  
❌ **Process notes** - "we had a meeting" doesn't belong unless it yielded a decision  
❌ **Generic celebrations** - "Good job team!" instead of specific achievements with names and details

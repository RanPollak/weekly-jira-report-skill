#!/usr/bin/env python3
"""
Generate Weekly Team Update in the specified format
"""
import requests
import os
from datetime import datetime
from config_loader import load_config, validate_required

CFG = load_config()
validate_required(CFG, ["JIRA_URL", "EMAIL", "API_TOKEN", "START_ISSUE", "TEAM_NAME", "OUTPUT_DIR"])

JIRA_URL = CFG["JIRA_URL"]
EMAIL = CFG["EMAIL"]
API_TOKEN = CFG["API_TOKEN"]
START_ISSUE = CFG["START_ISSUE"]
TEAM_NAME = CFG["TEAM_NAME"]
OUTPUT_DIR = CFG["OUTPUT_DIR"]

headers = {'Content-Type': 'application/json'}
AUTH = (EMAIL, API_TOKEN)

def get_issue(issue_key):
    """Fetch issue details from Jira"""
    try:
        response = requests.get(
            f"{JIRA_URL}/rest/api/3/issue/{issue_key}",
            headers=headers,
            auth=AUTH
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching {issue_key}: {e}")
        return None

def search_issues(jql, max_results=100):
    """Search for issues using JQL"""
    try:
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/search/jql",
            headers=headers,
            auth=AUTH,
            json={
                'jql': jql,
                'maxResults': max_results,
                'fields': ['summary', 'status', 'assignee', 'issuetype', 'priority', 'updated', 'parent', 'duedate', 'description']
            }
        )
        if response.status_code == 200:
            return response.json().get('issues', [])
        return []
    except Exception as e:
        print(f"Error searching: {e}")
        return []

def get_child_issues(issue_key):
    """Get all child issues"""
    jql = f'parent = {issue_key}'
    return search_issues(jql)

def categorize_issues(issues):
    """Categorize issues by status"""
    completed = []
    in_progress = []
    planned = []
    blocked = []

    for issue in issues:
        status = issue.get('fields', {}).get('status', {}).get('name', '').lower()

        if status in ['done', 'closed']:
            completed.append(issue)
        elif status in ['in progress', 'review']:
            in_progress.append(issue)
        elif status in ['blocked']:
            blocked.append(issue)
        else:
            planned.append(issue)

    return completed, in_progress, planned, blocked

def calculate_progress(completed, in_progress, planned):
    """Calculate percentage breakdown"""
    total = len(completed) + len(in_progress) + len(planned)
    if total == 0:
        return 0, 0, 0

    completed_pct = round((len(completed) / total) * 100)
    in_progress_pct = round((len(in_progress) / total) * 100)
    planned_pct = 100 - completed_pct - in_progress_pct

    return completed_pct, in_progress_pct, planned_pct

def extract_summary_from_description(description_text):
    """Extract or generate a meaningful summary from Jira description"""
    if not description_text:
        return ""

    # Clean up the text
    description_text = description_text.strip()
    if not description_text:
        return ""

    # Look for key sections in the description
    key_patterns = [
        'Objective:',
        'Goal:',
        'Goals:',
        'Overview:',
        'Summary:',
        'Description:',
        'Purpose:'
    ]

    # Try to find a key section
    lower_text = description_text.lower()
    for pattern in key_patterns:
        pattern_lower = pattern.lower()
        if pattern_lower in lower_text:
            # Find the section
            start = lower_text.index(pattern_lower) + len(pattern_lower)
            # Get text after the pattern until next section or end
            remaining = description_text[start:].strip()

            # Skip if remaining is empty or too short
            if len(remaining) < 10:
                continue

            # Find first complete sentence (look for ". " or ".\n")
            sentence_markers = []
            for marker in ['. ', '.\n']:
                idx = remaining.find(marker)
                if idx > 0:
                    sentence_markers.append(idx + 1)  # Include the period

            if sentence_markers:
                # Get the first complete sentence
                first_sentence_end = min(sentence_markers)
                summary = remaining[:first_sentence_end].strip()

                # If sentence is reasonable length, return it
                if 15 < len(summary) < 250:
                    return summary
                # If too long, try to find a natural break
                elif len(summary) >= 250:
                    # Look for comma or semicolon in first 150 chars
                    for break_char in [';', ',']:
                        break_idx = summary[:150].rfind(break_char)
                        if break_idx > 40:
                            return summary[:break_idx] + '.'

            # Fallback: take up to newline or reasonable length
            newline_idx = remaining.find('\n')
            if newline_idx > 15:
                segment = remaining[:newline_idx].strip()
                if segment and len(segment) > 15:
                    if not segment.endswith('.'):
                        segment += '.'
                    return segment if len(segment) < 200 else segment[:150] + '.'

    # If no key section found, use first paragraph/sentence
    # Split by double newline first (paragraphs)
    paragraphs = description_text.split('\n\n')
    first_para = paragraphs[0].strip()

    # Try to get first sentence
    sentences = first_para.split('. ')
    if sentences:
        first_sentence = sentences[0].strip()
        # Use if it's a reasonable length
        if 15 < len(first_sentence) < 200:
            result = first_sentence if first_sentence.endswith('.') else first_sentence + '.'
            return result
        elif len(first_sentence) >= 200:
            # Try to cut at a reasonable point
            last_space = first_sentence[:150].rfind(' ')
            if last_space > 40:
                return first_sentence[:last_space] + '...'

    # Final fallback: take first line
    first_line = description_text.split('\n')[0].strip()
    if 15 < len(first_line) < 200:
        return first_line if first_line.endswith('.') else first_line + '.'

    return ""

def format_issue_line(issue):
    """Format a single issue as a markdown line"""
    key = issue.get('key')
    summary = issue.get('fields', {}).get('summary', 'No summary')
    assignee = issue.get('fields', {}).get('assignee', {})
    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'

    # Extract description and create intelligent summary
    description = issue.get('fields', {}).get('description', {})
    short_desc = ""
    if description and isinstance(description, dict):
        # Jira description is in ADF (Atlassian Document Format)
        content = description.get('content', [])
        if content:
            text_parts = []
            for block in content:
                if block.get('type') == 'paragraph':
                    for item in block.get('content', []):
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
            full_text = ' '.join(text_parts).strip()

            summary_text = extract_summary_from_description(full_text)
            if summary_text:
                short_desc = f"<br>  *{summary_text}*"

    return f"- [{key}]({JIRA_URL}/browse/{key}) - {summary} (Assignee: {assignee_name}){short_desc}"

def generate_deep_dive(initiatives):
    """Generate deep dive section for major initiatives"""
    deep_dive = []

    for initiative in initiatives:
        key = initiative.get('key')
        summary = initiative.get('fields', {}).get('summary', '')
        status = initiative.get('fields', {}).get('status', {}).get('name', 'Unknown')
        priority = initiative.get('fields', {}).get('priority', {})
        priority_name = priority.get('name', 'Medium') if priority else 'Medium'
        duedate = initiative.get('fields', {}).get('duedate', 'TBD')

        # Get child issues for this initiative
        children = get_child_issues(key)
        completed, in_progress, planned, blocked = categorize_issues(children)
        completed_pct, in_progress_pct, planned_pct = calculate_progress(completed, in_progress, planned)

        # Determine status emoji
        status_emoji = "🟢"
        if blocked or status.lower() in ['blocked', 'at risk']:
            status_emoji = "🔴"
        elif in_progress_pct > 60 or status.lower() == 'in progress':
            status_emoji = "🟠"

        # Priority emoji
        priority_emoji = "🟢"
        if priority_name in ['Highest', 'High']:
            priority_emoji = "🔴"
        elif priority_name == 'Medium':
            priority_emoji = "🟠"

        deep_dive.append(f"\n### {summary} ([{key}]({JIRA_URL}/browse/{key}))")
        deep_dive.append(f"**Target Delivery Date:** {duedate if duedate != 'TBD' else 'Not Set'}")
        deep_dive.append(f"**Priority:** {priority_emoji} {priority_name}")
        deep_dive.append(f"**Status:** {status_emoji} {status}")
        deep_dive.append(f"\n🟢 {completed_pct}% Completed  🔄 {in_progress_pct}% In progress  ⚪ {planned_pct}% Planned")

        deep_dive.append("\n| Date | Original Target | Updated Target | Change Summary | Impact | Owner |")
        deep_dive.append("|------|----------------|----------------|----------------|---------|-------|")
        deep_dive.append("| TBD | TBD | TBD | TBD | TBD | TBD |")

        deep_dive.append(f"\n**Description:**")
        deep_dive.append(f"{summary}")

        # Add child breakdown if there are children
        if children:
            deep_dive.append(f"\n**Sub-tasks ({len(children)} total):**")
            if completed:
                deep_dive.append(f"\n*Completed ({len(completed)}):*")
                for issue in completed[:5]:  # Limit to top 5
                    deep_dive.append(format_issue_line(issue))

            if in_progress:
                deep_dive.append(f"\n*In Progress ({len(in_progress)}):*")
                for issue in in_progress[:5]:
                    deep_dive.append(format_issue_line(issue))

            if blocked:
                deep_dive.append(f"\n*Blocked ({len(blocked)}):*")
                for issue in blocked:
                    deep_dive.append(format_issue_line(issue))

        deep_dive.append("\n---")

    return "\n".join(deep_dive)

def generate_weekly_update():
    """Generate the complete weekly update"""
    today = datetime.now().strftime("%B %d, %Y")

    # Get the main issue
    main_issue = get_issue(START_ISSUE)
    if not main_issue:
        print("Failed to fetch main issue")
        return

    # Get all child initiatives
    initiatives = get_child_issues(START_ISSUE)

    # Categorize all issues
    all_completed, all_in_progress, all_planned, all_blocked = categorize_issues(initiatives)

    # Calculate overall progress
    completed_pct, in_progress_pct, planned_pct = calculate_progress(all_completed, all_in_progress, all_planned)

    # Determine overall status
    overall_status = "🟢 On Track"
    if len(all_blocked) > 0:
        overall_status = "🔴 Off Track"
    elif in_progress_pct > 60 or len(all_in_progress) > len(all_completed):
        overall_status = "🟠 At Risk / Delay"

    # Generate report
    report = []
    report.append(f"# Weekly {TEAM_NAME} Update – {today}\n")

    report.append("## Overall Status")
    report.append("🟢 On Track")
    report.append("🟠 At Risk / Delay")
    report.append("🔴 Off Track\n")
    report.append(f"**Current Status:** {overall_status}")
    report.append(f"*{completed_pct}% Completed, {in_progress_pct}% In Progress, {planned_pct}% Planned*\n")

    report.append("## This Week – What Actually Happened (🟢 Completed only)")
    if all_completed:
        for issue in all_completed[:10]:  # Top 10 completed
            report.append(format_issue_line(issue))
    else:
        report.append("*No completed items to report this week.*")
    report.append("")

    report.append("## Next Week – What Will Be Delivered (Planned & In Progress ⚪)")
    report.append("**Priority Order (Highest to Lowest):**\n")

    # Combine in-progress and high-priority planned
    next_week = all_in_progress + [i for i in all_planned if i.get('fields', {}).get('priority', {}).get('name', '') in ['Highest', 'High']]

    if next_week:
        for issue in next_week[:10]:  # Top 10
            report.append(format_issue_line(issue))
    else:
        report.append("*No planned work for next week.*")
    report.append("")

    report.append("## What Is Blocked")
    if all_blocked:
        for issue in all_blocked:
            report.append(format_issue_line(issue))
            report.append("  - **Blocker:** TBD (Update manually)")
            report.append("  - **Owner to unblock:** TBD (Update manually)\n")
    else:
        report.append("*No blockers at this time.* ✅")
    report.append("")

    report.append("## Risks")
    report.append("*Identify forward-looking risks manually based on team assessment.*")
    report.append("- Risk 1: TBD")
    report.append("- Risk 2: TBD\n")

    report.append("## Decisions Needed From Me")
    report.append("*List specific decisions required to move forward.*")
    report.append("- Decision 1: TBD")
    report.append("- Decision 2: TBD\n")

    report.append("## Team Health / Notes")
    report.append("*Provide team health update manually.*")
    report.append("- Overall team health: TBD")
    report.append("- Key notes: TBD\n")

    report.append("---\n")
    report.append("## Deep Dive – Major Work & End Goals\n")
    report.append(generate_deep_dive(initiatives[:10]))  # Top 10 initiatives

    return "\n".join(report)

# Main execution
if __name__ == "__main__":
    print(f"Generating weekly update for {TEAM_NAME}...\n")
    report = generate_weekly_update()

    if report:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{CFG['TEAM_NAME_SLUG']}_Weekly_Update_{datetime.now().strftime('%Y-%m-%d')}.md")

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"✓ Report generated: {output_file}")
        print(f"✓ Total length: {len(report)} characters")
    else:
        print("✗ Failed to generate report")

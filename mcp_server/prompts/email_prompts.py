# mcp_server/prompts/email_prompts.py
from mcp_server.config import mcp


# ─── Daily Summary ────────────────────────────────────────────────────────────


def _build_summary_template() -> str:
    """Build the daily email summary prompt template."""
    return """
    Analyze my emails from today and create an executive summary with these sections:

    1. **Urgent** — Emails that require immediate response
    2. **Pending tasks** — Actions I need to take
    3. **Relevant info** — Important updates or announcements
    4. **Low priority** — Emails that can wait

    Instructions:
    - Use the list_emails tool with query "newer_than:1d" to fetch today's emails
    - Prioritize by urgency and impact
    - Be concise and actionable
    - If there are no emails in a category, skip it
    """


@mcp.prompt()
def daily_email_summary() -> str:
    """
    Prompt: Generate an executive summary of today's emails.
    Instructs the LLM to categorize emails by urgency and priority.
    """
    return _build_summary_template()

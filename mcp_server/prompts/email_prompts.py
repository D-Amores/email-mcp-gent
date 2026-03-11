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


# ─── Compose Professional Email ───────────────────────────────────────────────


def _recipient_context(recipient: str) -> str:
    """Build recipient context string."""
    return f" to {recipient}" if recipient else ""


def _subject_context(subject: str) -> str:
    """Build subject context string."""
    return f' with subject "{subject}"' if subject else ""


def _build_compose_template(recipient: str, subject: str) -> str:
    """Build the professional email compose prompt template."""
    return f"""
    Help me write a professional email{_recipient_context(recipient)}{_subject_context(subject)}.

    Instructions:
    - Ask me for the purpose of the email if it is not clear
    - Use a professional and cordial tone
    - Follow this structure:
        1. Greeting
        2. Context
        3. Main message
        4. Call to action
        5. Closing
    - Check spelling and grammar before sending
    - Once the email is ready, use the send_email tool to send it
    """


@mcp.prompt()
def compose_professional_email(recipient: str = "", subject: str = "") -> str:
    """
    Prompt: Assistant for composing professional emails.

    Args:
        recipient: Email recipient (optional)
        subject: Email subject (optional)
    """
    return _build_compose_template(recipient, subject)

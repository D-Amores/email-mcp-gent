import base64
from email.mime.text import MIMEText
from mcp_server.config import mcp, SCOPES
from mcp_server.gmail_auth import get_gmail_service

# Constants
GMAIL_USER_ID = "me"


def _build_mime_message(to: str, subject: str, body: str) -> MIMEText:
    """Build a MIME email message with headers."""
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    return message


def _encode_message(message: MIMEText) -> dict:
    """Encode a MIME message to base64 for Gmail API."""
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def _send_raw_message(service, encoded_message: dict) -> dict:
    """Send an encoded message via Gmail API."""
    return (
        service.users()
        .messages()
        .send(userId=GMAIL_USER_ID, body=encoded_message)
        .execute()
    )


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email from the user's Gmail account.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Plain text email body

    Returns:
        Confirmation with sent message ID
    """
    try:
        service = get_gmail_service(scopes=SCOPES)

        mime_message = _build_mime_message(to, subject, body)
        encoded_message = _encode_message(mime_message)
        sent_message = _send_raw_message(service, encoded_message)

        return {
            "status": "sent",
            "message_id": sent_message["id"],
            "to": to,
            "subject": subject,
        }

    except Exception as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")

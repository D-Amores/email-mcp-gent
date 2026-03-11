from mcp_server.config import mcp, SCOPES
from mcp_server.gmail_auth import get_gmail_service

# Constants
GMAIL_USER_ID = "me"
HEADER_SUBJECT = "Subject"
HEADER_FROM = "From"
DEFAULT_SUBJECT = "No subject"
DEFAULT_SENDER = "Unknown"


def _get_header_value(headers: list[dict], name: str, default: str) -> str:
    """Extract a specific header value from a list of headers."""
    return next((h["value"] for h in headers if h["name"] == name), default)


def _parse_email(message: dict) -> dict:
    """Parse a raw Gmail message into a clean dictionary."""
    headers = message["payload"]["headers"]

    return {
        "id": message["id"],
        "subject": _get_header_value(headers, HEADER_SUBJECT, DEFAULT_SUBJECT),
        "from": _get_header_value(headers, HEADER_FROM, DEFAULT_SENDER),
        "snippet": message.get("snippet", ""),
    }


def _fetch_email_details(service, message_id: str) -> dict:
    """Fetch full details of a single email by ID."""
    return service.users().messages().get(userId=GMAIL_USER_ID, id=message_id).execute()


@mcp.tool()
def list_emails(max_results: int = 10, query: str = "") -> list[dict]:
    """
    List recent emails from the user's inbox.

    Args:
        max_results: Maximum number of emails to return (default: 10)
        query: Gmail search filter (e.g. 'from:juan@example.com', 'is:unread')

    Returns:
        List of emails with id, subject, sender and snippet
    """
    try:
        service = get_gmail_service(scopes=SCOPES)

        results = (
            service.users()
            .messages()
            .list(userId=GMAIL_USER_ID, maxResults=max_results, q=query)
            .execute()
        )

        messages = results.get("messages", [])

        return [
            _parse_email(_fetch_email_details(service, msg["id"])) for msg in messages
        ]

    except Exception as e:
        raise RuntimeError(f"Failed to list emails: {str(e)}")

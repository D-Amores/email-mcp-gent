from mcp_server.config import mcp, SCOPES
from mcp_server.gmail_auth import get_gmail_service

# Constants
GMAIL_USER_ID = "me"


def _fetch_profile(service) -> dict:
    """Fetch raw Gmail profile data."""
    return service.users().getProfile(userId=GMAIL_USER_ID).execute()


def _format_profile(profile: dict) -> str:
    """Format raw profile data into readable markdown."""
    return (
        f"# Gmail Profile\n\n"
        f"**Email:** {profile['emailAddress']}\n"
        f"**Total messages:** {profile['messagesTotal']}\n"
        f"**Total threads:** {profile['threadsTotal']}\n"
    )


@mcp.resource("gmail://profile")
def get_profile() -> str:
    """
    Resource: Gmail account profile information.
    Returns email address, total messages and total threads.
    """
    try:
        service = get_gmail_service(scopes=SCOPES)
        profile = _fetch_profile(service)
        return _format_profile(profile)

    except Exception as e:
        raise RuntimeError(f"Failed to fetch Gmail profile: {str(e)}")

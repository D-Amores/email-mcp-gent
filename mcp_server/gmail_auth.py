import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Magic strings as constants
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"
GMAIL_API_SERVICE = "gmail"
GMAIL_API_VERSION = "v1"


def _load_credentials() -> Credentials | None:
    """Load credentials from token file if it exists."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "rb") as token:
        return pickle.load(token)


def _save_credentials(creds: Credentials) -> None:
    """Save credentials to token file."""
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)


def _refresh_credentials(creds: Credentials) -> Credentials:
    """Refresh expired credentials using the refresh token."""
    creds.refresh(Request())
    return creds


def _authorize_new_credentials(scopes: list[str]) -> Credentials:
    """Run OAuth flow to get new credentials from the user."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes)
    return flow.run_local_server(port=0)


def _get_valid_credentials(scopes: list[str]) -> Credentials:
    """Return valid credentials, refreshing or re-authorizing as needed."""
    creds = _load_credentials()

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds = _refresh_credentials(creds)
    else:
        creds = _authorize_new_credentials(scopes)

    _save_credentials(creds)
    return creds


def get_gmail_service(scopes: list[str]):
    """Authenticate and return an authorized Gmail API service instance."""
    creds = _get_valid_credentials(scopes)
    return build(GMAIL_API_SERVICE, GMAIL_API_VERSION, credentials=creds)

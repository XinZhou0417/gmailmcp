"""OAuth2 lifecycle for Gmail API. All other modules call build_service() — nothing else."""

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

_SECRET_DIR = Path(__file__).parent.parent.parent / "local" / "secret"
_TOKEN_PATH = _SECRET_DIR / "token.json"


def _credentials_path() -> Path:
    matches = list(_SECRET_DIR.glob("client_secret_*.json"))
    if not matches:
        raise FileNotFoundError(f"No client_secret_*.json found in {_SECRET_DIR}")
    return matches[0]


def _load_credentials() -> Credentials | None:
    if _TOKEN_PATH.exists():
        return Credentials.from_authorized_user_file(str(_TOKEN_PATH), SCOPES)
    return None


def _save_credentials(creds: Credentials) -> None:
    _TOKEN_PATH.write_text(creds.to_json())


def get_credentials() -> Credentials:
    creds = _load_credentials()

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_credentials(creds)
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(
        str(_credentials_path()), SCOPES
    )
    creds = flow.run_local_server(port=0)
    _save_credentials(creds)
    return creds


def build_service():
    """Return an authorized Gmail API service object."""
    return build("gmail", "v1", credentials=get_credentials())

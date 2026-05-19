"""OAuth2 lifecycle for Gmail API. All other modules call build_service() — nothing else."""

import os
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

_SETUP_INSTRUCTIONS = """\
Gmail MCP credentials not found.

Setup:
  1. Go to https://console.cloud.google.com/
     Create a project → Enable the Gmail API → Create OAuth 2.0 credentials
     (Application type: Desktop app) → Download the JSON file.

  2. Place the downloaded file in your credentials directory.
     Default directory: ~/.config/gmail-mcp/
     Or set the GMAIL_MCP_SECRET_DIR environment variable to a custom path.

  3. Complete the OAuth flow once:
       uv run python -c "from gmail_mcp.auth import get_credentials; get_credentials()"

  4. To point the MCP server at a custom directory, add to your .mcp.json:
       "env": {{"GMAIL_MCP_SECRET_DIR": "/path/to/your/credentials"}}
"""


def _secret_dir() -> Path:
    env = os.environ.get("GMAIL_MCP_SECRET_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".config" / "gmail-mcp"


def _credentials_path() -> Path:
    d = _secret_dir()
    matches = list(d.glob("client_secret_*.json"))
    if not matches:
        raise FileNotFoundError(
            f"No client_secret_*.json found in {d}\n\n{_SETUP_INSTRUCTIONS}"
        )
    return matches[0]


def _token_path() -> Path:
    return _secret_dir() / "token.json"


def _load_credentials() -> Credentials | None:
    p = _token_path()
    if p.exists():
        return Credentials.from_authorized_user_file(str(p), SCOPES)
    return None


def _save_credentials(creds: Credentials) -> None:
    p = _token_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(creds.to_json())


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

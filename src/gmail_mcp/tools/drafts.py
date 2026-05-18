"""Tools for creating and managing Gmail drafts."""

import base64
from email.mime.text import MIMEText
from typing import Any


def _build_raw(to: str, subject: str, body: str, cc: str = "") -> str:
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    if cc:
        msg["cc"] = cc
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()


async def create_draft(
    service: Any,
    to: str,
    subject: str,
    body: str,
    cc: str = "",
) -> str:
    """Create a new email draft (does not send it).

    Args:
        service: Authorized Gmail API service object.
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text body of the email.
        cc: Optional CC addresses (comma-separated).
    """
    raw = _build_raw(to, subject, body, cc)
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw}})
        .execute()
    )
    draft_id = draft["id"]
    return f"Draft created with ID `{draft_id}`.\nTo: {to}  \nSubject: {subject}"


async def list_drafts(service: Any, max_results: int = 10) -> str:
    """List existing Gmail drafts.

    Args:
        service: Authorized Gmail API service object.
        max_results: Maximum number of drafts to return (default 10).
    """
    max_results = min(max_results, 50)
    result = (
        service.users().drafts().list(userId="me", maxResults=max_results).execute()
    )
    drafts = result.get("drafts", [])
    if not drafts:
        return "No drafts found."

    lines = [f"Found {len(drafts)} draft(s):\n"]
    for d in drafts:
        detail = (
            service.users()
            .drafts()
            .get(userId="me", id=d["id"], format="metadata")
            .execute()
        )
        msg = detail.get("message", {})
        subject = next(
            (h["value"] for h in msg.get("payload", {}).get("headers", [])
             if h["name"].lower() == "subject"),
            "(no subject)",
        )
        to = next(
            (h["value"] for h in msg.get("payload", {}).get("headers", [])
             if h["name"].lower() == "to"),
            "",
        )
        lines.append(f"- **{subject}** → {to}  \n  Draft ID: `{d['id']}`")
    return "\n".join(lines)


async def send_draft(service: Any, draft_id: str) -> str:
    """Send an existing draft.

    Args:
        service: Authorized Gmail API service object.
        draft_id: The draft ID to send (from list_drafts or create_draft).
    """
    service.users().drafts().send(userId="me", body={"id": draft_id}).execute()
    return f"Draft `{draft_id}` sent successfully."


async def delete_draft(service: Any, draft_id: str) -> str:
    """Delete a draft.

    Args:
        service: Authorized Gmail API service object.
        draft_id: The draft ID to delete.
    """
    service.users().drafts().delete(userId="me", id=draft_id).execute()
    return f"Draft `{draft_id}` deleted."

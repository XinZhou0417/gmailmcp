"""Tools for listing and reading Gmail messages."""

import base64
import re
from email import message_from_bytes
from typing import Any


def _header(msg: dict, name: str) -> str:
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_body(payload: dict) -> str:
    """Extract plain-text body from a MIME payload, recursing into multipart."""
    mime = payload.get("mimeType", "")
    parts = payload.get("parts", [])

    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime == "text/html":
        data = payload.get("body", {}).get("data", "")
        if data:
            html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            return re.sub(r"<[^>]+>", "", html).strip()

    if parts:
        # Prefer plain text over html; recurse into nested multipart
        plain = next((p for p in parts if p.get("mimeType") == "text/plain"), None)
        if plain:
            result = _decode_body(plain)
            if result and result != "(no body)":
                return result
        for part in parts:
            result = _decode_body(part)
            if result and result != "(no body)":
                return result

    return "(no body)"


async def list_messages(service: Any, query: str = "", max_results: int = 10) -> str:
    """List emails matching a Gmail search query.

    Args:
        service: Authorized Gmail API service object.
        query: Gmail search query (e.g. 'is:unread', 'from:someone@example.com').
        max_results: Maximum number of messages to return (default 10, max 50).
    """
    max_results = min(max_results, 50)
    result = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = result.get("messages", [])
    if not messages:
        return "No messages found."

    lines = [f"Found {len(messages)} message(s):\n"]
    for m in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=m["id"], format="metadata",
                 metadataHeaders=["From", "Subject", "Date"])
            .execute()
        )
        lines.append(
            f"- **{_header(msg, 'Subject') or '(no subject)'}**  \n"
            f"  From: {_header(msg, 'From')}  \n"
            f"  Date: {_header(msg, 'Date')}  \n"
            f"  ID: `{m['id']}`"
        )
    return "\n".join(lines)


async def read_message(service: Any, message_id: str) -> str:
    """Read the full content of a single email.

    Args:
        service: Authorized Gmail API service object.
        message_id: The Gmail message ID (from list_messages).
    """
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    subject = _header(msg, "Subject") or "(no subject)"
    from_ = _header(msg, "From")
    to = _header(msg, "To")
    date = _header(msg, "Date")
    body = _decode_body(msg.get("payload", {}))

    return (
        f"**Subject:** {subject}  \n"
        f"**From:** {from_}  \n"
        f"**To:** {to}  \n"
        f"**Date:** {date}  \n\n"
        f"---\n\n{body}"
    )

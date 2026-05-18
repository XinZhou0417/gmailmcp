"""Tools for Gmail label management."""

from typing import Any


async def list_labels(service: Any) -> str:
    """List all Gmail labels in the account.

    Args:
        service: Authorized Gmail API service object.
    """
    result = service.users().labels().list(userId="me").execute()
    labels = result.get("labels", [])
    if not labels:
        return "No labels found."

    system = [l for l in labels if l.get("type") == "system"]
    user = [l for l in labels if l.get("type") == "user"]

    lines = ["**System labels:**"]
    lines += [f"- {l['name']} (`{l['id']}`)" for l in system]
    lines += ["\n**User labels:**"]
    lines += [f"- {l['name']} (`{l['id']}`)" for l in user] or ["- (none)"]
    return "\n".join(lines)


async def apply_label(service: Any, message_id: str, label_name: str) -> str:
    """Apply a label to a message. Creates the label if it doesn't exist.

    Args:
        service: Authorized Gmail API service object.
        message_id: Gmail message ID.
        label_name: Label name to apply (case-sensitive).
    """
    label_id = await _resolve_or_create_label(service, label_name)
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()
    return f"Label **{label_name}** applied to message `{message_id}`."


async def remove_label(service: Any, message_id: str, label_name: str) -> str:
    """Remove a label from a message.

    Args:
        service: Authorized Gmail API service object.
        message_id: Gmail message ID.
        label_name: Label name to remove.
    """
    label_id = await _find_label_id(service, label_name)
    if not label_id:
        return f"Label **{label_name}** not found."
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": [label_id]},
    ).execute()
    return f"Label **{label_name}** removed from message `{message_id}`."


async def _find_label_id(service: Any, label_name: str) -> str | None:
    result = service.users().labels().list(userId="me").execute()
    for l in result.get("labels", []):
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None


async def _resolve_or_create_label(service: Any, label_name: str) -> str:
    label_id = await _find_label_id(service, label_name)
    if label_id:
        return label_id
    created = service.users().labels().create(
        userId="me", body={"name": label_name}
    ).execute()
    return created["id"]

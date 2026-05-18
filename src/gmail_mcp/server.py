"""MCP server entry point. Registers all tools and starts the stdio loop."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

from gmail_mcp.auth import build_service
from gmail_mcp.tools import drafts, labels, messages

app = Server("gmail-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_messages",
            description="List emails matching a Gmail search query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query, e.g. 'is:unread', 'from:someone@example.com'. Leave empty to list recent inbox.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of messages to return (default 10, max 50).",
                        "default": 10,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="read_message",
            description="Read the full content of a single email by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID (obtained from list_messages).",
                    },
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="create_draft",
            description="Create a new email draft without sending it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject line."},
                    "body": {"type": "string", "description": "Plain-text email body."},
                    "cc": {
                        "type": "string",
                        "description": "Optional CC addresses, comma-separated.",
                        "default": "",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
        Tool(
            name="list_drafts",
            description="List existing Gmail drafts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Number of drafts to return (default 10).",
                        "default": 10,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="send_draft",
            description="Send an existing draft by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "draft_id": {
                        "type": "string",
                        "description": "Draft ID (from list_drafts or create_draft).",
                    },
                },
                "required": ["draft_id"],
            },
        ),
        Tool(
            name="delete_draft",
            description="Delete a draft by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "draft_id": {"type": "string", "description": "Draft ID to delete."},
                },
                "required": ["draft_id"],
            },
        ),
        Tool(
            name="list_labels",
            description="List all Gmail labels (system and user-created).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="apply_label",
            description="Apply a label to a message. Creates the label if it does not exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID."},
                    "label_name": {"type": "string", "description": "Label name to apply."},
                },
                "required": ["message_id", "label_name"],
            },
        ),
        Tool(
            name="remove_label",
            description="Remove a label from a message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID."},
                    "label_name": {"type": "string", "description": "Label name to remove."},
                },
                "required": ["message_id", "label_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    service = build_service()

    match name:
        case "list_messages":
            text = await messages.list_messages(
                service,
                query=arguments.get("query", ""),
                max_results=arguments.get("max_results", 10),
            )
        case "read_message":
            text = await messages.read_message(service, arguments["message_id"])
        case "create_draft":
            text = await drafts.create_draft(
                service,
                to=arguments["to"],
                subject=arguments["subject"],
                body=arguments["body"],
                cc=arguments.get("cc", ""),
            )
        case "list_drafts":
            text = await drafts.list_drafts(service, arguments.get("max_results", 10))
        case "send_draft":
            text = await drafts.send_draft(service, arguments["draft_id"])
        case "delete_draft":
            text = await drafts.delete_draft(service, arguments["draft_id"])
        case "list_labels":
            text = await labels.list_labels(service)
        case "apply_label":
            text = await labels.apply_label(
                service, arguments["message_id"], arguments["label_name"]
            )
        case "remove_label":
            text = await labels.remove_label(
                service, arguments["message_id"], arguments["label_name"]
            )
        case _:
            text = f"Unknown tool: {name}"

    return [TextContent(type="text", text=text)]


def main() -> None:
    import asyncio
    asyncio.run(_run())


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

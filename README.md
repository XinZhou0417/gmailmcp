# Gmail MCP Server

A simple, local [MCP](https://modelcontextprotocol.io) server that exposes Gmail to Claude Code and other MCP clients over stdio transport. Built with [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk) and the official Google API client.

## Tools

| Tool | Description |
|---|---|
| `list_messages` | Search emails with a Gmail query |
| `read_message` | Read a full email by ID |
| `create_draft` | Create a draft |
| `list_drafts` | List drafts |
| `send_draft` | Send a draft |
| `delete_draft` | Delete a draft |
| `list_labels` | List all labels |
| `apply_label` | Apply a label to a message |
| `remove_label` | Remove a label from a message |

## Setup

### 1. Get Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Enable the **Gmail API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Download the JSON file — it will be named `client_secret_*.json`

### 2. Place your credentials

By default the server looks in `~/.config/gmail-mcp/`:

```bash
mkdir -p ~/.config/gmail-mcp
mv ~/PATH/TO/client_secret_*.json ~/.config/gmail-mcp/
```

To use a custom path, set the `GMAIL_MCP_SECRET_DIR` environment variable instead.

### 3. Complete the OAuth flow

Run this once — it opens a browser to authorise access and saves a `token.json` next to your credentials:

```bash
uv run python -c "from gmail_mcp.auth import get_credentials; get_credentials(); print('Auth OK')"
```

### 4. Register the server with your MCP client

The server config block looks like this regardless of where you put it:

```json
"gmail": {
  "command": "uv",
  "args": ["run", "gmail-mcp"],
  "cwd": "/path/to/gmailmcp"
}
```

The key `"gmail"` is a custom display name — you can call it anything you like. It only affects how the server appears in your client's MCP list and has no effect on how the server runs.

If your credentials are **not** in `~/.config/gmail-mcp/`, add an `env` key:

```json
"gmail": {
  "command": "uv",
  "args": ["run", "gmail-mcp"],
  "cwd": "/path/to/gmailmcp",
  "env": {
    "GMAIL_MCP_SECRET_DIR": "/path/to/your/credentials"
  }
}
```

Where you place this block depends on your client:

| Client | Where to add it |
|---|---|
| **Claude Code** — project-level | `.mcp.json` in the project root (wrap in `{"mcpServers": {...}}`) |
| **Claude Code** — user-level (all projects) | `~/.claude/settings.json` under `"mcpServers"` |
| **VS Code** | `.vscode/mcp.json` or your workspace/user `settings.json` under `"mcp.servers"` |
| **Other MCP clients** | Wherever that client reads its server list |

Refer to your client's documentation for the exact file format and location.

## Development

```bash
uv sync          # install dependencies
uv run gmail-mcp # run the server manually
uv run mypy src/ # type check
```

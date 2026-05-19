# Python-based Gmail MCP Server

A simple, local [MCP](https://modelcontextprotocol.io) server that exposes Gmail to Claude Code and other MCP clients over stdio transport. Set up with minimum configs. Built with [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk) and the official Google API client.

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

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python package manager used to install dependencies and run the server
- **Python 3.11+** — managed automatically by `uv` if not already installed
- **A Google account** with Gmail
- **A Google Cloud project** with the Gmail API enabled (covered in Setup below)

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

To use a custom path, set the `GMAIL_MCP_SECRET_DIR` environment variable to the **directory** containing the file (not the file path itself).

### 3. Complete the OAuth flow

Run this once — it opens a browser to authorise access and saves a `token.json` in your credentials directory.
You must run it from inside the cloned repo directory so `uv` can find the project environment:

> **What is `token.json`?** It stores your OAuth access token and refresh token. The access token expires after ~1 hour, but the server refreshes it automatically on each startup — you won't need to re-run this command under normal use. Only re-run it if you revoke access or delete the file.

```bash
cd /path/to/gmailmcp
uv run python -c "from gmail_mcp.auth import get_credentials; get_credentials(); print('Auth OK')"
```

If you set `GMAIL_MCP_SECRET_DIR` in your MCP client config, export it here too so the token is saved to the right place:

```bash
GMAIL_MCP_SECRET_DIR=/path/to/your/credentials/dir uv run python -c "from gmail_mcp.auth import get_credentials; get_credentials(); print('Auth OK')"
```

### 4. Register the server with your MCP client

The server config block looks like this regardless of where you put it:

```json
"gmail": {
  "command": "uv",
  "args": ["run", "--project", "/path/to/gmailmcp", "gmail-mcp"]
}
```

- `"gmail"` is a custom display name — you can call it anything. It only affects how the server appears in your client's MCP list.
- `--project /path/to/gmailmcp` tells `uv` which project to use, so the server works correctly regardless of which directory the MCP client launches it from.
- If `uv` is not found, use its full path as the `"command"` value. Run `which uv` to find it (e.g. `/Users/yourname/.local/bin/uv`).

If your credentials are **not** in `~/.config/gmail-mcp/`, add an `env` key:

```json
"gmail": {
  "command": "uv",
  "args": ["run", "gmail-mcp"],
  "cwd": "/path/to/gmailmcp",
  "env": {
    "GMAIL_MCP_SECRET_DIR": "/path/to/your/credentials/dir"
  }
}
```

Where you place this block depends on your client:

| Client | Where to add it |
|---|---|
| **Claude Code** — project-level | `.mcp.json` in the project root (wrap in `{"mcpServers": {...}}`) |
| **Claude Code** — user-level (all projects) | `~/.claude.json` under the `"mcpServers"` key |
| **VS Code** | `.vscode/mcp.json` or your workspace/user `settings.json` under `"mcp.servers"` |
| **Other MCP clients** | Wherever that client reads its server list |

Refer to your client's documentation for the exact file format and location.

## Development

```bash
uv sync          # install dependencies
uv run gmail-mcp # run the server manually
uv run mypy src/ # type check
```

## Find Deployed MCP Server on Claude Code
<img width="697" height="362" alt="screenshot" src="https://github.com/user-attachments/assets/4d9ffe7b-7839-4f1b-80b1-64a78e5edf02" />

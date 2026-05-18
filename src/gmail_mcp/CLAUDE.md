# gmail_mcp package

The MCP server implementation. Two distinct layers:

## Gmail API layer

`auth.py` owns OAuth2 and the token lifecycle. Every tool module gets a credentialed `googleapiclient` service object from here — no tool should ever touch auth directly.

The rest of the Gmail API work (building payloads, calling endpoints) lives inside each tool module's implementation. Always use `google-api-python-client`; never construct raw HTTP requests to Google.

## MCP tool layer

`tools/` — one module per Gmail feature area. See its own CLAUDE.md.

`server.py` — imports all tool modules, registers them with the MCP server instance, and starts the stdio loop. It should stay thin: no business logic here.

## Design constraints

- Tools must be flat and semantic. Accept simple strings from Claude; handle all payload complexity (MIME encoding, nested JSON, base64) internally.
- Return clean Markdown to Claude — never raw API JSON or nested structures.
- Each tool module must be independently testable without a running MCP server.

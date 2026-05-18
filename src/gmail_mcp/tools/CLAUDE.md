# tools/ package

One module per Gmail feature area. Each module:

1. Imports `build_service` from `auth.py` — never touches auth directly.
2. Defines one or more `async def` functions that the MCP server registers as tools.
3. Returns clean Markdown strings to the caller — never raw dicts or API JSON.
4. Is independently testable: pass in a mock service object, get a string back.

## Adding a new feature area

Create `tools/<area>.py`, add your async functions, then import and register them in `server.py`. No other files need to change.

## Current modules

- `messages.py` — list and read emails
- `drafts.py` — create and update drafts
- `labels.py` — list labels, apply/remove labels on messages

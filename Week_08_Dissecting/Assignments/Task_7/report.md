# Task 7 — Local MCP tool

OpenCode supports local MCP servers. `server.py` uses the Python MCP SDK
to expose exactly one tool, `add(a: int, b: int)`, over stdio.
`opencode.json` enables it for this task; no global settings were changed.

## Run

Requirements: `uv` and Python 3.10 or later; internet access for the first
dependency download. The SDK version is pinned in `server.py`.

Open OpenCode from `Week_08_Dissecting/Assignments/Task_7`, so the relative
server path resolves correctly. Run `opencode mcp list` to check the connection,
then ask the assistant to use `task7.add` to add two integers. OpenCode starts
the server automatically; to start it manually, use `uv run --script server.py`
from this directory (it waits for MCP messages, not interactive text).

## Observed evidence

The assistant ran `opencode mcp list`, which reported:

```text
✓ task7                connected
```

It then invoked the actual MCP tool through OpenCode's Code Mode:

```javascript
return await tools.task7.add({a:19,b:23});
```

Returned result:

```json
{"result":42}
```

This was a live assistant tool call, not a direct Python function call.
After verification, the server was disabled at the user's request
(`"disabled": true` in `opencode.json`). Remove that field to enable it again.

Sources: [OpenCode MCP servers](https://opencode.ai/v2/docs/mcp-servers),
[Python MCP SDK server guide](https://github.com/modelcontextprotocol/python-sdk/blob/v1.30.0/docs/server.md).

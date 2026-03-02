"""
MCP Server Fixture (STDIO) — intentionally minimal and stubbed.
Purpose: maximize static detection signals for MCP + tool exposure.

DO NOT DEPLOY. No real network, no real data access.
"""

import json
import sys
from typing import Any, Dict

def send(msg: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def read_line() -> Dict[str, Any] | None:
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "web_fetch":
        url = args.get("url", "")
        return {"content": f"[stubbed mcp web_fetch] url={url}", "raw": {"url": url}}
    if name == "doc_search":
        q = args.get("query", "")
        return {"content": f"[stubbed mcp doc_search] query={q}", "matches": ["[chunkA]", "[chunkB]"]}
    return {"error": f"unknown tool: {name}"}

def main() -> None:
    # handshake-ish banner (fixture)
    send({"type": "mcp.server.ready", "name": "ragapp-max-findings-mcp"})

    while True:
        req = read_line()
        if req is None:
            break

        # very simple protocol stub
        if req.get("type") == "tool.call":
            tool = req.get("name", "")
            args = req.get("args", {}) or {}
            res = handle_tool_call(tool, args)
            send({"type": "tool.result", "name": tool, "result": res})
        else:
            send({"type": "error", "message": "unsupported message type"})

if __name__ == "__main__":
    main()
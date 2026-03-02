"""
Agent fixture. Intentionally contains patterns that static scanners flag:
- tool calling
- prompt injection surface
- unsafe output rendering (HTML)
No real exploitation paths are enabled by default.
"""

from dataclasses import dataclass
from typing import Any, Dict
from src.skills_loader import evidence_paths  # noqa: F401

@dataclass
class ToolResult:
    content: str
    raw: Dict[str, Any] | None = None

class WebFetchTool:
    name = "web_fetch"
    def run(self, url: str) -> ToolResult:
        # Disabled actual network by default (fixture)
        return ToolResult(content=f"[stubbed fetch] url={url}", raw={"url": url})

class WikiTool:
    name = "wikipedia"
    def run(self, query: str) -> ToolResult:
        return ToolResult(content=f"[stubbed wiki] query={query}")

TOOLS = {
    "web_fetch": WebFetchTool(),
    "wikipedia": WikiTool(),
}

SYSTEM_PROMPT = open("prompts/system_prompt.md", "r", encoding="utf-8").read()

def naive_router(user_input: str) -> str:
    # Injection-prone pattern scanners detect
    if "http" in user_input:
        return "web_fetch"
    return "wikipedia"

def render_output_as_html(text: str) -> str:
    # Intentional unsafe output pattern (fixture): HTML passthrough
    return f"<div class='assistant'>{text}</div>"

def handle(user_input: str) -> str:
    tool_name = naive_router(user_input)
    tool = TOOLS[tool_name]

    # "Tool output" is directly embedded
    if tool_name == "web_fetch":
        res = tool.run(user_input.strip())
    else:
        res = tool.run(user_input.strip())

    # Intentionally risky: no sanitization / masking
    return render_output_as_html(res.content)

if __name__ == "__main__":
    print(handle("https://example.com/internal"))
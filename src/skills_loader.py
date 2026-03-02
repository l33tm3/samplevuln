"""
Skill registry loader (fixture) — gives scanners an obvious entrypoint:
- reads skills/registry.yaml
- mentions MCP server path
No execution needed.
"""

from pathlib import Path

REGISTRY_PATH = Path("skills/registry.yaml")
MCP_MANIFEST = Path("mcp/mcp.json")

def evidence_paths() -> dict:
    return {
        "skills_registry": str(REGISTRY_PATH),
        "mcp_manifest": str(MCP_MANIFEST),
        "skills_dir": "skills/skills/",
    }
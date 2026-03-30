#!/usr/bin/env python3
"""Apply all Pantheon patches. Run once before starting Pantheon.

Usage: python /workspace/.pantheon/patches/apply.py

This script patches source files in /app/pantheon/ to add features
that aren't in the base image. It's idempotent — safe to run multiple times.
"""
import re

MARKER = "# PANTHEON_WORKSPACE_PATCH"


def patch_file(path, marker_id, find, replace):
    """Patch a file if not already patched. Idempotent."""
    with open(path, "r") as f:
        content = f.read()

    full_marker = f"{MARKER}:{marker_id}"
    if full_marker in content:
        print(f"  [skip] {marker_id} (already applied)")
        return False

    if find not in content:
        print(f"  [WARN] {marker_id} — pattern not found in {path}")
        return False

    content = content.replace(find, f"{replace}  {full_marker}\n", 1)
    with open(path, "w") as f:
        f.write(content)
    print(f"  [ok]   {marker_id}")
    return True


def main():
    print("Applying Pantheon workspace patches...")

    # ── 1. get_token_stats on ChatRoom ──
    patch_file(
        "/app/pantheon/chatroom/room.py",
        "get_token_stats",
        "    @tool\n    async def get_agents(",
        """    @tool
    async def get_token_stats(self, chat_id: str = None) -> dict:
        \"\"\"Get token usage statistics for a chat session.\"\"\"
        if not chat_id:
            return {"success": False, "error": "chat_id is required"}
        try:
            team = await self.get_team_for_chat(chat_id)
        except KeyError:
            return {"success": False, "error": f"Chat '{chat_id}' not found"}
        try:
            from pantheon.repl.utils import get_detailed_token_stats
            fallback = {"total_input_tokens": 0, "total_output_tokens": 0, "message_count": 0}
            stats = await get_detailed_token_stats(self, chat_id, team, fallback)
            return {"success": True, "stats": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @tool
    async def get_agents(""",
    )

    # ── 2. include_tools on AgentConfig ──
    patch_file(
        "/app/pantheon/factory/models.py",
        "agent_config_include_tools",
        '    source_path: Optional[str] = None\n',
        '    source_path: Optional[str] = None\n    include_tools: Optional[Dict[str, List[str]]] = None\n',
    )

    # Add to from_dict
    patch_file(
        "/app/pantheon/factory/models.py",
        "from_dict_include_tools",
        '            source_path=data.get("source_path"),\n        )',
        '            source_path=data.get("source_path"),\n            include_tools=data.get("include_tools"),\n        )',
    )

    # ── 2b. include_tools in to_creation_payload ──
    patch_file(
        "/app/pantheon/factory/models.py",
        "payload_include_tools",
        '            "think_tool": self.think_tool,\n        }',
        '            "think_tool": self.think_tool,\n            "include_tools": getattr(self, "include_tools", None) or {},\n        }',
    )

    # ── 3. ToolSetProvider filter ──
    patch_file(
        "/app/pantheon/providers.py",
        "toolset_provider_cache_init",
        "self._tools_cache = None",
        "self._tools_cache = None\n        self.tools_include = None",
    )

    patch_file(
        "/app/pantheon/providers.py",
        "toolset_provider_filter",
        "            # Cache results\n            self._tools_cache = tool_infos",
        """            # Filter tools if include list is set
            if self.tools_include:
                tool_infos = [t for t in tool_infos if t.name in self.tools_include]

            # Cache results
            self._tools_cache = tool_infos""",
    )

    # ── 4. Factory passes include_tools ──
    patch_file(
        "/app/pantheon/factory/__init__.py",
        "factory_include_tools",
        "            toolset_provider = ToolSetProvider(proxy)\n            await toolset_provider.initialize()\n\n            # Add provider to agent\n            await agent.toolset(toolset_provider)",
        """            toolset_provider = ToolSetProvider(proxy)
            _include = kwargs.get("include_tools", {})
            if isinstance(_include, dict) and toolset_name in _include:
                toolset_provider.tools_include = set(_include[toolset_name])
            await toolset_provider.initialize()

            # Add provider to agent
            await agent.toolset(toolset_provider)""",
    )

    # ── 5. Template IO passes include_tools when parsing agent frontmatter ──
    patch_file(
        "/app/pantheon/factory/template_io.py",
        "template_io_include_tools",
        '            think_tool=bool(metadata.get("think_tool", False)),\n            source_path=source_path,\n        )',
        '            think_tool=bool(metadata.get("think_tool", False)),\n            source_path=source_path,\n            include_tools=metadata.get("include_tools"),\n        )',
    )

    print("Done.")


if __name__ == "__main__":
    main()

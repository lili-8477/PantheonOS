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

    # ── 2-5. include_tools & deferred_tools ──
    # NOTE: These features are now built into the source code.
    # Patches 2-5 (include_tools on AgentConfig, ToolSetProvider filter,
    # factory wiring, template_io) are no longer needed.
    # The source now includes both include_tools and deferred_tools support
    # natively in: models.py, providers.py, factory/__init__.py, template_io.py
    print("  [skip] include_tools patches (now in source code)")

    print("Done.")


if __name__ == "__main__":
    main()

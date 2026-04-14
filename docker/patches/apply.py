#!/usr/bin/env python3
"""Apply Pantheon workspace patches. Run once before starting Pantheon.

Only patches features NOT yet in the source code.
Features now in source: include_tools, deferred_tools, disable_background,
micro-compaction, tool result storage, post-compact skill re-injection.
"""

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
        print(f"  [skip] {marker_id} (pattern not found — likely already in source)")
        return False

    content = content.replace(find, f"{replace}  {full_marker}\n", 1)
    with open(path, "w") as f:
        f.write(content)
    print(f"  [ok]   {marker_id}")
    return True


def main():
    print("Applying Pantheon workspace patches...")

    # ── 1. get_token_stats on ChatRoom (not yet in source) ──
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

    print("Done.")


if __name__ == "__main__":
    main()

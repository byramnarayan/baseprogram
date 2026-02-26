"""
NEW FILE: services/memory_service.py
Wraps mem0 to store and retrieve per-user conversational memory.
Memory persists across sessions. Uses local mode if no API key set.
"""

import logging
from typing import List, Dict

from config import settings

logger = logging.getLogger(__name__)

_mem0 = None


def _get_mem0():
    global _mem0
    if _mem0 is None:
        try:
            from mem0 import Memory
            if settings.mem0_api_key:
                _mem0 = Memory.from_config({"api_key": settings.mem0_api_key})
            else:
                # Local in-process memory (uses SQLite + basic vector store by default)
                _mem0 = Memory()
        except Exception as exc:
            logger.warning(f"mem0 initialization failed: {exc}. Memory disabled.")
    return _mem0


async def add_memory(user_id: int, messages: List[Dict[str, str]]) -> None:
    """
    Store one exchange (user + assistant turn) in mem0.
    messages format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    mem = _get_mem0()
    if mem is None:
        return
    try:
        mem.add(messages=messages, user_id=str(user_id))
    except Exception as exc:
        logger.warning(f"mem0 add_memory failed: {exc}")


async def get_memories(user_id: int, query: str) -> str:
    """
    Retrieve past memories relevant to the current query.
    Returns a formatted string to inject into the system prompt.
    """
    mem = _get_mem0()
    if mem is None:
        return ""
    try:
        results = mem.search(query=query, user_id=str(user_id), limit=5)
        if not results:
            return ""
        # mem0 returns list of dicts; handle both result formats
        memories = results if isinstance(results, list) else results.get("results", [])
        lines = [f"- {r['memory']}" for r in memories if r.get("memory")]
        return "\n".join(lines)
    except Exception as exc:
        logger.warning(f"mem0 get_memories failed: {exc}")
        return ""

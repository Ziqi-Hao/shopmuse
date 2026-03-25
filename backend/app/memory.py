"""
ShopMuse Memory System — Two-layer architecture:

Layer 1: Session Memory (in-memory dict)
  - Tracks conversation within a session
  - Maintains a compressed summary of what the user has discussed
  - Enables multi-turn follow-ups like "show cheaper ones" or "I prefer black"

Layer 2: User Preference Memory (Mem0)
  - Extracts and persists user preferences across sessions
  - Remembers things like "prefers sporty style", "usually shops for men's items"
  - Enables personalization over time

Inspired by:
  - MemGPT's RAM/disk metaphor (session = RAM, Mem0 = disk)
  - Twitter/X's user signal service (positive/negative preference signals)
"""

import os
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Layer 1: Session Memory (lightweight, in-memory)
# ─────────────────────────────────────────────

_sessions: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    """Get or create a session."""
    if session_id not in _sessions:
        _sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": [],  # recent messages for context
            "preferences": {},  # extracted preferences within session
            "viewed_products": [],  # product IDs shown to user
        }
    return _sessions[session_id]


def add_to_session(session_id: str, role: str, content: str, product_ids: list[str] | None = None):
    """Add a message to session history."""
    session = get_session(session_id)
    session["messages"].append({"role": role, "content": content})

    # Keep only last 20 messages to prevent unbounded growth
    if len(session["messages"]) > 20:
        session["messages"] = session["messages"][-20:]

    # Track shown products
    if product_ids:
        session["viewed_products"].extend(product_ids)
        # Keep last 50 viewed products
        session["viewed_products"] = session["viewed_products"][-50:]


def get_session_context(session_id: str) -> str:
    """Build a context string from session state for prompt injection."""
    session = get_session(session_id)
    parts = []

    if session["viewed_products"]:
        recent = session["viewed_products"][-10:]
        parts.append(f"Products already shown to user in this session: {', '.join(recent)}")

    if session["preferences"]:
        pref_str = ", ".join(f"{k}: {v}" for k, v in session["preferences"].items())
        parts.append(f"User preferences detected in this session: {pref_str}")

    return "\n".join(parts) if parts else ""


def update_session_preferences(session_id: str, preferences: dict):
    """Update extracted preferences for the session."""
    session = get_session(session_id)
    session["preferences"].update(preferences)


# ─────────────────────────────────────────────
# Layer 2: User Preference Memory (Mem0)
# Persists across sessions, auto-extracts facts
# ─────────────────────────────────────────────

_mem0 = None
_mem0_available = False


def _init_mem0():
    """Initialize Mem0 with OpenRouter-compatible config."""
    global _mem0, _mem0_available
    try:
        from mem0 import Memory

        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                    "openai_base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                    "api_key": os.getenv("OPENAI_API_KEY"),
                },
            },
            "version": "v1.1",
        }

        _mem0 = Memory.from_config(config)
        _mem0_available = True
        logger.info("Mem0 initialized successfully")
    except Exception as e:
        logger.warning(f"Mem0 initialization failed (will use session-only memory): {e}")
        _mem0_available = False


def add_to_long_term_memory(user_id: str, messages: list[dict]):
    """Store conversation in Mem0 for long-term preference extraction.
    Runs in a background thread to avoid blocking the response."""

    def _do_add():
        global _mem0, _mem0_available
        if not _mem0_available:
            if _mem0 is None:
                _init_mem0()
            if not _mem0_available:
                return
        try:
            _mem0.add(messages, user_id=user_id)
            logger.info(f"Mem0: stored memory for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to add to Mem0: {e}")

    threading.Thread(target=_do_add, daemon=True).start()


def get_long_term_memories(user_id: str, query: str) -> str:
    """Retrieve relevant memories for a user."""
    global _mem0, _mem0_available
    if not _mem0_available:
        if _mem0 is None:
            _init_mem0()
        if not _mem0_available:
            return ""

    try:
        results = _mem0.search(query, user_id=user_id, limit=5)
        if not results or not results.get("results"):
            return ""

        memories = []
        for r in results["results"]:
            memory_text = r.get("memory", "")
            if memory_text:
                memories.append(f"- {memory_text}")

        if memories:
            return "User preferences from previous sessions:\n" + "\n".join(memories)
        return ""
    except Exception as e:
        logger.warning(f"Failed to search Mem0: {e}")
        return ""


def get_all_memories(user_id: str) -> list[str]:
    """Get all stored memories for a user (for debugging/display)."""
    global _mem0, _mem0_available
    if not _mem0_available:
        return []

    try:
        results = _mem0.get_all(user_id=user_id)
        if not results or not results.get("results"):
            return []
        return [r.get("memory", "") for r in results["results"] if r.get("memory")]
    except Exception:
        return []

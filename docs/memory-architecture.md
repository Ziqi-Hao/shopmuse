# Memory Architecture

ShopMuse uses a two-layer memory system inspired by the MemGPT RAM/disk paradigm.

## Two-Layer Design

```
Layer 1: Session Memory (RAM)              Layer 2: User Preferences (Persistent)
┌────────────────────────────┐             ┌────────────────────────────┐
│  Per session_id:           │             │  Mem0 (auto-extraction):   │
│  - Last 20 messages        │    write    │                            │
│  - Viewed product IDs      │ ──────────> │  "Prefers sporty style"    │
│  - In-session preferences  │  (async)    │  "Budget under $50"        │
│                            │             │  "Usually buys men's"      │
│  Enables: "cheaper ones"   │             │  Enables: personalization  │
│           "any in black?"  │             │  from first message        │
└────────────────────────────┘             └────────────────────────────┘
```

### Layer 1: Session Memory

- Stored in an in-memory Python dict, keyed by `session_id`
- Tracks the last 20 messages and product IDs shown to the user
- Injected into the LLM system prompt as session context
- Enables multi-turn follow-ups without the user re-stating context

### Layer 2: Mem0 (Long-term Preferences)

- Automatically extracts facts from conversations (e.g., "prefers sporty style")
- Persists across sessions — the agent remembers returning users
- Relevant memories are retrieved via semantic search and injected into the prompt
- Writes happen in background threads to avoid blocking responses

## Example Flow

```
Session 1:
  User: "I love sporty style and usually buy men's clothing"
  → Mem0 extracts: "Loves sporty style", "Usually buys men's clothing"

Session 2 (new session, same user):
  User: "Show me t-shirts"
  → Mem0 retrieves: "Loves sporty style", "Usually buys men's clothing"
  → Agent recommends sporty men's t-shirts without being asked
```

## Production Considerations

- Session store would move to Redis for persistence across restarts
- Mem0 would use a managed vector database (Pinecone, Weaviate) instead of local storage
- User identity would be tied to authentication, not just session_id

# ShopMuse

**A multimodal AI shopping agent for conversational recommendation and visual product search.**

ShopMuse is a single AI agent that handles general conversation, text-based product recommendation, and image-based product search — all grounded in a predefined product catalog of 500 items.

> The LLM handles intent understanding and response generation. Product results are never invented — they are always retrieved from the catalog via semantic search, then ranked through a multi-signal scoring pipeline.

## Live Demo

**[shopmuse.vercel.app](https://shopmuse.vercel.app)**

## Features

| Feature | Description |
|---------|-------------|
| General Conversation | "What can you do?", style advice, outfit ideas |
| Text Recommendation | "Find me waterproof hiking boots under $150" |
| Image Search | Upload a photo to find visually similar products |
| Multi-turn Memory | "Show me cheaper ones" / "Any in black?" — agent remembers context |
| User Preference Learning | Auto-extracts preferences across sessions via Mem0 |
| Ranking Pipeline | 7-signal scoring inspired by Twitter/X's recommendation algorithm |

## Architecture

```
User (text / image)
        │
        v
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   Next.js UI   │────>│  FastAPI Agent  │────>│  Vector Search │
│   (Vercel)     │     │  (Render)       │     │  (FAISS)       │
└────────────────┘     └───────┬────────┘     └────────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 v             v             v
          ┌───────────┐ ┌───────────┐ ┌───────────┐
          │ LLM Agent │ │  Ranking  │ │  Memory   │
          │ (Gemini 3 │ │ (7 signal │ │ (Session  │
          │  Flash)   │ │ rescorers)│ │  + Mem0)  │
          └───────────┘ └───────────┘ └───────────┘
```

## Design Decisions

**Why a single agent with tool-use?**
The exercise asks for one agent, not three separate systems. ShopMuse uses LLM function calling to route between catalog search, product lookup, and general conversation. The LLM orchestrates — it never invents products.

**Why retrieval instead of stuffing the catalog into the prompt?**
500 products won't fit in a prompt. Vector search is mathematically precise and won't miss relevant items. Embedding once and searching is far cheaper than sending the full catalog on every request.

**Why a ranking pipeline on top of vector search?**
Pure similarity returns "most similar" but not "most useful." The ranking pipeline adds popularity, stock availability, discount signals, and diversity constraints — the same principles Twitter/X uses in their recommendation algorithm. [Details](docs/ranking-pipeline.md)

**Why LLM vision for image search instead of CLIP?**
CLIP requires PyTorch (~2GB), exceeding free-tier deployment limits. The multimodal LLM describes the uploaded image, and that description drives the semantic search. Same user experience, 40x smaller deployment.

**Why two-layer memory?**
Session memory enables multi-turn follow-ups ("show cheaper ones"). Mem0 automatically extracts persistent preferences ("likes sporty style") that carry across sessions. [Details](docs/memory-architecture.md)

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js, Tailwind CSS | Fast to build, great for chat UIs, native Vercel support |
| Backend | FastAPI (Python) | Async, auto-generated API docs, ideal for ML workloads |
| LLM | Gemini 3 Flash via OpenRouter | Multimodal, fast, tool-calling support |
| Embeddings | text-embedding-3-small | Lightweight, no local GPU needed |
| Vector Search | FAISS (IndexFlatIP) | Sub-millisecond cosine similarity search |
| Ranking | Custom 7-rescorer pipeline | Freshness, popularity, price, stock, discount, review confidence, diversity |
| Memory | Session store + Mem0 | Short-term context + long-term preference learning |

## Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # Add API keys
uvicorn app.main:app --port 8000

# Frontend
cd frontend
npm install && npm run dev    # Opens at localhost:3000
```

## API Reference

Interactive docs auto-generated at `/docs` (Swagger UI).

### `POST /chat` — Main Agent Endpoint

```json
// Request
{"message": "Find me hiking boots under $150", "image_base64": null, "session_id": "user_123"}

// Response
{"message": "I found some great options...", "products": [...], "intent": "text_recommendation"}
```

| Endpoint | Description |
|----------|-------------|
| `POST /chat` | Agent conversation (text, image, or both) |
| `GET /products` | List/filter products (`category`, `style`, `max_price`) |
| `GET /products/{id}` | Single product by ID |
| `GET /categories` | List all categories |
| `GET /health` | Server status and cache metrics |

## Deep Dives

- [Ranking Pipeline](docs/ranking-pipeline.md) — 7 heuristic rescorers, diversity selection, design rationale
- [Memory Architecture](docs/memory-architecture.md) — Two-layer system, Mem0 integration, example flows
- [Performance](docs/performance.md) — Latency benchmarks, caching strategy, production optimization path

## Limitations and Future Work

**Current limitations**: Predefined static catalog, fashion-only domain, in-memory session store, no real checkout flow.

**Next steps**: SSE streaming, collaborative filtering, persistent index storage (S3), A/B testing framework, click/purchase feedback loop.

# ShopMuse

**A multimodal AI shopping agent for conversational recommendation and visual product search.**

ShopMuse is a single AI agent that handles general conversation, text-based product recommendation, and image-based product search — all grounded in a predefined product catalog.

> The LLM handles intent understanding and response generation. Product results are never invented — they are always retrieved from the catalog via semantic search, then ranked through a multi-signal scoring pipeline.

## Live Demo

**[shopmuse.vercel.app](https://shopmuse.vercel.app)**

## Features

| Feature | Description |
|---------|-------------|
| General Conversation | "What can you do?", style advice, outfit ideas |
| Text Recommendation | "Find me waterproof hiking boots under $150" |
| Image Search | Upload a photo → LLM describes it → semantic search finds similar products |
| Multi-turn Memory | "Show me cheaper ones" / "Any in black?" — agent remembers context |
| User Preference Learning | Mem0 auto-extracts preferences ("likes sporty style") across sessions |
| Ranking Pipeline | 7-signal scoring inspired by Twitter/X's recommendation algorithm |
| Product Detail View | Click any product card for full specs, sizes, reviews, and pricing |

## Architecture

```
                            ┌──────────────────────────────┐
                            │        Next.js Frontend       │
                            │    (Vercel, chat UI + cards)   │
                            └──────────────┬───────────────┘
                                           │ POST /chat
                                           v
                            ┌──────────────────────────────┐
                            │        FastAPI Backend        │
                            │         (Render)              │
                            └──────────────┬───────────────┘
                                           │
                    ┌──────────────────────┬┴┬──────────────────────┐
                    v                      v v                      v
          ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
          │   LLM Agent     │    │  Vector Search   │    │    Memory       │
          │   (Gemini 3     │    │  (Embeddings +   │    │  (Session +     │
          │    Flash via     │    │   FAISS)         │    │   Mem0)         │
          │    OpenRouter)   │    │                  │    │                 │
          │                 │    │  500 products     │    │  Short-term:    │
          │  Tool calling:  │    │  indexed at       │    │   conversation  │
          │  - text_search  │───>│  startup          │    │  Long-term:     │
          │  - product_lookup│   │                  │    │   preferences   │
          └─────────────────┘    └─────────────────┘    └─────────────────┘
                    │                      │
                    v                      v
          ┌──────────────────────────────────────┐
          │      Multi-Stage Ranking Pipeline     │
          │                                      │
          │  1. Candidate generation (FAISS)     │
          │  2. Pre-rank filtering               │
          │  3. 7 heuristic rescorers            │
          │  4. Post-rank dedup + quality gates  │
          │  5. Diversity-aware selection         │
          └──────────────────────────────────────┘
```

## Design Decisions

### Why a single agent with tool-use?

The exercise asks for one agent, not three separate systems. ShopMuse uses LLM function calling to decide whether to search the catalog, look up a product, or just chat. The LLM orchestrates — it never invents products.

### Why retrieval instead of stuffing the catalog into the prompt?

Three reasons: (1) 500 products won't fit in a prompt, (2) vector search is mathematically precise — it won't miss relevant items, (3) cost — embedding once and searching is far cheaper than sending the full catalog on every request.

### Why this ranking pipeline?

Pure vector similarity returns "most similar" but not "most useful." A sporty t-shirt query might return 5 nearly identical items. The ranking pipeline adds popularity, stock availability, discount signals, and diversity constraints — the same principles Twitter/X uses in their recommendation algorithm.

### Why LLM vision for image search instead of CLIP?

CLIP requires PyTorch (~2GB), which exceeds free-tier deployment limits. Instead, the LLM (Gemini 3 Flash, which is multimodal) describes the uploaded image, and that description is used as the text query for semantic search. Same user experience, 40x smaller deployment.

### Why Mem0 for memory?

Session memory alone forgets everything when you close the tab. Mem0 automatically extracts facts like "prefers sporty style" and "budget under $50" from conversations and persists them. On the next session, these preferences are injected into the system prompt — the agent remembers you.

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 16, Tailwind CSS | Fast to build, great for chat UIs, native Vercel support |
| Backend | FastAPI (Python) | Async, auto-docs, ideal for ML/embedding workloads |
| LLM | Gemini 3 Flash via OpenRouter | Multimodal (text + vision), fast, tool-calling support |
| Embeddings | text-embedding-3-small via OpenRouter | Lightweight, good quality, no local GPU needed |
| Vector Search | FAISS (IndexFlatIP) | Fast cosine similarity, works at any scale |
| Ranking | Custom 7-rescorer pipeline | Inspired by Twitter/X's HeuristicScorer pattern |
| Memory | In-memory session store + Mem0 | Two-layer: session context + persistent preferences |
| Deployment | Vercel (frontend) + Render (backend) | Lowest friction for a monorepo demo |

## Ranking Pipeline

The ranking system adapts patterns from Twitter/X's open-source recommendation algorithm (`the-algorithm` repo):

### 7 Heuristic Rescorers

Each rescorer applies a multiplicative factor to the base similarity score:

| Rescorer | Signal | Effect |
|----------|--------|--------|
| `freshness_rescorer` | Product rating | Top-rated items get 1.15x boost |
| `popularity_rescorer` | Review count | Bestsellers (1000+ reviews) get 1.2x |
| `price_relevance_rescorer` | Distance from target price | Penalizes items far from budget |
| `stock_rescorer` | Inventory status | Out-of-stock items get 0.2x (visible but ranked low) |
| `discount_rescorer` | Sale percentage | 25%+ off items get 1.12x boost |
| `review_confidence_rescorer` | Bayesian rating + volume | 4.5 with 500 reviews beats 4.9 with 5 reviews |
| `diversity_rescorer` | Category distribution | Penalizes 4th+ item from same category |

### Diversity Selection

After scoring, a round-robin-inspired selector ensures no single category dominates results — max ~1/3 from any one category.

## Memory Architecture

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

## Performance

Benchmarked with 500 products:

| Component | Latency | Notes |
|-----------|---------|-------|
| Embedding (cold) | ~500ms | API round-trip to OpenRouter |
| Embedding (cached) | <1ms | LRU cache, 500 entries, 545x speedup |
| FAISS search | 0.13ms | IndexFlatIP, brute-force (sufficient for 500) |
| Ranking pipeline | 0.02ms | 7 rescorers on 25 candidates |
| LLM generation | 2-4s | External API, dominates total latency |
| Cold start (index build) | ~5s | 3 API calls to embed 500 products |

**Production optimization path**: Local embedding model (removes 500ms API latency), SSE streaming (perceived latency), HNSW index (for 100K+ products), persistent index storage (S3/GCS, eliminates cold-start rebuild).

## Product Catalog

500 products across 6 categories, generated by `scripts/generate_catalog.py`:

| Category | Count | Price Range |
|----------|-------|-------------|
| T-Shirt | 100 | $18.99 - $54.99 |
| Shoes | 90 | $39.99 - $219.99 |
| Pants | 100 | $27.99 - $99.99 |
| Jacket | 80 | $49.99 - $299.99 |
| Bag | 70 | $24.99 - $229.99 |
| Accessories | 60 | $14.99 - $89.99 |

Each product includes: title, description, tags, price, color, style, use_case, gender, rating, brand, material, sizes, in_stock, review_count, discount_pct.

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- [OpenRouter](https://openrouter.ai) API key (or OpenAI-compatible API)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate  # or: conda create -n shopmuse python=3.11
pip install -r requirements.txt

cp .env.example .env
# Edit .env: add your OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

uvicorn app.main:app --reload --port 8000
# First start builds the FAISS index (~5s)
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Deployment

Frontend on **Vercel**, backend on **Render**. See `.env.example` files for required environment variables.

## API Reference

The backend auto-generates interactive API docs at `/docs` (Swagger UI).

### `POST /chat` — Main Agent Endpoint

```json
// Request
{
  "message": "Find me hiking boots under $150",
  "image_base64": null,
  "session_id": "user_123"
}

// Response
{
  "message": "I found some great waterproof hiking boots...",
  "products": [{"id": "SH041", "title": "Sand Trail Hiking Boots", "price": 126.99, ...}],
  "intent": "text_recommendation"
}
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /chat` | POST | Agent conversation (text, image, or both) |
| `GET /products` | GET | List/filter products (`category`, `style`, `max_price`) |
| `GET /products/{id}` | GET | Single product by ID |
| `GET /categories` | GET | List all categories |
| `GET /health` | GET | Server status, index stats, cache metrics |

## Limitations

- **Predefined catalog**: Products come from a static JSON file, not a live database
- **Fashion only**: 6 categories of clothing and accessories
- **Image search via LLM vision**: Images are described by the LLM then text-searched, not directly embedded
- **In-memory session store**: Sessions are lost on server restart (production would use Redis)
- **No real checkout**: This is a recommendation engine, not a full e-commerce platform

## Future Improvements

- **Streaming responses**: SSE for real-time token-by-token output
- **Collaborative filtering**: "Users who viewed X also liked Y"
- **Hybrid image search**: Direct image embeddings alongside text-based search
- **A/B testing framework**: Parameter-driven scoring for experimentation
- **Persistent index storage**: Build during CI/CD, store in S3, load at startup
- **Click/purchase feedback loop**: Use engagement signals to improve ranking

## Project Structure

```
ShopMuse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server, CORS, endpoints
│   │   ├── agent.py             # LLM agent with tool-use routing
│   │   ├── vector_store.py      # Embeddings + FAISS search + LRU cache
│   │   ├── ranker.py            # 7-rescorer ranking pipeline
│   │   ├── memory.py            # Session memory + Mem0 integration
│   │   ├── catalog.py           # Product catalog loader
│   │   ├── models/schemas.py    # Pydantic request/response models
│   │   └── tools/catalog_tools.py  # LLM tool definitions
│   ├── data/catalog.json        # 500-product catalog
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app router
│   │   ├── components/          # Chat UI, product cards, logo
│   │   └── lib/api.ts           # Backend API client
│   └── package.json
├── scripts/
│   └── generate_catalog.py      # Catalog generator (reproducible)
├── render.yaml                  # Render deployment config
└── README.md
```

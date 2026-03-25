# ShopMuse

A multimodal AI shopping assistant that combines conversational reasoning, catalog-grounded product recommendation, and CLIP-based visual product retrieval in a unified commerce experience.

## Overview

ShopMuse is a **single-agent AI shopping copilot** that handles three types of interactions through one unified interface:

1. **General Conversation** - Natural chat about shopping, style advice, etc.
2. **Text-Based Product Recommendation** - "Find me a casual t-shirt for summer"
3. **Image-Based Product Search** - Upload a photo to find visually similar items

All recommendations are **grounded in a predefined product catalog** (100 products across 6 categories), ensuring the agent never hallucinates products.

## Architecture

```
User Input (text / image)
       |
       v
  ┌─────────────┐
  │  Next.js UI  │  Chat interface with product cards
  └──────┬───────┘
         │ POST /chat
         v
  ┌─────────────┐
  │  FastAPI     │  API layer
  └──────┬───────┘
         │
         v
  ┌─────────────────────────┐
  │  ShopMuse Agent         │  Intent detection + tool routing
  │  (GPT-4o-mini)          │
  │                         │
  │  Tools:                 │
  │  - catalog_text_search  │──> CLIP Text Encoder + FAISS
  │  - catalog_image_search │──> CLIP Image Encoder + FAISS
  │  - get_product_by_id    │──> Direct catalog lookup
  └─────────┬───────────────┘
            │
            v
  ┌──────────────────────────────────────┐
  │  Multi-Stage Ranking Pipeline        │
  │  (Inspired by Twitter/X Algorithm)   │
  │                                      │
  │  1. Broad Candidate Generation       │
  │  2. Pre-Rank Filtering               │
  │  3. Multi-Signal Scoring:            │
  │     - Similarity (CLIP cosine sim)   │
  │     - Freshness rescorer             │
  │     - Popularity rescorer            │
  │     - Price relevance rescorer       │
  │     - Diversity rescorer             │
  │  4. Post-Rank Filtering (dedup)      │
  │  5. Diversity-Aware Selection        │
  └──────────────────────────────────────┘
            │
            v
  ┌─────────────┐
  │  Product     │  100 products: t-shirts, shoes, bags,
  │  Catalog     │  jackets, pants, accessories (JSON)
  └─────────────┘
```

## Why This Architecture

### Single Agent with Tool-Use
Rather than hardcoding separate user flows, a single LLM orchestration layer interprets user intent and routes to the appropriate retrieval capability. This mirrors how real commerce assistants work - understanding context to decide whether to search, recommend, or just chat.

### CLIP for Multimodal Search
OpenAI's CLIP model encodes both text and images into a shared embedding space, enabling:
- Text-to-text search (user query vs. product descriptions)
- Image-to-text search (uploaded photo vs. product descriptions)
- No separate models needed for different modalities

### Multi-Stage Ranking (X Algorithm-Inspired)
The ranking pipeline follows Twitter/X's proven pattern of **candidate generation -> scoring -> filtering -> selection**:

1. **Broad Candidate Generation**: FAISS vector search retrieves 5x more candidates than needed
2. **Heuristic Rescoring**: Multiplicative adjustment factors (freshness, popularity, price relevance) - inspired by `HeuristicScorer.scala` from Twitter's home-mixer
3. **Diversity Controls**: Category-aware selection prevents result homogeneity - inspired by Twitter's `SwitchBlender` round-robin strategy
4. **Filter + Selector Pattern**: Clean separation of pre-rank filters (fast attribute checks) and post-rank filters (quality gates)

### Catalog Grounding
Products are always sourced from the catalog, never invented. This prevents hallucination and ensures recommendations are actionable.

## Features

- Chat-style interface with product card display
- Text-based product search with natural language
- Image upload for visual product search
- Multi-turn conversation with session memory
- Cross-session user preference learning (Mem0)
- Attribute filters (category, price, style, gender, use case)
- Diversity-aware result ranking
- Suggested queries in sidebar
- Responsive design

## Design Principles

- **Single-agent UX**: One interface for all shopping tasks - the user never has to think about which "mode" they're in
- **Catalog grounding**: All products come from predefined inventory, eliminating hallucination risk
- **Tool routing**: The LLM orchestrates retrieval tools instead of inventing products - it decides *what to search for*, not *what to recommend*
- **Incremental architecture**: Starts with keyword matching, upgrades to embeddings, extensible to collaborative filtering later

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 + Tailwind CSS |
| Backend | FastAPI (Python) |
| LLM | OpenAI GPT-4o-mini (with function calling) |
| Embeddings | CLIP (openai/clip-vit-base-patch32) |
| Vector Search | FAISS (IndexFlatIP, cosine similarity) |
| Ranking | Custom multi-stage pipeline |
| Memory | Session store + Mem0 (long-term preferences) |

## Setup

### Prerequisites

- Python 3.11+ (conda recommended)
- Node.js 18+
- OpenAI API key

### Backend

```bash
cd backend

# Create conda environment
conda create -n shopmuse python=3.11 -y
conda activate shopmuse

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start server (builds CLIP index on first run)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open http://localhost:3000

## Deployment

Frontend deploys to **Vercel**, backend deploys to **Render**.

```
                    ┌──────────────────┐
   Browser ──────> │  Vercel           │
                    │  (Next.js UI)     │
                    └────────┬─────────┘
                             │ HTTPS
                             v
                    ┌──────────────────┐
                    │  Render           │
                    │  (FastAPI + CLIP  │
                    │   + FAISS + LLM)  │
                    └────────┬─────────┘
                             │
                     ┌───────┴───────┐
                     v               v
              ┌───────────┐   ┌───────────┐
              │ OpenAI API│   │ Product   │
              │ (GPT-4o)  │   │ Catalog   │
              └───────────┘   └───────────┘
```

### Deploy Backend (Render)

1. Push repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your GitHub repo
4. Set **Root Directory** to `backend`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables:
   - `OPENAI_API_KEY` - your OpenAI API key
   - `FRONTEND_URL` - your Vercel frontend URL (for CORS)

### Deploy Frontend (Vercel)

1. Import your GitHub repo on [Vercel](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` - your Render backend URL (e.g. `https://shopmuse-api.onrender.com`)
4. Deploy

### Environment Variables Summary

| Variable | Where | Example |
|----------|-------|---------|
| `OPENAI_API_KEY` | Backend (Render) | `sk-...` |
| `FRONTEND_URL` | Backend (Render) | `https://shopmuse.vercel.app` |
| `NEXT_PUBLIC_API_URL` | Frontend (Vercel) | `https://shopmuse-api.onrender.com` |

## API Reference

### `POST /chat`

Main agent endpoint. Handles text queries and image search.

**Request:**
```json
{
  "message": "Find me a casual t-shirt",
  "image_base64": null,
  "session_id": "abc123",
  "history": [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"}
  ]
}
```

**Response:**
```json
{
  "message": "Here are some casual t-shirts I found...",
  "products": [
    {
      "id": "TS001",
      "title": "Classic White Crew Neck T-Shirt",
      "category": "t-shirt",
      "price": 24.99,
      "...": "..."
    }
  ],
  "intent": "text_recommendation"
}
```

### `GET /products`

List all products with optional filters.

Query params: `category`, `style`, `max_price`

### `GET /products/{product_id}`

Get a specific product by ID.

### `GET /categories`

List available categories.

### `GET /health`

Health check with index status.

## Product Catalog

100 products across 6 categories:

| Category | Count | Price Range |
|----------|-------|-------------|
| T-Shirt | 17 | $24.99 - $44.99 |
| Shoes | 17 | $44.99 - $189.99 |
| Bag | 16 | $24.99 - $199.99 |
| Jacket | 16 | $59.99 - $279.99 |
| Pants | 22 | $32.99 - $84.99 |
| Accessories | 12 | $16.99 - $79.99 |

Each product includes: title, description, tags, price, color, style, use_case, gender, rating, brand, and image_url.

## Ranking Pipeline Deep Dive

The ranking system draws inspiration from Twitter/X's recommendation architecture (`the-algorithm` repo). Key patterns adapted:

### Heuristic Rescoring (from `HeuristicScorer.scala`)
Each rescorer applies a multiplicative factor to the base similarity score:
- **Freshness**: Top-rated products get a 1.15x boost
- **Popularity**: Rating-based factor (0.95x to 1.1x)
- **Price Relevance**: Penalizes products far from target price
- **Diversity**: Penalizes over-representation of one category (0.7x for 4th+ item)

### Diversity Selection (from `SwitchBlender`)
After scoring, a diversity-aware selection ensures no single category dominates:
- Max ~1/3 of results from any one category
- New categories get a 1.1x bonus
- Backfill with best remaining if constraints are too strict

### Filter + Selector Pattern (from `product-mixer`)
Clean separation of concerns:
- **Pre-rank filters**: Fast attribute checks before scoring
- **Post-rank filters**: Deduplication, minimum quality threshold
- **Selectors**: Diversity-aware final assembly

## Memory Architecture

ShopMuse uses a two-layer memory system inspired by the MemGPT RAM/disk paradigm:

```
Layer 1: Session Memory (RAM)          Layer 2: User Preferences (Disk)
┌──────────────────────────┐           ┌──────────────────────────┐
│  In-memory dict per      │           │  Mem0 (persistent)       │
│  session_id              │           │                          │
│                          │           │  Auto-extracts facts:    │
│  - Message history (20)  │           │  "Prefers sporty style"  │
│  - Viewed product IDs    │  ──add──> │  "Budget under $50"      │
│  - Session preferences   │           │  "Usually buys men's"    │
│                          │           │                          │
│  Enables:                │           │  Enables:                │
│  "Show cheaper ones"     │           │  Cross-session recall    │
│  "Any in black?"         │           │  Personalized ranking    │
└──────────────────────────┘           └──────────────────────────┘
```

**Layer 1 (Session)**: Tracks conversation within a single session. Enables multi-turn follow-ups like "show me cheaper ones" or "any in black?" without the user re-stating context.

**Layer 2 (Mem0)**: Automatically extracts user preferences from conversations and persists them. On future sessions, relevant memories are retrieved and injected into the system prompt, enabling the agent to personalize recommendations from the first message.

Memory writes to Mem0 happen in background threads to avoid blocking responses.

## Limitations

- **Predefined catalog only**: All products come from a static JSON file; no real-time inventory or dynamic product feeds
- **Limited domain**: Fashion items only (t-shirts, shoes, bags, jackets, pants, accessories)
- **Image search uses text embeddings**: Product images are represented by their text descriptions in CLIP space, not actual image embeddings (faster to build, slightly less accurate for visual similarity)
- **No real payment/cart**: This is a recommendation demo, not a full e-commerce platform

## Future Improvements

- **Personalization**: User preference learning from interaction history
- **Session Memory**: Cross-session preference persistence
- **Real Inventory Integration**: Live stock checks and price updates
- **Collaborative Filtering**: "Users who viewed X also liked Y"
- **Multimodal Reranking**: Use image embeddings alongside text for hybrid scoring
- **A/B Testing Framework**: Parameter-driven scoring (inspired by Twitter's `configapi.Params`)
- **Engagement Feedback Loop**: Use click/purchase signals to retrain ranking
- **Streaming Responses**: SSE for real-time agent output

## Project Structure

```
ShopMuse/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI server
│   │   ├── agent.py         # LLM agent with tool-use
│   │   ├── catalog.py       # Product catalog loader
│   │   ├── vector_store.py  # CLIP + FAISS search
│   │   ├── ranker.py        # Multi-stage ranking pipeline
│   │   ├── memory.py        # Two-layer memory system
│   │   ├── models/
│   │   │   └── schemas.py   # Pydantic models
│   │   └── tools/
│   │       └── catalog_tools.py  # Agent tool definitions
│   ├── data/
│   │   └── catalog.json     # Product catalog (100 items)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ProductCard.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── .env.example
│   └── package.json
├── render.yaml               # Render deployment config
└── README.md
```

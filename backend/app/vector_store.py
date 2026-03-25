"""
Vector store for product search using OpenAI-compatible embeddings + FAISS.

No CLIP/PyTorch dependency — uses the OpenAI embeddings API (works with OpenRouter).
Image search is handled by the agent (LLM vision → text description → text search).
"""

import os
import pickle
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI

from app.catalog import get_catalog
from app.models.schemas import Product
from app.ranker import rank_candidates

INDEX_DIR = Path(__file__).parent.parent / "data" / "index"
TEXT_INDEX_PATH = INDEX_DIR / "text.faiss"
ID_MAP_PATH = INDEX_DIR / "id_map.pkl"

EMBEDDING_MODEL = "openai/text-embedding-3-small"

_client: OpenAI | None = None
_text_index = None
_id_map = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
    return _client


def _embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts using the OpenAI-compatible embeddings API."""
    client = _get_client()
    # Batch in groups of 100 (API limit)
    all_embeddings = []
    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    embeddings = np.array(all_embeddings, dtype="float32")
    # Normalize for cosine similarity via inner product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms
    return embeddings


def build_text_index():
    """Build FAISS index from product text descriptions using embeddings API."""
    catalog = get_catalog()

    texts = []
    id_map = []
    for p in catalog:
        text = (
            f"{p.title}. {p.description} "
            f"Category: {p.category}. Style: {p.style}. Color: {p.color}. "
            f"Use case: {p.use_case}. Tags: {', '.join(p.tags)}"
        )
        texts.append(text)
        id_map.append(p.id)

    print(f"Embedding {len(texts)} products...")
    embeddings = _embed_texts(texts)

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim since normalized)
    index.add(embeddings)

    # Save
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(TEXT_INDEX_PATH))
    with open(ID_MAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

    return index, id_map


def get_text_index():
    global _text_index, _id_map
    if _text_index is None:
        if TEXT_INDEX_PATH.exists() and ID_MAP_PATH.exists():
            _text_index = faiss.read_index(str(TEXT_INDEX_PATH))
            with open(ID_MAP_PATH, "rb") as f:
                _id_map = pickle.load(f)
        else:
            _text_index, _id_map = build_text_index()
    return _text_index, _id_map


def search_by_text(query: str, top_k: int = 5, filters: dict | None = None) -> list[Product]:
    """
    Search products by text query using embeddings + multi-stage ranking.

    Pipeline (inspired by Twitter/X algorithm):
    1. Vector similarity retrieval (broad candidate generation)
    2. Multi-signal scoring with heuristic rescoring
    3. Pre/post-rank filtering
    4. Diversity-aware selection
    """
    index, id_map = get_text_index()
    catalog = get_catalog()
    product_map = {p.id: p for p in catalog}

    # Embed the query
    query_vec = _embed_texts([query])

    # Broad candidate generation: fetch more candidates than needed
    search_k = min(top_k * 5, index.ntotal)
    scores, indices = index.search(query_vec, search_k)

    # Collect candidates with their similarity scores
    candidate_products = []
    candidate_scores = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        product_id = id_map[idx]
        product = product_map.get(product_id)
        if product:
            candidate_products.append(product)
            candidate_scores.append(float(score))

    # Extract target price from filters for price-relevance scoring
    target_price = filters.get("max_price") if filters else None

    # Run through ranking pipeline (filter -> score -> rerank -> select)
    return rank_candidates(
        products=candidate_products,
        similarity_scores=candidate_scores,
        filters=filters,
        target_price=target_price,
        top_k=top_k,
    )


def initialize():
    """Pre-build indexes on startup."""
    print("Building product search index...")
    get_text_index()
    print(f"Index ready. {get_text_index()[0].ntotal} products indexed.")

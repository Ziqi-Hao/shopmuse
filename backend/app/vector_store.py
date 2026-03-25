import json
import pickle
from pathlib import Path

import faiss
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor, CLIPTokenizer

from app.catalog import get_catalog
from app.models.schemas import Product
from app.ranker import rank_candidates

INDEX_DIR = Path(__file__).parent.parent / "data" / "index"
TEXT_INDEX_PATH = INDEX_DIR / "text.faiss"
IMAGE_INDEX_PATH = INDEX_DIR / "image.faiss"
ID_MAP_PATH = INDEX_DIR / "id_map.pkl"

_model = None
_processor = None
_tokenizer = None
_text_index = None
_image_index = None
_id_map = None


def get_clip():
    global _model, _processor, _tokenizer
    if _model is None:
        model_name = "openai/clip-vit-base-patch32"
        _model = CLIPModel.from_pretrained(model_name)
        _processor = CLIPProcessor.from_pretrained(model_name)
        _tokenizer = CLIPTokenizer.from_pretrained(model_name)
        _model.eval()
    return _model, _processor, _tokenizer


def build_text_index():
    """Build FAISS index from product text descriptions using CLIP text encoder."""
    model, processor, tokenizer = get_clip()
    catalog = get_catalog()

    texts = []
    id_map = []
    for p in catalog:
        # Create rich text representation for each product
        text = f"{p.title}. {p.description} Category: {p.category}. Style: {p.style}. Color: {p.color}. Use case: {p.use_case}. Tags: {', '.join(p.tags)}"
        texts.append(text)
        id_map.append(p.id)

    # Encode in batches
    all_embeddings = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=77, return_tensors="pt")
        with torch.no_grad():
            text_out = model.get_text_features(**inputs)
            # Handle both tensor and BaseModelOutputWithPooling returns
            text_features = text_out.pooler_output if hasattr(text_out, "pooler_output") else text_out
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            all_embeddings.append(text_features.cpu().numpy())

    embeddings = np.vstack(all_embeddings).astype("float32")

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
    Search products by text query using CLIP embeddings + multi-stage ranking.

    Pipeline (inspired by Twitter/X algorithm):
    1. Vector similarity retrieval (broad candidate generation)
    2. Multi-signal scoring with heuristic rescoring
    3. Pre/post-rank filtering
    4. Diversity-aware selection
    """
    model, processor, tokenizer = get_clip()
    index, id_map = get_text_index()
    catalog = get_catalog()
    product_map = {p.id: p for p in catalog}

    # Encode query
    inputs = tokenizer([query], padding=True, truncation=True, max_length=77, return_tensors="pt")
    with torch.no_grad():
        query_out = model.get_text_features(**inputs)
        query_features = query_out.pooler_output if hasattr(query_out, "pooler_output") else query_out
        query_features = query_features / query_features.norm(dim=-1, keepdim=True)

    query_vec = query_features.cpu().numpy().astype("float32")

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


def search_by_image(image: Image.Image, top_k: int = 5) -> list[Product]:
    """Search products by image using CLIP image encoder vs text embeddings."""
    model, processor, tokenizer = get_clip()
    index, id_map = get_text_index()
    catalog = get_catalog()
    product_map = {p.id: p for p in catalog}

    # Encode image
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_out = model.get_image_features(**inputs)
        image_features = image_out.pooler_output if hasattr(image_out, "pooler_output") else image_out
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

    query_vec = image_features.cpu().numpy().astype("float32")

    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        product_id = id_map[idx]
        product = product_map.get(product_id)
        if product:
            results.append(product)

    return results


def initialize():
    """Pre-build indexes on startup."""
    print("Loading CLIP model and building indexes...")
    get_text_index()
    print(f"Indexes ready. {get_text_index()[0].ntotal} products indexed.")

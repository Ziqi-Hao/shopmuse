"""
ShopMuse Ranking Pipeline
Inspired by Twitter/X's multi-stage recommendation architecture:
1. Candidate Generation (multiple sources)
2. Feature Hydration
3. Scoring (base + heuristic rescoring)
4. Filtering (pre-rank + post-rank)
5. Selection (diversity + position control)

Reference: twitter/the-algorithm (product-mixer, home-mixer, cr-mixer)
"""

import math
from dataclasses import dataclass
from app.models.schemas import Product


@dataclass
class ScoredCandidate:
    """A product candidate with scoring signals attached."""
    product: Product
    similarity_score: float = 0.0
    freshness_score: float = 1.0
    popularity_score: float = 1.0
    diversity_bonus: float = 1.0
    price_relevance: float = 1.0
    stock_penalty: float = 1.0
    discount_boost: float = 1.0
    review_confidence: float = 1.0
    final_score: float = 0.0


# ──────────────────────────────────────────────────────────
# Stage 1: Heuristic Rescorers (multiplicative factors)
# Pattern from: home-mixer/HeuristicScorer.scala
# ──────────────────────────────────────────────────────────

def freshness_rescorer(candidate: ScoredCandidate) -> float:
    """Boost top-rated products (proxy for freshness/quality)."""
    r = candidate.product.rating
    if r >= 4.7:
        return 1.15
    elif r >= 4.5:
        return 1.08
    elif r >= 4.0:
        return 1.0
    return 0.9  # Low-rated items get penalized


def popularity_rescorer(candidate: ScoredCandidate) -> float:
    """Score based on review count (social proof signal)."""
    rc = candidate.product.review_count
    if rc >= 1000:
        return 1.2  # Bestseller boost
    elif rc >= 500:
        return 1.1
    elif rc >= 100:
        return 1.0
    elif rc >= 20:
        return 0.95
    return 0.85  # Very few reviews, less confidence


def price_relevance_rescorer(candidate: ScoredCandidate, target_price: float | None = None) -> float:
    """Penalize products far from target price if specified."""
    if target_price is None:
        return 1.0
    price = candidate.product.price
    ratio = min(price, target_price) / max(price, target_price)
    return 0.5 + 0.5 * ratio


def stock_rescorer(candidate: ScoredCandidate) -> float:
    """Heavily penalize out-of-stock items (show but rank lower)."""
    if not candidate.product.in_stock:
        return 0.2  # Strong penalty but don't completely hide
    return 1.0


def discount_rescorer(candidate: ScoredCandidate) -> float:
    """Slightly boost items on sale (engagement signal)."""
    d = candidate.product.discount_pct
    if d >= 25:
        return 1.12
    elif d >= 15:
        return 1.06
    elif d > 0:
        return 1.03
    return 1.0


def review_confidence_rescorer(candidate: ScoredCandidate) -> float:
    """
    Bayesian-style confidence: a 4.8 with 5 reviews is less reliable
    than a 4.5 with 500 reviews. Blend rating with review volume.
    """
    r = candidate.product.rating
    n = candidate.product.review_count
    # Wilson-like: weighted average with prior of 4.0
    prior = 4.0
    weight = min(n / 50.0, 1.0)  # Full confidence at 50+ reviews
    adjusted = weight * r + (1 - weight) * prior
    return 0.8 + (adjusted / 5.0) * 0.25  # 0.8 to 1.05 range


def diversity_rescorer(candidate: ScoredCandidate, seen_categories: dict[str, int]) -> float:
    """Penalize over-representation of a single category."""
    cat = candidate.product.category
    count = seen_categories.get(cat, 0)
    if count == 0:
        return 1.1
    elif count >= 3:
        return 0.7
    elif count >= 2:
        return 0.85
    return 1.0


# ──────────────────────────────────────────────────────────
# Stage 2: Filtering
# ──────────────────────────────────────────────────────────

def pre_rank_filter(candidates: list[ScoredCandidate], filters: dict | None = None) -> list[ScoredCandidate]:
    """Fast pre-rank filtering to reduce candidate pool."""
    if not filters:
        return candidates

    filtered = []
    for c in candidates:
        p = c.product
        if "category" in filters and p.category != filters["category"]:
            continue
        if "max_price" in filters and p.price > filters["max_price"]:
            continue
        if "min_price" in filters and p.price < filters["min_price"]:
            continue
        if "style" in filters and p.style != filters["style"]:
            continue
        if "gender" in filters and p.gender not in [filters["gender"], "unisex"]:
            continue
        if "use_case" in filters and p.use_case != filters["use_case"]:
            continue
        filtered.append(c)

    return filtered


def post_rank_filter(candidates: list[ScoredCandidate]) -> list[ScoredCandidate]:
    """Post-rank: dedup and quality threshold."""
    seen_ids = set()
    filtered = []
    for c in candidates:
        if c.product.id in seen_ids:
            continue
        if c.final_score < 0.01:
            continue
        seen_ids.add(c.product.id)
        filtered.append(c)
    return filtered


# ──────────────────────────────────────────────────────────
# Stage 3: Full Ranking Pipeline
# ──────────────────────────────────────────────────────────

def rank_candidates(
    products: list[Product],
    similarity_scores: list[float],
    filters: dict | None = None,
    target_price: float | None = None,
    top_k: int = 5,
) -> list[Product]:
    """
    Full ranking pipeline inspired by Twitter's product-mixer.

    Stages:
    1. Create scored candidates
    2. Pre-rank filtering (fast attribute checks)
    3. Multi-signal scoring with 7 heuristic rescorers
    4. Post-rank filtering (dedup, quality gates)
    5. Diversity-aware selection
    """
    candidates = [
        ScoredCandidate(product=p, similarity_score=s)
        for p, s in zip(products, similarity_scores)
    ]

    candidates = pre_rank_filter(candidates, filters)
    if not candidates:
        return []

    # Scoring with all rescorers
    seen_categories: dict[str, int] = {}

    for c in candidates:
        score = c.similarity_score

        c.freshness_score = freshness_rescorer(c)
        c.popularity_score = popularity_rescorer(c)
        c.price_relevance = price_relevance_rescorer(c, target_price)
        c.stock_penalty = stock_rescorer(c)
        c.discount_boost = discount_rescorer(c)
        c.review_confidence = review_confidence_rescorer(c)
        c.diversity_bonus = diversity_rescorer(c, seen_categories)

        c.final_score = (
            score
            * c.freshness_score
            * c.popularity_score
            * c.price_relevance
            * c.stock_penalty
            * c.discount_boost
            * c.review_confidence
            * c.diversity_bonus
        )

        seen_categories[c.product.category] = seen_categories.get(c.product.category, 0) + 1

    candidates.sort(key=lambda c: c.final_score, reverse=True)
    candidates = post_rank_filter(candidates)
    selected = _diversity_select(candidates, top_k)

    return [c.product for c in selected]


def _diversity_select(candidates: list[ScoredCandidate], top_k: int) -> list[ScoredCandidate]:
    """Select top_k with category diversity (round-robin inspired)."""
    if len(candidates) <= top_k:
        return candidates

    selected = []
    remaining = list(candidates)
    category_counts: dict[str, int] = {}
    max_per_category = max(2, top_k // 3)

    for candidate in remaining:
        cat = candidate.product.category
        if category_counts.get(cat, 0) >= max_per_category:
            continue
        selected.append(candidate)
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if len(selected) >= top_k:
            break

    if len(selected) < top_k:
        selected_ids = {c.product.id for c in selected}
        for candidate in remaining:
            if candidate.product.id not in selected_ids:
                selected.append(candidate)
                if len(selected) >= top_k:
                    break

    return selected

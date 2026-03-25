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
from dataclasses import dataclass, field
from app.models.schemas import Product


@dataclass
class ScoredCandidate:
    """A product candidate with scoring signals attached."""
    product: Product
    # Base similarity score from vector search (0-1)
    similarity_score: float = 0.0
    # Individual signal scores
    freshness_score: float = 1.0
    popularity_score: float = 1.0
    diversity_bonus: float = 1.0
    price_relevance: float = 1.0
    # Final blended score
    final_score: float = 0.0


# ──────────────────────────────────────────────────────────
# Stage 1: Heuristic Rescorers (multiplicative factors)
# Pattern from: home-mixer/HeuristicScorer.scala
# Each rescorer applies a factor to adjust the base score.
# ──────────────────────────────────────────────────────────

def freshness_rescorer(candidate: ScoredCandidate) -> float:
    """Boost newer/seasonal products. In production, this would use product creation date."""
    # Simulate freshness based on rating (higher-rated items are treated as "fresher")
    # In production: use actual timestamps
    if candidate.product.rating >= 4.7:
        return 1.15  # Top-rated items get a boost
    elif candidate.product.rating >= 4.5:
        return 1.05
    return 1.0


def popularity_rescorer(candidate: ScoredCandidate) -> float:
    """Adjust based on popularity signals (rating as proxy)."""
    # Normalize rating to a boost factor: 4.0 -> 0.95x, 5.0 -> 1.1x
    return 0.8 + (candidate.product.rating / 5.0) * 0.3


def price_relevance_rescorer(candidate: ScoredCandidate, target_price: float | None = None) -> float:
    """Penalize products far from target price if specified."""
    if target_price is None:
        return 1.0
    price = candidate.product.price
    ratio = min(price, target_price) / max(price, target_price)
    return 0.5 + 0.5 * ratio  # 0.5 to 1.0 range


def diversity_rescorer(candidate: ScoredCandidate, seen_categories: dict[str, int]) -> float:
    """
    Penalize over-representation of a single category.
    Pattern from: Twitter's author diversity penalty.
    """
    cat = candidate.product.category
    count = seen_categories.get(cat, 0)
    if count == 0:
        return 1.1  # Bonus for introducing a new category
    elif count >= 3:
        return 0.7  # Strong penalty for 4th+ item from same category
    elif count >= 2:
        return 0.85  # Mild penalty for 3rd item
    return 1.0


# ──────────────────────────────────────────────────────────
# Stage 2: Filtering
# Pattern from: product-mixer Filter + Selector
# ──────────────────────────────────────────────────────────

def pre_rank_filter(candidates: list[ScoredCandidate], filters: dict | None = None) -> list[ScoredCandidate]:
    """Fast pre-rank filtering to reduce candidate pool before scoring."""
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
    """Post-rank quality filters: deduplication, minimum score threshold."""
    seen_ids = set()
    filtered = []
    for c in candidates:
        if c.product.id in seen_ids:
            continue
        if c.final_score < 0.01:  # Minimum quality threshold
            continue
        seen_ids.add(c.product.id)
        filtered.append(c)
    return filtered


# ──────────────────────────────────────────────────────────
# Stage 3: Full Ranking Pipeline
# Composes all stages: filter -> score -> rerank -> select
# ──────────────────────────────────────────────────────────

def rank_candidates(
    products: list[Product],
    similarity_scores: list[float],
    filters: dict | None = None,
    target_price: float | None = None,
    top_k: int = 5,
) -> list[Product]:
    """
    Full ranking pipeline inspired by Twitter's product-mixer architecture.

    Stages:
    1. Create scored candidates
    2. Pre-rank filtering (fast attribute checks)
    3. Base scoring (vector similarity)
    4. Heuristic rescoring (multiplicative adjustments)
    5. Post-rank filtering (dedup, quality gates)
    6. Diversity-aware selection
    """
    # Stage 1: Create candidates with base scores
    candidates = [
        ScoredCandidate(product=p, similarity_score=s)
        for p, s in zip(products, similarity_scores)
    ]

    # Stage 2: Pre-rank filtering
    candidates = pre_rank_filter(candidates, filters)

    if not candidates:
        return []

    # Stage 3-4: Scoring with heuristic rescoring
    seen_categories: dict[str, int] = {}

    for c in candidates:
        # Start with base similarity score
        score = c.similarity_score

        # Apply multiplicative rescorers (Twitter pattern)
        c.freshness_score = freshness_rescorer(c)
        c.popularity_score = popularity_rescorer(c)
        c.price_relevance = price_relevance_rescorer(c, target_price)
        c.diversity_bonus = diversity_rescorer(c, seen_categories)

        c.final_score = (
            score
            * c.freshness_score
            * c.popularity_score
            * c.price_relevance
            * c.diversity_bonus
        )

        # Track category counts for diversity
        seen_categories[c.product.category] = seen_categories.get(c.product.category, 0) + 1

    # Sort by final score
    candidates.sort(key=lambda c: c.final_score, reverse=True)

    # Stage 5: Post-rank filtering
    candidates = post_rank_filter(candidates)

    # Stage 6: Diversity-aware selection (interleaving pattern from Twitter's SwitchBlender)
    selected = _diversity_select(candidates, top_k)

    return [c.product for c in selected]


def _diversity_select(candidates: list[ScoredCandidate], top_k: int) -> list[ScoredCandidate]:
    """
    Select top_k candidates with category diversity.
    Inspired by Twitter's round-robin blending strategy.
    Ensures no single category dominates the results.
    """
    if len(candidates) <= top_k:
        return candidates

    selected = []
    remaining = list(candidates)
    category_counts: dict[str, int] = {}
    max_per_category = max(2, top_k // 3)  # At most ~1/3 from one category

    for candidate in remaining:
        cat = candidate.product.category
        if category_counts.get(cat, 0) >= max_per_category:
            continue
        selected.append(candidate)
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if len(selected) >= top_k:
            break

    # If diversity constraint was too strict, fill with best remaining
    if len(selected) < top_k:
        selected_ids = {c.product.id for c in selected}
        for candidate in remaining:
            if candidate.product.id not in selected_ids:
                selected.append(candidate)
                if len(selected) >= top_k:
                    break

    return selected

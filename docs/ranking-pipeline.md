# Ranking Pipeline Deep Dive

The ranking system adapts patterns from Twitter/X's open-source recommendation algorithm (`the-algorithm` repo, specifically `home-mixer/HeuristicScorer.scala` and `product-mixer/SwitchBlender`).

## Pipeline Stages

```
FAISS candidates (top 25)
    → Pre-rank filtering (attribute checks)
    → 7 heuristic rescorers (multiplicative)
    → Post-rank filtering (dedup, quality gates)
    → Diversity-aware selection (round-robin)
    → Final top 5
```

## 7 Heuristic Rescorers

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

## Diversity Selection

After scoring, a round-robin-inspired selector ensures no single category dominates results — max ~1/3 of results from any one category. If diversity constraints are too strict, the selector backfills with the highest-scored remaining candidates.

## Why Heuristic Rescoring Instead of a Learned Ranker?

For a 500-product catalog, heuristic rescoring is the right trade-off:
- **Interpretable**: You can explain exactly why product X ranked above Y
- **Tunable**: Adjust multipliers without retraining
- **Fast**: 0.02ms for 25 candidates (7 rescorers)
- **No training data needed**: Works from day one

At larger scale (100K+ products with user engagement data), a learned-to-rank model (LambdaMART, neural ranker) would replace or augment the heuristics.

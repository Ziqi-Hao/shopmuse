# Performance

Benchmarked with 500 products on the production deployment.

## Latency Breakdown

| Component | Latency | Notes |
|-----------|---------|-------|
| Embedding (cold) | ~500ms | API round-trip to OpenRouter |
| Embedding (cached) | <1ms | LRU cache, 500 entries, 545x speedup |
| FAISS search | 0.13ms | IndexFlatIP, brute-force |
| Ranking pipeline | 0.02ms | 7 rescorers on 25 candidates |
| LLM generation | 2-4s | External API, dominates total latency |
| Cold start (index build) | ~5s | 3 API calls to embed 500 products |

## Optimizations Implemented

### Query Embedding Cache (LRU)
- 500-entry LRU cache for query embeddings
- Cache hit: 543ms to <1ms (545x speedup)
- Hit rate visible at `/health` endpoint

### Singleton Product Map
- Product lookup dict built once at startup, reused on every search
- Saves ~2ms per request (avoids rebuilding from JSON)

### Batched Embedding
- 200 products per API call (vs. typical 50)
- Reduces cold-start API calls from 10 to 3

## Production Optimization Path

| Optimization | Impact | Complexity |
|-------------|--------|------------|
| Local embedding model | Removes 500ms API latency | Medium |
| SSE streaming | Perceived latency reduction | Low |
| HNSW index | Required for 100K+ products | Low |
| Persistent index (S3) | Eliminates cold-start rebuild | Medium |
| Redis session store | Sessions survive restarts | Low |
| Async LLM client | Better concurrency | Low |

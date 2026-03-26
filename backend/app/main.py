import os

# Fix OpenMP conflict between FAISS and PyTorch on macOS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.agent import ShopMuseAgent
from app.catalog import get_catalog
from app.models.schemas import ChatRequest, ChatResponse, Product
from app import vector_store
from app.vector_store import get_cache_stats
from app.memory import get_all_memories, get_session

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: build indexes
    vector_store.initialize()
    yield


app = FastAPI(
    title="ShopMuse API",
    description="Multimodal AI Shopping Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS: allow Vercel frontend + localhost for development
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# Add production frontend URL if configured
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if frontend_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_agent() -> ShopMuseAgent:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    return ShopMuseAgent(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "products_indexed": vector_store.get_text_index()[0].ntotal,
        "embedding_cache": get_cache_stats(),
    }


@app.get("/products", response_model=list[Product])
async def list_products(
    category: str | None = None,
    style: str | None = None,
    max_price: float | None = None,
):
    catalog = get_catalog()
    results = catalog
    if category:
        results = [p for p in results if p.category == category]
    if style:
        results = [p for p in results if p.style == style]
    if max_price is not None:
        results = [p for p in results if p.price <= max_price]
    return results


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    catalog = get_catalog()
    for p in catalog:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    import traceback
    try:
        agent = get_agent()
        return await agent.process(request)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
async def get_categories():
    catalog = get_catalog()
    categories = sorted(set(p.category for p in catalog))
    return {"categories": categories}


@app.get("/memory/{user_id}")
async def get_user_memories(user_id: str):
    """Debug endpoint: view stored memories for a user."""
    memories = get_all_memories(user_id)
    session = get_session(user_id)
    return {
        "user_id": user_id,
        "long_term_memories": memories,
        "session": {
            "message_count": len(session["messages"]),
            "viewed_products": session["viewed_products"][-10:],
            "preferences": session["preferences"],
        },
    }

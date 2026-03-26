from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    id: str
    title: str
    category: str
    description: str
    tags: list[str]
    price: float
    color: str
    style: str
    use_case: str
    gender: str
    rating: float
    brand: str
    image_url: str
    # New fields for richer catalog
    material: Optional[str] = None
    sizes: Optional[list[str]] = None
    in_stock: bool = True
    review_count: int = 0
    discount_pct: int = 0  # 0-50, percentage off


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    products: Optional[list[Product]] = None
    image_base64: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None  # base64 encoded image
    history: Optional[list[ChatMessage]] = None
    session_id: Optional[str] = None  # for conversation tracking


class ChatResponse(BaseModel):
    message: str
    products: Optional[list[Product]] = None
    intent: str  # "general_chat", "text_recommendation", "image_search"

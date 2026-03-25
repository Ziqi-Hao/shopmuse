"""
Tool definitions for the ShopMuse agent.
These are called by the LLM agent via function calling.
"""

import json
from app.vector_store import search_by_text, search_by_image
from app.catalog import get_catalog
from app.models.schemas import Product
from PIL import Image


def catalog_text_search(query: str, category: str = None, max_price: float = None,
                        min_price: float = None, style: str = None,
                        gender: str = None, use_case: str = None,
                        top_k: int = 5) -> list[Product]:
    """Search the product catalog using natural language text query with optional filters."""
    filters = {}
    if category:
        filters["category"] = category
    if max_price is not None:
        filters["max_price"] = max_price
    if min_price is not None:
        filters["min_price"] = min_price
    if style:
        filters["style"] = style
    if gender:
        filters["gender"] = gender
    if use_case:
        filters["use_case"] = use_case

    return search_by_text(query, top_k=top_k, filters=filters if filters else None)


def catalog_image_search(image: Image.Image, top_k: int = 5) -> list[Product]:
    """Search the product catalog using an uploaded image to find visually similar products."""
    return search_by_image(image, top_k=top_k)


def get_product_by_id(product_id: str) -> Product | None:
    """Look up a specific product by its ID."""
    catalog = get_catalog()
    for p in catalog:
        if p.id == product_id:
            return p
    return None


def list_categories() -> list[str]:
    """List all available product categories."""
    catalog = get_catalog()
    return sorted(set(p.category for p in catalog))


def get_price_range() -> dict:
    """Get the price range across all products."""
    catalog = get_catalog()
    prices = [p.price for p in catalog]
    return {"min": min(prices), "max": max(prices), "avg": sum(prices) / len(prices)}


# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "catalog_text_search",
            "description": "Search the product catalog using a natural language query. Use this when the user wants product recommendations, is looking for specific items, or describes what they want. Always use this tool when the user asks about products, recommendations, or shopping-related queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query describing what the user wants, e.g. 'casual summer t-shirt' or 'waterproof hiking boots'"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["t-shirt", "shoes", "bag", "jacket", "pants", "accessories"],
                        "description": "Filter by product category"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["casual", "sporty", "formal", "smart casual", "streetwear", "outdoor", "trendy"],
                        "description": "Filter by style"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["men", "women", "unisex"],
                        "description": "Filter by gender"
                    },
                    "use_case": {
                        "type": "string",
                        "enum": ["everyday", "sports", "office", "outdoor", "summer", "winter", "formal", "festival", "travel", "lounge"],
                        "description": "Filter by use case"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_by_id",
            "description": "Look up a specific product by its ID. Use when the user references a product ID or wants details about a specific item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID, e.g. 'TS001'"
                    }
                },
                "required": ["product_id"]
            }
        }
    }
]

import json
from pathlib import Path
from app.models.schemas import Product

CATALOG_PATH = Path(__file__).parent.parent / "data" / "catalog.json"


def load_catalog() -> list[Product]:
    with open(CATALOG_PATH, "r") as f:
        data = json.load(f)
    return [Product(**item) for item in data]


# Singleton catalog
_catalog: list[Product] | None = None


def get_catalog() -> list[Product]:
    global _catalog
    if _catalog is None:
        _catalog = load_catalog()
    return _catalog

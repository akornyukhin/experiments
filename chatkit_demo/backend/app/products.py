from typing import Any, TypedDict

from chatkit.widgets import WidgetTemplate

from app.config import PRODUCT_WIDGET_PATH
from app.mcp import store_mcp_server


class Product(TypedDict):
    title: str
    name: str
    description: str
    price: float
    image: str


product_widget_template = WidgetTemplate.from_file(str(PRODUCT_WIDGET_PATH))


def coerce_products(payload: Any) -> list[Product]:
    if not isinstance(payload, list):
        return []
    return [product for product in payload if isinstance(product, dict)]


async def load_store_products() -> list[Product]:
    result = await store_mcp_server.call_tool("list_products", {})
    if not result.structuredContent:
        return []

    products = result.structuredContent.get("products")
    return coerce_products(products)


def format_price(price: float) -> str:
    return f"${price:.2f}"


def build_widget_items(products: list[Product]) -> list[dict[str, str]]:
    return [
        {
            "name": product["name"],
            "title": product["title"],
            "description": product["description"],
            "priceText": format_price(product["price"]),
            "image": product["image"],
        }
        for product in products
    ]


def build_products_widget(products: list[Product]):
    return product_widget_template.build({"items": build_widget_items(products)})

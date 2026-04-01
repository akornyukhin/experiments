from typing import TypedDict

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="store-products", host="127.0.0.1", port=8001)


class Product(TypedDict):
    title: str
    name: str
    description: str
    price: float
    image: str


PRODUCTS: list[Product] = [
    {
        "title": "Catnip Latte Mug",
        "name": "catnip-latte-mug",
        "description": "A mug with a catnip latte design",
        "price": 18.99,
        "image": "https://www.placekittens.com/400/400?image=1",
    },
    {
        "title": "Midnight Tabby Hoodie",
        "name": "midnight-tabby-hoodie",
        "description": "A hoodie with a midnight tabby design",
        "price": 54.0,
        "image": "https://www.placekittens.com/400/400?image=2",
    },
    {
        "title": "Whisker Desk Lamp",
        "name": "whisker-desk-lamp",
        "description": "A desk lamp with a whisker design",
        "price": 39.5,
        "image": "https://www.placekittens.com/400/400?image=3",
    },
    {
        "title": "Purr Mode Keyboard Mat",
        "name": "purr-mode-keyboard-mat",
        "description": "A keyboard mat with a purr mode design",
        "price": 24.75,
        "image": "https://www.placekittens.com/400/400?image=4",
    },
]


@mcp.tool()
def list_products() -> dict[str, list[Product]]:
    """Return the list of products available in the store."""
    print("Listing store products")
    return {"products": PRODUCTS}


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")

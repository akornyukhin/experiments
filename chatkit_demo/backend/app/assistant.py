from agents import Agent, RunContextWrapper, function_tool
from chatkit.agents import AgentContext

from app.config import logger
from app.products import build_products_widget, load_store_products


@function_tool(description_override="Show the available store products as a widget.")
async def show_store_products(ctx: RunContextWrapper[AgentContext]) -> str:
    logger.info("Showing store products")
    products = await load_store_products()
    await ctx.context.stream_widget(
        build_products_widget(products),
        copy_text="Available store products",
    )
    return f"Displayed {len(products)} products."


def create_assistant() -> Agent:
    return Agent(
        name="assistant",
        instructions=(
            "You are a helpful assistant. When users ask to browse, show, or list "
            "store products, call `show_store_products` so the products render as "
            "a widget. Use MCP tools when you need product data."
        ),
        model="gpt-4.1-mini",
        tools=[show_store_products],
    )


assistant = create_assistant()

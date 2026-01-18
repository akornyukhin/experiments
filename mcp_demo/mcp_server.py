from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"Adding {a} and {b}")
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print(f"Subtracting {a} and {b}")
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print(f"Multiplying {a} and {b}")
    return a * b

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    print(f"Greeting user {name} with style {style}")
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
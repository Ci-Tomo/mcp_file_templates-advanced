from fastmcp import FastMCP

mcp = FastMCP("mcp-book-template-advanced")


@mcp.tool
def greet(name: str) -> str:
    """指定した名前への挨拶を返す。"""
    return f"Hello, {name}!"


@mcp.tool
def add(a: int, b: int) -> int:
    """2つの整数を足し算する。"""
    return a + b


if __name__ == "__main__":
    mcp.run()

from mcp.server.fastmcp import FastMCP
from app import services
from app.graph_store import index_repo

mcp = FastMCP("codegraph")


@mcp.tool()
def onboard(repo_path: str) -> dict:
    """Index a code repository (local path or public git URL) into the graph. Run this first for any repo you haven't analyzed yet."""
    return index_repo(repo_path)


@mcp.tool()
def who_calls(name: str) -> list:
    """Find functions that DIRECTLY call the given function — its immediate callers."""
    return services.who_calls(name)


@mcp.tool()
def impact_of_change(name: str, depth: int = 3) -> list:
    """Everything that TRANSITIVELY calls the given function — the blast radius before changing it. depth 1-5."""
    return services.impact_of_change(name, depth)


@mcp.tool()
def depends_on(name: str, depth: int = 3) -> list:
    """Everything the given function TRANSITIVELY calls, with 'hop' distance — what it relies on. depth 1-5."""
    return services.depends_on(name, depth)


if __name__ == "__main__":
    mcp.run()
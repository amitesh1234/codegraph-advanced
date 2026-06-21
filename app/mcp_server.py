import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP   # your existing imports continue below
from app import services
from app.graph_store import index_repo, parse_local_path

mcp = FastMCP("codegraph")


@mcp.tool()
def onboard(repo_path: str) -> dict:
    """Index a code repository (local path) into the graph. Run this first for any repo you haven't analyzed yet."""
    print(f"[onboard] called with: {repo_path}", file=sys.stderr)
    local_path, cleanup = parse_local_path(repo_path)
    try:
        result = index_repo(local_path)
        print(f"[onboard] result: {result}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"[onboard] ERROR: {e!r}", file=sys.stderr)
        raise
    finally:
        if cleanup:
            shutil.rmtree(local_path, ignore_errors=True)


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
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print(onboard("https://github.com/psf/requests"))   # quick headless sanity check
    else:
        mcp.run()
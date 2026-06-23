from app.db import run_query
from app.memory import log_run

_search_index_ready = False

def _ensure_search_index():
    global _search_index_ready
    if not _search_index_ready:
        run_query(
            "CREATE FULLTEXT INDEX function_search IF NOT EXISTS "
            "FOR (f:Function) ON EACH [f.name, f.docstring, f.body]"
        )
        _search_index_ready = True


def search_code(query: str, limit: int = 10) -> list:
    _ensure_search_index()
    return run_query(
        "CALL db.index.fulltext.queryNodes('function_search', $query) "
        "YIELD node, score "
        "RETURN node.id AS id, node.name AS name, node.file AS file, "
        "node.line AS line, left(node.body, 200) AS snippet, score "
        "ORDER BY score DESC "
        "LIMIT $limit",
        {"query": query, "limit": limit},
    )


def get_function_source(function_id: str):
    rows = run_query(
        "MATCH (f:Function {id: $id}) "
        "RETURN f.id AS id, f.name AS name, f.file AS file, f.line AS line, f.body AS body",
        {"id": function_id},
    )
    return rows[0] if rows else None


def who_calls(name: str) -> list:
    return run_query(
        "MATCH (c:Function)-[:CALLS]->(:Function {name: $name}) "
        "RETURN DISTINCT c.name AS name, c.file AS file",
        {"name": name},
    )


def impact_of_change(name: str, depth: int = 3) -> list:
    depth = max(1, min(depth, 5))
    return run_query(
        "MATCH (c:Function)-[:CALLS*1.." + str(depth) + "]->(:Function {name: $name}) "
        "RETURN DISTINCT c.name AS name, c.file AS file",
        {"name": name},
    )


def depends_on(name: str, depth: int = 3) -> list:
    depth = max(1, min(depth, 5))
    return run_query(
        "MATCH path = (:Function {name: $name})-[:CALLS*1.." + str(depth) + "]->(d:Function) "
        "WITH d, min(length(path)) AS hop "
        "RETURN d.name AS name, d.file AS file, hop "
        "ORDER BY hop, name",
        {"name": name},
    )
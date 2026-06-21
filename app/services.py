from app.db import run_query
from app.memory import log_run


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
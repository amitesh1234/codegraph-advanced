import os
import shutil
import tempfile
import subprocess
from app.db import run_query
from app.parser import parse_repo

def index_repo(repo_path):
    functions, edges = parse_repo(repo_path)

    # 1) Write function nodes (idempotent)
    run_query(
        """
        UNWIND $rows AS row
        MERGE (f:Function {id: row.id})
        SET f.name = row.name, f.file = row.file, f.line = row.line
        """,
        {"rows": functions},
    )

    # 2) Write CALLS edges (nodes must exist first)
    edge_rows = [{"caller": a, "callee": b} for a, b in edges]
    run_query(
        """
        UNWIND $rows AS row
        MATCH (a:Function {id: row.caller})
        MATCH (b:Function {id: row.callee})
        MERGE (a)-[:CALLS]->(b)
        """,
        {"rows": edge_rows},
    )

    return {
        "functions_indexed": len(functions),
        "call_edges_indexed": len(edges),
    }

def is_git_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "git@")) or value.endswith(".git")

def clone_repo(url: str) -> str:
    """Shallow-clone a git URL into a temp dir, return the local path."""
    dest = tempfile.mkdtemp(prefix="codegraph_")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, dest],
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        shutil.rmtree(dest, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {e.stderr.strip()}")
    return dest
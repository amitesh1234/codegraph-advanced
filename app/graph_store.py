import os
import shutil
import sys
import tempfile
import subprocess
from app.db import run_query
from app.parser import parse_repo

def parse_local_path(repo_path):
    # if is_git_url(repo_path):
    #     local_path = clone_repo(repo_path)          # clone, get temp dir
    #     cleanup = True
    # else:
    #     if not os.path.isdir(repo_path):
    #         raise RuntimeError(f"Path not found: {repo_path}")
    #     local_path = repo_path
    #     cleanup = False
    # return (local_path, cleanup)   
    if not os.path.isdir(repo_path):
        raise RuntimeError(f"Path not found: {repo_path}")
    local_path = repo_path
    cleanup = False
    return (local_path, cleanup)    
    

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

GIT = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"

def clone_repo(url: str) -> str:
    dest = tempfile.mkdtemp(prefix="codegraph_")
    print(f"[clone] git={GIT}  url={url}  dest={dest}", file=sys.stderr)

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"   # never prompt for credentials — fail instead of hanging
    env["GCM_INTERACTIVE"] = "never"   # disable Git Credential Manager popups

    try:
        proc = subprocess.run(
            [GIT, "clone", "--depth", "1", url, dest],
            capture_output=True, text=True,
            env=env,
            timeout=120,               # hard ceiling — never hang forever
        )
    except subprocess.TimeoutExpired:
        print("[clone] TIMEOUT after 120s", file=sys.stderr)
        raise RuntimeError("git clone timed out")

    print(f"[clone] returncode={proc.returncode}", file=sys.stderr)
    print(f"[clone] stderr={proc.stderr}", file=sys.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"git clone failed: {proc.stderr.strip()}")
    print(f"[clone] files={os.listdir(dest)}", file=sys.stderr)
    return dest
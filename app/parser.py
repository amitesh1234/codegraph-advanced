import os

from app.parsers.python_backend import PythonBackend
from app.parsers.js_backend import JsBackend
from app.parsers.ts_backend import TsBackend, TsxBackend

BACKENDS = [PythonBackend(), JsBackend(), TsBackend(), TsxBackend()]
EXT_MAP = {ext: b for b in BACKENDS for ext in b.extensions}

def parse_repo(repo_root):
    all_functions, all_raw_calls = [], []

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", ".venv", "__pycache__", "node_modules"}]
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            backend = EXT_MAP.get(ext)
            if not backend:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), repo_root).replace(os.sep, "/")
            with open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="ignore") as f:
                funcs, calls = backend.extract(f.read(), rel)
            all_functions.extend(funcs)
            all_raw_calls.extend(calls)

    # --- language-agnostic resolution (unchanged) ---
    name_index = {}
    for f in all_functions:
        name_index.setdefault(f["name"], []).append(f["id"])

    edges = set()
    for caller_id, callee_name in all_raw_calls:
        for callee_id in name_index.get(callee_name, []):
            if callee_id != caller_id:
                edges.add((caller_id, callee_id))

    return all_functions, list(edges)
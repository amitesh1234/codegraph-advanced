import ast
import os


def parse_file(path, repo_root):
    """One Python file -> (functions, raw_calls).
    functions: [{id, name, file, line}]
    raw_calls: [(caller_id, callee_name)]
    """
    rel = os.path.relpath(path, repo_root)
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=rel)
    except (SyntaxError, UnicodeDecodeError):
        return [], []

    functions, raw_calls = [], []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.stack = []  # enclosing function ids

        def _visit_func(self, node):
            fid = f"{rel}::{node.name}"
            functions.append({"id": fid, "name": node.name,
                              "file": rel, "line": node.lineno})
            self.stack.append(fid)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _visit_func
        visit_AsyncFunctionDef = _visit_func

        def visit_Call(self, node):
            if self.stack:
                callee = None
                if isinstance(node.func, ast.Name):        # foo()
                    callee = node.func.id
                elif isinstance(node.func, ast.Attribute):  # obj.method()
                    callee = node.func.attr
                if callee:
                    raw_calls.append((self.stack[-1], callee))
            self.generic_visit(node)

    Visitor().visit(tree)
    return functions, raw_calls


def parse_repo(repo_root):
    """Whole repo -> (functions, edges). edges: [(caller_id, callee_id)]"""
    all_functions, all_raw_calls = [], []

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", ".venv", "__pycache__", "node_modules"}]
        for fn in filenames:
            if fn.endswith(".py"):
                funcs, calls = parse_file(os.path.join(dirpath, fn), repo_root)
                all_functions.extend(funcs)
                all_raw_calls.extend(calls)

    name_index = {}
    for f in all_functions:
        name_index.setdefault(f["name"], []).append(f["id"])

    edges = set()
    for caller_id, callee_name in all_raw_calls:
        for callee_id in name_index.get(callee_name, []):
            if callee_id != caller_id:
                edges.add((caller_id, callee_id))

    return all_functions, list(edges)

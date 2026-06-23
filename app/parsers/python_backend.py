import ast
from app.parsers.base import LanguageBackend


class PythonBackend(LanguageBackend):
    extensions = (".py",)

    def extract(self, source: str, rel_path: str):
        """One Python file's source -> (functions, raw_calls)."""
        try:
            tree = ast.parse(source, filename=rel_path)
        except SyntaxError:
            return [], []

        functions, raw_calls = [], []

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.stack = []  # enclosing function ids

            def _visit_func(self, node):
                fid = f"{rel_path}::{node.name}"
                functions.append({
                    "id": fid,
                    "name": node.name,
                    "file": rel_path,
                    "line": node.lineno,
                    "language": "python",
                    "body": ast.get_source_segment(source, node) or "",
                    "docstring": ast.get_docstring(node) or "",
                })
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
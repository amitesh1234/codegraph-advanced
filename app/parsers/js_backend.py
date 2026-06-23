import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser
from app.parsers.base import LanguageBackend

JS_LANGUAGE = Language(tsjs.language())

# node types that represent "a function" in JS
FUNC_NODES = {
    "function_declaration",   # function foo() {}
    "function_expression",    # const foo = function() {}
    "arrow_function",         # const foo = () => {}
    "method_definition",      # class { foo() {} }
}


class JsBackend(LanguageBackend):
    extensions = (".js", ".jsx", ".mjs", ".cjs")

    def __init__(self):
        self.parser = Parser(JS_LANGUAGE)

    def _node_name(self, node):
        """Best-effort name for a function node."""
        # function_declaration / method_definition have a 'name' field
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf8", "ignore")
        # arrow / function expression: name comes from the variable it's assigned to
        #   (variable_declarator name: (identifier) value: (arrow_function))
        parent = node.parent
        if parent and parent.type == "variable_declarator":
            n = parent.child_by_field_name("name")
            if n:
                return n.text.decode("utf8", "ignore")
        # object property: { foo: () => {} }  ->  (pair key: (property_identifier))
        if parent and parent.type == "pair":
            k = parent.child_by_field_name("key")
            if k:
                return k.text.decode("utf8", "ignore")
        return None

    def _statement_node(self, node):
        """Walk up from arrow/function-expression to its statement-level ancestor."""
        if node.type in ("arrow_function", "function_expression"):
            p = node.parent
            if p and p.type == "variable_declarator":
                pp = p.parent
                if pp and pp.type in ("variable_declaration", "lexical_declaration"):
                    return pp
        return node

    def _leading_comment(self, node):
        """Return the text of the immediately preceding // or /* */ comment, or ''."""
        stmt = self._statement_node(node)
        prev = stmt.prev_named_sibling
        if prev and prev.type == "comment":
            text = prev.text.decode("utf8", "ignore").strip()
            if text.startswith("//"):
                return text[2:].strip()
            if text.startswith("/*") and text.endswith("*/"):
                return text[2:-2].strip()
            return text
        return ""

    def extract(self, source: str, rel_path: str):
        tree = self.parser.parse(bytes(source, "utf8"))
        functions, raw_calls = [], []

        def walk(node, func_stack):
            # is this node a function?
            pushed = False
            if node.type in FUNC_NODES:
                name = self._node_name(node)
                if name:
                    fid = f"{rel_path}::{name}"
                    functions.append({
                        "id": fid,
                        "name": name,
                        "file": rel_path,
                        "line": node.start_point[0] + 1,  # 0-indexed -> 1-indexed
                        "language": "js",
                        "body": node.text.decode("utf8", "ignore"),
                        "docstring": self._leading_comment(node),
                    })
                    func_stack.append(fid)
                    pushed = True

            # is this node a call?  call_expression -> function: (identifier | member_expression)
            if node.type == "call_expression" and func_stack:
                fn = node.child_by_field_name("function")
                callee = None
                if fn is not None:
                    if fn.type == "identifier":                 # foo()
                        callee = fn.text.decode("utf8", "ignore")
                    elif fn.type == "member_expression":         # obj.method()
                        prop = fn.child_by_field_name("property")
                        if prop:
                            callee = prop.text.decode("utf8", "ignore")
                if callee:
                    raw_calls.append((func_stack[-1], callee))

            for child in node.children:
                walk(child, func_stack)

            if pushed:
                func_stack.pop()

        walk(tree.root_node, [])
        return functions, raw_calls
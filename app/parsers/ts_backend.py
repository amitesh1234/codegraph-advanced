import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser
from app.parsers.js_backend import JsBackend

TS_LANGUAGE = Language(tsts.language_typescript())
TSX_LANGUAGE = Language(tsts.language_tsx())


class TsBackend(JsBackend):
    extensions = (".ts",)
    language_name = "ts"

    def _language(self):
        return TS_LANGUAGE


class TsxBackend(JsBackend):
    extensions = (".tsx",)
    language_name = "tsx"

    def _language(self):
        return TSX_LANGUAGE
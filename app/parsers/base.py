class LanguageBackend:
    extensions: tuple = ()
    def extract(self, source: str, rel_path: str):
        """Return (functions, raw_calls) for one file.
        functions: [{id, name, file, line, language}]
        raw_calls: [(caller_id, callee_name)]
        """
        raise NotImplementedError
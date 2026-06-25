# Query words overlap the function name / body / docstring — full-text's strength
WORD_OVERLAP = [
    ("prepare a request",                  "prepare"),
    ("prepare the request headers",        "prepare_headers"),
    ("prepare the request body",           "prepare_body"),
    ("prepare authentication",             "prepare_auth"),
    ("send a request",                     "send"),
    ("merge settings",                     "merge_setting"),
    ("merge environment settings",         "merge_environment_settings"),
    ("merge cookies",                      "merge_cookies"),
    ("resolve redirects",                  "resolve_redirects"),
    ("build a digest authentication header","build_digest_header"),
    ("mount an adapter",                   "mount"),
    ("get the encoding from headers",      "get_encoding_from_headers"),
]

# Query describes the behavior with DIFFERENT vocabulary than the code uses —
# the hard cases that probe whether keyword search is enough
CONCEPT_ONLY = [
    ("combine per-request and session config",      "merge_setting"),
    ("figure out where to follow a 301 or 302",     "resolve_redirects"),
    ("turn a Request object into something sendable","prepare"),
    ("read the character set of a response",         "get_encoding_from_headers"),
    ("retry against a server that asks for login",   "handle_401"),
    ("attach a connection pool for a URL scheme",    "mount"),
    ("decide which proxy to use for a host",         "should_bypass_proxies"),
    ("stream the response content in chunks",        "iter_content"),
]

# Combined set used by the eval
SEARCH_CASES = WORD_OVERLAP + CONCEPT_ONLY

IMPACT_CASES = [
    ("send", 3,
     "Should surface functions that depend on send, including handle_401 (auth) "
     "and the request flow up toward the public API."),
    ("prepare", 3,
     "Should surface that prepare is reached via Session.prepare_request and "
     "Session.request, i.e. effectively the whole request path."),
]
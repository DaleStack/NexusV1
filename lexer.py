import re

# Token Specification
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),  # Integer or decimal number
    ("STRING",   r'"[^"\n]*"'),    # Double-quoted string
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),  # Identifiers
    ("OP",       r"==|!=|>=|<=|[+\-*/=<>]"),  # Operators
    ("PUNCT",    r"[(){}\[\]:,]"),  # Punctuation
    ("NEWLINE",  r"\n"),            # Line endings
    ("SKIP",     r"[ \t]+"),        # Spaces/tabs
    ("COMMENT",  r"#.*"),           # Comment
]
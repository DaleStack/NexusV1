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

# Combine into regex
TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

KEYWORDS = {
    "var", "say", "ask", "if", "else", "for", "inclusive",
    "by", "break", "continue", "func", "return", "true", "false"
}
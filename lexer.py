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

def lexer(code):
    tokens = []
    for match in re.finditer(TOKEN_REGEX, code):
        kind = match.lastgroup
        value = match.group()

        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "STRING":
            value = value.strip('"')
        elif kind == "ID" and value in KEYWORDS:
            kind = value.upper()  # Make keywords uppercase token type
        elif kind == "ID":
            pass  # leave as ID
        elif kind == "SKIP" or kind == "COMMENT":
            continue
        elif kind == "NEWLINE":
            continue

        tokens.append((kind, value))

    return tokens
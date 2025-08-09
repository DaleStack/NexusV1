import re

# Token Specification
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("STRING",   r'"[^"\n]*"'),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"), 
    ("OP",       r"==|!=|>=|<=|and|or|not|[+\-*/%=<>]"),
    ("PUNCT",    r"[(){}\[\]:,]"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#.*"),
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

KEYWORDS = {
    "var", "say", "ask", "if", "else", "for", "inclusive",
    "by", "break", "continue", "func", "return", "true", "false"
}

def lexer(code):
    tokens = []
    indent_stack = [0]  # Track indentation levels
    line_start = True

    pos = 0
    while pos < len(code):
        match = re.match(TOKEN_REGEX, code[pos:])
        if not match:
            raise SyntaxError(f"Unexpected character: {code[pos]}")

        kind = match.lastgroup
        value = match.group()

        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "STRING":
            value = value.strip('"')
        elif kind == "ID":
            if value in KEYWORDS:
                kind = value.upper()
            elif value in ("and", "or", "not"):
                kind = "OP"

        if kind == "NEWLINE":
            tokens.append(("NEWLINE", value))
            line_start = True
            pos += len(value)
            continue

        if line_start:
            # Handle indentation at the start of a line
            if kind == "SKIP":
                indent = len(value.replace("\t", "    "))  # tabs = 4 spaces
                if indent > indent_stack[-1]:
                    indent_stack.append(indent)
                    tokens.append(("INDENT", indent))
                elif indent < indent_stack[-1]:
                    while indent < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(("DEDENT", indent))
                pos += len(value)
                line_start = False
                continue
            else:
                # No indent → check for dedent
                if indent_stack[-1] != 0:
                    while indent_stack[-1] != 0:
                        indent_stack.pop()
                        tokens.append(("DEDENT", 0))
                line_start = False

        if kind not in ("SKIP", "COMMENT"):
            tokens.append((kind, value))

        pos += len(match.group())

    # End of file — close all open indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(("DEDENT", 0))

    return tokens

# Test
if __name__ == "__main__":
    code = '''
var name = "John"
say("Hello, " + name)
if name == "John":
    say("It's John")
    say("Another line")
else:
    say("Not John")
'''
    for t in lexer(code):
        print(t)

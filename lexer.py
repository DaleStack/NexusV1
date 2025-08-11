import re

# Token Specification
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),      # This already handles floats!
    ("STRING",   r'"[^"\n]*"'),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"), 
    ("OP",       r"==|!=|>=|<=|and|or|not|[+\-*/%=<>]"),
    ("PUNCT",    r"[(){}\[\]:,]"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#.*"),
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

# Updated keywords dictionary with float
KEYWORDS = {
    "var": "VAR", 
    "say": "SAY", 
    "ask": "ASK", 
    "if": "IF", 
    "else": "ELSE", 
    "for": "FOR", 
    "inclusive": "INCLUSIVE",
    "by": "BY", 
    "break": "BREAK", 
    "continue": "CONTINUE", 
    "func": "FUNC", 
    "return": "RETURN", 
    "True": "BOOLEAN",     
    "true": "BOOLEAN",     
    "False": "BOOLEAN",    
    "false": "BOOLEAN",    
    "in": "IN", 
    "to": "TO",
    # NEW: Add float as a type keyword
    "int": "TYPE",
    "str": "TYPE", 
    "bool": "TYPE",
    "float": "TYPE"
}

# IMPORTANT: Special operators that should be OP tokens
OPERATORS = {
    "and": "OP",
    "or": "OP", 
    "not": "OP"
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
            # Enhanced number parsing to distinguish int vs float
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        elif kind == "STRING":
            value = value.strip('"')
        elif kind == "ID":
            # FIXED: Check operators first, then keywords
            if value in OPERATORS:
                kind = OPERATORS[value]  # and, or, not -> OP
            elif value in KEYWORDS:
                kind = KEYWORDS[value]   # var, say, True, int, float, etc. -> their specific types

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

# Test with float support
if __name__ == "__main__":
    test_code = '''
var price float = 19.99
var discount float = 0.15
var total float = price * (1.0 - discount)
say("Total: " + total)
'''
    
    print("=== FLOAT LEXER TEST ===")
    tokens = lexer(test_code)
    for i, token in enumerate(tokens):
        print(f"{i:2}: {token}")
        
    print("\n=== TYPE CHECKING ===")
    print("Looking for TYPE tokens:")
    for i, (token_type, token_value) in enumerate(tokens):
        if token_type == "TYPE":
            print(f"Found type '{token_value}' at position {i}")
        elif token_type == "NUMBER" and isinstance(token_value, float):
            print(f"Found float literal {token_value} at position {i}")
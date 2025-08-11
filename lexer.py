import re

# Token Specification
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),      
    ("STRING",   r'"[^"\n]*"'),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"), 
    ("OP",       r"==|!=|>=|<=|and|or|not|[+\-*/%=<>]"),
    ("PUNCT",    r"[(){}\[\]:,.]"),  # ADDED: . for member access
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t]+"),
    ("COMMENT",  r"#.*"),
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

# Updated keywords dictionary with struct
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
    "struct": "STRUCT",  # NEW: struct keyword
    # Type keywords
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
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        elif kind == "STRING":
            value = value.strip('"')
        elif kind == "ID":
            # Check operators first, then keywords
            if value in OPERATORS:
                kind = OPERATORS[value]  
            elif value in KEYWORDS:
                kind = KEYWORDS[value]   

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

# Test struct lexing
if __name__ == "__main__":
    test_code = '''
struct Dog():
    var name str
    var age int

var myPet = Dog()
myPet.name = "Buddy"
myPet.age = 3
say(myPet.name)
'''
    
    print("=== STRUCT LEXER TEST ===")
    tokens = lexer(test_code)
    for i, token in enumerate(tokens):
        print(f"{i:2}: {token}")
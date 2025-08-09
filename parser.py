# parser.py
from lexer import lexer

# AST Node classes
class VarDecl:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class SayStmt:
    def __init__(self, expr):
        self.expr = expr

class IfStmt:
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Literal:
    def __init__(self, value):
        self.value = value

class VarRef:
    def __init__(self, name):
        self.name = name


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def eat(self, kind=None):
        token = self.current()
        if kind and token[0] != kind:
            raise SyntaxError(f"Expected {kind} but got {token}")
        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            tok_type, _ = self.current()
            if tok_type == "VAR":
                statements.append(self.parse_var_decl())
            elif tok_type == "SAY":
                statements.append(self.parse_say())
            elif tok_type == "IF":
                statements.append(self.parse_if())
            else:
                self.pos += 1
        return statements

    def parse_var_decl(self):
        self.eat("VAR")
        _, name = self.eat("ID")
        value = None
        if self.current()[0] == "OP" and self.current()[1] == "=":
            self.eat("OP")
            value = self.parse_expression()
        return VarDecl(name, value)

    def parse_say(self):
        self.eat("SAY")
        self.eat("PUNCT")  # (
        expr = self.parse_expression()
        self.eat("PUNCT")  # )
        return SayStmt(expr)

    def parse_if(self):
        self.eat("IF")
        condition = self.parse_expression()
        self.eat("PUNCT")  # :
        body = [self.parse_say()]  # TODO: make this handle multiple statements
        return IfStmt(condition, body)

    def parse_expression(self):
        left = self.parse_term()
        while self.current()[0] == "OP":
            _, op = self.eat("OP")
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        return left

    def parse_term(self):
        tok_type, tok_value = self.current()
        if tok_type in ("NUMBER", "STRING"):
            self.eat()
            return Literal(tok_value)
        elif tok_type == "ID":
            self.eat()
            return VarRef(tok_value)
        else:
            raise SyntaxError(f"Unexpected token: {tok_type}")


if __name__ == "__main__":
    # Simple test
    code = '''
    var name = "John"
    say("Hello, "+name)
    if name == "John":
        say("It's John")
    '''
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    for node in ast:
        print(node.__class__.__name__, vars(node))

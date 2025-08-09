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

class ForStmt:
    def __init__(self, var_name, start, end, step, body, inclusive=False, infinite=False):
        self.var_name = var_name          # string or None if infinite loop
        self.start = start                # expressions
        self.end = end
        self.step = step
        self.body = body                  # list of statements
        self.inclusive = inclusive
        self.infinite = infinite

class BreakStmt:
    pass

class ContinueStmt:
    pass

class AskStmt:
    def __init__(self, prompt_expr, var_name=None):
        self.prompt_expr = prompt_expr  # expression for the prompt string
        self.var_name = var_name        # optional variable name to assign input

class FuncDecl:
    def __init__(self, name, params, body):
        self.name = name          # string
        self.params = params      # list of param names (strings)
        self.body = body          # list of statements

class FuncCall:
    def __init__(self, name, args):
        self.name = name          # string
        self.args = args          # list of expressions

class ReturnStmt:
    def __init__(self, expr):
        self.expr = expr          # expression node or None



class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def eat(self, kind=None, value=None):
        tok = self.current()
        if kind and tok[0] != kind:
            raise SyntaxError(f"Expected token type {kind} but got {tok}")
        if value and tok[1] != value:
            raise SyntaxError(f"Expected token value '{value}' but got {tok}")
        self.pos += 1
        return tok

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            tok_type, tok_val = self.current()
            if tok_type == "VAR":
                statements.append(self.parse_var_decl())
            elif tok_type == "SAY":
                statements.append(self.parse_say())
            elif tok_type == "IF":
                statements.append(self.parse_if())
            elif tok_type == "FOR":
                statements.append(self.parse_for())
            elif tok_type == "BREAK":
                statements.append(self.parse_break())
            elif tok_type == "CONTINUE":
                statements.append(self.parse_continue())
            elif tok_type == "ASK":
                statements.append(self.parse_ask())
            elif tok_type == "FUNC":          # <-- Add this
                statements.append(self.parse_func_decl())
            elif tok_type == "RETURN":
                statements.append(self.parse_return())
            elif tok_type == "ID":
                # Could be a function call or a variable reference
                # Peek next token to check if it's '('
                next_tok = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else (None, None)
                if next_tok[0] == "PUNCT" and next_tok[1] == "(":
                    statements.append(self.parse_func_call())
                else:
                    self.pos += 1  # Skip or raise error depending on your grammar
            elif tok_type == "NEWLINE":
                self.eat("NEWLINE")
            else:
                self.pos += 1
        return statements

    def parse_var_decl(self):
        self.eat("VAR")
        _, name = self.eat("ID")
        value = None
        if self.current()[0] == "OP" and self.current()[1] == "=":
            self.eat("OP")
            if self.current()[0] == "ASK":
                value = self.parse_ask()
            else:
                value = self.parse_expression()
        return VarDecl(name, value)

    def parse_say(self):
        self.eat("SAY")
        self.eat("PUNCT", "(")
        expr = self.parse_expression()
        self.eat("PUNCT", ")")
        return SayStmt(expr)

    def parse_if(self):
        self.eat("IF")
        condition = self.parse_expression()
        self.eat("PUNCT", ":")
        self.eat("NEWLINE")
        self.eat("INDENT")
        body = self.parse_block()
        else_body = None

        if self.current()[0] == "ELSE":
            self.eat("ELSE")
            # Handle else-if as nested if inside else_body list
            if self.current()[0] == "IF":
                else_body = [self.parse_if()]
            else:
                self.eat("PUNCT", ":")
                self.eat("NEWLINE")
                self.eat("INDENT")
                else_body = self.parse_block()

        return IfStmt(condition, body, else_body)

    def parse_for(self):
        self.eat("FOR")

        if self.current()[0] == "PUNCT" and self.current()[1] == ":":
            # Infinite loop
            self.eat("PUNCT", ":")
            self.eat("NEWLINE")
            self.eat("INDENT")
            body = self.parse_block()
            return ForStmt(None, None, None, None, body, infinite=True)

        _, var_name = self.eat("ID")
        if self.current()[0] != "IN":
            raise SyntaxError(f"Expected 'in' after for variable but got {self.current()}")
        self.eat("IN")

        self.eat("PUNCT", "(")
        inclusive = False
        if self.current()[0] == "INCLUSIVE":
            self.eat("INCLUSIVE")
            inclusive = True

        start = self.parse_expression()

        if self.current()[0] != "TO":
            raise SyntaxError(f"Expected 'to' in for loop range but got {self.current()}")
        self.eat("TO")

        end = self.parse_expression()

        step = Literal(1)
        if self.current()[0] == "BY":
            self.eat("BY")
            step = self.parse_expression()

        self.eat("PUNCT", ")")
        self.eat("PUNCT", ":")
        self.eat("NEWLINE")
        self.eat("INDENT")
        body = self.parse_block()

        return ForStmt(var_name, start, end, step, body, inclusive=inclusive)

    def parse_break(self):
        self.eat("BREAK")
        if self.current()[0] == "NEWLINE":
            self.eat("NEWLINE")
        return BreakStmt()

    def parse_continue(self):
        self.eat("CONTINUE")
        if self.current()[0] == "NEWLINE":
            self.eat("NEWLINE")
        return ContinueStmt()

    def parse_ask(self):
        self.eat("ASK")
        self.eat("PUNCT", "(")
        prompt_expr = self.parse_expression()
        self.eat("PUNCT", ")")
        return AskStmt(prompt_expr)
    
    def parse_return(self):
        self.eat("RETURN")
        expr = None
        if self.current()[0] != "NEWLINE":
            expr = self.parse_expression()
        if self.current()[0] == "NEWLINE":
            self.eat("NEWLINE")
        return ReturnStmt(expr)
    
    def parse_func_decl(self):
        self.eat("FUNC")
        _, name = self.eat("ID")
        self.eat("PUNCT", "(")
        
        params = []
        if self.current()[0] != "PUNCT" or self.current()[1] != ")":
            while True:
                _, param = self.eat("ID")
                params.append(param)
                if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                    self.eat("PUNCT", ",")
                else:
                    break
        self.eat("PUNCT", ")")
        self.eat("PUNCT", ":")
        self.eat("NEWLINE")
        self.eat("INDENT")
        body = self.parse_block()
        return FuncDecl(name, params, body)
    
    def parse_func_call(self):
        _, name = self.eat("ID")
        self.eat("PUNCT", "(")
        args = []
        if self.current()[0] != "PUNCT" or self.current()[1] != ")":
            while True:
                arg = self.parse_expression()
                args.append(arg)
                if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                    self.eat("PUNCT", ",")
                else:
                    break
        self.eat("PUNCT", ")")
        if self.current()[0] == "NEWLINE":
            self.eat("NEWLINE")
        return FuncCall(name, args)

    def parse_block(self):
        statements = []
        while self.current()[0] not in ("DEDENT", None):
            tok_type, _ = self.current()
            if tok_type == "VAR":
                statements.append(self.parse_var_decl())
            elif tok_type == "SAY":
                statements.append(self.parse_say())
            elif tok_type == "IF":
                statements.append(self.parse_if())
            elif tok_type == "FOR":
                statements.append(self.parse_for())
            elif tok_type == "BREAK":
                statements.append(self.parse_break())
            elif tok_type == "CONTINUE":
                statements.append(self.parse_continue())
            elif tok_type == "ASK":
                statements.append(self.parse_ask())
            elif tok_type == "FUNC":                # <-- Add here if nested functions allowed
                statements.append(self.parse_func_decl())
            elif tok_type == "RETURN":
                statements.append(self.parse_return())
            elif tok_type == "ID":                  # <-- ADD THIS CASE
                statements.append(self.parse_func_call())
            elif tok_type == "NEWLINE":
                self.eat("NEWLINE")
            else:
                self.pos += 1
        self.eat("DEDENT")
        return statements

    # Expression parsing methods omitted for brevity (unchanged) ...
    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.current()[0] == "OP" and self.current()[1] == "or":
            _, op = self.eat("OP")
            right = self.parse_and()
            node = BinaryOp(node, op, right)
        return node

    def parse_and(self):
        node = self.parse_equality()
        while self.current()[0] == "OP" and self.current()[1] == "and":
            _, op = self.eat("OP")
            right = self.parse_equality()
            node = BinaryOp(node, op, right)
        return node

    def parse_equality(self):
        node = self.parse_comparison()
        while self.current()[0] == "OP" and self.current()[1] in ("==", "!="):
            _, op = self.eat("OP")
            right = self.parse_comparison()
            node = BinaryOp(node, op, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current()[0] == "OP" and self.current()[1] in ("<", ">", "<=", ">="):
            _, op = self.eat("OP")
            right = self.parse_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current()[0] == "OP" and self.current()[1] in ("+", "-"):
            _, op = self.eat("OP")
            right = self.parse_factor()
            node = BinaryOp(node, op, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current()[0] == "OP" and self.current()[1] in ("*", "/", "%"):
            _, op = self.eat("OP")
            right = self.parse_unary()
            node = BinaryOp(node, op, right)
        return node

    def parse_unary(self):
        tok_type, tok_value = self.current()
        if tok_type == "OP" and tok_value == "not":
            self.eat()
            right = self.parse_unary()
            return BinaryOp(None, "not", right)
        elif tok_type == "OP" and tok_value == "-":
            self.eat()
            right = self.parse_unary()
            # Treat unary minus as BinaryOp with left=None, op='-', right=right
            return BinaryOp(None, "-", right)
        else:
            return self.parse_primary()

    def parse_primary(self):
        tok_type, tok_value = self.current()

        if tok_type == "PUNCT" and tok_value == "(":
            self.eat("PUNCT", "(")
            expr = self.parse_expression()
            self.eat("PUNCT", ")")
            return expr

        elif tok_type == "NUMBER" or tok_type == "STRING":
            self.eat()
            return Literal(tok_value)

        elif tok_type == "ID":
            self.eat()
            # Peek next token to see if this is a function call
            if self.current()[0] == "PUNCT" and self.current()[1] == "(":
                # It's a function call expression
                return self.parse_func_call_expr(tok_value)
            else:
                return VarRef(tok_value)

        else:
            raise SyntaxError(f"Unexpected token: {tok_type} {tok_value}")

    def parse_func_call_expr(self, func_name):
        self.eat("PUNCT", "(")
        args = []
        if self.current()[0] != "PUNCT" or self.current()[1] != ")":
            while True:
                arg = self.parse_expression()
                args.append(arg)
                if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                    self.eat("PUNCT", ",")
                else:
                    break
        self.eat("PUNCT", ")")
        return FuncCall(func_name, args)


if __name__ == "__main__":
    code = '''
func greet(name):
    say("Hello, " + name)

greet("World")
'''
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    for node in ast:
        print(node.__class__.__name__, vars(node) if hasattr(node, '__dict__') else node)

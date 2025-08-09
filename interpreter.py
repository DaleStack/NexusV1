from lexer import lexer
from parser import Parser, VarDecl, SayStmt, IfStmt, BinaryOp, Literal, VarRef

class Interpreter:
    def __init__(self):
        self.env = {}  # Stores variables

    def eval_expr(self, node):
        if isinstance(node, Literal):
            return node.value
        elif isinstance(node, VarRef):
            return self.env.get(node.name, None)
        elif isinstance(node, BinaryOp):
            # Handle unary 'not' operator
            if node.op == 'not':
                return not bool(self.eval_expr(node.right))
            
            # Handle binary operators
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)

            if node.op == '+': return left + right
            if node.op == '-': return left - right
            if node.op == '*': return left * right
            if node.op == '/': return left / right
            if node.op == '%': return left % right

            if node.op == '==': return left == right
            if node.op == '!=': return left != right
            if node.op == '<': return left < right
            if node.op == '>': return left > right
            if node.op == '<=': return left <= right
            if node.op == '>=': return left >= right

            if node.op == 'and': return bool(left) and bool(right)
            if node.op == 'or': return bool(left) or bool(right)

        else:
            raise RuntimeError(f"Unknown expression: {node}")

    def exec_stmt(self, node):
        if isinstance(node, VarDecl):
            self.env[node.name] = self.eval_expr(node.value) if node.value else None
        elif isinstance(node, SayStmt):
            print(self.eval_expr(node.expr))
        elif isinstance(node, IfStmt):
            if self.eval_expr(node.condition):
                for stmt in node.body:
                    self.exec_stmt(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.exec_stmt(stmt)
        else:
            raise RuntimeError(f"Unknown statement: {node}")

    def run(self, ast):
        for node in ast:
            self.exec_stmt(node)


if __name__ == "__main__":
    # Test with string concatenation first
    code1 = '''
    var name = "John"
    say("Hello, " + name)
    if name == "John":
        say("It's John")
    '''
    
    print("=== Test 1: String operations ===")
    tokens = lexer(code1)
    for token in tokens:
        print(token)
    
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)
    
    print("\n=== Test 2: Math operations ===")
    # Test with math operations
    code2 = """
    var x = 10
    var y = 3

    say(x + y)
    say(x - y) 
    say(x * y)
    say(x / y)
    say(x % y)

    if x > y and y != 0:
        say("Valid math")

    if not (x < y):
        say("x is not less than y")
    """
    
    tokens2 = lexer(code2)
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()

    interpreter2 = Interpreter()
    interpreter2.run(ast2)
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
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                return left / right
            elif node.op == '==':
                return left == right
            elif node.op == '!=':
                return left != right
            elif node.op == '>':
                return left > right
            elif node.op == '<':
                return left < right
            elif node.op == '>=':
                return left >= right
            elif node.op == '<=':
                return left <= right
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
    code = '''
    var name = "John"
    say("Hello, " + name)
    if name == "John":
        say("It's John")
    '''
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    interpreter.run(ast)

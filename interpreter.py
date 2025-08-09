from lexer import lexer
from parser import Parser, Literal, VarRef, BinaryOp, VarDecl, SayStmt, IfStmt


class Interpreter:
    def __init__(self):
        self.env = {}

    def eval_expr(self, node):
        if isinstance(node, Literal):
            return node.value
        elif isinstance(node, VarRef):
            if node.name in self.env:
                return self.env[node.name]
            else:
                raise NameError(f"Undefined variable '{node.name}'")
        elif isinstance(node, BinaryOp):
            left = self.eval_expr(node.left) if node.left else None
            right = self.eval_expr(node.right)
            op = node.op
            if op == "+":
                return left + right
            elif op == "-":
                return left - right
            elif op == "*":
                return left * right
            elif op == "/":
                return left / right
            elif op == "%":
                return left % right
            elif op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == "<":
                return left < right
            elif op == "<=":
                return left <= right
            elif op == ">":
                return left > right
            elif op == ">=":
                return left >= right
            elif op == "and":
                return left and right
            elif op == "or":
                return left or right
            elif op == "not":
                return not right
            else:
                raise ValueError(f"Unknown operator: {op}")
        else:
            raise TypeError(f"Unknown expression node: {node}")

    def exec_stmt(self, node):
        if isinstance(node, VarDecl):
            self.env[node.name] = self.eval_expr(node.value)
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
            raise TypeError(f"Unknown statement node: {node}")


    def run(self, ast):
        for stmt in ast:
            self.exec_stmt(stmt)


if __name__ == "__main__":
    code = '''
var name = "Bob"

if name == "John":
    say("It's John")
else if name == "Bob":
    say("It's Bob")
else:
    say("Someone else")
'''
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)

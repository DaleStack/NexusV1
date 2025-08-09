from lexer import lexer
from parser import Parser, Literal, VarRef, BinaryOp, VarDecl, SayStmt, IfStmt, ForStmt, BreakStmt, ContinueStmt, AskStmt


# Custom exceptions for control flow
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

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
                # Handle unary minus if left is None
                if left is None:
                    return -right
                else:
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
            # If the value is an AskStmt, perform input and assign result
            if isinstance(node.value, AskStmt):
                prompt = self.eval_expr(node.value.prompt_expr)
                user_input = input(str(prompt))
                self.env[node.name] = user_input
            else:
                self.env[node.name] = self.eval_expr(node.value)

        elif isinstance(node, SayStmt):
            print(self.eval_expr(node.expr))

        elif isinstance(node, IfStmt):
            if self.eval_expr(node.condition):
                for stmt in node.body:
                    self.exec_stmt(stmt)
            elif node.else_body:
                if isinstance(node.else_body, list):
                    for stmt in node.else_body:
                        self.exec_stmt(stmt)
                else:
                    self.exec_stmt(node.else_body)

        elif isinstance(node, ForStmt):
            self.exec_for(node)

        elif isinstance(node, BreakStmt):
            raise BreakException()

        elif isinstance(node, ContinueStmt):
            raise ContinueException()

        elif isinstance(node, AskStmt):
            # Standalone ask: prompt and ignore result
            prompt = self.eval_expr(node.prompt_expr)
            input(str(prompt))

        else:
            raise TypeError(f"Unknown statement node: {node}")



    def exec_for(self, node: ForStmt):
        if node.infinite:
            while True:
                try:
                    for stmt in node.body:
                        self.exec_stmt(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
        else:
            start = self.eval_expr(node.start)
            end = self.eval_expr(node.end)
            step = self.eval_expr(node.step)
            var = node.var_name

            if step == 0:
                raise ValueError("Step cannot be zero in for loop.")

            def loop_condition(i):
                if step > 0:
                    return i <= end if node.inclusive else i < end
                else:
                    return i >= end if node.inclusive else i > end

            i = start
            while loop_condition(i):
                self.env[var] = i
                try:
                    for stmt in node.body:
                        self.exec_stmt(stmt)
                except BreakException:
                    break
                except ContinueException:
                    i += step
                    continue
                i += step

    def run(self, ast):
        for stmt in ast:
            self.exec_stmt(stmt)


if __name__ == "__main__":
    code = '''
var a = ask("Enter First Name: ")
var b = ask("Enter Second Name: ")
say(a +" "+ b)
'''
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)

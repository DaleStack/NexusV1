from lexer import lexer
from parser import (
    Parser, Literal, VarRef, BinaryOp, VarDecl, SayStmt, IfStmt, ForStmt,
    BreakStmt, ContinueStmt, AskStmt, FuncDecl, FuncCall, ReturnStmt,
    ArrayLiteral, IndexExpr, AssignIndexStmt, ForEachStmt
)


# Custom exceptions for control flow
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def __getitem__(self, key):
        if key in self.vars:
            return self.vars[key]
        elif self.parent:
            return self.parent[key]
        else:
            raise NameError(f"Undefined variable '{key}'")

    def __setitem__(self, key, value):
        self.vars[key] = value

    def __contains__(self, key):
        if key in self.vars:
            return True
        elif self.parent:
            return key in self.parent
        else:
            return False


class Interpreter:
    def __init__(self):
        self.env = Env()          # global environment
        self.functions = {}       # function name -> FuncDecl node

    def eval_expr(self, node, env=None):
        if env is None:
            env = self.env

        if isinstance(node, Literal):
            return node.value

        elif isinstance(node, VarRef):
            if node.name in env:
                return env[node.name]
            else:
                raise NameError(f"Undefined variable '{node.name}'")

        elif isinstance(node, BinaryOp):
            left = self.eval_expr(node.left, env) if node.left else None
            right = self.eval_expr(node.right, env)
            op = node.op

            if op == "+":
                return left + right
            elif op == "-":
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

        elif isinstance(node, ArrayLiteral):
            # Evaluate each element into a list
            return [self.eval_expr(elem, env) for elem in node.elements]

        elif isinstance(node, IndexExpr):
            collection = self.eval_expr(node.collection, env)
            index = self.eval_expr(node.index, env)
            try:
                return collection[index]
            except Exception as e:
                raise RuntimeError(f"Index error: {e}")

        elif isinstance(node, FuncCall):
            return self.exec_func_call(node, env)

        else:
            raise TypeError(f"Unknown expression node: {node}")

    def exec_stmt(self, node, env=None):
        if env is None:
            env = self.env

        if isinstance(node, VarDecl):
            if isinstance(node.value, AskStmt):
                prompt = self.eval_expr(node.value.prompt_expr, env)
                user_input = input(str(prompt))
                env[node.name] = user_input
            elif node.value is not None:
                env[node.name] = self.eval_expr(node.value, env)
            else:
                # If declared as array but no value given, assign empty list
                if node.is_array:
                    env[node.name] = []
                else:
                    env[node.name] = None

        elif isinstance(node, AssignIndexStmt):
            collection = self.eval_expr(node.collection, env)
            index = self.eval_expr(node.index, env)
            value = self.eval_expr(node.value, env)

            try:
                collection[index] = value
            except Exception as e:
                raise RuntimeError(f"Assignment index error: {e}")

        elif isinstance(node, SayStmt):
            print(self.eval_expr(node.expr, env))

        elif isinstance(node, IfStmt):
            if self.eval_expr(node.condition, env):
                for stmt in node.body:
                    self.exec_stmt(stmt, env)
            elif node.else_body:
                if isinstance(node.else_body, list):
                    for stmt in node.else_body:
                        self.exec_stmt(stmt, env)
                else:
                    self.exec_stmt(node.else_body, env)

        elif isinstance(node, ForEachStmt):
            iterable = self.eval_expr(node.iterable_expr, env)
            for item in iterable:
                env[node.var_name] = item
                try:
                    for stmt in node.body:
                        self.exec_stmt(stmt, env)
                except BreakException:
                    break
                except ContinueException:
                    continue

        elif isinstance(node, ForStmt):
            self.exec_for(node, env)

        elif isinstance(node, BreakStmt):
            raise BreakException()

        elif isinstance(node, ContinueStmt):
            raise ContinueException()

        elif isinstance(node, AskStmt):
            prompt = self.eval_expr(node.prompt_expr, env)
            input(str(prompt))

        elif isinstance(node, FuncDecl):
            # Store function globally (only top-level supported)
            self.functions[node.name] = node

        elif isinstance(node, FuncCall):
            # Call function and ignore return value here
            self.exec_func_call(node, env)

        elif isinstance(node, ReturnStmt):
            value = self.eval_expr(node.expr, env) if node.expr else None
            raise ReturnException(value)

        else:
            raise TypeError(f"Unknown statement node: {node}")

    def exec_func_call(self, node, caller_env=None):
        if caller_env is None:
            caller_env = self.env

        if node.name not in self.functions:
            raise NameError(f"Undefined function '{node.name}'")
        func = self.functions[node.name]
        if len(node.args) != len(func.params):
            raise TypeError(f"Function '{node.name}' expects {len(func.params)} arguments, got {len(node.args)}")

        # Use global env as parent so functions can access global functions & variables
        local_env = Env(parent=self.env)

        for param, arg_expr in zip(func.params, node.args):
            value = self.eval_expr(arg_expr, caller_env)
            local_env[param] = value

        try:
            for stmt in func.body:
                self.exec_stmt(stmt, local_env)
        except ReturnException as ret:
            return ret.value
        return None

    def exec_for(self, node: ForStmt, env):
        if node.infinite:
            while True:
                try:
                    for stmt in node.body:
                        self.exec_stmt(stmt, env)
                except BreakException:
                    break
                except ContinueException:
                    continue
        else:
            start = self.eval_expr(node.start, env)
            end = self.eval_expr(node.end, env)
            step = self.eval_expr(node.step, env)
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
                env[var] = i
                try:
                    for stmt in node.body:
                        self.exec_stmt(stmt, env)
                except BreakException:
                    break
                except ContinueException:
                    i += step
                    continue
                i += step

    def run(self, ast):
        for stmt in ast:
            self.exec_stmt(stmt, self.env)


if __name__ == "__main__":
    code = '''
var fruits[] = ["Apple", "Orange", "Banana"]
var empty[] = []
var numbers[] int = [1, 2, 3]

fruits[2] = "Strawberry"

for fruit in fruits:
    say(fruit)

for number in numbers:
    say(number)

func greeting():
    say("Hello, people!")

greeting()
'''

    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)

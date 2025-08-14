from platform import node
from .lexer import lexer
from .parser import (
    Parser, Literal, SyntaxErrorWithContext, VarRef, BinaryOp, VarDecl, SayStmt, IfStmt, ForStmt,
    BreakStmt, ContinueStmt, AskStmt, FuncDecl, FuncCall, ReturnStmt,
    ArrayLiteral, IndexExpr, AssignIndexStmt, ForEachStmt, DictLiteral,
    StructDecl, StructInstantiation, MemberAccess, MemberAssignment,
    ClassDecl, MethodCall, ClassInstantiation, MethodDecl, SelfRef
)


# Custom exceptions for control flow
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class StructInstance:
    """Represents an instance of a struct"""
    def __init__(self, struct_name, fields):
        self.struct_name = struct_name
        self.fields = {}
        # Initialize fields with None or empty collections
        for field in fields:
            if field.is_array:
                self.fields[field.name] = []
            elif field.is_dict:
                self.fields[field.name] = {}
            else:
                self.fields[field.name] = None
    
    def __str__(self):
        return f"<struct {self.struct_name} instance>"

class ClassInstance:
    """Represents an instance of a class"""
    def __init__(self, class_name, class_decl, interpreter):
        self.class_name = class_name
        self.interpreter = interpreter
        self.fields = {}
        self.methods = {}
        
        # Initialize fields
        for field in class_decl.fields:
            if field.is_array:
                self.fields[field.name] = []
            elif field.is_dict:
                self.fields[field.name] = {}
            else:
                self.fields[field.name] = None
        
        # Store methods
        for method in class_decl.methods:
            self.methods[method.name] = method


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

    def define(self, key, value):
        """Define a variable in this environment"""
        self.vars[key] = value


class Interpreter:
    def __init__(self):
        self.env = Env()          # global environment
        self.functions = {}       # function name -> FuncDecl node
        self.var_types = {}       # Store variable type information
        self.classes = {}         # class name -> ClassDecl node
        self.structs = {}
        self.had_error = False
        self.current_line = 1    # Track error line


    def error(self, message, line=None, hint=None, context=None):
        """Raise a syntax error with friendly formatting"""
        self.had_error = True
        raise SyntaxErrorWithContext(
            message,
            line or self.current_line,
            hint,
            context
        )
        
    

    def check_type(self, var_name, value):
        """Check if value matches the declared type for variable"""
        if var_name not in self.var_types:
            return  # No type declared, allow anything
        
        expected_type = self.var_types[var_name]
        if expected_type is None:
            return  # No type constraint
            
        # Map your language types to Python types
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool
        }
        
        if expected_type in type_map:
            expected_python_type = type_map[expected_type]
            if not isinstance(value, expected_python_type):
                raise TypeError(f"Variable '{var_name}' expects {expected_type} but got {type(value).__name__}")

    def eval_expr(self, node, env=None):
        try:
            if env is None:
                env = self.env

            if isinstance(node, Literal):
                return node.value

            elif isinstance(node, VarRef):
                if node.name in env:
                    return env[node.name]
                else:
                    raise NameError(f"Undefined variable '{node.name}'")
            
            elif isinstance(node, SelfRef):
                # Handle 'self' keyword - should be in environment when in method context
                if "self" in env:
                    return env["self"]
                else:
                    raise NameError("'self' used outside of class method")
            
            elif isinstance(node, ClassInstantiation):
                # First attempt: check if class exists
                if node.class_name in self.classes:
                    class_decl = self.classes[node.class_name]
                    instance = ClassInstance(node.class_name, class_decl, self)

                    # Call init method if it exists
                    if "init" in instance.methods:
                        init_method = instance.methods["init"]
                        local_env = Env(parent=self.env)

                        # Add self reference
                        local_env["self"] = instance

                        # Check number of args
                        if len(node.args) != len(init_method.params):
                            raise TypeError(f"init method expects {len(init_method.params)} arguments, got {len(node.args)}")
                        # Evaluate and bind arguments
                        for param, arg in zip(init_method.params, node.args):
                            local_env[param] = self.eval_expr(arg, env)

                        try:
                            for stmt in init_method.body:
                                self.exec_stmt(stmt, local_env)
                        except ReturnException:
                            pass  # Init usually does not return
                    return instance

                # Fallback: if no class found, check if a struct exists with that name
                elif node.class_name in self.structs:
                    struct_decl = self.structs[node.class_name]
                    instance = StructInstance(struct_decl.name, struct_decl.fields)
                    return instance

                else:
                    raise NameError(f"Undefined class or struct '{node.class_name}'")
            
            elif isinstance(node, MemberAccess):
                # Handle obj.field access
                obj = self.eval_expr(node.object_expr, env)
                if isinstance(obj, (StructInstance, ClassInstance)):
                    if node.member_name in obj.fields:
                        return obj.fields[node.member_name]
                    else:
                        obj_type = "Class" if isinstance(obj, ClassInstance) else "Struct"
                        raise AttributeError(f"{obj_type} '{obj.class_name if isinstance(obj, ClassInstance) else obj.struct_name}' has no field '{node.member_name}'")
                else:
                    raise TypeError(f"Cannot access member '{node.member_name}' on {type(obj).__name__}")
            
            elif isinstance(node, StructInstantiation):
                if node.struct_name not in self.structs:
                    raise NameError(f"Undefined struct '{node.struct_name}'")
                
                struct_decl = self.structs[node.struct_name]
                instance = StructInstance(struct_decl.name, struct_decl.fields)
                return instance

            elif isinstance(node, BinaryOp):
                left = self.eval_expr(node.left, env) if node.left else None
                right = self.eval_expr(node.right, env)
                op = node.op

                if op == "+":
                    # Handle string concatenation with automatic type conversion
                    if isinstance(left, str) or isinstance(right, str):
                        return str(left) + str(right)
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

            elif isinstance(node, DictLiteral):
                # Evaluate dictionary literal into a Python dict
                result = {}
                for key_expr, value_expr in node.pairs:
                    key = self.eval_expr(key_expr, env)
                    value = self.eval_expr(value_expr, env)
                    result[key] = value
                return result

            elif isinstance(node, IndexExpr):
                collection = self.eval_expr(node.collection, env)
                index = self.eval_expr(node.index, env)
                try:
                    return collection[index]
                except Exception as e:
                    raise RuntimeError(f"Index error: {e}")

            elif isinstance(node, FuncCall):
                return self.exec_func_call(node, env)
            
            elif isinstance(node, MethodCall):
                # Handle method calls that return values
                obj = self.eval_expr(node.object_expr, env)
                method_name = node.method_name
                
                if isinstance(obj, ClassInstance):
                    if method_name in obj.methods:
                        method = obj.methods[method_name]
                        local_env = Env(parent=self.env)
                        
                        # Add self reference
                        local_env["self"] = obj
                        
                        # Add arguments
                        if len(node.args) != len(method.params):
                            raise TypeError(f"Method '{method_name}' expects {len(method.params)} arguments, got {len(node.args)}")
                        
                        for param, arg in zip(method.params, node.args):
                            local_env[param] = self.eval_expr(arg, env)
                        
                        try:
                            for stmt in method.body:
                                self.exec_stmt(stmt, local_env)
                        except ReturnException as ret:
                            return ret.value
                        return None
                    else:
                        raise AttributeError(f"Class '{obj.class_name}' has no method '{method_name}'")
                else:
                    raise TypeError(f"Cannot call method '{method_name}' on {type(obj).__name__}")

            else:
                raise TypeError(f"Unknown expression node: {node}")
        except SyntaxErrorWithContext:
            raise
        except NameError as e:
            self.error(
                str(e),
                getattr(node, 'line_number', None),
                "Make sure the variable is declared before use"
            )
        except TypeError as e:
            self.error(
                str(e),
                getattr(node, 'line_number', None),
                "Check that your types are compatible for this operation"
            )
        except Exception as e:
            self.error(
                f"Error evaluating expression: {str(e)}",
                getattr(node, 'line_number', None),
                "This might be a complex expression issue - try breaking it down"
            )
        

    def exec_stmt(self, node, env=None):
        try:
            if env is None:
                env = self.env
        
            if isinstance(node, ClassDecl):
                # Store class definition
                self.classes[node.name] = node
            
            elif isinstance(node, StructDecl):
                # Store struct definition
                self.structs[node.name] = node

            elif isinstance(node, MemberAssignment):
                # Handle obj.field = value - THIS IS THE KEY FIX
                obj = self.eval_expr(node.object_expr, env)
                value = self.eval_expr(node.value_expr, env)
                
                if isinstance(obj, (StructInstance, ClassInstance)):
                    # Always allow assignment to any field name, even if not explicitly declared
                    obj.fields[node.member_name] = value
                else:
                    raise TypeError(f"Cannot assign to member '{node.member_name}' on {type(obj).__name__}")

            elif isinstance(node, VarDecl):
                # Store type information if it exists
                if hasattr(node, 'var_type') and node.var_type:
                    self.var_types[node.name] = node.var_type
                
                if isinstance(node.value, AskStmt):
                    prompt = self.eval_expr(node.value.prompt_expr, env)
                    user_input = input(str(prompt))
                    self.check_type(node.name, user_input)
                    env[node.name] = user_input
                elif node.value is not None:
                    # Explicitly check for StructInstantiation
                    if isinstance(node.value, StructInstantiation):
                        if node.value.struct_name not in self.structs:
                            raise NameError(f"Undefined struct '{node.value.struct_name}'")
                        value = self.eval_expr(node.value, env)
                    else:
                        value = self.eval_expr(node.value, env)
                    
                    self.check_type(node.name, value)
                    env[node.name] = value
                else:
                    # Handle empty declarations
                    if node.is_array:
                        env[node.name] = []
                    elif node.is_dict:
                        env[node.name] = {}
                    else:
                        env[node.name] = None

            elif isinstance(node, AssignIndexStmt):
                if node.index is None:
                    # Simple variable assignment: var = value
                    value = self.eval_expr(node.value, env)
                    if isinstance(node.collection, VarRef):
                        var_name = node.collection.name
                        
                        # Check if we're in a class method context and trying to assign to a field
                        if "self" in env and isinstance(env["self"], ClassInstance):
                            self_instance = env["self"]
                            # If this variable name matches a field in the class, assign to the field instead
                            if var_name in self_instance.fields:
                                self_instance.fields[var_name] = value
                                return
                        
                        self.check_type(var_name, value)  # Check type on assignment
                        
                        # SIMPLE FIX: If variable exists in global scope, update it there
                        if var_name in self.env and env != self.env:
                            self.env[var_name] = value
                        else:
                            env[var_name] = value
                    elif isinstance(node.collection, MemberAccess):
                        # Handle member assignment like self.name = value when parsed as AssignIndexStmt
                        obj = self.eval_expr(node.collection.object_expr, env)
                        if isinstance(obj, (StructInstance, ClassInstance)):
                            obj.fields[node.collection.member_name] = value
                        else:
                            raise TypeError(f"Cannot assign to member '{node.collection.member_name}' on {type(obj).__name__}")
                    else:
                        raise RuntimeError("Invalid assignment target")
                else:
                    # Array/Dictionary index assignment: collection[index] = value
                    collection = self.eval_expr(node.collection, env)
                    index = self.eval_expr(node.index, env)
                    value = self.eval_expr(node.value, env)
                    try:
                        collection[index] = value
                    except Exception as e:
                        raise RuntimeError(f"Assignment index error: {e}")
            
            elif isinstance(node, MethodCall):
                # Handle method calls like obj.method(args) - when used as statements
                self.eval_expr(node, env)  # Use the eval_expr version

            elif isinstance(node, ClassInstantiation):
                # Handle class instantiation as a statement (shouldn't normally happen)
                return self.eval_expr(node, env)
                    
            elif isinstance(node, SayStmt):
                result = self.eval_expr(node.expr, env)
                print(result)

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
                
                # Handle dictionary iteration (iterate over keys)
                if isinstance(iterable, dict):
                    for key in iterable:
                        env[node.var_name] = key
                        try:
                            for stmt in node.body:
                                self.exec_stmt(stmt, env)
                        except BreakException:
                            break
                        except ContinueException:
                            continue
                # Handle list/array iteration
                elif isinstance(iterable, list):
                    for item in iterable:
                        env[node.var_name] = item
                        try:
                            for stmt in node.body:
                                self.exec_stmt(stmt, env)
                        except BreakException:
                            break
                        except ContinueException:
                            continue
                else:
                    raise RuntimeError(f"Cannot iterate over {type(iterable).__name__}")

            elif isinstance(node, ForStmt):
                self.exec_for(node, env)

            elif isinstance(node, BreakStmt):
                raise BreakException()

            elif isinstance(node, ContinueStmt):
                raise ContinueException()

            elif isinstance(node, AskStmt):
                prompt = self.eval_expr(node.prompt_expr, env)
                return input(str(prompt))

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
        except (BreakException, ContinueException):
            raise  # Re-raise control flow exceptions unchanged
        except SyntaxErrorWithContext:
            raise
        except NameError as e:
            self.error(
                str(e),
                getattr(node, 'line_number', None),
                "Make sure the variable is declared before use"
            )
        except TypeError as e:
            self.error(
                str(e),
                getattr(node, 'line_number', None),
                "Check that your types are compatible for this operation"
            )
        except Exception as e:
            self.error(
                f"Error executing statement: {str(e)}",
                getattr(node, 'line_number', None),
                "Check the statement syntax and surrounding context"
            )
        

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
                    pass  # Just continue to the increment
                i += step

    def run(self, ast):
        """Execute the AST while preserving parser error formatting"""
        try:
            for stmt in ast:
                self.current_line = getattr(stmt, 'line_number', None) or self.current_line
                self.exec_stmt(stmt)
        except SyntaxErrorWithContext:
            raise  # Re-raise parser errors unchanged
        except Exception as e:
            # Convert other errors to our friendly format
            self.error(
                f"Runtime error: {str(e)}",
                hint="This error occurred while executing your program",
                context=f"While executing {type(stmt).__name__} at line {self.current_line}"
            )


if __name__ == "__main__":
    # Debug test for init method
    test_code = '''
# Test 17: Structs
struct Point():
    var x int
    var y int

var p1 = Point()
p1.x = 10
p1.y = 20
say("Point coordinates: " + p1.x + ", " + p1.y)

# Test 18: Classes
class Animal():
    var type str
    var name str
    var age int
    var sound str
    
    func init(t, n, a, s):
        self.type = t
        self.name = n
        self.age = a
        self.sound = s
    
    func speak():
        say(self.sound + " I am " + self.name)

var dog = Animal("Dog", "Buddy", 3, "Woof Woof")
dog.speak()
'''

    try:
        # Lex and parse
        tokens = lexer(test_code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.run(ast)
        
    except SyntaxErrorWithContext as e:
        print(e)  # Will show the friendly formatted error
        exit(1)
from lexer import lexer

class SyntaxErrorWithContext(Exception):
    """Custom syntax error with friendly messaging and context"""
    def __init__(self, message, line_number=None, hint=None, context=None):
        self.message = message
        self.line_number = line_number
        self.hint = hint
        self.context = context
        super().__init__(self.format_error())
    
    def format_error(self):
        error_msg = f" Syntax Error"
        if self.line_number:
            error_msg += f" (Line {self.line_number})"
        error_msg += f":\n\n{self.message}"
        
        if self.context:
            error_msg += f"\n\n Context: {self.context}"
        
        if self.hint:
            error_msg += f"\n\n Hint: {self.hint}"
        
        error_msg += "\n\nDon't worry! These errors are part of learning. Keep going! "
        return error_msg

# AST Node classes (keeping all existing classes unchanged)
class VarDecl:
    def __init__(self, name, value, is_array=False, array_type=None, is_dict=False, dict_type=None, var_type=None):
        self.name = name
        self.value = value
        self.is_array = is_array
        self.array_type = array_type
        self.is_dict = is_dict
        self.dict_type = dict_type
        self.var_type = var_type

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
        self.var_name = var_name
        self.start = start
        self.end = end
        self.step = step
        self.body = body
        self.inclusive = inclusive
        self.infinite = infinite

class BreakStmt:
    pass

class ContinueStmt:
    pass

class AskStmt:
    def __init__(self, prompt_expr, var_name=None):
        self.prompt_expr = prompt_expr
        self.var_name = var_name

class FuncDecl:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnStmt:
    def __init__(self, expr):
        self.expr = expr

class ArrayLiteral:
    def __init__(self, elements):
        self.elements = elements

class IndexExpr:
    def __init__(self, collection, index):
        self.collection = collection
        self.index = index

class ForEachStmt:
    def __init__(self, var_name, iterable_expr, body):
        self.var_name = var_name
        self.iterable_expr = iterable_expr
        self.body = body

class AssignIndexStmt:
    def __init__(self, collection, index, value):
        self.collection = collection
        self.index = index
        self.value = value

class DictLiteral:
    def __init__(self, pairs):
        self.pairs = pairs

class StructDecl:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

class StructInstantiation:
    def __init__(self, struct_name, args=None):
        self.struct_name = struct_name
        self.args = args or []

class MemberAccess:
    def __init__(self, object_expr, member_name):
        self.object_expr = object_expr
        self.member_name = member_name

class MemberAssignment:
    def __init__(self, object_expr, member_name, value_expr):
        self.object_expr = object_expr
        self.member_name = member_name
        self.value_expr = value_expr

class ClassDecl:
    def __init__(self, name, fields, methods):
        self.name = name
        self.fields = fields
        self.methods = methods

class MethodDecl:
    def __init__(self, name, params, body, is_init=False):
        self.name = name
        self.params = params
        self.body = body
        self.is_init = is_init

class ClassInstantiation:
    def __init__(self, class_name, args=None):
        self.class_name = class_name
        self.args = args or []

class MethodCall:
    def __init__(self, object_expr, method_name, args):
        self.object_expr = object_expr
        self.method_name = method_name
        self.args = args

class SelfRef:
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.line_map = self._build_line_map()

    def _build_line_map(self):
        """Build a map of token positions to line numbers"""
        line_map = {}
        current_line = 1
        
        for i, (token_type, token_value) in enumerate(self.tokens):
            line_map[i] = current_line
            if token_type == "NEWLINE":
                current_line += 1
        
        return line_map

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def get_current_line(self):
        return self.line_map.get(self.pos, 1)

    def eat(self, kind=None, value=None):
        tok = self.current()
        line_num = self.get_current_line()
        
        if kind and tok[0] != kind:
            self._raise_friendly_error(
                f"Expected a {kind.lower()} token but found '{tok[1]}' instead",
                line_num,
                f"Make sure you're using the right syntax. If you meant to use a {kind.lower()}, check your spelling and placement.",
                f"Found '{tok[0]}' token with value '{tok[1]}'"
            )
        
        if value and tok[1] != value:
            self._raise_friendly_error(
                f"Expected '{value}' but found '{tok[1]}' instead",
                line_num,
                self._get_token_hint(value, tok[1]),
                f"Looking for '{value}' but got '{tok[1]}'"
            )
        
        self.pos += 1
        return tok

    def _get_token_hint(self, expected, found):
        """Provide helpful hints based on common mistakes"""
        hints = {
            "(": "Functions and method calls need opening parentheses. Did you forget to add '(' after the function name?",
            ")": "Make sure to close all parentheses. Every '(' needs a matching ')'.",
            "[": "Array access needs opening brackets. Are you trying to access an array element?",
            "]": "Make sure to close all brackets. Every '[' needs a matching ']'.",
            "{": "Dictionaries and code blocks need opening braces.",
            "}": "Make sure to close all braces. Every '{' needs a matching '}'.",
            ":": "Colons are needed after if statements, for loops, function definitions, and in dictionaries.",
            "=": "Use '=' for assignment. Did you mean to assign a value to a variable?",
            "==": "Use '==' for comparison. Did you mean to check if two values are equal?",
        }
        
        return hints.get(expected, f"Double-check your syntax. Expected '{expected}' but got '{found}'.")

    def _raise_friendly_error(self, message, line_number=None, hint=None, context=None):
        """Raise a friendly syntax error with helpful information"""
        raise SyntaxErrorWithContext(message, line_number, hint, context)

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            try:
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
                elif tok_type == "FUNC":
                    statements.append(self.parse_func_decl())
                elif tok_type == "STRUCT":
                    statements.append(self.parse_struct_decl())
                elif tok_type == "RETURN":
                    statements.append(self.parse_return())
                elif tok_type == "CLASS":
                    statements.append(self.parse_class_decl())
                elif tok_type == "ID":
                    statements.append(self.parse_statement_starting_with_id())
                elif tok_type == "NEWLINE":
                    self.eat("NEWLINE")
                else:
                    self.pos += 1
            except SyntaxErrorWithContext:
                raise  # Re-raise our custom errors
            except Exception as e:
                # Wrap any other errors in our friendly format
                self._raise_friendly_error(
                    f"Something unexpected happened while parsing",
                    self.get_current_line(),
                    "This might be a complex syntax issue. Try breaking your code into smaller parts to identify the problem.",
                    f"Internal error: {str(e)}"
                )
        return statements

    def parse_statement_starting_with_id(self):
        try:
            _, name = self.eat("ID")
            node = VarRef(name)

            while True:
                if self.current()[0] == "PUNCT" and self.current()[1] == "[":
                    self.eat("PUNCT", "[")
                    index_expr = self.parse_expression()
                    self.eat("PUNCT", "]")
                    node = IndexExpr(node, index_expr)
                elif self.current()[0] == "PUNCT" and self.current()[1] == ".":
                    self.eat("PUNCT", ".")
                    _, member_name = self.eat("ID")
                    node = MemberAccess(node, member_name)
                else:
                    break

            if self.current()[0] == "OP" and self.current()[1] == "=":
                self.eat("OP", "=")
                value_expr = self.parse_expression()
                if self.current()[0] == "NEWLINE":
                    self.eat("NEWLINE")
                
                if isinstance(node, MemberAccess):
                    return MemberAssignment(node.object_expr, node.member_name, value_expr)
                elif isinstance(node, IndexExpr):
                    return AssignIndexStmt(node.collection, node.index, value_expr)
                else:
                    return AssignIndexStmt(node, None, value_expr)
            
            elif self.current()[0] == "PUNCT" and self.current()[1] == "(":
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
                
                if isinstance(node, MemberAccess):
                    return MethodCall(node.object_expr, node.member_name, args)
                elif isinstance(node, VarRef):
                    return FuncCall(node.name, args)
                else:
                    self._raise_friendly_error(
                        "Invalid function or method call syntax",
                        self.get_current_line(),
                        "Make sure you're calling functions like 'myFunction()' or methods like 'object.method()'."
                    )
            
            elif self.current()[0] == "NEWLINE":
                self.eat("NEWLINE")
                return node
            
            else:
                self._raise_friendly_error(
                    f"Unexpected token '{self.current()[1]}' after identifier '{name}'",
                    self.get_current_line(),
                    "After a variable name, you can assign a value with '=', call it as a function with '()', or access its properties with '.'."
                )
        except SyntaxErrorWithContext:
            raise
        except Exception as e:
            self._raise_friendly_error(
                "Problem parsing statement that starts with an identifier",
                self.get_current_line(),
                "Check if you're trying to assign a value, call a function, or access an object property correctly."
            )

    def parse_var_decl(self):
        try:
            self.eat("VAR")
            _, name = self.eat("ID")

            is_array = False
            array_type = None
            is_dict = False
            dict_type = None
            var_type = None

            if self.current()[0] == "PUNCT" and self.current()[1] == "[":
                self.eat("PUNCT", "[")
                self.eat("PUNCT", "]")
                is_array = True
                if self.current()[0] == "TYPE":
                    _, array_type = self.eat("TYPE")
            
            elif self.current()[0] == "PUNCT" and self.current()[1] == "{":
                self.eat("PUNCT", "{")
                self.eat("PUNCT", "}")
                is_dict = True
                if self.current()[0] == "TYPE":
                    _, dict_type = self.eat("TYPE")
            
            elif self.current()[0] == "TYPE":
                _, var_type = self.eat("TYPE")

            value = None
            if self.current()[0] == "OP" and self.current()[1] == "=":
                self.eat("OP", "=")
                if self.current()[0] == "ASK":
                    value = self.parse_ask()
                else:
                    value = self.parse_expression()

            return VarDecl(name, value, is_array=is_array, array_type=array_type, 
                        is_dict=is_dict, dict_type=dict_type, var_type=var_type)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with variable declaration",
                self.get_current_line(),
                "Variable declarations should look like: 'var myVar = value' or 'var myArray[] = [1, 2, 3]'"
            )

    def parse_say(self):
        try:
            self.eat("SAY")
            self.eat("PUNCT", "(")
            expr = self.parse_expression()
            self.eat("PUNCT", ")")
            return SayStmt(expr)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with say statement",
                self.get_current_line(),
                "Say statements should look like: say(\"Hello World\") or say(myVariable)"
            )

    def parse_if(self):
        try:
            self.eat("IF")
            condition = self.parse_expression()
            self.eat("PUNCT", ":")
            self.eat("NEWLINE")
            self.eat("INDENT")
            body = self.parse_block()
            else_body = None

            if self.current()[0] == "ELSE":
                self.eat("ELSE")
                if self.current()[0] == "IF":
                    else_body = self.parse_if()
                else:
                    self.eat("PUNCT", ":")
                    self.eat("NEWLINE")
                    self.eat("INDENT")
                    else_body = self.parse_block()

            return IfStmt(condition, body, else_body)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with if statement",
                self.get_current_line(),
                "If statements should look like: 'if condition:' followed by an indented block"
            )

    def parse_expression_until(self, stop_tokens):
        expr_tokens = []
        paren_count = 0

        while True:
            tok = self.current()
            if tok == (None, None):
                break

            if tok in stop_tokens and paren_count == 0:
                break

            if tok[0] == "PUNCT":
                if tok[1] == "(":
                    paren_count += 1
                elif tok[1] == ")":
                    if paren_count == 0:
                        break
                    paren_count -= 1

            expr_tokens.append(tok)
            self.pos += 1

        temp_parser = Parser(expr_tokens)
        expr = temp_parser.parse_expression()
        return expr

    def parse_for(self):
        try:
            self.eat("FOR")

            if self.current()[0] == "PUNCT" and self.current()[1] == ":":
                self.eat("PUNCT", ":")
                self.eat("NEWLINE")
                self.eat("INDENT")
                body = self.parse_block()
                return ForStmt(None, None, None, None, body, infinite=True)

            if self.current()[0] != "ID":
                self._raise_friendly_error(
                    "For loops need a variable name after 'for'",
                    self.get_current_line(),
                    "Try: 'for i in (1 to 10 by 1):' or 'for item in myArray:'"
                )
            _, var_name = self.eat("ID")

            if self.current()[0] != "IN":
                self._raise_friendly_error(
                    "Expected 'in' after the for loop variable",
                    self.get_current_line(),
                    "For loops need 'in': 'for variable in something:'"
                )
            self.eat("IN")

            if self.current()[0] == "PUNCT" and self.current()[1] == "(":
                self.eat("PUNCT", "(")

                inclusive = False
                if self.current()[0] == "INCLUSIVE":
                    self.eat("INCLUSIVE")
                    inclusive = True

                start = self.parse_expression_until([("TO", "to")])

                if self.current()[0] != "TO":
                    self._raise_friendly_error(
                        "Expected 'to' in for loop range",
                        self.get_current_line(),
                        "Numeric for loops need 'to': for i in (1 to 10 by 1):"
                    )
                self.eat("TO")

                end = self.parse_expression_until([("BY", "by"), ("PUNCT", ")")])

                step = Literal(1)
                if self.current()[0] == "BY":
                    self.eat("BY")
                    step = self.parse_expression_until([("PUNCT", ")")])

                if self.current()[0] != "PUNCT" or self.current()[1] != ")":
                    self._raise_friendly_error(
                        "Missing closing parenthesis in for loop range",
                        self.get_current_line(),
                        "Make sure to close your range with ')': for i in (1 to 10 by 1):"
                    )
                self.eat("PUNCT", ")")

                self.eat("PUNCT", ":")
                self.eat("NEWLINE")
                self.eat("INDENT")
                body = self.parse_block()

                return ForStmt(var_name, start, end, step, body, inclusive=inclusive)
            
            else:
                iterable_expr = self.parse_expression()
                self.eat("PUNCT", ":")
                self.eat("NEWLINE")
                self.eat("INDENT")
                body = self.parse_block()
                return ForEachStmt(var_name, iterable_expr, body)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with for loop",
                self.get_current_line(),
                "For loops should look like 'for i in (1 to 10 by 1):' or 'for item in myArray:'"
            )

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
        try:
            self.eat("ASK")
            self.eat("PUNCT", "(")
            prompt_expr = self.parse_expression()
            self.eat("PUNCT", ")")
            return AskStmt(prompt_expr)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with ask statement",
                self.get_current_line(),
                "Ask statements should look like: ask(\"What's your name?\")"
            )

    def parse_return(self):
        self.eat("RETURN")
        expr = None
        if self.current()[0] != "NEWLINE":
            expr = self.parse_expression()
        if self.current()[0] == "NEWLINE":
            self.eat("NEWLINE")
        return ReturnStmt(expr)

    def parse_func_decl(self):
        try:
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
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with function declaration",
                self.get_current_line(),
                "Functions should look like: 'func myFunction(param1, param2):' followed by an indented block"
            )

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
    
    def parse_class_decl(self):
        try:
            self.eat("CLASS")
            _, name = self.eat("ID")
            
            self.eat("PUNCT", "(")
            self.eat("PUNCT", ")")
            self.eat("PUNCT", ":")
            self.eat("NEWLINE")
            self.eat("INDENT")
            
            fields = []
            methods = []
            
            while self.current()[0] != "DEDENT":
                if self.current()[0] == "VAR":
                    fields.append(self.parse_var_decl())
                elif self.current()[0] == "FUNC":
                    methods.append(self.parse_method_decl())
                elif self.current()[0] == "NEWLINE":
                    self.eat("NEWLINE")
                else:
                    self._raise_friendly_error(
                        f"Unexpected token '{self.current()[1]}' in class body",
                        self.get_current_line(),
                        "Class bodies can only contain variable declarations (var) and method definitions (func)"
                    )
            
            self.eat("DEDENT")
            return ClassDecl(name, fields, methods)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with class declaration",
                self.get_current_line(),
                "Classes should look like: 'class MyClass():' followed by an indented block with variables and methods"
            )

    def parse_method_decl(self):
        self.eat("FUNC")
        _, name = self.eat("ID")
        
        is_init = (name == "init")
        
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
        
        return MethodDecl(name, params, body, is_init)

    def parse_array_literal(self):
        try:
            self.eat("PUNCT", "[")
            elements = []
            if not (self.current()[0] == "PUNCT" and self.current()[1] == "]"):
                while True:
                    elem = self.parse_expression()
                    elements.append(elem)
                    if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                        self.eat("PUNCT", ",")
                    else:
                        break
            self.eat("PUNCT", "]")
            return ArrayLiteral(elements)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with array literal",
                self.get_current_line(),
                "Arrays should look like: [1, 2, 3] or [\"apple\", \"banana\"]"
            )

    def skip_whitespace_tokens(self):
        while self.current()[0] in ("NEWLINE", "INDENT", "DEDENT"):
            self.eat()

    def parse_dict_literal(self):
        try:
            self.eat("PUNCT", "{")
            pairs = []
            
            self.skip_whitespace_tokens()
            
            if self.current()[0] == "PUNCT" and self.current()[1] == "}":
                self.eat("PUNCT", "}")
                return DictLiteral(pairs)
            
            while True:
                self.skip_whitespace_tokens()
                
                if self.current()[0] == "PUNCT" and self.current()[1] == "}":
                    break
                
                key_expr = self.parse_expression()
                self.skip_whitespace_tokens()
                
                if not (self.current()[0] == "PUNCT" and self.current()[1] == ":"):
                    self._raise_friendly_error(
                        "Missing ':' after dictionary key",
                        self.get_current_line(),
                        "Dictionary entries need a colon between key and value: {\"key\": \"value\"}"
                    )
                self.eat("PUNCT", ":")
                
                self.skip_whitespace_tokens()
                
                value_expr = self.parse_expression()
                pairs.append((key_expr, value_expr))
                
                self.skip_whitespace_tokens()
                
                if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                    self.eat("PUNCT", ",")
                    self.skip_whitespace_tokens()
                    if self.current()[0] == "PUNCT" and self.current()[1] == "}":
                        break
                else:
                    break
            
            self.eat("PUNCT", "}")
            return DictLiteral(pairs)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with dictionary literal",
                self.get_current_line(),
                "Dictionaries should look like: {\"key\": \"value\", \"name\": \"John\"}"
            )
    
    def parse_struct_decl(self):
        try:
            self.eat("STRUCT")
            _, name = self.eat("ID")
            self.eat("PUNCT", "(")
            self.eat("PUNCT", ")")
            self.eat("PUNCT", ":")
            self.eat("NEWLINE")
            self.eat("INDENT")
            
            fields = []
            while self.current()[0] not in ("DEDENT", None):
                if self.current()[0] == "VAR":
                    fields.append(self.parse_var_decl())
                elif self.current()[0] == "NEWLINE":
                    self.eat("NEWLINE")
                else:
                    self._raise_friendly_error(
                        "Only variable declarations allowed in struct",
                        self.get_current_line(),
                        "Structs can only contain variable declarations like: var name str"
                    )
            
            self.eat("DEDENT")
            return StructDecl(name, fields)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem with struct declaration",
                self.get_current_line(),
                "Structs should look like: 'struct Person():' followed by variable declarations"
            )

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
            elif tok_type == "FUNC":
                statements.append(self.parse_func_decl())
            elif tok_type == "RETURN":
                statements.append(self.parse_return())
            elif tok_type == "ID":
                statements.append(self.parse_statement_starting_with_id())
            elif tok_type == "NEWLINE":
                self.eat("NEWLINE")
            else:
                self.pos += 1
        self.eat("DEDENT")
        return statements

    # Expression parsing methods
    def parse_expression(self):
        try:
            return self.parse_or()
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem parsing expression",
                self.get_current_line(),
                "Check your expression syntax. Make sure parentheses are balanced and operators are used correctly."
            )

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
            return BinaryOp(None, "-", right)
        else:
            return self.parse_primary()

    def parse_primary(self):
        try:
            tok_type, tok_value = self.current()

            if tok_type == "PUNCT" and tok_value == "(":
                self.eat("PUNCT", "(")
                expr = self.parse_expression()
                self.eat("PUNCT", ")")
                return expr

            elif tok_type == "PUNCT" and tok_value == "[":
                return self.parse_array_literal()

            elif tok_type == "PUNCT" and tok_value == "{":
                return self.parse_dict_literal()

            elif tok_type in ("NUMBER", "STRING"):
                self.eat()
                return Literal(tok_value)
            
            elif tok_type == "BOOLEAN":
                self.eat()
                bool_value = tok_value.lower() == 'true'
                return Literal(bool_value)
            
            elif tok_type == "SELF" or (tok_type == "ID" and tok_value == "self"):
                self.eat(tok_type)
                node = SelfRef()
                
                while True:
                    if self.current()[0] == "PUNCT" and self.current()[1] == ".":
                        self.eat("PUNCT", ".")
                        _, member = self.eat("ID")
                        
                        if self.current()[0] == "PUNCT" and self.current()[1] == "(":
                            node = self.parse_method_call(node, member)
                        else:
                            node = MemberAccess(node, member)
                    else:
                        break
                
                return node

            elif tok_type == "ID":
                self.eat()
                if self.current()[0] == "PUNCT" and self.current()[1] == "(":
                    return self.parse_call_or_instantiation(tok_value)
                node = VarRef(tok_value)
                
                # Handle array indexing, member access and method calls
                while True:
                    if self.current()[0] == "PUNCT" and self.current()[1] == "[":
                        # Array indexing: var[index]
                        self.eat("PUNCT", "[")
                        index_expr = self.parse_expression()
                        self.eat("PUNCT", "]")
                        node = IndexExpr(node, index_expr)
                    elif self.current()[0] == "PUNCT" and self.current()[1] == ".":
                        self.eat("PUNCT", ".")
                        _, member = self.eat("ID")
                        
                        if self.current()[0] == "PUNCT" and self.current()[1] == "(":
                            node = self.parse_method_call(node, member)
                        else:
                            node = MemberAccess(node, member)
                    else:
                        break
                
                return node

            else:
                self._raise_friendly_error(
                    f"Unexpected token '{tok_value}' of type {tok_type}",
                    self.get_current_line(),
                    "Expected a value, variable name, function call, or expression in parentheses."
                )
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                "Problem parsing primary expression",
                self.get_current_line(),
                "This could be a variable, number, string, function call, or expression in parentheses."
            )

    def parse_call_or_instantiation(self, name):
        try:
            self.eat("PUNCT", "(")
            args = []
            if self.current()[0] != "PUNCT" or self.current()[1] != ")":
                while True:
                    args.append(self.parse_expression())
                    if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                        self.eat("PUNCT", ",")
                    else:
                        break
            self.eat("PUNCT", ")")
            
            if name[0].isupper():
                return ClassInstantiation(name, args)
            return FuncCall(name, args)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                f"Problem with function call or class instantiation '{name}'",
                self.get_current_line(),
                "Make sure function calls look like: myFunction(arg1, arg2)"
            )
    
    def parse_method_call(self, obj, method_name):
        try:
            self.eat("PUNCT", "(")
            args = []
            if self.current()[0] != "PUNCT" or self.current()[1] != ")":
                while True:
                    args.append(self.parse_expression())
                    if self.current()[0] == "PUNCT" and self.current()[1] == ",":
                        self.eat("PUNCT", ",")
                    else:
                        break
            self.eat("PUNCT", ")")
            return MethodCall(obj, method_name, args)
        except SyntaxErrorWithContext:
            raise
        except Exception:
            self._raise_friendly_error(
                f"Problem with method call '{method_name}'",
                self.get_current_line(),
                "Method calls should look like: object.methodName(arg1, arg2)"
            )

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


# Test the enhanced parser with friendly error handling
if __name__ == "__main__":
    from lexer import lexer
    
    test_code = '''

'''
    
    print("=== TESTING ENHANCED PARSER WITH ERROR HANDLING ===")
    tokens = lexer(test_code)
    
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("\nPARSING SUCCESSFUL!")
        print(f"Generated {len(ast)} AST nodes:")
        
        for i, node in enumerate(ast):
            print(f"  {i}: {node.__class__.__name__}")
                
    except SyntaxErrorWithContext as e:
        print(f"\n{e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
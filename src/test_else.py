from .lexer import lexer
from .parser import Parser
from .interpreter import Interpreter

code = '''
for i in (0 to 5 by 1):
    say(i)


'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

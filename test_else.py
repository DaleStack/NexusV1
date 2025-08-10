from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''

'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

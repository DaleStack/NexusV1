from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var fruits[] str = ["Apple", "Orange", "Banana"]

for fruit in fruits:
    say(fruit)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

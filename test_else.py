from lexer import lexer
from parser import Parser
from interpreter import Interpreter

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

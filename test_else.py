from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var a = ask("Enter name: ")

func greetName(name):
    say("Hello, "+name)

greetName(a)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

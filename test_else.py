from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var a = ask("Enter number ")
var b = ask("Enter number ")

func greetName(c, d):
    say(c + d)

greetName(a, b)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

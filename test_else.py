from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var firstName = ask("What is your first name? ")
var secondName = ask("What is your second name? ")

say(firstName + " " + secondName)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

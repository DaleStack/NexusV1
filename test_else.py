from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var city = "Cavite"

if city != "Cavite":
    say("You are not in Cavite or Manila")
else if city == "Manila":
    say("You are in manila")
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

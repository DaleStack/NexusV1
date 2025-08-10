from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var fruits[] = ["Apple", "Orange", "Banana"]

for i in (0 to 5 by 1):
    say(i)

fruits[2] = "Strawberry"    
for fruit in fruits:
    say(fruit)

var name = "Casey"

say(name)

'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

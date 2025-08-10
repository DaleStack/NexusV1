from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var fruits[] = ["Apple", "Orange", "Banana"]

func readFruit():
    for fruit in fruits:
        say(fruit)
readFruit()

fruits[2] = "Strawberry"

readFruit()

say(fruits[0])
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

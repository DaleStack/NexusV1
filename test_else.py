from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var Car{} = {
    "name": "Corvette"
}
for key in Car:
    say(Car[key])
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
# This is a test comment
var test = ask("name: ")

var Person{} = {
    "name": test,
    "age": 18,
    "locale": "Cavite"
}

say(Person["age"])

for key in Person:
    say(key + ": " + Person[key])
    
say(6%4)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

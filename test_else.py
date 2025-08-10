from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''

var test = ask("name: ")

var Person{} = {
    "name": test,
    "age": 18,
    "locale": "Cavite"
}

say(Person["age"])

for key in Person:
    say(key + ": " + Person[key])
    

'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

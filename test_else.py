from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var name = "Kei"

say(2*4)

if name == "John":
    say("It's John")
else if name == "Bob":
    say("It's Bob")
else if name == "Kei":
    say("Hello my creator!")
else: 
    say("Someone else")
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

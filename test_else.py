from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
struct Dog():
    var name str
    var age int

var pet1 = Dog()
pet1.name = 1
pet1.age = "2"

say(pet1.name)
say(pet1.age)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

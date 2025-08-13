from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
struct Dog():
    var name str
    var age int

var pet1 = Dog()
pet1.name = "Buddy"
pet1.age = 5

say(pet1.name)
say(pet1.age)

class Person():
    var name str

    func init(n):
        self.name = n
    
    func say_name():
        say("Hello, I am "+self.name)

var Me = Person("Kei")
Me.say_name()
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

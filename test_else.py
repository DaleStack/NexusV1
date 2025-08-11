from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
class Dog():
    var name str
    var age int

    func bark():
        say(self.name + " barks at you!")

var pet1 = Dog()
pet1.name = "Buddy"
pet1.age = 3
pet1.bark()

class Cat():
    var name str
    var age int

    func init(n, a):
        self.name = n
        self.age = a
    
    func meow():
        say(self.name + " meows at you!")

var pet2 = Cat("Navi", 1)
pet2.meow()


'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

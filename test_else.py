from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
struct Dog():
    var name str
    var age int
    var isGoodBoy bool

struct Person():
    var firstName str
    var lastName str
    var pet

var myPet = Dog()
myPet.name = "Buddy"
myPet.age = 3
myPet.isGoodBoy = true

var owner = Person()
owner.firstName = "John"
owner.lastName = "Doe"
owner.pet = myPet

say(myPet.name + " is " + myPet.age + " years old!")
say("Is " + myPet.name + " a good boy? " + myPet.isGoodBoy)
say(owner.firstName + " " + owner.lastName + " owns " + owner.pet.name)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

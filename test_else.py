from lexer import lexer
from parser import Parser
from interpreter import Interpreter

code = '''
var isMember = False

say("You are not a member of this group")
var answer = ask("Do you want to be a member?")

func register():
    isMember = True

func checkMember(state):
    if state == True:
        say("You are now a member")
    else: 
        say("You are not a member")

if answer == "Yes" or answer == "yes":
    register()
else:
    say("Be a member next time")

checkMember(isMember)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

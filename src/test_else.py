from .lexer import lexer
from .parser import Parser
from .interpreter import Interpreter

code = '''
# Test 8: Basic for loop
say("Counting up:")
for i in (0 to 5 by 1):
    say(i)

# Test 9: Inclusive loop
say("Inclusive count:")
for i in (inclusive 0 to 5 by 1):
    say(i)

# Test 10: Reverse loop
say("Countdown:")
for i in (5 to 0 by -1):
    say(i)

say("Skipping 2:")
for i in (0 to 5 by 1):
    if i == 2:
        continue
    say(i)    

# Test 11: Loop control
say("Breaking at 3:")
for i in (0 to 5 by 1):
    if i == 3:
        break
    say(i)
'''

tokens = lexer(code)
parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
interpreter.run(ast)

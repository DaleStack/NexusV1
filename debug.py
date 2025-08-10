from lexer import lexer
from parser import Parser
from interpreter import Interpreter

# Test all boolean logic cases
test_code = '''
var isMember = True
var age = 20
var city = "Manila"

say("=== Testing Basic Boolean ===")
say(isMember)
say(not isMember)

say("=== Testing NOT Logic ===")
if not isMember:
    say("You should sign up")
else:
    say("Welcome member!")

say("=== Testing AND Logic ===")
if isMember and age > 18:
    say("Adult member access granted")
else:
    say("Access denied")

say("=== Testing OR Logic ===") 
if city == "Manila" or city == "Cavite":
    say("You're in Luzon!")
else:
    say("You're somewhere else")

say("=== Testing Complex Logic ===")
if (age > 18 and isMember) or city == "Manila":
    say("Complex condition met")
else:
    say("Complex condition failed")

say("=== Testing False Cases ===")
var notMember = False
if not notMember:
    say("This should print (not False = True)")

if notMember or age > 25:
    say("This should not print (False or False)")
else:
    say("This should print (else branch)")
'''

print("=== COMPLETE SYSTEM TEST ===")

try:
    # Step 1: Tokenize
    print("1. Tokenizing...")
    tokens = lexer(test_code)
    print(f"   ✓ Generated {len(tokens)} tokens")
    
    # Step 2: Parse
    print("2. Parsing...")
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"   ✓ Generated AST with {len(ast)} statements")
    
    # Step 3: Execute
    print("3. Executing...")
    print("-" * 40)
    interpreter = Interpreter()
    interpreter.run(ast)
    print("-" * 40)
    print("   ✓ Execution completed successfully!")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
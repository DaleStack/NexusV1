from lexer import lexer
from parser import Parser
from interpreter import Interpreter

# Test code
code = '''
var city = "Cavite"

if city != "Cavite":
    say("You are not in Cavite or Manila")
else if city == "Manila":
    say("You are in manila")
'''

print("=== DEBUGGING SCRIPT ===")

# Step 1: Test lexer
print("1. Testing Lexer:")
try:
    tokens = lexer(code)
    print(f"   Tokens generated: {len(tokens)}")
    for i, token in enumerate(tokens):
        print(f"   {i}: {token}")
    print("   Lexer: OK")
except Exception as e:
    print(f"   Lexer ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit()

# Step 2: Test parser
print("\n2. Testing Parser:")
try:
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"   AST generated: {len(ast)} statements")
    for i, node in enumerate(ast):
        print(f"   {i}: {node.__class__.__name__}")
        if hasattr(node, '__dict__'):
            for key, value in vars(node).items():
                print(f"      {key}: {value}")
    print("   Parser: OK")
except Exception as e:
    print(f"   Parser ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit()

# Step 3: Test interpreter
print("\n3. Testing Interpreter:")
try:
    interpreter = Interpreter()
    print("   Starting interpretation...")
    interpreter.run(ast)
    print("   Interpreter: OK")
except Exception as e:
    print(f"   Interpreter ERROR: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Test simple cases
print("\n4. Testing Simple Cases:")

# Test 1: Simple variable and say
print("   Test 1: Simple variable assignment and say")
simple_code1 = '''
var city = "Cavite"
say(city)
'''
try:
    tokens1 = lexer(simple_code1)
    parser1 = Parser(tokens1)
    ast1 = parser1.parse()
    interpreter1 = Interpreter()
    interpreter1.run(ast1)
    print("   Test 1: OK")
except Exception as e:
    print(f"   Test 1 ERROR: {e}")

# Test 2: Simple comparison
print("   Test 2: Simple comparison")
simple_code2 = '''
var city = "Cavite"
say(city != "Manila")
'''
try:
    tokens2 = lexer(simple_code2)
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()
    interpreter2 = Interpreter()
    interpreter2.run(ast2)
    print("   Test 2: OK")
except Exception as e:
    print(f"   Test 2 ERROR: {e}")

# Test 3: Simple if statement
print("   Test 3: Simple if statement")
simple_code3 = '''
var city = "Cavite"
if city == "Cavite":
    say("You are in Cavite")
'''
try:
    tokens3 = lexer(simple_code3)
    parser3 = Parser(tokens3)
    ast3 = parser3.parse()
    interpreter3 = Interpreter()
    interpreter3.run(ast3)
    print("   Test 3: OK")
except Exception as e:
    print(f"   Test 3 ERROR: {e}")

print("\n=== END DEBUG ===")
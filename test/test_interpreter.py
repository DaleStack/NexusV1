import pytest # type: ignore
import sys
import os
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.nexus.interpreter import Interpreter
from src.nexus.parser import Parser
from src.nexus.lexer import lexer

class TestInterpreterBasicOperations:
    """Test basic interpreter operations"""
    
    def test_variable_assignment(self):
        code = '''var a = 5
say(a)'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "5"
    
    def test_arithmetic_operations(self):
        code = '''var result = (10 + 5) * 2
say(result)'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "30"
    
    def test_string_concatenation(self):
        code = '''var name = "World"
say("Hello, " + name)'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "Hello, World"

class TestControlFlow:
    """Test control flow statements"""
    
    def test_if_statement(self):
        code = '''var a = 10
if a > 5:
    say("Greater")
else:
    say("Smaller")'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "Greater"
    
    def test_for_loop(self):
        code = '''for i in (0 to 3 by 1):
    say(i)'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().splitlines() == ["0", "1", "2"]

class TestFunctions:
    """Test function execution"""
    
    def test_function_call(self):
        code = '''func greet(name):
    say("Hello, " + name)
greet("Alice")'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "Hello, Alice"
    
    def test_function_return(self):
        code = '''func add(a, b):
    return a + b
var result = add(3, 4)
say(result)'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().strip() == "7"

class TestDataStructures:
    """Test data structure operations"""
    
    def test_array_operations(self):
        code = '''var fruits[] = ["Apple", "Banana"]
fruits[1] = "Orange"
say(fruits[0])
say(fruits[1])'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().splitlines() == ["Apple", "Orange"]
    
    def test_dictionary_operations(self):
        code = '''var person{} = {"name": "Alice"}
person["age"] = 30
say(person["name"])
say(person["age"])'''
        interpreter = Interpreter()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.run(Parser(lexer(code)).parse())
            assert fake_out.getvalue().splitlines() == ["Alice", "30"]


class TestBuiltins:
    """Test built-in functions"""
    
    def test_ask_input(self):
        code = 'var name = ask("Your name?")'
        interpreter = Interpreter()
        with patch('builtins.input', return_value="Alice"):
            interpreter.run(Parser(lexer(code)).parse())
            assert interpreter.env["name"] == "Alice"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
import pytest #type: ignore
from src.lexer import lexer, TOKEN_SPEC, KEYWORDS, OPERATORS

class TestBasicTokens:
    """Test basic token recognition"""
    
    def test_numbers(self):
        tokens = lexer("42 3.14")
        assert tokens[0] == ("NUMBER", 42)
        assert tokens[1] == ("NUMBER", 3.14)
    
    def test_strings(self):
        
        tokens = lexer('"hello" \'world\'')
        assert tokens[0] == ("STRING", "hello")
        assert tokens[1] == ("STRING", "'world'")
        
        tokens2 = lexer('"test string"')
        assert tokens2[0] == ("STRING", "test string")
    
    def test_identifiers(self):
        tokens = lexer("myVar _private var123")
        assert tokens[0] == ("ID", "myVar")
        assert tokens[1] == ("ID", "_private") 
        assert tokens[2] == ("ID", "var123")
    
    def test_operators(self):
        tokens = lexer("+ - * / == != >= <= and or not")
        expected_ops = ["+", "-", "*", "/", "==", "!=", ">=", "<=", "and", "or", "not"]
        for i, op in enumerate(expected_ops):
            assert tokens[i] == ("OP", op)
    
    def test_punctuation(self):
        tokens = lexer("(){[]}:,.")
        expected_punct = ["(", ")", "{", "[", "]", "}", ":", ",", "."]
        for i, punct in enumerate(expected_punct):
            assert tokens[i] == ("PUNCT", punct)

class TestKeywords:
    """Test keyword recognition"""
    
    def test_control_keywords(self):
        tokens = lexer("if else for break continue")
        assert tokens[0] == ("IF", "if")
        assert tokens[1] == ("ELSE", "else") 
        assert tokens[2] == ("FOR", "for")
        assert tokens[3] == ("BREAK", "break")
        assert tokens[4] == ("CONTINUE", "continue")
    
    def test_function_keywords(self):
        tokens = lexer("func return var")
        assert tokens[0] == ("FUNC", "func")
        assert tokens[1] == ("RETURN", "return")
        assert tokens[2] == ("VAR", "var")
    
    def test_io_keywords(self):
        tokens = lexer("say ask")
        assert tokens[0] == ("SAY", "say")
        assert tokens[1] == ("ASK", "ask")
    
    def test_boolean_keywords(self):
        tokens = lexer("True false")
        assert tokens[0] == ("BOOLEAN", "True")
        assert tokens[1] == ("BOOLEAN", "false")
    
    def test_struct_keywords(self):
        tokens = lexer("struct class self")
        assert tokens[0] == ("STRUCT", "struct")
        assert tokens[1] == ("CLASS", "class") 
        assert tokens[2] == ("SELF", "self")
    
    def test_type_keywords(self):
        tokens = lexer("int str bool float")
        assert tokens[0] == ("TYPE", "int")
        assert tokens[1] == ("TYPE", "str")
        assert tokens[2] == ("TYPE", "bool")
        assert tokens[3] == ("TYPE", "float")

class TestIndentation:
    """Test indentation handling"""
    
    def test_simple_indent(self):
        code = "if True:\n    say('hello')"
        tokens = lexer(code)
        # Should have: IF, BOOLEAN, :, NEWLINE, INDENT, SAY, (, STRING, ), DEDENT
        assert ("IF", "if") in tokens 
        assert ("BOOLEAN", "True") in tokens
        assert ("INDENT", 4) in tokens
        assert ("DEDENT", 0) in tokens
    
    def test_nested_indentation(self):
        code = """if True:
    if False:
        say('nested')
    say('back')
"""
        tokens = lexer(code)
        indent_tokens = [t for t in tokens if t[0] in ("INDENT", "DEDENT")]
        assert ("INDENT", 4) in indent_tokens
        assert ("INDENT", 8) in indent_tokens
        assert ("DEDENT", 4) in indent_tokens
        assert ("DEDENT", 0) in indent_tokens

class TestStructSyntax:
    """Test struct-specific syntax"""
    
    def test_struct_definition(self):
        code = "struct Dog():"
        tokens = lexer(code)
        assert tokens[0] == ("STRUCT", "struct")
        assert tokens[1] == ("ID", "Dog")
        assert tokens[2] == ("PUNCT", "(")
        assert tokens[3] == ("PUNCT", ")")
        assert tokens[4] == ("PUNCT", ":")
    
    def test_member_access(self):
        code = "myPet.name"
        tokens = lexer(code)
        assert tokens[0] == ("ID", "myPet")
        assert tokens[1] == ("PUNCT", ".")
        assert tokens[2] == ("ID", "name")
    
    def test_complete_struct_example(self):
        code = '''struct Dog():
    var name str
    var age int

var myPet = Dog()
myPet.name = "Buddy"
'''
        tokens = lexer(code)
        
        # Check key tokens are present
        token_values = [t[1] for t in tokens]
        assert "struct" in token_values
        assert "Dog" in token_values
        assert "name" in token_values
        assert "str" in token_values
        assert "myPet" in token_values
        assert "Buddy" in token_values

class TestComments:
    """Test comment handling"""
    
    def test_comment_ignored(self):
        code = "var x = 5  # This is a comment"
        tokens = lexer(code)
        # Comments should be filtered out
        token_types = [t[0] for t in tokens]
        assert "COMMENT" not in token_types
        assert ("VAR", "var") in tokens
        assert ("ID", "x") in tokens

class TestWhitespace:
    """Test whitespace handling"""
    
    def test_whitespace_skipped(self):
        code = "var    x   =   5"
        tokens = lexer(code)
        # Whitespace should be skipped except for indentation
        token_types = [t[0] for t in tokens]
        assert "SKIP" not in token_types
        assert len([t for t in tokens if t[0] in ("VAR", "ID", "OP", "NUMBER")]) == 4

class TestErrorHandling:
    """Test error cases"""
    
    def test_invalid_character(self):
        with pytest.raises(SyntaxError, match="Unexpected character"):
            lexer("var x = $invalid")

class TestOperatorPrecedence:
    """Test that operators are correctly identified"""
    
    def test_logical_operators_as_ops(self):
        code = "x and y or not z"
        tokens = lexer(code)
        assert tokens[1] == ("OP", "and")
        assert tokens[3] == ("OP", "or") 
        assert tokens[4] == ("OP", "not")

class TestComplexExpressions:
    """Test more complex token combinations"""
    
    def test_function_call(self):
        code = 'say("Hello, World!")'
        tokens = lexer(code)
        assert tokens[0] == ("SAY", "say")
        assert tokens[1] == ("PUNCT", "(")
        assert tokens[2] == ("STRING", "Hello, World!")
        assert tokens[3] == ("PUNCT", ")")
    
    def test_for_loop(self):
        code = "for i in range(10):"
        tokens = lexer(code)
        assert tokens[0] == ("FOR", "for")
        assert tokens[1] == ("ID", "i")
        assert tokens[2] == ("IN", "in")
        assert tokens[3] == ("ID", "range")
    
    def test_variable_assignment(self):
        code = "var myNum int = 42"
        tokens = lexer(code)
        assert tokens[0] == ("VAR", "var")
        assert tokens[1] == ("ID", "myNum")
        assert tokens[2] == ("TYPE", "int")
        assert tokens[3] == ("OP", "=")
        assert tokens[4] == ("NUMBER", 42)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
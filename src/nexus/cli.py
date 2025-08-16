#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from nexus.lexer import lexer
from nexus.parser import Parser
from nexus.interpreter import Interpreter

def validate_file_extension(file_path):
    """Validate the file has .nx extension"""
    if not file_path.lower().endswith('.nx'):
        raise ValueError("Nexus scripts must have .nx extension")

def run_script(file_path):
    """Execute a NexusV1 .nx script file"""
    try:
        validate_file_extension(file_path)
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        tokens = lexer(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.run(ast)
        
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing script: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main CLI entry point for NexusV1 interpreter"""
    parser = argparse.ArgumentParser(
        prog='nexus',
        description='NexusV1 Language Interpreter (.nx files)',
        epilog='Example: nexus sample.nx'
    )
    
    # Make script argument optional when -v is used
    parser.add_argument(
        'script',
        metavar='SCRIPT.nx',
        nargs='?',  # Makes this argument optional
        help='NexusV1 script file to execute (must have .nx extension)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='show version information'
    )
    
    args = parser.parse_args()
    
    if args.version:
        from nexus import __version__
        print(f"NexusV1 v{__version__}")
        sys.exit(0)
        
    if not args.script:
        parser.print_help()
        sys.exit(1)
        
    run_script(args.script)

if __name__ == "__main__":
    main()
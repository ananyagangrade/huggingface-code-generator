# generator/validator.py
import ast

def validate_python(code: str):
    try:
        ast.parse(code)
        return True, "Valid Python Syntax"
    except SyntaxError as e:
        return False, f"invalid syntax: {e}"


def validate_js(code: str):
    try:
        from pyjsparser import PyJsParser
        parser = PyJsParser()
        parser.parse(code)
        return True, "Valid JS Syntax"
    except Exception as e:
        return False, str(e)

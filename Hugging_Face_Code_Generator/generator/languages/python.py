# generator/languages/python.py
from generator.prompts import function_prompt, class_prompt, api_prompt
from generator.formatter import format_python
from generator.validator import validate_python

class PythonLanguage:
    name = "python"

    @staticmethod
    def build_prompt(description, mode):
        if mode == "function":
            return function_prompt(description, "python")
        elif mode == "class":
            return class_prompt(description, "python")
        elif mode == "api":
            return api_prompt(description, "python")
        else:
            raise ValueError("Unsupported mode for Python")

    @staticmethod
    def format(code):
        return format_python(code)

    @staticmethod
    def validate(code):
        return validate_python(code)

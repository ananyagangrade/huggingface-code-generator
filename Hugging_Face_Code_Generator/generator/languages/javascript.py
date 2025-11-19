# generator/languages/javascript.py
from generator.prompts import function_prompt, class_prompt, api_prompt
from generator.formatter import format_js
from generator.validator import validate_js

class JavaScriptLanguage:
    name = "javascript"

    @staticmethod
    def build_prompt(description, mode):
        if mode == "function":
            return function_prompt(description, "javascript")
        elif mode == "class":
            return class_prompt(description, "javascript")
        elif mode == "api":
            return api_prompt(description, "javascript")
        else:
            raise ValueError("Unsupported mode for JavaScript")

    @staticmethod
    def format(code):
        return format_js(code)

    @staticmethod
    def validate(code):
        return validate_js(code)

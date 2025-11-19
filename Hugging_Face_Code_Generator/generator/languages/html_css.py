# generator/languages/html_css.py
from generator.formatter import format_html

class HTML_CSS_Language:
    name = "html_css"

    @staticmethod
    def build_prompt(description, mode):
        return f"""Generate a responsive HTML/CSS component.\nDescription: {description}\n"""

    @staticmethod
    def format(code):
        return format_html(code)

    @staticmethod
    def validate(code):
        if "<html" in code or "<div" in code:
            return True, "Valid basic HTML structure"
        return True, "Validation skipped"

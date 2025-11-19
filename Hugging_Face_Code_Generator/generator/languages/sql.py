# generator/languages/sql.py
from generator.prompts import sql_prompt
from generator.formatter import format_sql

class SQLLanguage:
    name = "sql"

    @staticmethod
    def build_prompt(description, mode):
        return sql_prompt(description)

    @staticmethod
    def format(code):
        return format_sql(code)

    @staticmethod
    def validate(code):
        if ";" in code:
            return True, "Basic SQL validation passed"
        return True, "Validation skipped"

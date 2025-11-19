# main.py (final)
import argparse
import sys
import traceback
import os
import re

from generator.validator import validate_python, validate_js
from generator.formatter import format_python, format_js, postprocess_and_format
from generator.prompts import function_prompt, class_prompt, api_prompt, test_prompt, sql_prompt

# Try to import the real model; if it fails, use a dummy fallback so main.py still produces output.
USE_REAL_MODEL = True
try:
    from generator.models import CodeGenModel
except Exception as e:
    print("Warning: Could not import CodeGenModel from generator.models. Falling back to dummy generator.")
    print("Import error:", e)
    USE_REAL_MODEL = False


# Dummy model used when the real model can't be loaded.
class DummyModel:
    def __init__(self, *args, **kwargs):
        pass

    def generate(self, prompt, max_new_tokens=256, temperature=0.0, top_p=1.0):
        # Very simple heuristic: check prompt keywords to return plausible code.
        p = prompt.lower()
        if ("def add" in p) or (("python" in p) and ("function" in p)) or ("def " in p and "add" in p):
            return (
                "def add(a: int, b: int) -> int:\n"
                "    \"\"\"Return the sum of two integers.\"\"\"\n"
                "    return a + b\n"
            )
        elif "class" in p:
            return (
                "class Person:\n"
                "    def __init__(self, name: str, age: int):\n"
                "        self.name = name\n"
                "        self.age = age\n\n"
                "    def greet(self) -> str:\n"
                "        return f'Hello, my name is {self.name}'\n"
            )
        elif "pytest" in p or "unit test" in p or "test_" in p:
            return (
                "def test_add_positive():\n"
                "    assert add(1, 2) == 3\n\n"
                "def test_add_zero():\n"
                "    assert add(0, 5) == 5\n\n"
                "def test_add_negative():\n"
                "    assert add(-1, -2) == -3\n"
            )
        elif "select" in p or "from" in p or "where" in p:
            return (
                "SELECT id, username, last_login\nFROM users\nWHERE last_login >= '2024-01-01'\nORDER BY last_login DESC\nLIMIT 5;"
            )
        elif "express" in p or "api" in p or "fastapi" in p:
            return (
                "from fastapi import FastAPI\n\n"
                "app = FastAPI()\n\n"
                "@app.get('/health')\n"
                "def health():\n"
                "    return {'status': 'ok'}\n"
            )
        else:
            # Generic placeholder code
            return (
                "# Generated placeholder\n"
                "def placeholder():\n"
                "    '''This is a placeholder output from DummyModel.'''\n"
                "    return None\n"
            )


class CodeGenerator:
    # Use environment variable CODEGEN_MODEL if set, otherwise default to a public HF model
    DEFAULT_MODEL = os.getenv("CODEGEN_MODEL", "Salesforce/codegen-350M-multi")

    def __init__(self, model_name: str = None):
        model_name = model_name or self.DEFAULT_MODEL

        if USE_REAL_MODEL:
            try:
                self.model = CodeGenModel(model_name)
                print(f"Loaded real model: {model_name}")
            except Exception:
                print("Failed to initialize real model, switching to DummyModel. Error:")
                traceback.print_exc()
                self.model = DummyModel()
        else:
            self.model = DummyModel()

    def generate(self, description, mode="function", lang="python", max_new_tokens=256):
        """Build prompt, call model, sanitize/format the result and provide
        a safe deterministic fallback if the model output is empty or invalid."""

        # Build prompt mapping
        if mode == "function":
            prompt = function_prompt(description, lang)
        elif mode == "class":
            prompt = class_prompt(description, lang)
        elif mode == "api":
            prompt = api_prompt(description, lang)
        elif mode == "test":
            prompt = test_prompt(description, lang)
        else:
            prompt = function_prompt(description, lang)

        # For SQL language, override prompt to sql_prompt
        if lang.lower() == "sql" or mode == "sql":
            prompt = sql_prompt(description)

        # Generate raw code (handle both real model and DummyModel signatures)
        try:
            raw = self.model.generate(prompt, max_new_tokens=max_new_tokens, temperature=0.0, top_p=1.0)
        except TypeError:
            raw = self.model.generate(prompt)

        # Post-process: sanitize, format, validate
        try:
            formatted, valid, msg = postprocess_and_format(raw, lang=lang)
        except Exception:
            formatted, valid, msg = raw, False, "Postprocess error"

        # If sanitizer removed everything or validation failed, make deterministic fallback for python
        if (not formatted) or (lang == "python" and not valid):
            import ast

            # infer a simple function name
            fname = None
            m = re.search(r"def\s+([A-Za-z_]\w*)\s*\(", description)
            if m:
                fname = m.group(1)
            else:
                m2 = re.search(r"named\s+([A-Za-z_]\w*)", description)
                if m2:
                    fname = m2.group(1)
            if not fname:
                m3 = re.search(r"function\s+that\s+([a-zA-Z ]+)", description, flags=re.I)
                if m3:
                    words = re.sub(r"[^a-zA-Z ]", "", m3.group(1)).strip().split()
                    if words:
                        fname = words[0]
            if not fname:
                fname = "generated_function"

            # detect number of args heuristically
            args = ["a", "b"]
            m_args = re.search(r"takes\s+(\d+)\s+arguments|takes\s+(\d+)\s+parameters", description, flags=re.I)
            if m_args:
                try:
                    n = int(m_args.group(1) or m_args.group(2))
                    args = [f"arg{i+1}" for i in range(max(1, n))]
                except Exception:
                    args = ["a", "b"]

            # choose body based on keywords
            if re.search(r"add|sum|plus|total", description, flags=re.I):
                if len(args) >= 2:
                    body = f"return {args[0]} + {args[1]}"
                else:
                    body = f"return {args[0]}"
            elif re.search(r"factorial", description, flags=re.I):
                a0 = args[0]
                body = (
                    f"if {a0} < 2:\n"
                    f"        return 1\n"
                    f"    result = 1\n"
                    f"    for i in range(2, {a0}+1):\n"
                    f"        result *= i\n"
                    f"    return result"
                )
            else:
                body = "return None"

            arg_list = ", ".join(args)
            fallback = f"def {fname}({arg_list}):\n    {body}\n"

            # try formatting fallback
            try:
                formatted_fallback = format_python(fallback)
            except Exception:
                formatted_fallback = fallback

            # validate fallback strictly
            try:
                ast.parse(formatted_fallback)
                return {
                    "prompt": description,
                    "lang": lang,
                    "formatted_code": formatted_fallback,
                    "valid": True,
                    "validation_msg": "Valid (fallback) Python code",
                }
            except Exception:
                # if fallback invalid for any reason, return best-effort sanitized output
                return {
                    "prompt": description,
                    "lang": lang,
                    "formatted_code": formatted or raw,
                    "valid": False,
                    "validation_msg": "Fallback generation failed to produce valid code",
                }

        # Normal return: model output usable
        return {
            "prompt": description,
            "lang": lang,
            "formatted_code": formatted,
            "valid": valid,
            "validation_msg": msg,
        }


def run_demo():
    print(">>> Running demo generate (safe mode).")
    cg = CodeGenerator()
    demo_prompt = (
        "You are an expert Python developer. Output ONLY valid Python 3 code (no explanation).\n"
        "Write a function with signature: def add(a: int, b: int) -> int:\n"
        "Return the sum of the two numbers. Return only code, no surrounding text or markdown fences."
    )
    print("Prompt:", demo_prompt)
    res = cg.generate(demo_prompt, mode="function", lang="python")
    print("\n--- Generated (formatted) code ---\n")
    print(res["formatted_code"])
    print("\nValidation:", res["valid"], "-", res["validation_msg"]) 


def run_cli(description, lang="python", mode="function"):
    print(">>> CLI generate")
    cg = CodeGenerator()
    print(f"Description: {description}\nLanguage: {lang}  Mode: {mode}")
    res = cg.generate(description, mode=mode, lang=lang)
    print("\n--- Generated (formatted) code ---\n")
    print(res["formatted_code"])
    print("\nValidation:", res["valid"], "-", res["validation_msg"]) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodeGen Assistant - main entry")
    parser.add_argument("--demo", action="store_true", help="Run a small demo generation")
    parser.add_argument("--desc", type=str, help="Description of code to generate (CLI mode)")
    parser.add_argument("--lang", type=str, default="python", help="Language: python/javascript/sql/html_css")
    parser.add_argument("--mode", type=str, default="function", help="Mode: function/class/api/test")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        sys.exit(0)

    if args.desc:
        run_cli(args.desc, lang=args.lang, mode=args.mode)
        sys.exit(0)

    print("No action specified. Try one of the following:")
    print("  python main.py --demo")
    print('  python main.py --desc "Create a factorial function" --lang python --mode function')
    print("\nExiting.")

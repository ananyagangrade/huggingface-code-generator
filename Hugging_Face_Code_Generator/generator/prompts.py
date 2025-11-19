# generator/prompts.py

def function_prompt(description: str, lang: str = "python") -> str:
    # A strict, short prompt for function generation
    if lang.lower() == "python":
        return (
            "You are an expert Python developer. Output ONLY valid Python 3 code (no explanation).\n"
            "Write a function with signature exactly as described.\n"
            f"Description: {description}\n"
        )
    else:
        return f"You are an expert {lang} developer. Output ONLY code. Description: {description}\n"


def class_prompt(description: str, lang: str = "python") -> str:
    if lang.lower() == "python":
        return (
            "You are an expert Python developer. Output ONLY valid Python 3 code (no explanation).\n"
            "Write a class as described.\n"
            f"Description: {description}\n"
        )
    else:
        return f"You are an expert {lang} developer. Output ONLY code. Description: {description}\n"


def api_prompt(description: str, lang: str = "python") -> str:
    if lang.lower() == "python":
        return (
            "You are an expert Python developer. Output ONLY valid Python 3 code for an API endpoint (no explanation).\n"
            "Write a small API scaffold as described.\n"
            f"Description: {description}\n"
        )
    else:
        return f"You are an expert {lang} developer. Output ONLY code. Description: {description}\n"


def test_prompt(description: str, lang: str = "python") -> str:
    """
    Prompt to ask the model to generate unit tests for the described function/module.
    """
    if lang.lower() == "python":
        return (
            "You are an expert Python developer and test engineer. "
            "Output ONLY pytest-compatible Python unit tests (no explanation).\n"
            f"Target: {description}\n"
            "Write concise, deterministic unit tests that cover edge cases and typical cases. "
            "Use simple inputs and assert exact outputs. Use only code (no markdown).\n"
        )
    else:
        return (
            f"You are an expert {lang} developer and test engineer. Output ONLY tests for {lang} "
            f"(no explanation). Target: {description}\n"
        )


def sql_prompt(description: str) -> str:
    return (
        "You are an SQL expert. Output ONLY a single optimized SQL query (no explanation).\n"
        f"Description: {description}\n"
        "Prefer readable formatting and avoid vendor-specific functions unless requested."
    )

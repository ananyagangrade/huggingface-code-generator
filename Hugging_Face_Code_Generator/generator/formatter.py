# generator/formatter.py
import re
import ast

def format_python(code: str) -> str:
    try:
        import black
        mode = black.Mode()
        return black.format_str(code, mode=mode)
    except Exception:
        return code


def format_js(code: str) -> str:
    try:
        import subprocess, tempfile, os
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8")
        tf.write(code)
        tf.flush()
        tf.close()
        subprocess.run(["prettier", "--write", tf.name], check=False)
        with open(tf.name, "r", encoding="utf-8") as f:
            out = f.read()
        try:
            os.unlink(tf.name)
        except Exception:
            pass
        return out
    except Exception:
        return code


def format_sql(code: str) -> str:
    try:
        import sqlparse
        formatted = sqlparse.format(code, reindent=True, keyword_case='upper')
        return formatted
    except Exception:
        return code


def sanitize_code(raw: str) -> str:
    import re
    # 1) If there's a fenced code block, extract it
    m = re.search(r"```(?:python)?\n(.*?)```", raw, flags=re.S | re.I)
    if m:
        code = m.group(1)
    else:
        # find first sensible code start
        idxs = []
        for pattern in [r"\ndef\s", r"\nclass\s", r"\nfrom\s", r"\nimport\s", r"^def\s", r"^class\s"]:
            mm = re.search(pattern, raw, flags=re.I)
            if mm:
                idxs.append(mm.start())
        if idxs:
            start = min(idxs)
            code = raw[start:].lstrip()
        else:
            code = raw

    # collapse consecutive duplicate lines
    lines = code.splitlines()
    cleaned_lines = []
    prev = None
    for ln in lines:
        if ln.strip() == prev:
            continue
        cleaned_lines.append(ln)
        prev = ln.strip()
    code = "\n".join(cleaned_lines).strip()

    # remove unterminated triple quotes
    if code.count('"""') % 2 == 1:
        code = code.replace('"""', '')
    if code.count("'''") % 2 == 1:
        code = code.replace("'''", '')

    # drop leading natural-language lines until a code-like line
    code_lines = code.splitlines()
    i = 0
    while i < len(code_lines):
        ln = code_lines[i].lstrip()
        if ln.startswith(("def ", "class ", "import ", "from ", "@")) or re.match(r"[a-zA-Z_]\w*\s*=", ln):
            break
        i += 1
    code = "\n".join(code_lines[i:]).strip()
    return code


def postprocess_and_format(raw: str, lang: str = "python"):
    code = sanitize_code(raw)
    if not code:
        return raw, False, "Empty after sanitization"

    if lang == "python":
        try:
            ast.parse(code)
            valid = True
            msg = "Valid Python Syntax"
        except SyntaxError as e:
            # try light cleanup attempts
            lines = code.splitlines()
            while lines and re.match(r"^[-._]{2,}$", lines[0].strip()):
                lines.pop(0)
            code_try = "\n".join(lines).strip()
            try:
                ast.parse(code_try)
                code = code_try
                valid = True
                msg = "Valid after light cleanup"
            except SyntaxError:
                valid = False
                msg = f"invalid syntax: {e}"
        if valid:
            try:
                formatted = format_python(code)
            except Exception:
                formatted = code
        else:
            formatted = code
        return formatted, valid, msg
    else:
        return code, True, "No validation implemented for this language"

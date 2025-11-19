# Hugging Face Code Generator

A code generation assistant built using Hugging Face CodeGen models. This project automatically generates functions, classes, API endpoints, test cases, SQL queries, and HTML templates from natural language descriptions. Includes syntax validation, formatting, and a simple CLI for easy usage.

## Features
- Function generation from natural language descriptions
- Class and module scaffolding
- API endpoint (FastAPI/Express) templates
- Test case (pytest) generation
- SQL query builder and HTML/CSS templates
- Formatting and syntax validation (Python, JS/TS, SQL)
- CLI tool for quick generation
- Safe fallback generator if model unavailable

## Quickstart (local)
```bash
# optional: create venv
python -m venv .venv
.venv\Scripts\activate     # Windows PowerShell
pip install -r requirements.txt

# Run demo
python main.py --demo

# Generate from description
python main.py --desc "Write a function that returns factorial" --lang python --mode function

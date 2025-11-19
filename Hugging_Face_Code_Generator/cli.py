# cli.py
import argparse
from main import CodeGenerator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("description", type=str, nargs="?")
    parser.add_argument("--lang", default="python")
    parser.add_argument("--type", default="function")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    cg = CodeGenerator()

    if args.demo:
        print("Running demo from CLI")
        cg.generate("Write a Python function that adds two numbers.", mode="function", lang="python")
        return

    if not args.description:
        print("Provide a description or use --demo")
        return

    res = cg.generate(args.description, mode=args.type, lang=args.lang)
    print(res["formatted_code"])

if __name__ == "__main__":
    main()

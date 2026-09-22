import ast
import os
import sys

def check_file(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"SyntaxError in {path}: {e}")
        print(f"Line: {e.lineno}")
        print(f"Offset: {e.offset}")
        print(f"Text: {e.text}")
        return False
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return False

def main() -> int:
    files = sys.argv[1:]
    if not files:
        files = []
        for root, _, filenames in os.walk("src"):
            for fname in filenames:
                if fname.endswith(".py"):
                    files.append(os.path.join(root, fname))

    has_errors = False
    for f in files:
        if not check_file(f):
            has_errors = True

    if not has_errors:
        print(f"Syntax OK: {len(files)} files checked.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())


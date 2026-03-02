import ast
import sys

file_path = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX\src\presentacion_reflex\pages\recaudos.py"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("Syntax OK")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    print(f"Line: {e.lineno}")
    print(f"Offset: {e.offset}")
    print(f"Text: {e.text}")
except Exception as e:
    print(f"Error: {e}")

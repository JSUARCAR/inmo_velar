import reflex as rx
val = rx.color("blue", 9)
print(f"Has _js_expr: {hasattr(val, '_js_expr')}")
if hasattr(val, '_js_expr'):
    print(f"_js_expr: {val._js_expr}")

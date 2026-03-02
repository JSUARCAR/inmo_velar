import reflex as rx
val = rx.color("blue", 9)
print(f"Type: {type(val)}")
try:
    print(f"Cached var name: {val._cached_var_name}")
except AttributeError:
    print("No _cached_var_name")
try:
    print(f"String: {str(val)}")
except Exception as e:
    print(f"Error str: {e}")

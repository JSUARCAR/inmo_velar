import reflex as rx
prop = rx.Var.create({'key': '123'})
c = rx.Var.create('Text: ') + prop['key'].to(str)
print('Render prop to(str):', c._var_value if hasattr(c, '_var_value') else 'none')
try:
  print(c._js_expr)
except Exception as e:
  print('ERROR in to(str):', type(e).__name__)

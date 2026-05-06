import reflex as rx
var = rx.Var.create('test')
try:
  a = 'A' + var
except Exception as e: print('Failed +:', e)
try:
  b = f'B{var}'
  print('f-string:', type(b))
except Exception as e: print('Failed f-string:', type(e).__name__)
try:
  c = rx.Var.create('C') + var
  print('Var + Var:', type(c))
except Exception as e: print('Failed Var+:', e)

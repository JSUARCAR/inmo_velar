import reflex as rx
var = rx.Var.create('test')
try:
  c = rx.Var.create('C') + var
  print('SUCCESS:', type(c))
except Exception as e:
  print('ERROR:', e)

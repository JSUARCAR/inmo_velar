import reflex as rx
prop = rx.Var.create({'codigo_energia': '123'})
try:
  c = rx.Var.create('Energía: ') + prop['codigo_energia'].to(str)
  print('SUCCESS:', type(c))
except Exception as e:
  print('ERROR:', e)

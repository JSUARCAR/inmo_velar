import reflex as rx
class S(rx.State):
  v: bool = True
try:
  comp = rx.card('hello', color_scheme=rx.cond(S.v, 'green', 'red'))
  print('Render card:', comp.render())
except Exception as e:
  print('ERROR:', type(e).__name__)

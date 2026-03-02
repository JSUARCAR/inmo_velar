import reflex as rx
class S(rx.State):
  v: str = 'a'
try:
  c = rx.cond(S.v == 'a', 'green', 'red')
  print('Color 3:', rx.color(c, 3))
except Exception as e:
  print('ERROR:', type(e).__name__)

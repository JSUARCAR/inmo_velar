import reflex as rx
class S(rx.State):
  v: bool = True
try:
  comp = rx.icon(rx.cond(S.v, 'circle_alert', 'info'))
  print('Render icon:', comp.render())
except Exception as e:
  print('ERROR:', type(e).__name__)

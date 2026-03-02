import reflex as rx
class S(rx.State):
  items: list[int] = [1,2,3]
comp = rx.foreach(S.items, lambda i: rx.icon('shield-alert', tooltip='Hello'))
try:
  print('Render tooltip:', comp.render())
except Exception as e:
  print('ERROR:', type(e).__name__)

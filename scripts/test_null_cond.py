import reflex as rx
class S(rx.State):
  v: bool = False
comp = rx.cond(S.v, rx.hover_card.root(rx.hover_card.content(None)))
try:
  print('Render cond:', comp.render())
except Exception as e:
  print('ERROR:', type(e).__name__)

import reflex as rx
try:
  a = rx.hover_card.content(None)
  print('Render null child:', a.render())
except Exception as e:
  print('ERROR:', type(e).__name__)

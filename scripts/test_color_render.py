import reflex as rx
class S(rx.State):
  v: str = 'a'
comp = rx.box(bg=rx.color(rx.cond(S.v == 'a', 'green', 'red'), 3))
print('Render:', comp.render())
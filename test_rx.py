import reflex as rx

class State(rx.State):
    my_list: list[dict] = [{"val": 10}]

def comp():
    return rx.foreach(
        State.my_list,
        lambda i: rx.cond(i['val'].to(int) <= 30, rx.text('a'), rx.text('b'))
    )

print("Test passed.")

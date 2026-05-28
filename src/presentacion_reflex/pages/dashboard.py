import reflex as rx

@rx.page(route="/dashboard", title="Panel")
def dashboard():
    return rx.center(
        rx.vstack(
            rx.heading("Dashboard Simple"),
            rx.text("Aislamiento completo de componentes."),
            spacing="4",
        ),
        height="100vh",
    )

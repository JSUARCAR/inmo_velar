import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout

@rx.page(route="/dashboard", title="Panel")
def dashboard():
    return dashboard_layout(
        rx.vstack(
            rx.heading("Dashboard con Layout"),
            rx.text("Probando sidebar y estructura."),
            spacing="4",
        )
    )

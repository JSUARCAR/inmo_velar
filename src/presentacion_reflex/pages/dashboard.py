import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex import styles

def dashboard_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Dashboard Minimalista - Modo Diagnóstico"),
            rx.text("Si ves esto, el ruteo y el renderizado básico funcionan."),
            rx.button("Cargar Datos (Prueba)", on_click=rx.window_alert("Evento OK")),
            rx.link("Volver al Login", href="/login"),
            spacing="4",
            align="center",
        ),
        height="100vh",
        width="100%",
    )

@rx.page(
    route="/dashboard",
    title="Panel | Diagnóstico",
)
def dashboard():
    return dashboard_page()

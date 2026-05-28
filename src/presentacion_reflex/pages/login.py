import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex import styles

def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("INMOBILIARIA VELAR S.A.S"),
            rx.text("MODO DE SEGURIDAD ACTIVADO"),
            rx.form(
                rx.vstack(
                    rx.input(placeholder="Usuario", name="username"),
                    rx.input(placeholder="Contraseña", name="password", type="password"),
                    rx.button("Acceder", type="submit", width="100%"),
                    spacing="4",
                ),
                on_submit=AuthState.login,
            ),
            spacing="6",
            padding="10",
            border="1px solid gray",
            border_radius="16px",
        ),
        height="100vh",
        width="100%",
    )

@rx.page(route="/login", title="Login | Velar")
def login():
    return login_page()

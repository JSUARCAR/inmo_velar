import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState


def login_page() -> rx.Component:
    """
    Página de Login Premium.
    Diseño moderno con tarjeta flotante y fondo de gradiente.
    """
    return rx.center(
        rx.vstack(
            # Logo / Título
            rx.heading("Inmobiliaria Velar", size="8", weight="bold", color="white"),
            rx.text("Gestión Integral de Propiedades", color="rgba(255,255,255, 0.8)", size="4"),
            # Card de Login
            rx.card(
                rx.vstack(
                    rx.heading("Iniciar Sesión", size="6", margin_bottom="4"),
                    rx.form(
                        rx.vstack(
                            rx.text("Usuario", size="2", weight="bold"),
                            rx.input(
                                placeholder="usuario.sistema",
                                name="username",
                                size="3",
                                width="100%",
                            ),
                            rx.text("Contraseña", size="2", weight="bold"),
                            rx.input(
                                type="password",
                                placeholder="••••••••",
                                name="password",
                                size="3",
                                width="100%",
                            ),
                            # Mensaje de error (condicional)
                            rx.cond(
                                AuthState.error_message != "",
                                rx.callout(
                                    AuthState.error_message,
                                    icon="triangle_alert",
                                    color_scheme="red",
                                    role="alert",
                                    width="100%",
                                ),
                            ),
                            rx.button(
                                "Ingresar",
                                type="submit",
                                size="3",
                                width="100%",
                                loading=AuthState.is_loading,
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        on_submit=AuthState.login,
                        width="100%",
                    ),
                    rx.divider(margin_y="4"),
                    rx.text(
                        "¿Olvidó su contraseña?",
                        size="2",
                        color="gray",
                        cursor="pointer",
                        _hover={"text_decoration": "underline"},
                    ),
                    padding="6",
                    align="center",
                ),
                width="100%",
                max_width="400px",
                size="4",
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            ),
            spacing="6",
            align="center",
            z_index="10",
        ),
        # Fondo decorativo
        background="linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%)",
        height="100vh",
        width="100%",
    )

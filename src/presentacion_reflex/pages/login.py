import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.shared.aurora_background import aurora_background
from src.presentacion_reflex.components.shared.matrix_background import matrix_background
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def login_page() -> rx.Component:
    """
    Página de Login Premium.
    Diseño moderno con tarjeta flotante y fondo de gradiente.
    """
    return rx.box(
        rx.center(
            rx.vstack(
                # Logo de la Empresa (Dinámico) o Título por defecto
                # Logo/Titulo (Texto estático para garantizar rendimiento de animación)
                rx.heading(
                    "INMOBILIARIA VELAR", 
                    font_size=["1.5rem", "2rem", "2.5rem"], # Responsive size via style prop
                    weight="bold", 
                    color="white",
                    text_align="center",
                ),
                rx.text(
                    "Gestión Integral de Propiedades", 
                    color="rgba(255,255,255, 0.8)", 
                    font_size=["0.9rem", "1.1rem"], # Responsive size via style prop
                    text_align="center",
                ),
                # Card de Login
                rx.card(
                    rx.vstack(
                        rx.heading("Iniciar Sesión", size="6", margin_bottom="4"),
                        rx.form(
                            rx.vstack(
                                rx.text("Usuario", size="2", weight="bold"),
                                rx.input(
                                    placeholder="usuario sistema",
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
                padding=["4", "6"], # Padding for mobile edges
                width="100%",
            ),
            # Center content
            height="100%",
            width="100%",
        ),
        # Fondo Aurora Animado
        aurora_background(),
        # Fondo Matrix (Lluvia Digital)
        matrix_background(),
        position="fixed",
        top="0px",
        left="0px",
        right="0px",
        bottom="0px",
        z_index="999",
        on_mount=ConfiguracionState.cargar_datos_empresa,
    )

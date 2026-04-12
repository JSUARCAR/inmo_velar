import datetime
import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.shared.aurora_background import (
    aurora_background,
)
from src.presentacion_reflex.components.shared.matrix_background import (
    matrix_background,
)
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def login_card() -> rx.Component:
    """Tarjeta de login Glassmorphism Elite."""
    return rx.box(
        rx.form(
            rx.vstack(
                # Header del Card
                rx.vstack(
                    rx.cond(
                        ConfiguracionState.logo_preview != "",
                        rx.image(
                            src=ConfiguracionState.logo_preview,
                            height="80px",
                            width="auto",
                            object_fit="contain",
                            margin_bottom="4",
                        ),
                        rx.icon("building", size=60, color="white", margin_bottom="4"),
                    ),
                    rx.heading(
                        rx.cond(
                            ConfiguracionState.empresa["nombre_empresa"] != "",
                            ConfiguracionState.empresa["nombre_empresa"],
                            "INMOBILIARIA VELAR",
                        ),
                        size="6",
                        weight="bold",
                        class_name="claude-text-elite",
                    ),
                    rx.text(
                        "Panel de Gestión Corporativa",
                        size="2",
                        class_name="claude-subtext-elite",
                        weight="medium",
                    ),
                    align="center",
                    spacing="1",
                    width="100%",
                    margin_bottom="6",
                ),
                # Formulario
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Usuario",
                            size="2",
                            weight="bold",
                            class_name="claude-text-elite",
                        ),
                        rx.input(
                            placeholder="Ingrese su usuario",
                            name="username",
                            size="3",
                            width="100%",
                            variant="surface",
                            class_name="claude-input-elite",
                        ),
                        align_items="start",
                        width="100%",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text(
                            "Contraseña",
                            size="2",
                            weight="bold",
                            class_name="claude-text-elite",
                        ),
                        rx.box(
                            rx.input(
                                type=rx.cond(
                                    AuthState.password_visible, "text", "password"
                                ),
                                placeholder="••••••••",
                                name="password",
                                size="3",
                                width="100%",
                                variant="surface",
                                class_name="claude-input-elite",
                                padding_right="40px",
                            ),
                            rx.box(
                                rx.cond(
                                    AuthState.password_visible,
                                    rx.icon(
                                        "eye-off",
                                        size=16,
                                        class_name="claude-eye-icon",
                                        cursor="pointer",
                                        on_click=AuthState.toggle_password_visibility,
                                    ),
                                    rx.icon(
                                        "eye",
                                        size=16,
                                        class_name="claude-eye-icon",
                                        cursor="pointer",
                                        on_click=AuthState.toggle_password_visibility,
                                    ),
                                ),
                                position="absolute",
                                right="10px",
                                top="50%",
                                transform="translateY(-50%)",
                                z_index="1",
                            ),
                            position="relative",
                            width="100%",
                        ),
                        align_items="start",
                        width="100%",
                        spacing="2",
                    ),
                    rx.button(
                        "Iniciar Sesión",
                        type="submit",
                        size="3",
                        color_scheme="blue",
                        class_name="login-button-elite",
                        style={
                            "border_radius": "12px",
                            "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.4)",
                            "margin_top": "1rem",
                            "font_weight": "bold",
                            "background": "rgba(59, 130, 246, 0.9)",
                            "backdrop_filter": "blur(4px)",
                            "cursor": "pointer",
                        },
                        loading=AuthState.is_loading,
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.hstack(
                            rx.icon("circle_alert", size=14, color="#f87171"),
                            rx.text(
                                AuthState.error_message,
                                color="#f87171",
                                size="2",
                                weight="medium",
                            ),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    align="center",
                    spacing="4",
                    width="100%",
                    max_width="340px",
                ),
                # Footer
                rx.text(
                    f"© {datetime.datetime.now().year} Inmobiliaria Velar SAS. Todos los derechos reservados.",
                    size="1",
                    class_name="claude-subtext-elite",
                    margin_top="8",
                ),
                padding="10",
                width="100%",
                align="center",
            ),
            on_submit=AuthState.login,
        ),
        width="100%",
        max_width="450px",
        class_name="claude-card-elite",
        position="relative",
    )


@rx.page(route="/login", title="Login | Inmobiliaria Velar")
def login_page() -> rx.Component:
    """
    Página de Login Premium.
    Diseño moderno con tarjeta flotante y fondo de gradiente.
    """
    return rx.box(
        # Dual Visual Effects (Aurora base + Matrix rain)
        aurora_background(),
        matrix_background(),
        # Header (Title and subtitle)
        rx.box(
            rx.vstack(
                rx.heading(
                    "VELAR CORE",
                    color=rx.cond(
                        rx.color_mode == "light", "rgba(0,0,0,0.85)", "white"
                    ),
                    size="8",
                    font_size=["1.5em", "1.75em", "2em", "2.5em"],
                    weight="bold",
                    letter_spacing="-0.02em",
                ),
                rx.text(
                    "Sistema de Gestión Inmobiliaria Elite",
                    color=rx.cond(
                        rx.color_mode == "light",
                        "rgba(0,0,0,0.6)",
                        "rgba(255,255,255,0.7)",
                    ),
                    size="3",
                    weight="medium",
                ),
                align="center",
                spacing="1",
            ),
            class_name="login-header-elite",
            width="100%",
        ),
        # Content
        rx.box(
            login_card(),
            class_name="login-container-elite",
        ),
        width="100%",
        min_height="100vh",
        class_name="login-page-root",
    )

import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.shared.aurora_background import aurora_background
from src.presentacion_reflex.components.shared.matrix_background import matrix_background
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def login_card() -> rx.Component:
    """Tarjeta de login Neumorphic Executive."""
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
                        rx.icon("building", size=60, color="#3b82f6", margin_bottom="4"),
                    ),
                    rx.heading(
                        rx.cond(
                            ConfiguracionState.empresa["nombre_empresa"] != "",
                            ConfiguracionState.empresa["nombre_empresa"],
                            "INMOBILIARIA VELAR",
                        ),
                        size="6",
                        weight="bold",
                        color="#1e293b",
                    ),
                    rx.text(
                        "Panel de Gestión Corporativa",
                        size="2",
                        color="#64748b",
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
                        rx.text("Usuario", size="2", weight="bold", color="#475569"),
                        rx.input(
                            placeholder="Ingrese su usuario",
                            name="username",
                            size="3",
                            width="100%",
                            variant="surface",
                            style={
                                "background": "white",
                                "border_radius": "12px",
                                "border": "1px solid #e2e8f0",
                            },
                        ),
                        align_items="start",
                        width="100%",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="2", weight="bold", color="#475569"),
                        rx.input(
                            type="password",
                            placeholder="••••••••",
                            name="password",
                            size="3",
                            width="100%",
                            variant="surface",
                            style={
                                "background": "white",
                                "border_radius": "12px",
                                "border": "1px solid #e2e8f0",
                            },
                        ),
                        align_items="start",
                        width="100%",
                        spacing="2",
                    ),
                    rx.button(
                        "Iniciar Sesión",
                        type="submit",
                        size="3",
                        width="100%",
                        color_scheme="blue",
                        style={
                            "border_radius": "12px",
                            "box_shadow": "0 10px 15px -3px rgba(59, 130, 246, 0.3)",
                            "margin_top": "1rem",
                            "font_weight": "bold",
                        },
                        loading=AuthState.is_loading,
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.text(AuthState.error_message, color="red", size="2", weight="medium"),
                    ),
                    spacing="4",
                    width="100%",
                ),
                # Footer
                rx.text(
                    "© 2024 Inmobiliaria Velar SAS. Todos los derechos reservados.",
                    size="1",
                    color="#94a3b8",
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
        background="white",
        border_radius="24px",
        box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        overflow="hidden",
        position="relative",
    )


@rx.page(route="/login", title="Login | Inmobiliaria Velar")
def login_page() -> rx.Component:
    """
    Página de Login Premium.
    Diseño moderno con tarjeta flotante y fondo de gradiente.
    """
    return rx.fragment(
        rx.box(
            # Dual Visual Effects (Aurora base + Matrix rain)
            aurora_background(),
            matrix_background(),
            # Header (Title and subtitle)
            rx.box(
                rx.vstack(
                    rx.heading(
                        "VELAR CORE",
                        color=rx.cond(rx.color_mode == "light", "rgba(0,0,0,0.85)", "white"),
                        size="8",
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
        ),
    )

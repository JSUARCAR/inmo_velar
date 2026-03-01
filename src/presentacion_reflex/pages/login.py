import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.shared.aurora_background import aurora_background
from src.presentacion_reflex.components.shared.matrix_background import matrix_background
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState
from src.presentacion_reflex import styles


def login_page() -> rx.Component:
    """
    Página de Login Premium.
    Diseño moderno con tarjeta flotante y fondo de gradiente.
    """
    return rx.box(
        rx.center(
            rx.vstack(
                # Logo/Titulo (Texto estático para garantizar rendimiento de animación)
                rx.heading(
                    "INMOBILIARIA VELAR", 
                    font_size=["2rem", "2.5rem", "3.2rem"],
                    weight="bold", 
                    color="white",
                    text_align="center",
                    letter_spacing="3px",
                    text_shadow="0 0 25px rgba(255,255,255,0.4), 0 4px 15px rgba(0,0,0,0.6)",
                ),
                rx.text(
                    "Gestión Integral de Propiedades", 
                    color="rgba(255, 255, 255, 0.85)", 
                    font_size=["1rem", "1.2rem"],
                    text_align="center",
                    font_weight="500",
                    letter_spacing="1px",
                    text_shadow="0 2px 5px rgba(0,0,0,0.5)",
                    margin_bottom="4",
                ),
                # Card de Login con efecto Glassmorphism Responsive (Light/Dark)
                rx.card(
                    rx.vstack(
                        rx.heading(
                            "Iniciar Sesión", 
                            size="6", 
                            margin_bottom="4", 
                            color=rx.color_mode_cond(light="rgba(0,0,0,0.85)", dark="white"), 
                            font_weight="bold",
                            text_shadow=rx.color_mode_cond(light="none", dark="0 2px 4px rgba(0,0,0,0.3)")
                        ),
                        rx.form(
                            rx.vstack(
                                rx.text("Usuario", size="2", weight="bold", color=rx.color_mode_cond(light="rgba(0,0,0,0.7)", dark="rgba(255,255,255,0.9)")),
                                rx.input(
                                    placeholder="usuario sistema",
                                    name="username",
                                    size="3",
                                    width="100%",
                                    style=styles.NEU_INPUT_STYLE,
                                ),
                                rx.text("Contraseña", size="2", weight="bold", color=rx.color_mode_cond(light="rgba(0,0,0,0.7)", dark="rgba(255,255,255,0.9)")),
                                rx.input(
                                    type="password",
                                    placeholder="••••••••",
                                    name="password",
                                    size="3",
                                    width="100%",
                                    style=styles.NEU_INPUT_STYLE,
                                ),
                                # Mensaje de error (condicional) con Glassmorphism
                                rx.cond(
                                    AuthState.error_message != "",
                                    rx.callout(
                                        AuthState.error_message,
                                        icon="triangle_alert",
                                        color_scheme="red",
                                        role="alert",
                                        width="100%",
                                        background_color=rx.color_mode_cond(light="rgba(255, 59, 48, 0.1)", dark="rgba(255, 59, 48, 0.15)"),
                                        border=rx.color_mode_cond(light="1px solid rgba(255, 59, 48, 0.3)", dark="1px solid rgba(255, 59, 48, 0.3)"),
                                        backdrop_filter="blur(10px)",
                                        color=rx.color_mode_cond(light="rgba(220, 38, 38, 0.9)", dark="white"),
                                    ),
                                ),
                                rx.button(
                                    "Ingresar",
                                    type="submit",
                                    size="3",
                                    width="100%",
                                    loading=AuthState.is_loading,
                                    background=rx.color_mode_cond(
                                        light="linear-gradient(135deg, rgba(37, 99, 235, 0.9) 0%, rgba(29, 78, 216, 1) 100%)",
                                        dark="linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%)"
                                    ),
                                    border=rx.color_mode_cond(
                                        light="1px solid rgba(59, 130, 246, 0.5)",
                                        dark="1px solid rgba(255, 255, 255, 0.2)"
                                    ),
                                    box_shadow=rx.color_mode_cond(
                                        light="0 8px 32px 0 rgba(37, 99, 235, 0.3)",
                                        dark="0 8px 32px 0 rgba(0, 0, 0, 0.3)"
                                    ),
                                    backdrop_filter="blur(10px)",
                                    color="white",
                                    font_weight="bold",
                                    letter_spacing="1px",
                                    margin_top="2",
                                    _hover={
                                        "background": rx.color_mode_cond(
                                            light="linear-gradient(135deg, rgba(59, 130, 246, 1) 0%, rgba(37, 99, 235, 1) 100%)",
                                            dark="linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.1) 100%)"
                                        ),
                                        "border": rx.color_mode_cond(
                                            light="1px solid rgba(96, 165, 250, 0.8)",
                                            dark="1px solid rgba(255, 255, 255, 0.4)"
                                        ),
                                        "box_shadow": rx.color_mode_cond(
                                            light="0 12px 40px 0 rgba(37, 99, 235, 0.4)",
                                            dark="0 12px 40px 0 rgba(0, 0, 0, 0.4)"
                                        ),
                                        "transform": "translateY(-2px)",
                                    },
                                    _active={
                                        "transform": "translateY(0px)",
                                        "box_shadow": rx.color_mode_cond(
                                            light="0 4px 15px 0 rgba(37, 99, 235, 0.3)",
                                            dark="0 4px 15px 0 rgba(0, 0, 0, 0.3)"
                                        ),
                                    },
                                    transition="all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)",
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            on_submit=AuthState.login,
                            width="100%",
                        ),
                        rx.divider(margin_y="5", border_color=rx.color_mode_cond(light="rgba(0,0,0,0.1)", dark="rgba(255,255,255,0.15)")),
                        rx.text(
                            "¿Olvidó su contraseña?",
                            size="2",
                            color=rx.color_mode_cond(light="rgba(0,0,0,0.6)", dark="rgba(255,255,255,0.7)"),
                            cursor="pointer",
                            transition="all 0.3s ease",
                            _hover={
                                "color": rx.color_mode_cond(light="rgba(0,0,0,0.9)", dark="white"), 
                                "text_decoration": "underline", 
                                "text_shadow": rx.color_mode_cond(light="none", dark="0 0 8px rgba(255,255,255,0.5)")
                            },
                        ),
                        padding="8",
                        align="center",
                        width="100%",
                    ),
                    width="100%",
                    max_width="420px",
                    background_color="transparent",
                    background=rx.color_mode_cond(
                        light="transparent",
                        dark="linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.03) 100%)"
                    ),
                    backdrop_filter="blur(16px) saturate(120%)",
                    border=rx.color_mode_cond(
                        light="1px solid rgba(255, 255, 255, 0.3)",
                        dark="1px solid rgba(255, 255, 255, 0.15)"
                    ),
                    border_radius="24px",
                    box_shadow=rx.color_mode_cond(
                        light="0 30px 60px -12px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.4)",
                        dark="0 30px 60px -12px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.2)"
                    ),
                    padding="2",
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

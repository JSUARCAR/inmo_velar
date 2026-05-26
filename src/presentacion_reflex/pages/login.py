import datetime
import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState
from src.presentacion_reflex import styles


def login_card() -> rx.Component:
    """Tarjeta de login refinada con estética 'The Digital Curator'."""
    return rx.box(
        rx.form(
            rx.vstack(
                # Header del Card
                rx.vstack(
                    rx.heading(
                        "INMOBILIARIA VELAR S.A.S",
                        size="6",
                        weight="bold",
                        font_family=styles.FONT_DISPLAY,
                        color=styles.BRAND_PRIMARY,
                        letter_spacing="-0.03em",
                    ),
                    rx.text(
                        "¡BIENVENIDOS!",
                        size="1",
                        weight="bold",
                        color=styles.TEXT_SECONDARY,
                        letter_spacing="0.15em",
                    ),
                    align="center",
                    spacing="1",
                    width="100%",
                    margin_bottom="8",
                ),
                # Formulario
                rx.vstack(
                    rx.vstack(
                        rx.text(
                            "Usuario",
                            size="2",
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        rx.input(
                            placeholder="nombre.usuario",
                            name="username",
                            size="3",
                            width="100%",
                            style=styles.NEU_INPUT_STYLE,
                            aria_label="Usuario",
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
                            color=styles.TEXT_PRIMARY,
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
                                style=styles.NEU_INPUT_STYLE,
                                padding_right="40px",
                                aria_label="Contraseña",
                            ),
                            rx.box(
                                rx.cond(
                                    AuthState.password_visible,
                                    rx.icon(
                                        "eye-off",
                                        size=16,
                                        color=styles.TEXT_TERTIARY,
                                        cursor="pointer",
                                        on_click=AuthState.toggle_password_visibility,
                                    ),
                                    rx.icon(
                                        "eye",
                                        size=16,
                                        color=styles.TEXT_TERTIARY,
                                        cursor="pointer",
                                        on_click=AuthState.toggle_password_visibility,
                                    ),
                                ),
                                position="absolute",
                                right="12px",
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
                        "Acceder al Panel",
                        type="submit",
                        size="3",
                        width="100%",
                        style=styles.NEU_BUTTON_PRIMARY_STYLE,
                        margin_top="4",
                        loading=AuthState.is_loading,
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.hstack(
                            rx.icon("alert_triangle", size=14, color="#f87171"),
                            rx.text(
                                AuthState.error_message,
                                color="#f87171",
                                size="2",
                                weight="medium",
                            ),
                            spacing="2",
                            align="center",
                            margin_top="2",
                        ),
                    ),
                    align="center",
                    spacing="4",
                    width="100%",
                ),
                # Footer sutil
                rx.text(
                    f"© {datetime.datetime.now().year} Velar Inmobiliaria SAS",
                    size="1",
                    color=styles.TEXT_TERTIARY,
                    margin_top="12",
                    font_weight="medium",
                ),
                padding_x=["1.5rem", "2rem", "3rem"],
                padding_y="3rem",
                width="100%",
                align="center",
            ),
            on_submit=AuthState.login,
        ),
        width="100%",
        max_width="440px",
        background_color=styles.BG_PANEL,
        border_radius="24px",
        box_shadow=styles.SHADOW_WHISPER,
        padding="1",
        position="relative",
    )


@rx.page(route="/login", title="Login Elite | Inmobiliaria Velar")
def login_page() -> rx.Component:
    """
    Página de Login Elite con diseño asimétrico responsivo.
    Escritorio: Diseño de pantalla dividida (Imagen | Formulario).
    Móvil: Imagen de fondo (opacidad 60%) con tarjeta superpuesta.
    """
    return rx.flex(
        # Panel Visual (Hero en Desktop / Fondo en Móvil)
        rx.box(
            rx.image(
                src="/login/image_login_velar.png",
                height="100vh",
                width="100%",
                object_fit="cover",
                filter="sepia(0.2) contrast(1.1)",
                opacity=["0.6", "0.6", "1", "1"],  # 60% opacidad en móvil
            ),
            width=["100%", "100%", "50%", "60%"],
            height="100vh",
            position=["absolute", "absolute", "relative", "relative"],
            top="0",
            left="0",
            z_index="0",
            overflow="hidden",
        ),
        # Panel de Acceso (Formulario)
        rx.center(
            rx.vstack(
                login_card(),
                width="100%",
                align="center",
                padding="4",
            ),
            width=["100%", "100%", "50%", "40%"],
            height="100vh",
            background_color=["transparent", "transparent", styles.BG_APP, styles.BG_APP],
            z_index="1",
            position="relative",
        ),
        width="100%",
        height="100vh",
        background_color=styles.BG_APP,
        direction="row",
        position="relative",
    )

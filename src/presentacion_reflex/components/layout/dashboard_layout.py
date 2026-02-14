import reflex as rx


def dashboard_layout(content: rx.Component) -> rx.Component:
    """
    Layout principal para páginas autenticadas.
    Incluye Sidebar y area de contenido.
    """
    from src.presentacion_reflex import styles
    from src.presentacion_reflex.components.layout.mobile_nav import mobile_nav
    from src.presentacion_reflex.components.layout.sidebar import sidebar

    return rx.flex(
        mobile_nav(),  # Top on mobile, hidden on desktop
        sidebar(),  # Left on desktop, hidden on mobile
        rx.box(
            content,
            flex="1",
            height="100vh",
            overflow_y="auto",
            background=styles.BG_APP,  # Semantic Token
            width="100%",
        ),
        rx.toast.provider(),
        spacing="0",
        flex_direction=[
            "column",
            "column",
            "row",
            "row",
            "row",
        ],  # Stack vertically on mobile, horizontally on desktop
        width="100%",
        height="100vh",
        overflow="hidden",  # Prevent double scrollbars
    )

import reflex as rx

def aurora_background() -> rx.Component:
    """
    Componente de fondo animado "Aurora".
    Crea un efecto de gradientes en movimiento suave usando keyframes y blur.
    """
    return rx.box(
        # Capa de fondo base (oscuro)
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            bg="#0f172a", # Slate 900
            z_index="-2",
        ),
        # Orbe 1
        rx.box(
            position="absolute",
            top="-10%",
            left="-10%",
            width="50vw",
            height="50vw",
            background="radial-gradient(circle, rgba(76, 29, 149, 0.4) 0%, rgba(0,0,0,0) 70%)", # Purple
            filter="blur(60px)",
            animation="aurora-1 15s infinite alternate",
            opacity="0.6",
        ),
        # Orbe 2
        rx.box(
            position="absolute",
            top="10%",
            right="-10%",
            width="40vw",
            height="40vw",
            background="radial-gradient(circle, rgba(13, 148, 136, 0.4) 0%, rgba(0,0,0,0) 70%)", # Teal
            filter="blur(60px)",
            animation="aurora-2 20s infinite alternate",
            opacity="0.6",
        ),
        # Orbe 3
        rx.box(
            position="absolute",
            bottom="-10%",
            left="20%",
            width="60vw",
            height="60vw",
            background="radial-gradient(circle, rgba(29, 78, 216, 0.4) 0%, rgba(0,0,0,0) 70%)", # Blue
            filter="blur(80px)",
            animation="aurora-3 18s infinite alternate",
            opacity="0.6",
        ),
        # Keyframes ahora definidos en assets/aurora.css
        position="fixed",
        top="0",
        left="0",
        width="100%",
        height="100%",
        z_index="-1",
        overflow="hidden",
    )

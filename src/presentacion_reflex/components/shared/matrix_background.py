import reflex as rx

def matrix_background() -> rx.Component:
    """
    Componente de fondo Matrix (Lluvia Digital).
    Usa un canvas HTML5 y un script JS externo para el renderizado.
    """
    return rx.box(
        # Canvas para el efecto
        rx.el.canvas(
            id="matrix-canvas",
            style={
                "width": "100%",
                "height": "100%",
                "display": "block",
            }
        ),
        
        # Estilos para posicionar el canvas sobre (o bajo) el Aurora
        style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "opacity": "0.6",
            "z_index": "1", # Visible
            "pointer_events": "none",
        }
    )

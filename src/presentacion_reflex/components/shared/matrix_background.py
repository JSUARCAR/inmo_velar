import reflex as rx

def matrix_background() -> rx.Component:
    """
    Componente de fondo Matrix (Lluvia Digital).
    Usa un canvas HTML5 y un script JS externo para el renderizado.
    """
    return rx.box(
        # Canvas para el efecto
        rx.html('<canvas id="matrix-canvas"></canvas>'),
        
        # Trigger init logic when component mounts, with polling to ensure JS is loaded
        # Trigger init logic when component mounts
        # The external matrix.js (v5) now handles auto-binding via requestAnimationFrame
        # so no inline script is needed here.
        rx.script("console.log('Matrix Component Mounted');"),
        
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

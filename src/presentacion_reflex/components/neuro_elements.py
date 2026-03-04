import reflex as rx
from .. import styles

def neuro_input(*args, **kwargs) -> rx.Component:
    """Input estándar con estilo Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    # Fusionar estilos preservando el contrato del tema
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}
    
    # Asegurar que no haya variantes de Radix que rompan el diseño
    kwargs.setdefault("variant", "surface")
    
    return rx.input(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_select_root(*args, **kwargs) -> rx.Component:
    """Select.root configurado con el disparador neumórfico."""
    trigger_placeholder = kwargs.pop("placeholder", "Seleccionar...")
    trigger_width = kwargs.pop("width", "100%")
    
    # La jerarquía correcta es Root -> (Trigger, Content -> Items)
    return rx.select.root(
        rx.select.trigger(
            placeholder=trigger_placeholder,
            style=styles.NEU_SELECT_STYLE,
            width=trigger_width,
        ),
        rx.select.content(
            *args,
        ),
        **kwargs
    )

def neuro_button(*args, **kwargs) -> rx.Component:
    """Botón con elevación neumórfica y feedback táctil."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_BUTTON_STYLE, **custom_style}
    
    # Forzar variante para evitar overrides de Radix
    kwargs.setdefault("variant", "surface")
    
    return rx.button(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_text_area(*args, **kwargs) -> rx.Component:
    """TextArea estándar con estilo Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    # Reutilizar gran parte del estilo de input
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}
    
    # TextArea de Radix no siempre responde bien a variant="none" como el input
    # Forzamos los estilos base para asegurar el look hundido
    kwargs.setdefault("min_height", "100px")
    
    return rx.text_area(
        *args,
        style=final_style,
        variant="surface", # Usamos surface como base pero el style lo sobreescribe
        **kwargs
    )

def neuro_panel(*args, **kwargs) -> rx.Component:
    """Contenedor universal con elevación neumática y bordes suaves."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_PANEL_STYLE, **custom_style}
    
    return rx.box(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_divider(**kwargs) -> rx.Component:
    """Divisor neumático con efecto de surco tallado."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_DIVIDER_STYLE, **custom_style}
    return rx.box(style=final_style, **kwargs)

def neuro_badge(text: str, color_scheme: str = "blue", **kwargs) -> rx.Component:
    """Badge neumático con profundidad de tallado."""
    # Mapeo de colores semánticos a variables de Radix
    base_color = f"var(--{color_scheme}-9)"
    
    return rx.box(
        rx.text(text, size="1", weight="bold", color=base_color),
        background=styles.BG_PANEL,
        box_shadow=styles.NEU_INSET_LIGHT,
        border_radius="20px",
        padding="2px 10px",
        display="inline-flex",
        align_items="center",
        justify_content="center",
        **kwargs
    )

def neuro_progress(value: int, color_scheme: str = "blue", **kwargs) -> rx.Component:
    """Barra de progreso con track hundido e indicador volumétrico."""
    bar_color = f"var(--{color_scheme}-9)"
    
    return rx.box(
        rx.box(
            width=f"{value}%",
            height="100%",
            background=bar_color,
            border_radius="inherit",
            box_shadow=f"0 0 8px {bar_color}",
            transition="width 0.5s ease-in-out",
        ),
        width="100%",
        height="8px",
        background=styles.BG_PANEL,
        box_shadow=styles.NEU_INSET,
        border_radius="full",
        overflow="hidden",
        **kwargs
    )

def neuro_table_container(*args, **kwargs) -> rx.Component:
    """Contenedor para tablas con scroll y estilo neumático (overflow y sombra dual)."""
    custom_style = kwargs.pop("style", {})
    final_style = {
        **styles.NEU_PANEL_STYLE,
        "padding": "0",
        "overflow_x": "auto",
        "overflow_y": "hidden",
        "border_radius": "16px",
        "width": "100%",
        **custom_style
    }
    
    return rx.box(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_tooltip(content, children: rx.Component, **kwargs) -> rx.Component:
    """Tooltip con diseño panel neumórfico."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_TOOLTIP_STYLE, **custom_style}
    
    # Customizando el content_style del tooltip de radix a través del componente HoverCard de reflex
    # Reflex HoverCard nos permite mayor personalización de estilos que rx.tooltip
    
    content_render = content if isinstance(content, rx.Component) else rx.text(content, size="2", color=styles.TEXT_PRIMARY)
    
    return rx.hover_card.root(
        rx.hover_card.trigger(children),
        rx.hover_card.content(
            content_render,
            style=final_style,
        ),
        **kwargs
    )

def neuro_badge(text, *args, **kwargs) -> rx.Component:
    """Badge con estilo neumático y mapeo semántico de colores."""
    color_scheme = kwargs.pop("color_scheme", "gray")
    custom_style = kwargs.pop("style", {})
    
    bg_color = f"var(--{color_scheme}-3)" if color_scheme != "gray" else styles.BG_PANEL
    text_color = f"var(--{color_scheme}-11)" if color_scheme != "gray" else styles.TEXT_PRIMARY
    
    # Variante solid para que aplique nuestro background custom en lugar del default de radix variant=soft
    kwargs.setdefault("variant", "outline") 
    
    final_style = {
        "background": bg_color,
        "box_shadow": styles.NEU_INSET_LIGHT,
        "border": f"1px solid var(--{color_scheme}-6)" if color_scheme != "gray" else f"1px solid {styles.BORDER_DEFAULT}",
        "border_radius": "12px",
        "padding": "0.25rem 0.5rem",
        "color": text_color,
        **custom_style
    }
    
    return rx.badge(text, *args, style=final_style, **kwargs)

def neuro_progress(*args, **kwargs) -> rx.Component:
    """Barra de progreso con estilo neumático (canal tallado)."""
    custom_style = kwargs.pop("style", {})
    color_scheme = kwargs.pop("color_scheme", "blue")
    
    # El track (contenedor) recibe el canal tallado Inset
    final_style = {
        "background": styles.BG_PANEL,
        "box_shadow": styles.NEU_INSET,
        "border_radius": "999px",
        "overflow": "hidden",
        "height": kwargs.get("height", "8px"),
        # Apuntamos a la caja interna del indicador para darle volumen/color
        "& > div": {
            "background": f"var(--{color_scheme}-9)",
            "box_shadow": "inset 0 1px 3px rgba(255,255,255,0.4), inset 0 -1px 3px rgba(0,0,0,0.1)",
        },
        **custom_style
    }
    
    return rx.progress(
        *args,
        color_scheme=color_scheme,
        style=final_style,
        **kwargs
    )

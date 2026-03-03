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

import reflex as rx
from .. import styles

def neuro_input(*args, **kwargs) -> rx.Component:
    """Input estándar con estilo Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    # Fusionar estilos preservando el contrato del tema
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}
    
    # Forzar variante 'soft' - 'ghost' no es válido para TextField en Reflex 0.8.x
    kwargs["variant"] = "soft"
    kwargs.setdefault("size", "3")
    
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
            variant="soft",  # Cambiado de ghost a soft para compatibilidad
        ),
        rx.select.content(
            *args,
            style={
                "background": styles.BG_PANEL,
                "box_shadow": styles.NEU_MODAL_SHADOW,
                "border_radius": "12px",
            }
        ),
        size=kwargs.pop("size", "3"),
        **kwargs
    )

def neuro_button(*args, **kwargs) -> rx.Component:
    """Botón con elevación neumórfica y feedback táctil."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_BUTTON_STYLE, **custom_style}
    
    # Los botones sí soportan la variante 'ghost'
    kwargs.setdefault("variant", "ghost")
    kwargs.setdefault("size", "3")
    
    return rx.button(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_text_area(*args, **kwargs) -> rx.Component:
    """TextArea estándar con estilo Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}
    
    kwargs.setdefault("min_height", "120px")
    kwargs.setdefault("size", "3")
    kwargs["variant"] = "soft" # Forzar variante compatible
    
    return rx.text_area(
        *args,
        style=final_style,
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

def neuro_badge(text, *args, **kwargs) -> rx.Component:
    """Badge con estilo neumático y mapeo semántico de colores."""
    color_scheme = kwargs.pop("color_scheme", "gray")
    custom_style = kwargs.pop("style", {})
    
    bg_color = f"var(--{color_scheme}-3)" if color_scheme != "gray" else styles.BG_PANEL
    text_color = f"var(--{color_scheme}-11)" if color_scheme != "gray" else styles.TEXT_PRIMARY
    
    kwargs.setdefault("variant", "outline") 
    
    final_style = {
        "background": bg_color,
        "box_shadow": styles.NEU_INSET_LIGHT,
        "border": f"1px solid var(--{color_scheme}-6)" if color_scheme != "gray" else f"1px solid {styles.BORDER_DEFAULT}",
        "border_radius": "12px",
        "padding": "0.25rem 0.75rem",
        "color": text_color,
        "font_weight": "bold",
        **custom_style
    }
    
    return rx.badge(text, *args, style=final_style, **kwargs)

def neuro_progress(*args, **kwargs) -> rx.Component:
    """Barra de progreso con estilo neumático (canal tallado)."""
    custom_style = kwargs.pop("style", {})
    color_scheme = kwargs.pop("color_scheme", "blue")
    
    final_style = {
        "background": styles.BG_PANEL,
        "box_shadow": styles.NEU_INSET,
        "border_radius": "999px",
        "overflow": "hidden",
        "height": kwargs.get("height", "12px"), # Más grueso para look executive
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

def neuro_table_container(*args, **kwargs) -> rx.Component:
    """Contenedor para tablas que asegura scroll horizontal y estilo neumático."""
    custom_style = kwargs.pop("style", {})
    final_style = {
        "width": "100%",
        "overflow_x": "auto",
        "padding": "1px",  # Espacio para que no se corten las sombras
        **custom_style
    }
    
    return rx.box(
        *args,
        style=final_style,
        **kwargs
    )

def neuro_tooltip(children=None, **kwargs) -> rx.Component:
    """Tooltip con estilo neumático. Soporta contenido complejo mediante rx.hover_card."""
    content = kwargs.pop("content", "")
    # El trigger puede venir como children o pasarse explícitamente
    trigger = children if children is not None else kwargs.pop("children", rx.box())
    
    # En Reflex 0.8.x, rx.tooltip solo acepta string en 'content'.
    # Para contenido complejo (como en kpi_card.py), usamos rx.hover_card.
    return rx.hover_card.root(
        rx.hover_card.trigger(trigger),
        rx.hover_card.content(
            rx.cond(
                isinstance(content, str),
                rx.text(content, size="2"),
                content # Si es un componente (VStack, etc.)
            ),
            style=styles.NEU_TOOLTIP_STYLE,
            **kwargs
        )
    )

def neuro_switch(*args, **kwargs) -> rx.Component:
    """Switch (Toggle) con apariencia Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    color_scheme = kwargs.pop("color_scheme", "green")
    
    # Reflex usa Radix bajo el capó para el switch.
    # El estilo debe afectar al contenedor (root) y al thumb.
    final_style = {
        "box_shadow": styles.NEU_INSET,
        "background": styles.BG_PANEL,
        "border": f"1px solid {styles.BORDER_DEFAULT}",
        "cursor": "pointer",
        "border_radius": "9999px",
        "transition": styles.GLOBAL_TRANSITION,
        
        # Estado activo/encendido
        "&[data-state='checked']": {
             "background": f"var(--{color_scheme}-9)",
             "box_shadow": f"inset 0 2px 4px rgba(0,0,0,0.3), 0 0 8px var(--{color_scheme}-6)",
        },
        
        # El "thumb" del switch en Radix
        "& .rt-SwitchThumb": { 
            "background": styles.BG_PANEL,
            "box_shadow": "4px 4px 8px rgba(163, 177, 198, 0.4), -4px -4px 8px rgba(255, 255, 255, 0.8), inset 1px 1px 2px rgba(255,255,255,1), inset -1px -1px 2px rgba(163, 177, 198, 0.2)",
            "border": f"1px solid {styles.BORDER_DEFAULT}",
        },
        
        "&[data-state='checked'] .rt-SwitchThumb": {
             "box_shadow": "2px 2px 4px rgba(0,0,0,0.2), inset 1px 1px 2px rgba(255,255,255,0.4)",
             "border": "none",
        },
        **custom_style
    }
    
    return rx.switch(*args, color_scheme=color_scheme, style=final_style, **kwargs)

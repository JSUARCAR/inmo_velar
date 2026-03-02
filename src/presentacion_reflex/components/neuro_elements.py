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
    
    # El estilo se aplica al trigger, no al root
    return rx.select.root(
        rx.select.trigger(
            placeholder=trigger_placeholder,
            style=styles.NEU_SELECT_STYLE,
            width=trigger_width,
        ),
        *args,
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

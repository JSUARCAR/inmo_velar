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

    return rx.input(*args, style=final_style, **kwargs)


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
            },
        ),
        size=kwargs.pop("size", "3"),
        **kwargs,
    )


def neuro_button(*args, **kwargs) -> rx.Component:
    """Botón con elevación neumórfica y feedback táctil."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_BUTTON_STYLE, **custom_style}

    # Los botones sí soportan la variante 'ghost'
    kwargs.setdefault("variant", "ghost")
    kwargs.setdefault("size", "3")

    return rx.button(*args, style=final_style, **kwargs)


def neuro_text_area(*args, **kwargs) -> rx.Component:
    """TextArea estándar con estilo Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}

    kwargs.setdefault("min_height", "120px")
    kwargs.setdefault("size", "3")
    kwargs["variant"] = "soft"  # Forzar variante compatible

    return rx.text_area(*args, style=final_style, **kwargs)


def neuro_panel(*args, **kwargs) -> rx.Component:
    """Contenedor universal con elevación neumática y bordes suaves."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_PANEL_STYLE, **custom_style}

    return rx.box(*args, style=final_style, **kwargs)


def neuro_divider(**kwargs) -> rx.Component:
    """Divisor neumático con efecto de surco tallado."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_DIVIDER_STYLE, **kwargs.pop("style", {})}
    return rx.box(style=final_style, **kwargs)


def neuro_form_label(text: str, required: bool = False, **kwargs) -> rx.Component:
    """Etiqueta de formulario con estilo Neumorphic Executive.

    Args:
        text: Texto de la etiqueta.
        required: Si True, muestra indicador de campo obligatorio (*).
        **kwargs: Props adicionales pasados al rx.text.

    Returns:
        rx.Component: Etiqueta con estilos neumórficos.
    """
    custom_style = kwargs.pop("style", {})
    final_style = {
        "color": styles.TEXT_PRIMARY,
        "font_size": "0.875rem",
        "font_weight": "500",
        "margin_bottom": "0.375rem",
        **custom_style,
    }

    label_text = f"*{text}" if required else text
    label_color = "var(--danger-9)" if required else styles.TEXT_PRIMARY

    return rx.text(
        label_text,
        style=final_style,
        color=label_color,
        **kwargs,
    )


def neuro_badge(text, *args, **kwargs) -> rx.Component:
    """Badge neumórfico con color semántico basado en la escala Radix CSS.

    Compatible con Vars reactivos (rx.match, rx.cond) en color_scheme.
    Usa var(--{color_scheme}-N) directamente para evitar comparaciones Python
    contra Vars que romperían la compilación de Reflex.

    Args:
        text: Texto o Var a mostrar en el badge.
        color_scheme: Nombre de escala Radix: "blue", "green", "red", "orange",
                      "cyan", "violet", "gray", etc. Acepta rx.Var.
        style: Estilos CSS adicionales a fusionar.
    """
    color_scheme = kwargs.pop("color_scheme", "gray")
    custom_style = kwargs.pop("style", {})

    # ── Usar siempre la escala Radix pura ──────────────────────────────────
    # var(--gray-3), var(--gray-6), var(--gray-11) son tokens válidos en Radix,
    # igual que var(--blue-3), var(--green-3), etc.  No se necesita bifurcación.
    bg_color = f"var(--{color_scheme}-3)"
    text_color = f"var(--{color_scheme}-11)"
    border_val = f"1px solid var(--{color_scheme}-6)"

    kwargs.setdefault("variant", "outline")

    final_style = {
        "background": bg_color,
        "box_shadow": styles.NEU_INSET_LIGHT,
        "border": border_val,
        "border_radius": "12px",
        "padding": "0.25rem 0.75rem",
        "color": text_color,
        "font_weight": "bold",
        **custom_style,
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
        "height": kwargs.get("height", "12px"),  # Más grueso para look executive
        "& > div": {
            "background": f"var(--{color_scheme}-9)",
            "box_shadow": "inset 0 1px 3px rgba(255,255,255,0.4), inset 0 -1px 3px rgba(0,0,0,0.1)",
        },
        **custom_style,
    }

    return rx.progress(*args, color_scheme=color_scheme, style=final_style, **kwargs)


def neuro_table_container(*args, **kwargs) -> rx.Component:
    """Contenedor para tablas que asegura scroll horizontal y estilo neumático."""
    custom_style = kwargs.pop("style", {})
    final_style = {
        "width": "100%",
        "overflow_x": "auto",
        "padding": "1px",  # Espacio para que no se corten las sombras
        **custom_style,
    }

    return rx.box(*args, style=final_style, **kwargs)


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
                content,  # Si es un componente (VStack, etc.)
            ),
            style=styles.NEU_TOOLTIP_STYLE,
            **kwargs,
        ),
    )


def neuro_switch(*args, **kwargs) -> rx.Component:
    """Switch (Toggle) con apariencia Neumorphic Executive."""
    custom_style = kwargs.pop("style", {})
    color_scheme = kwargs.pop("color_scheme", "green")

    # Reflex usa Radix bajo el capó para el switch.
    # Forzamos variant soft/surface para minimizar estilos nativos que interfieran
    kwargs.setdefault("variant", "surface")

    final_style = {
        "box_shadow": styles.NEU_INSET + " !important",
        "background": styles.BG_PANEL + " !important",
        "border": f"1px solid {styles.BORDER_DEFAULT} !important",
        "cursor": "pointer",
        "border_radius": "9999px",
        "transition": styles.GLOBAL_TRANSITION,
        "padding": "2px",
        "width": "44px",
        "height": "24px",
        # Estado activo/encendido
        "&[data-state='checked']": {
            "background": f"var(--{color_scheme}-9) !important",
            "box_shadow": f"inset 0 2px 4px rgba(0,0,0,0.3), 0 0 8px var(--{color_scheme}-6) !important",
        },
        # El "thumb" del switch en Radix - Target exacto por clase y atributo
        "& .rt-SwitchThumb": {
            "background": "white !important",
            "box_shadow": "2px 2px 5px rgba(0,0,0,0.2) !important",
            "transform": "translateX(2px)",
            "transition": "transform 250ms cubic-bezier(0.4, 0, 0.2, 1)",
        },
        "&[data-state='checked'] .rt-SwitchThumb": {
            "transform": "translateX(20px)",
            "background": "white !important",
        },
        **custom_style,
    }

    return rx.switch(*args, color_scheme=color_scheme, style=final_style, **kwargs)


# ---------------------------------------------------------------------------
# TAREA 1.1 — neuro_spinner
# ---------------------------------------------------------------------------


def neuro_spinner(size: str = "3", **kwargs) -> rx.Component:
    """Spinner neumórfico con color de acento dinámico y rotación suave.

    Args:
        size: Tamaño Radix del spinner ("1"–"3"). Default "3".
        **kwargs: Props adicionales pasados a rx.spinner.

    Returns:
        rx.Component: Spinner con color ACCENT_COLOR y efecto glow.
    """
    custom_style = kwargs.pop("style", {})
    final_style = {
        # Color de marca: hereda la variable CSS para soporte dark-mode automático
        "color": styles.ACCENT_COLOR,
        # Halo sutil que refuerza la sensación neumórfica sin peso visual
        # 'neu-pulse' combina el glow con la rotación nativa del spinner Radix
        "filter": "drop-shadow(0 0 6px var(--blue-6))",
        # @keyframes spin definido globalmente en assets/custom_layout.css
        "animation": "spin 1s linear infinite",
        "transition": styles.GLOBAL_TRANSITION,
        **custom_style,
    }

    return rx.spinner(size=size, style=final_style, **kwargs)


# ---------------------------------------------------------------------------
# TAREA 1.2 — neuro_callout
# ---------------------------------------------------------------------------

# Mapa semántico: color_scheme → var CSS de Radix para fondo y texto
_CALLOUT_COLOR_MAP: dict[str, dict[str, str]] = {
    "blue": {
        "bg": "var(--blue-3)",
        "border": "var(--blue-6)",
        "icon_color": "var(--blue-9)",
    },
    "green": {
        "bg": "var(--green-3)",
        "border": "var(--green-6)",
        "icon_color": "var(--green-9)",
    },
    "red": {
        "bg": "var(--red-3)",
        "border": "var(--red-6)",
        "icon_color": "var(--red-9)",
    },
    "yellow": {
        "bg": "var(--yellow-3)",
        "border": "var(--yellow-6)",
        "icon_color": "var(--yellow-9)",
    },
    "gray": {
        "bg": styles.BG_PANEL,
        "border": styles.BORDER_DEFAULT,
        "icon_color": styles.TEXT_SECONDARY,
    },
}


def neuro_callout(
    text: str | rx.Component,
    icon: str = "info",
    color_scheme: str = "blue",
    **kwargs,
) -> rx.Component:
    """Callout con elevación neumórfica (border-radius 12px, NEU_MODAL_SHADOW).

    Construido manualmente para no depender del renderizado plano de rx.callout.

    Args:
        text: Mensaje del callout (str o componente Reflex).
        icon: Nombre del icono Lucide/Radix. Default "info".
        color_scheme: Esquema semántico: "blue", "green", "red", "yellow", "gray".
        **kwargs: Props adicionales pasados al rx.box contenedor.

    Returns:
        rx.Component: Callout neumórfico con icono, sombra modal y borde redondeado.
    """
    custom_style = kwargs.pop("style", {})
    colors = _CALLOUT_COLOR_MAP.get(color_scheme, _CALLOUT_COLOR_MAP["blue"])

    contenedor_style = {
        "background": colors["bg"],
        "box_shadow": styles.NEU_MODAL_SHADOW,
        "border": f"1px solid {colors['border']}",
        "border_radius": "12px",
        "padding": "1rem 1.25rem",
        "transition": styles.GLOBAL_TRANSITION,
        "width": "100%",
        **custom_style,
    }

    cuerpo_texto = (
        rx.text(text, size="2", color=styles.TEXT_PRIMARY)
        if isinstance(text, str)
        else text
    )

    return rx.box(
        rx.hstack(
            rx.icon(
                tag=icon,
                size=18,
                color=colors["icon_color"],
                flex_shrink="0",
            ),
            cuerpo_texto,
            align="center",
            gap="0.75rem",
            width="100%",
        ),
        style=contenedor_style,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# TAREA 1.3 — neuro_card_footer
# ---------------------------------------------------------------------------


def neuro_card_footer(*children, **kwargs) -> rx.Component:
    """Footer estandarizado para tarjetas neumórficas.

    Muestra un divisor superior y distribuye el contenido en dos zonas:
    - Zona izquierda (precio / información secundaria).
    - Zona derecha (acciones / botones).

    Args:
        *children: Componentes hijo. El primero va a la izquierda, el resto a la derecha.
        **kwargs: Props adicionales pasados al rx.box contenedor.

    Returns:
        rx.Component: Footer con divisor y layoute justify-between.

    Example:
        neuro_card_footer(
            rx.text("$1.200.000", weight="bold"),
            neuro_button("Ver", on_click=...),
            neuro_button("Editar", on_click=...),
        )
    """
    custom_style = kwargs.pop("style", {})

    contenedor_style = {
        "width": "100%",
        "padding_top": "1rem",
        "margin_top": "0.75rem",
        # Divisor superior tallado (neumorfismo inset)
        "border_top": f"1.5px solid transparent",
        "background_image": (
            "linear-gradient(var(--bg-panel), var(--bg-panel)), "
            "linear-gradient(to right, rgba(163,177,198,0.5), rgba(255,255,255,0.9), rgba(163,177,198,0.5))"
        ),
        "background_origin": "border-box",
        "background_clip": "padding-box, border-box",
        **custom_style,
    }

    # Primer hijo → zona izquierda (precio). Resto → zona derecha (acciones).
    zona_izq = children[0] if children else rx.fragment()
    zona_der_hijos = children[1:] if len(children) > 1 else []

    return rx.box(
        rx.hstack(
            # Zona izquierda
            rx.box(zona_izq),
            # Zona derecha — acciones agrupadas con gap estándar
            rx.hstack(
                *zona_der_hijos,
                gap="0.5rem",
                align="center",
                flex_shrink="0",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        style=contenedor_style,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# TAREA 2.2 — neuro_icon_action_button
# ---------------------------------------------------------------------------


def neuro_icon_action_button(
    icon_tag: str,
    *,
    color_scheme: str = "gray",
    size: str = "2",
    tooltip_content: str = "",
    disabled: bool | rx.Var = False,
    on_click=None,
    **kwargs,
) -> rx.Component:
    """IconButton neumórfico de acción con ciclo táctil completo.

    Ciclo de sombras:
    - Reposo → ``shadow-flat-elite`` (superficie limpia, no elevada).
    - Hover  → ``shadow-raised-elite`` (emerge del plano).
    - Active → ``shadow-inset-elite`` (se hunde al confirmar la acción).

    Este patrón elimina definitivamente la variante ``ghost`` (transparente)
    y reemplaza la variante ``surface`` genérica con una semántica táctil
    propia del sistema Neumorphism Executive de Velar.

    Args:
        icon_tag: Nombre del icono Lucide (ej. ``"pencil"``).
        color_scheme: Esquema de color Radix para el icono (ej. ``"blue"``).
        size: Tamaño del botón Radix (``"1"``, ``"2"``, ``"3"``). Default ``"2"``.
        tooltip_content: Texto del tooltip. Si vacío, no se envuelve.
        disabled: Deshabilita el botón. Acepta ``bool`` o ``rx.Var``.
        on_click: Handler del evento clic.
        **kwargs: Props adicionales para ``rx.icon_button``.

    Returns:
        rx.Component: IconButton (opcionalmente envuelto en tooltip).

    Example:
        neuro_icon_action_button(
            "pencil",
            color_scheme="gray",
            tooltip_content="Editar",
            on_click=MiState.abrir_edicion,
        )
    """
    btn_style: dict = {
        "background": styles.BG_PANEL,
        "box_shadow": styles.SHADOW_FLAT_ELITE,
        "border": f"1px solid {styles.BORDER_DEFAULT}",
        "border_radius": "10px",
        "color": f"var(--{color_scheme}-9)",
        "transition": styles.GLOBAL_TRANSITION,
        "cursor": "pointer",
        "_hover": {
            "box_shadow": styles.SHADOW_RAISED_ELITE,
            "background": styles.BG_HOVER,
            "transform": "translateY(-1px)",
        },
        "_active": {
            "box_shadow": styles.SHADOW_INSET_ELITE,
            "transform": "scale(0.96)",
        },
        "_disabled": {
            "opacity": "0.4",
            "cursor": "not-allowed",
            "box_shadow": "none",
        },
        **kwargs.pop("style", {}),
    }

    btn = rx.icon_button(
        rx.icon(tag=icon_tag, size=16),
        variant="surface",
        size=size,
        color_scheme=color_scheme,
        disabled=disabled,
        on_click=on_click,
        style=btn_style,
        **kwargs,
    )

    if tooltip_content:
        return rx.tooltip(btn, content=tooltip_content)
    return btn

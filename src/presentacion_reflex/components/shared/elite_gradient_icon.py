"""Módulo: elite_gradient_icon
Componente de icono circular monocromático basado en el tema Claude (Anthropic).
Centrado absoluto vía Flexbox y soporte de estados para retroalimentación táctil.

Uso:
    elite_gradient_icon("file-text", size=28)
    elite_gradient_icon("building-2", size=40, color_scheme="terracotta")
"""

import reflex as rx
from src.presentacion_reflex import styles

# --- Colores sólidos tema Claude (sin gradientes) ---
# Sistema de colores monocromáticos basado en el tema Claude
_COLORS: dict[str, str] = {
    "default": "var(--brand-primary)",  # Terracotta - Default
    "terracotta": "var(--brand-primary)",  # Terracotta Brand
    "coral": "var(--brand-accent)",  # Coral Accent
    "primary": "var(--text-primary)",  # Near Black
    "secondary": "var(--text-secondary)",  # Olive Gray
    "muted": "var(--text-tertiary)",  # Stone Gray
    "dark": "var(--bg-panel)",  # Dark Surface
    "light": "var(--bg-hover)",  # Warm Sand
}


def elite_gradient_icon(
    icon_tag: str,
    *,
    size: int = 32,
    color_scheme: str = "default",
    raised: bool = True,
    class_name: str = "",
    **kwargs,
) -> rx.Component:
    """Icono circular con color sólido del tema Claude.

    El contenedor usa Flexbox para centrado matemático absoluto (sin
    posicionamiento relativo/absoluto que provoque desalineación).
    Soporta el ciclo de estados: raised (reposo) → flat (hover) → inset (active).

    Args:
        icon_tag: Nombre del icono Lucide (ej. ``"file-text"``).
        size: Tamaño en px del icono SVG. Default 32.
        color_scheme: Clave del color: ``"default"``, ``"terracotta"``,
            ``"coral"``, ``"primary"``, ``"secondary"``, ``"muted"``.
        raised: Si ``True``, aplica ``shadow-raised-elite``; si ``False``,
            aplica ``shadow-flat-elite`` como estado base.
        class_name: Clases CSS extra para el contenedor.
        **kwargs: Props adicionales pasados al ``rx.box`` contenedor externo.

    Returns:
        rx.Component: Contenedor circular con color sólido e icono centrado.

    Example:
        elite_gradient_icon("file-text", size=28, color_scheme="terracotta")
    """
    bg_color = _COLORS.get(color_scheme, _COLORS["default"])
    container_size = f"{size + 20}px"  # padding óptico = size + 20px

    shadow_base = styles.SHADOW_RAISED_ELITE if raised else styles.SHADOW_FLAT_ELITE

    contenedor_style: dict = {
        # Centrado matemático absoluto via Flexbox
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "flex_shrink": "0",
        # Morfología circular
        "width": container_size,
        "height": container_size,
        "border_radius": "50%",
        # Color sólido del tema Claude (sin gradientes)
        "background": bg_color,
        # Ring shadow
        "box_shadow": shadow_base,
        # Feedback táctil
        "transition": styles.GLOBAL_TRANSITION,
        "cursor": "pointer",
        # Hover: aplanar sombra
        "_hover": {
            "box_shadow": styles.SHADOW_FLAT_ELITE,
            "transform": "scale(1.05)",
        },
        # Active/clic: hundir (inset)
        "_active": {
            "box_shadow": styles.SHADOW_INSET_ELITE,
            "transform": "scale(0.97)",
        },
    }

    # Determinar color del icono basado en el fondo
    icon_color = (
        "white"
        if color_scheme in ["default", "terracotta", "coral", "dark"]
        else "inherit"
    )

    return rx.box(
        rx.icon(
            tag=icon_tag,
            size=size,
            color=icon_color,
            stroke_width="1.8",
        ),
        style=contenedor_style,
        class_name=f"elite-icon {class_name}".strip(),
        **kwargs,
    )


def elite_gradient_icon_labeled(
    icon_tag: str,
    label: str,
    *,
    size: int = 28,
    color_scheme: str = "default",
    description: str = "",
    **kwargs,
) -> rx.Component:
    """Icono monocromático con etiqueta y descripción opcional (para headers de módulo).

    Combina ``elite_gradient_icon`` con un ``rx.vstack`` de texto para
    construir el header estándar de páginas del sistema Velar.

    Args:
        icon_tag: Nombre del icono Lucide.
        label: Título principal (ej. ``"Gestión de Contratos"``).
        size: Tamaño del icono en px. Default 28.
        color_scheme: Clave de color del tema.
        description: Subtítulo opcional.
        **kwargs: Props del contenedor ``rx.hstack`` externo.

    Returns:
        rx.Component: HStack con icono + vstack de texto.

    Example:
        elite_gradient_icon_labeled(
            "file-text",
            "Gestión de Contratos",
            description="Mandatos y Arrendamientos",
            color_scheme="terracotta",
        )
    """
    icon_component = elite_gradient_icon(icon_tag, size=size, color_scheme=color_scheme)

    texto = rx.vstack(
        rx.heading(label, size="7", weight="bold", color=styles.TEXT_PRIMARY),
        *(
            [rx.text(description, size="2", color=styles.TEXT_SECONDARY)]
            if description
            else []
        ),
        spacing="1",
        align="start",
    )

    return rx.hstack(
        icon_component,
        texto,
        align="center",
        spacing="4",
        **kwargs,
    )

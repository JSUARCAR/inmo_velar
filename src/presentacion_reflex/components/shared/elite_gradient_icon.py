"""Módulo: elite_gradient_icon
Componente de icono tricolor con gradiente Violeta→Azul→Morado, centrado
absoluto vía Flexbox y soporte de estado active/inset para retroalimentación
táctil neumórfica.

Uso:
    elite_gradient_icon("file-text", size=28)
    elite_gradient_icon("building-2", size=40, accent="purple")
"""

import reflex as rx
from src.presentacion_reflex import styles

# --- Paleta tricolor ELITE ---
# Gradiente oficial: Violeta (#8B5CF6) → Azul (#3B82F6) → Morado (#6D28D9)
_GRADIENT_TRICOLOR = "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #6D28D9 100%)"

# Variantes de gradiente por acento (para flexibilidad semántica)
_GRADIENTS: dict[str, str] = {
    "default": _GRADIENT_TRICOLOR,
    "blue":    "linear-gradient(135deg, #3B82F6 0%, #60A5FA 50%, #2563EB 100%)",
    "green":   "linear-gradient(135deg, #10B981 0%, #34D399 50%, #059669 100%)",
    "red":     "linear-gradient(135deg, #EF4444 0%, #F87171 50%, #DC2626 100%)",
    "purple":  _GRADIENT_TRICOLOR,
    "cyan":    "linear-gradient(135deg, #06B6D4 0%, #22D3EE 50%, #0891B2 100%)",
    "amber":   "linear-gradient(135deg, #F59E0B 0%, #FCD34D 50%, #D97706 100%)",
}


def elite_gradient_icon(
    icon_tag: str,
    *,
    size: int = 32,
    accent: str = "default",
    raised: bool = True,
    class_name: str = "",
    **kwargs,
) -> rx.Component:
    """Icono circular con gradiente tricolor y sombras neumórficas.

    El contenedor usa Flexbox para centrado matemático absoluto (sin
    posicionamiento relativo/absoluto que provoque desalineación).
    Soporta el ciclo táctil: raised (reposo) → flat (hover) → inset (active).

    Args:
        icon_tag: Nombre del icono Lucide (ej. ``"file-text"``).
        size: Tamaño en px del icono SVG. Default 32.
        accent: Clave del gradiente: ``"default"``, ``"blue"``, ``"green"``,
            ``"red"``, ``"purple"``, ``"cyan"``, ``"amber"``.
        raised: Si ``True``, aplica ``shadow-raised-elite``; si ``False``,
            aplica ``shadow-flat-elite`` como estado base.
        class_name: Clases CSS extra para el contenedor.
        **kwargs: Props adicionales pasados al ``rx.box`` contenedor externo.

    Returns:
        rx.Component: Contenedor circular con gradiente e icono centrado.

    Example:
        elite_gradient_icon("file-text", size=28, accent="blue")
    """
    gradient = _GRADIENTS.get(accent, _GRADIENT_TRICOLOR)
    container_size = f"{size + 20}px"  # padding óptico = size + 20px

    shadow_base = (
        styles.SHADOW_RAISED_ELITE if raised else styles.SHADOW_FLAT_ELITE
    )

    contenedor_style: dict = {
        # Centrado matemático absoluto via Flexbox
        "display":          "flex",
        "align_items":      "center",
        "justify_content":  "center",
        "flex_shrink":      "0",

        # Morfología circular
        "width":            container_size,
        "height":           container_size,
        "border_radius":    "50%",

        # Gradiente tricolor premium
        "background":       gradient,

        # Sombras neumórficas duales (raised base, inset al clic)
        "box_shadow":       shadow_base,

        # Feedback táctil
        "transition":       styles.GLOBAL_TRANSITION,
        "cursor":           "pointer",

        # Hover: aplanar sombra
        "_hover": {
            "box_shadow":   styles.SHADOW_FLAT_ELITE,
            "transform":    "scale(1.05)",
        },

        # Active/clic: hundir (inset)
        "_active": {
            "box_shadow":   styles.SHADOW_INSET_ELITE,
            "transform":    "scale(0.97)",
        },
    }

    return rx.box(
        rx.icon(
            tag=icon_tag,
            size=size,
            color="white",
            stroke_width="1.8",
        ),
        style=contenedor_style,
        class_name=f"elite-gradient-icon {class_name}".strip(),
        **kwargs,
    )


def elite_gradient_icon_labeled(
    icon_tag: str,
    label: str,
    *,
    size: int = 28,
    accent: str = "default",
    description: str = "",
    **kwargs,
) -> rx.Component:
    """Icono tricolor con etiqueta y descripción opcional (para headers de módulo).

    Combina ``elite_gradient_icon`` con un ``rx.vstack`` de texto para
    construir el header estándar de páginas del sistema Velar.

    Args:
        icon_tag: Nombre del icono Lucide.
        label: Título principal (ej. ``"Gestión de Contratos"``).
        size: Tamaño del icono en px. Default 28.
        accent: Clave de gradiente.
        description: Subtítulo opcional.
        **kwargs: Props del contenedor ``rx.hstack`` externo.

    Returns:
        rx.Component: HStack con icono + vstack de texto.

    Example:
        elite_gradient_icon_labeled(
            "file-text",
            "Gestión de Contratos",
            description="Mandatos y Arrendamientos",
            accent="purple",
        )
    """
    icon_component = elite_gradient_icon(icon_tag, size=size, accent=accent)

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

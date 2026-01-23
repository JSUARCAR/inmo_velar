"""
Modal de Checklist de Desocupación - Diseño Elite
Implementación premium con visualización avanzada del progreso.
"""
import reflex as rx
from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState


def _header_section() -> rx.Component:
    """Header con información de la desocupación y barra de progreso."""
    return rx.vstack(
        # Información de la propiedad
        rx.hstack(
            rx.icon("home", size=24, color="var(--accent-9)"),
            rx.vstack(
                rx.text(
                    DesocupacionesState.checklist_info["direccion"],
                    font_weight="bold",
                    font_size="1.1em"
                ),
                rx.text(
                    DesocupacionesState.checklist_info["inquilino"],
                    color="var(--gray-11)",
                    font_size="0.9em"
                ),
                spacing="1",
                align_items="start"
            ),
            align_items="start",
            spacing="3",
            width="100%"
        ),
        
        # Fecha programada y estado
        rx.hstack(
            rx.hstack(
                rx.icon("calendar", size=16, color="var(--gray-10)"),
                rx.text(
                    DesocupacionesState.checklist_info["fecha_programada"],
                    font_size="0.85em",
                    color="var(--gray-11)"
                ),
                spacing="2",
                align_items="center"
            ),
            rx.badge(
                DesocupacionesState.checklist_info["estado"],
                variant="soft",
                color_scheme=rx.cond(
                    DesocupacionesState.checklist_info["estado"] == "En Proceso",
                    "blue",
                    rx.cond(
                        DesocupacionesState.checklist_info["estado"] == "Completada",
                        "green",
                        "gray"
                    )
                )
            ),
            justify="between",
            width="100%"
        ),
        
        # Barra de progreso con estadísticas
        rx.vstack(
            rx.hstack(
                rx.text("Progreso", font_weight="medium", font_size="0.9em"),
                rx.hstack(
                    rx.text(DesocupacionesState.checklist_info["tareas_completadas"]),
                    rx.text(" de "),
                    rx.text(DesocupacionesState.checklist_info["tareas_total"]),
                    rx.text(" tareas"),
                    spacing="0",
                    font_size="0.85em",
                    color="var(--gray-11)"
                ),
                justify="between",
                width="100%"
            ),
            rx.progress(
                value=DesocupacionesState.checklist_info["progreso"],
                width="100%",
                height="10px"
            ),
            rx.hstack(
                rx.text(
                    DesocupacionesState.checklist_info["progreso"],
                    font_weight="bold",
                    font_size="1.2em",
                    color="var(--blue-9)"
                ),
                rx.text("%", font_weight="bold", font_size="1.2em", color="var(--blue-9)"),
                spacing="0"
            ),
            spacing="2",
            width="100%"
        ),
        
        spacing="4",
        width="100%",
        padding="1em",
        background="var(--gray-2)",
        border_radius="12px",
        margin_bottom="1em"
    )


def _checklist_item(item: dict) -> rx.Component:
    """Item individual del checklist con diseño premium."""
    return rx.hstack(
        # Checkbox con estilo mejorado
        rx.box(
            rx.cond(
                item["completada"],
                rx.icon(
                    "circle_check_big",
                    size=24,
                    color="var(--green-9)",
                    cursor="default"
                ),
                rx.icon_button(
                    rx.icon("circle", size=24),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                    on_click=lambda: DesocupacionesState.toggle_tarea(item["id_tarea"], True),
                    cursor="pointer"
                )
            ),
            display="flex",
            align_items="center",
            justify_content="center"
        ),
        
        # Contenido de la tarea
        rx.vstack(
            rx.hstack(
                rx.text(
                    item["orden"],
                    font_weight="bold",
                    color="var(--gray-10)",
                    min_width="24px"
                ),
                rx.text(
                    item["descripcion"],
                    font_weight=rx.cond(item["completada"], "normal", "medium"),
                    color=rx.cond(
                        item["completada"],
                        "var(--gray-10)",
                        "var(--gray-12)"
                    ),
                    text_decoration=rx.cond(
                        item["completada"],
                        "line-through",
                        "none"
                    )
                ),
                width="100%",
                spacing="2"
            ),
            rx.cond(
                item["completada"],
                rx.hstack(
                    rx.cond(
                        item["responsable"] != "",
                        rx.hstack(
                            rx.icon("user", size=12, color="var(--gray-9)"),
                            rx.text(
                                item["responsable"],
                                font_size="0.75em",
                                color="var(--gray-10)"
                            ),
                            spacing="1",
                            align_items="center"
                        )
                    ),
                    rx.cond(
                        item["fecha_completada"] != "",
                        rx.hstack(
                            rx.icon("clock", size=12, color="var(--gray-9)"),
                            rx.text(
                                item["fecha_completada"],
                                font_size="0.75em",
                                color="var(--gray-10)"
                            ),
                            spacing="1",
                            align_items="center"
                        )
                    ),
                    spacing="3",
                    width="100%"
                )
            ),
            spacing="1",
            align_items="start",
            flex="1"
        ),
        
        # Badge de estado
        rx.cond(
            item["completada"],
            rx.badge("Completada", variant="soft", color_scheme="green", size="1"),
            rx.badge("Pendiente", variant="soft", color_scheme="orange", size="1")
        ),
        
        align_items="center",
        spacing="3",
        padding="12px 16px",
        background=rx.cond(
            item["completada"],
            "var(--green-2)",
            "var(--gray-1)"
        ),
        border_radius="8px",
        border=rx.cond(
            item["completada"],
            "1px solid var(--green-5)",
            "1px solid var(--gray-5)"
        ),
        width="100%",
        _hover={
            "background": rx.cond(
                item["completada"],
                "var(--green-3)",
                "var(--gray-2)"
            )
        },
        transition="all 0.2s ease"
    )


def _footer_section() -> rx.Component:
    """Footer con acciones."""
    return rx.hstack(
        rx.cond(
            DesocupacionesState.checklist_info["progreso"] == 100,
            rx.callout(
                "¡Todas las tareas completadas! Puede finalizar el proceso.",
                icon="check",
                color_scheme="green",
                size="1"
            )
        ),
        rx.spacer(),
        rx.dialog.close(
            rx.button(
                "Cerrar",
                variant="soft",
                color_scheme="gray",
                on_click=DesocupacionesState.close_checklist_modal
            )
        ),
        justify="between",
        width="100%",
        margin_top="1em"
    )


def checklist_modal() -> rx.Component:
    """Modal de checklist con diseño élite."""
    return rx.dialog.root(
        rx.dialog.content(
            # Título con icono
            rx.hstack(
                rx.icon("clipboard_list", size=24, color="var(--accent-9)"),
                rx.dialog.title("Checklist de Desocupación"),
                align_items="center",
                spacing="2"
            ),
            rx.dialog.description(
                "Verifique cada item antes de finalizar el proceso de entrega."
            ),
            
            # Loading state
            rx.cond(
                DesocupacionesState.is_loading,
                rx.center(
                    rx.spinner(size="3"),
                    padding="2em"
                ),
                rx.vstack(
                    # Header con info
                    _header_section(),
                    
                    # Lista de tareas
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                DesocupacionesState.checklist_actual,
                                _checklist_item
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        type="auto",
                        scrollbars="vertical",
                        style={"max_height": "350px"}
                    ),
                    
                    # Footer
                    _footer_section(),
                    
                    spacing="3",
                    width="100%"
                )
            ),
            
            width="600px",
            max_width="95vw",
            padding="1.5em"
        ),
        open=DesocupacionesState.modal_checklist_open,
        on_open_change=DesocupacionesState.set_modal_checklist_open
    )

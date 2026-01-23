import reflex as rx
from typing import Dict, Any
from src.presentacion_reflex.state.incidentes_state import IncidentesState

def _get_priority_color(priority: str) -> str:
    # Reflex Note: 'priority' here is likely a Var during compilation. 
    # We should avoid python string methods like .lower() if it causes issues in foreach.
    # We will use a direct mapping or rx.cond if needed. 
    # For now, let's revert to a simpler exact match or mapped approach 
    # that matches the capitalization used in the backend ("Alta", "Media", "Baja").
    
    return rx.match(
        priority,
        ("Alta", "red"),
        ("alta", "red"),
        ("Media", "orange"),
        ("media", "orange"),
        ("Baja", "green"),
        ("baja", "green"),
        "gray" # Default
    )

def _get_status_color(status: str) -> str:
    return rx.match(
        status,
        ("Reportado", "red"),
        ("Cotizado", "orange"),
        ("Aprobado", "green"),
        ("En Reparacion", "blue"),
        ("En Reparación", "blue"), # Handle both spellings if present
        ("Finalizado", "gray"),
        ("Cancelado", "gray"),
        "gray"
    )

def incident_card(incident: Dict[str, Any]) -> rx.Component:
    """
    Componente de tarjeta de incidente con diseño 'Elite Expert'.
    Color principal basado en el ESTADO del incidente.
    """
    priority_color = _get_priority_color(incident["prioridad"])
    # Elite: Case-insensitive status matching with Slate for better visibility
    status_base_color = rx.match(
        incident["estado"].to(str).lower(),
        ("reportado", "red"),
        ("cotizado", "orange"),
        ("aprobado", "green"),
        ("en reparacion", "blue"),
        ("en reparación", "blue"),
        ("finalizado", "slate"),
        ("cancelado", "slate"),
        "slate"
    )

    return rx.box(
        rx.hstack(
            # Franja lateral VIVIDA (Elite: 6px width)
            rx.box(
                width="6px",
                height="100%",
                bg=rx.color(status_base_color, 9),
                border_radius="0", 
            ),
            # Contenedor principal de contenido
            rx.vstack(
                # Header: ID + Badge Prioridad
                rx.hstack(
                    rx.text(
                        f"INC-{incident['id']}", 
                        size="1", 
                        color="var(--gray-10)", 
                        weight="bold", 
                        letter_spacing="0.05em",
                        font_family="monospace"
                    ),
                    rx.spacer(),
                    rx.badge(
                        incident["prioridad"],
                        color_scheme=priority_color,
                        variant="soft",
                        radius="full",
                        size="1",
                        padding_x="2"
                    ),
                    width="100%",
                    align_items="center",
                ),
                
                # Body: Descripción del incidente
                rx.text(
                    incident["descripcion"],
                    size="3",
                    weight="bold",
                    color="var(--gray-12)",
                    line_height="1.4",
                    style={
                        "display": "-webkit-box",
                        "-webkitLineClamp": "2",
                        "-webkitBoxOrient": "vertical",
                        "overflow": "hidden",
                    },
                    margin_y="2px",
                    title=incident["descripcion"] # Tooltip nativo para texto truncado
                ),

                # Divider sutil
                # rx.divider(margin_y="1", color="var(--gray-4)"),

                # Metadata Bloque 1: Propiedad y Fecha
                rx.flex(
                    rx.hstack(
                        rx.icon("map_pin", size=13, color="var(--gray-9)"),
                        rx.text(incident.get("direccion_propiedad", f"#{incident['id_propiedad']}"), size="1", color="gray", weight="medium"),
                        spacing="1",
                        align_items="center",
                        title="Propiedad"
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.icon("calendar", size=13, color="var(--gray-9)"),
                        # Manejo seguro de fecha (reemplazar T por espacio para split seguro)
                        rx.text(
                             incident["fecha"].to(str).split("T")[0], 
                             size="1", 
                             color="gray"
                        ),
                        spacing="1",
                        align_items="center",
                        title="Fecha del reporte"
                    ),
                    width="100%",
                    align_items="center",
                    margin_top="4px"
                ),

                # Metadata Bloque 2: Origen y Proveedor
                rx.hstack(
                    rx.badge(
                        rx.hstack(
                            rx.icon("megaphone", size=10),
                            rx.text(incident.get("origen", "Inquilino"), size="1"),
                            spacing="1",
                            align_items="center"
                        ),
                        variant="surface", # O surface
                        color_scheme="gray",
                        size="1",
                        radius="medium"
                    ),
                    rx.spacer(),
                     # Indicador de Proveedor Asignado
                     rx.cond(
                         incident["id_proveedor"],
                         rx.tooltip(
                             rx.box(
                                 rx.icon("hard_hat", size=14, color="var(--blue-9)"),
                                 padding="5px",
                                 bg="var(--blue-3)",
                                 border_radius="full",
                                 border="1px solid var(--blue-5)"
                             ),
                             content="Proveedor Asignado"
                         )
                     ),
                    width="100%",
                    align_items="center",
                    padding_top="6px",
                    border_top="1px dashed var(--gray-4)", # Separador sutil
                    margin_top="4px"
                ),
                
                spacing="2",
                padding_y="3",
                padding_right="3",
                padding_left="2", # Menos padding izq porque ya esta la franja
                width="100%",
                align_items="start",
            ),
            spacing="0", 
            height="100%",
            width="100%",
            align_items="stretch" # Estirar para que la franja ocupe todo el alto
        ),
        bg="white",
        # Elite: Colored border shows status at a glance
        border="2px solid",
        border_color=rx.color(status_base_color, 5),
        border_radius="lg",
        shadow="sm",
        position="relative",
        overflow="hidden",
        width="100%",
        
        # Elite Interacción
        cursor="pointer",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px) scale(1.01)",
            "box_shadow": f"0 20px 40px -15px var(--gray-alpha-4), 0 8px 20px -8px var(--gray-alpha-3)",
            "border_color": rx.color(status_base_color, 9),
            "& > div > div:first-child": {
                "bg": rx.color(status_base_color, 11),
                "width": "8px"
            }
        },
        on_click=lambda: IncidentesState.select_incidente(incident)
    )

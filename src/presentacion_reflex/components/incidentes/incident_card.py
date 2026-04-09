from typing import Any, Dict

import reflex as rx

from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex import styles


def _get_priority_color(priority: str) -> str:
    return rx.match(
        priority,
        ("Alta", "red"),
        ("Media", "orange"),
        ("Baja", "blue"),
        "gray",
    )


def incident_card(incident: Dict[str, Any]) -> rx.Component:
    priority_color = _get_priority_color(incident["prioridad"])

    status_bg = rx.match(
        incident["estado"],
        ("Reportado", "var(--red-9)"),
        ("Cotizado", "var(--orange-9)"),
        ("Aprobado", "var(--green-9)"),
        ("En Reparacion", "var(--blue-9)"),
        ("En Reparacion", "var(--blue-9)"),
        ("Finalizado", "var(--slate-9)"),
        ("Cancelado", "var(--slate-9)"),
        "var(--slate-9)",
    )

    status_bg_hover = rx.match(
        incident["estado"],
        ("Reportado", "var(--red-11)"),
        ("Cotizado", "var(--orange-11)"),
        ("Aprobado", "var(--green-11)"),
        ("En Reparacion", "var(--blue-11)"),
        ("En Reparacion", "var(--blue-11)"),
        ("Finalizado", "var(--slate-11)"),
        ("Cancelado", "var(--slate-11)"),
        "var(--slate-11)",
    )

    return rx.box(
        rx.hstack(
            rx.box(
                width="6px",
                height="100%",
                bg=status_bg,
                border_radius="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "INC-",
                        incident["id"],
                        size="1",
                        color="var(--gray-10)",
                        weight="bold",
                        letter_spacing="0.05em",
                        font_family="monospace",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.icon("calendar", size=11, color="var(--gray-9)"),
                        rx.text(incident["fecha"], size="1", color="gray"),
                        spacing="1",
                        align_items="center",
                    ),
                    rx.badge(
                        incident["prioridad"],
                        color_scheme=priority_color,
                        variant="soft",
                        radius="full",
                        size="1",
                        padding_x="2",
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.hstack(
                    rx.icon("home", size=15, color="var(--primary-9)"),
                    rx.text(
                        rx.cond(
                            incident["direccion_propiedad"] != "",
                            incident["direccion_propiedad"],
                            rx.text("#", incident["id_propiedad"]),
                        ),
                        size="2",
                        weight="bold",
                        color="var(--gray-12)",
                        style={
                            "display": "-webkit-box",
                            "-webkitLineClamp": "1",
                            "-webkitBoxOrient": "vertical",
                            "overflow": "hidden",
                        },
                    ),
                    spacing="1",
                    align_items="center",
                    title="Propiedad Afectada",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.icon("user", size=12, color="var(--green-9)"),
                        rx.text(
                            rx.cond(
                                incident["nombre_propietario"] != "",
                                incident["nombre_propietario"],
                                "Sin propietario",
                            ),
                            size="1",
                            color="gray",
                            weight="medium",
                        ),
                        rx.cond(
                            incident["telefono_propietario"] != "",
                            rx.hstack(
                                rx.text(" / ", size="1", color="var(--gray-7)"),
                                rx.icon("phone", size=10, color="var(--green-9)"),
                                rx.text(
                                    incident["telefono_propietario"],
                                    size="1",
                                    color="gray",
                                ),
                                spacing="1",
                            ),
                            rx.text("", size="1"),
                        ),
                        spacing="1",
                        align_items="center",
                        title="Propietario",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.icon("user_check", size=12, color="var(--blue-9)"),
                        rx.text(
                            rx.cond(
                                incident["nombre_inquilino"] != "",
                                incident["nombre_inquilino"],
                                "Sin inquilino",
                            ),
                            size="1",
                            color="gray",
                            weight="medium",
                        ),
                        rx.cond(
                            incident["telefono_inquilino"] != "",
                            rx.hstack(
                                rx.text(" / ", size="1", color="var(--gray-7)"),
                                rx.icon("phone", size=10, color="var(--blue-9)"),
                                rx.text(
                                    incident["telefono_inquilino"],
                                    size="1",
                                    color="gray",
                                ),
                                spacing="1",
                            ),
                            rx.text("", size="1"),
                        ),
                        spacing="1",
                        align_items="center",
                        title="Inquilino",
                        width="100%",
                    ),
                    rx.cond(
                        incident["nombre_habitante"] != "",
                        rx.hstack(
                            rx.icon("users", size=12, color="var(--orange-9)"),
                            rx.text(
                                incident["nombre_habitante"],
                                size="1",
                                color="gray",
                                weight="medium",
                            ),
                            rx.cond(
                                incident["telefono_habitante"] != "",
                                rx.hstack(
                                    rx.text(" / ", size="1", color="var(--gray-7)"),
                                    rx.icon("phone", size=10, color="var(--orange-9)"),
                                    rx.text(
                                        incident["telefono_habitante"],
                                        size="1",
                                        color="gray",
                                    ),
                                    spacing="1",
                                ),
                                rx.text("", size="1"),
                            ),
                            spacing="1",
                            align_items="center",
                            title="Habitante",
                            width="100%",
                        ),
                        rx.text("", size="1"),
                    ),
                    spacing="2",
                    width="100%",
                    align_items="start",
                ),
                rx.hstack(
                    rx.badge(
                        rx.hstack(
                            rx.icon("megaphone", size=10),
                            rx.text(incident["origen"], size="1"),
                            spacing="1",
                            align_items="center",
                        ),
                        variant="surface",
                        color_scheme="gray",
                        size="1",
                        radius="medium",
                    ),
                    rx.spacer(),
                    width="100%",
                    align_items="center",
                    padding_top="4px",
                    border_top="1px dashed var(--gray-4)",
                    margin_top="3px",
                ),
                spacing="2",
                padding_y="3",
                padding_right="3",
                padding_left="2",
                width="100%",
                align_items="start",
            ),
            spacing="0",
            height="100%",
            width="100%",
            align_items="stretch",
        ),
        bg=styles.BG_PANEL,
        border="none",
        border_radius="16px",
        box_shadow=styles.NEU_SHADOW,
        position="relative",
        overflow="hidden",
        width="100%",
        cursor="pointer",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": rx.color_mode_cond(
                light="12px 12px 24px rgba(184, 195, 218, 0.5), -12px -12px 24px rgba(255, 255, 255, 1)",
                dark="12px 12px 24px rgba(0, 0, 0, 0.9), -12px -12px 24px rgba(45, 47, 53, 0.5)",
            ),
            "& > div > div:first-child": {"bg": status_bg_hover, "width": "8px"},
        },
        on_click=lambda: IncidentesState.select_incidente(incident),
    )

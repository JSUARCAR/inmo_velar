"""
Modal de Detalle de Contrato
Muestra información completa del contrato en modo solo lectura.
"""

import reflex as rx

from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import neuro_button
from src.presentacion_reflex import styles


def detail_field(label: str, value: str) -> rx.Component:
    """Campo de detalle solo lectura."""
    return rx.box(
        rx.vstack(
            rx.text(label, size="1", weight="bold", color="gray.500", text_transform="uppercase"),
            rx.text(value, size="3", weight="medium", color="var(--gray-12)"),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        padding="0.5em 1em",
        border_radius="8px",
        style={"box_shadow": styles.SHADOW_INSET_ELITE, "background": "rgba(255,255,255,0.4)"},
    )


def section_divider(title: str) -> rx.Component:
    """Divisor de sección con título."""
    return rx.vstack(
        rx.divider(margin_y="1em"),
        rx.text(title, size="3", weight="bold", color="blue.600"),
        spacing="2",
        width="100%",
    )


def modal_detalle_contrato() -> rx.Component:
    """Modal que muestra detalles completos de un contrato."""
    return rx.dialog.root(
        rx.dialog.content(
            # --- ELITE HEADER ---
            rx.vstack(
                rx.hstack(
                    rx.icon("file-search", size=24, color="var(--blue-9)"),
                    rx.dialog.title(
                        rx.cond(
                            ContratosState.contrato_detalle["tipo"] == "Mandato",
                            "Detalle de Contrato de Mandato",
                            "Detalle de Contrato de Arrendamiento",
                        ),
                        size="6",
                        weight="bold",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.separator(),
                spacing="3",
                padding_bottom="4",
            ),
            rx.vstack(
                # Información Básica
                rx.grid(
                    detail_field("ID Contrato", ContratosState.contrato_detalle["id_view"]),
                    detail_field("Estado", ContratosState.contrato_detalle["estado"]),
                    detail_field(
                        "Fecha Inicio", ContratosState.contrato_detalle["fecha_inicio"]
                    ),
                    detail_field(
                        "Fecha Fin", ContratosState.contrato_detalle["fecha_fin"]
                    ),
                    detail_field(
                        "Duración (meses)", ContratosState.contrato_detalle["duracion"]
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                section_divider("Información de la Propiedad"),
                rx.grid(
                    detail_field(
                        "Matrícula", ContratosState.contrato_detalle["matricula"]
                    ),
                    detail_field(
                        "Tipo", ContratosState.contrato_detalle["tipo_propiedad"]
                    ),
                    detail_field(
                        "Dirección", ContratosState.contrato_detalle["direccion"]
                    ),
                    detail_field(
                        "Área (m²)", ContratosState.contrato_detalle["area_m2"]
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Información Financiera - diferente para Mandato vs Arrendamiento
                section_divider("Información Financiera"),
                rx.cond(
                    ContratosState.contrato_detalle["tipo"] == "Mandato",
                    # Mandato
                    rx.grid(
                        detail_field(
                            "Canon Mandato",
                            rx.cond(
                                ContratosState.contrato_detalle["canon"],
                                ContratosState.contrato_detalle["canon_view"],
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "Comisión (%)",
                            rx.cond(
                                ContratosState.contrato_detalle["comision"],
                                ContratosState.contrato_detalle["comision_view"],
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "IVA (%)",
                            rx.cond(
                                ContratosState.contrato_detalle["iva_pct"],
                                ContratosState.contrato_detalle["iva_view"],
                                "N/A",
                            ),
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    # Arrendamiento
                    rx.grid(
                        detail_field(
                            "Canon Arrendamiento",
                            rx.cond(
                                ContratosState.contrato_detalle["canon"],
                                ContratosState.contrato_detalle["canon_view"],
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "Depósito Garantía",
                            rx.cond(
                                ContratosState.contrato_detalle["deposito"],
                                ContratosState.contrato_detalle["deposito_view"],
                                "N/A",
                            ),
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                ),
                # Información de Persona - Propietario o Arrendatario
                section_divider(
                    rx.cond(
                        ContratosState.contrato_detalle["tipo"] == "Mandato",
                        "Información del Propietario",
                        "Información del Arrendatario",
                    )
                ),
                rx.grid(
                    detail_field(
                        "Nombre",
                        rx.cond(
                            ContratosState.contrato_detalle["tipo"] == "Mandato",
                            ContratosState.contrato_detalle["propietario"],
                            ContratosState.contrato_detalle["arrendatario"],
                        ),
                    ),
                    detail_field(
                        "Documento", ContratosState.contrato_detalle["documento"]
                    ),
                    detail_field(
                        "Teléfono", ContratosState.contrato_detalle["telefono"]
                    ),
                    detail_field("Email", ContratosState.contrato_detalle["email"]),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Codeudor (solo para Arrendamiento)
                rx.cond(
                    ContratosState.contrato_detalle["tipo"] == "Arrendamiento",
                    rx.vstack(
                        section_divider("Información del Codeudor"),
                        rx.grid(
                            detail_field(
                                "Nombre", ContratosState.contrato_detalle["codeudor"]
                            ),
                            detail_field(
                                "Documento",
                                ContratosState.contrato_detalle["documento_codeudor"],
                            ),
                            columns="2",
                            spacing="4",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.box(),
                ),
                # Información Adicional
                section_divider("Información Adicional"),
                rx.grid(
                    detail_field("Asesor", ContratosState.contrato_detalle["asesor"]),
                    detail_field(
                        "Creado por", ContratosState.contrato_detalle["created_by"]
                    ),
                    detail_field(
                        "Fecha Creación", ContratosState.contrato_detalle["created_at"]
                    ),
                    rx.cond(
                        ContratosState.contrato_detalle["motivo_cancelacion"],
                        detail_field(
                            "Motivo Cancelación",
                            ContratosState.contrato_detalle["motivo_cancelacion"],
                        ),
                        rx.box(),
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Botón Cerrar
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cerrar Detalles",
                            on_click=ContratosState.close_detail_modal,
                            variant="soft",
                            color_scheme="gray",
                            style={"box_shadow": styles.SHADOW_FLAT_ELITE, "_hover": {"box_shadow": styles.SHADOW_RAISED_ELITE, "transform": "scale(1.02)"}, "_active": {"box_shadow": styles.SHADOW_INSET_ELITE, "transform": "scale(0.98)"}},
                        )
                    ),
                    justify="end",
                    width="100%",
                    margin_top="1em",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="800px",
            style={"max_height": "90vh", "overflow_y": "auto"},
        ),
        open=ContratosState.show_detail_modal,
        on_open_change=ContratosState.close_detail_modal,
    )

"""
Modal de Detalle de Contrato
Muestra información completa del contrato en modo solo lectura.
"""

import reflex as rx

from src.presentacion_reflex.state.contratos_state import ContratosState


def detail_field(label: str, value: str) -> rx.Component:
    """Campo de detalle solo lectura."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.600"),
        rx.text(value, size="2", weight="regular"),
        spacing="1",
        align_items="start",
        width="100%",
    )


def section_divider(title: str) -> rx.Component:
    """Divisor de sección con título."""
    return rx.vstack(
        rx.divider(margin_y="1em"),
        rx.text(title, size="3", weight="bold", color="blue.600"),
        spacing="2",
        width="100%",
    )


def contrato_detail_modal() -> rx.Component:
    """Modal que muestra detalles completos de un contrato."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    ContratosState.contrato_detalle.get("tipo") == "Mandato",
                    "Detalle de Contrato de Mandato",
                    "Detalle de Contrato de Arrendamiento",
                )
            ),
            rx.vstack(
                # Información Básica
                rx.grid(
                    detail_field("ID Contrato", ContratosState.contrato_detalle.get("id", "N/A")),
                    detail_field("Estado", ContratosState.contrato_detalle.get("estado", "N/A")),
                    detail_field(
                        "Fecha Inicio", ContratosState.contrato_detalle.get("fecha_inicio", "N/A")
                    ),
                    detail_field(
                        "Fecha Fin", ContratosState.contrato_detalle.get("fecha_fin", "N/A")
                    ),
                    detail_field(
                        "Duración (meses)", ContratosState.contrato_detalle.get("duracion", "N/A")
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                section_divider("Información de la Propiedad"),
                rx.grid(
                    detail_field(
                        "Matrícula", ContratosState.contrato_detalle.get("matricula", "N/A")
                    ),
                    detail_field(
                        "Tipo", ContratosState.contrato_detalle.get("tipo_propiedad", "N/A")
                    ),
                    detail_field(
                        "Dirección", ContratosState.contrato_detalle.get("direccion", "N/A")
                    ),
                    detail_field(
                        "Área (m²)", ContratosState.contrato_detalle.get("area_m2", "N/A")
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Información Financiera - diferente para Mandato vs Arrendamiento
                section_divider("Información Financiera"),
                rx.cond(
                    ContratosState.contrato_detalle.get("tipo") == "Mandato",
                    # Mandato
                    rx.grid(
                        detail_field(
                            "Canon Mandato",
                            rx.cond(
                                ContratosState.contrato_detalle.get("canon"),
                                f"${ContratosState.contrato_detalle.get('canon', 0):,}".replace(
                                    ",", "."
                                ),
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "Comisión (%)",
                            rx.cond(
                                ContratosState.contrato_detalle.get("comision_pct"),
                                f"{ContratosState.contrato_detalle.get('comision_pct', 0

):.2f}%",
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "IVA (%)",
                            rx.cond(
                                ContratosState.contrato_detalle.get("iva_pct"),
                                f"{ContratosState.contrato_detalle.get('iva_pct', 0):.2f}%",
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
                                ContratosState.contrato_detalle.get("canon"),
                                f"${ContratosState.contrato_detalle.get('canon', 0):,}".replace(
                                    ",", "."
                                ),
                                "N/A",
                            ),
                        ),
                        detail_field(
                            "Depósito Garantía",
                            rx.cond(
                                ContratosState.contrato_detalle.get("deposito"),
                                f"${ContratosState.contrato_detalle.get('deposito', 0):,}".replace(
                                    ",", "."
                                ),
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
                        ContratosState.contrato_detalle.get("tipo") == "Mandato",
                        "Información del Propietario",
                        "Información del Arrendatario",
                    )
                ),
                rx.grid(
                    detail_field(
                        "Nombre",
                        rx.cond(
                            ContratosState.contrato_detalle.get("tipo") == "Mandato",
                            ContratosState.contrato_detalle.get("propietario", "N/A"),
                            ContratosState.contrato_detalle.get("arrendatario", "N/A"),
                        ),
                    ),
                    detail_field(
                        "Documento", ContratosState.contrato_detalle.get("documento", "N/A")
                    ),
                    detail_field(
                        "Teléfono", ContratosState.contrato_detalle.get("telefono", "N/A")
                    ),
                    detail_field("Email", ContratosState.contrato_detalle.get("email", "N/A")),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Codeudor (solo para Arrendamiento)
                rx.cond(
                    ContratosState.contrato_detalle.get("tipo") == "Arrendamiento",
                    rx.vstack(
                        section_divider("Información del Codeudor"),
                        rx.grid(
                            detail_field(
                                "Nombre", ContratosState.contrato_detalle.get("codeudor", "N/A")
                            ),
                            detail_field(
                                "Documento",
                                ContratosState.contrato_detalle.get("documento_codeudor", "N/A"),
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
                    detail_field("Asesor", ContratosState.contrato_detalle.get("asesor", "N/A")),
                    detail_field(
                        "Creado por", ContratosState.contrato_detalle.get("created_by", "N/A")
                    ),
                    detail_field(
                        "Fecha Creación", ContratosState.contrato_detalle.get("created_at", "N/A")
                    ),
                    rx.cond(
                        ContratosState.contrato_detalle.get("motivo_cancelacion"),
                        detail_field(
                            "Motivo Cancelación",
                            ContratosState.contrato_detalle.get("motivo_cancelacion", ""),
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
                        rx.button(
                            "Cerrar",
                            on_click=ContratosState.close_detail_modal,
                            variant="soft",
                            color_scheme="gray",
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

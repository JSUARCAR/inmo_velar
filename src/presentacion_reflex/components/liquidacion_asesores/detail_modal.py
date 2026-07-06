import reflex as rx

from src.presentacion_reflex.components.document_manager_elite import (
    document_manager_elite,
)
from src.presentacion_reflex.state.liquidacion_asesores_state import (
    LiquidacionAsesoresState,
)
from src.presentacion_reflex.state.liquidacion_asesores.form_state import (
    LiquidacionFormState,
)
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_button,
    neuro_icon_action_button,
)


def detail_modal() -> rx.Component:
    """Modal para ver detalles de una liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Detalles de Liquidación", size="5"),
            rx.scroll_area(
                rx.cond(
                    LiquidacionFormState.liquidacion_actual,
                    rx.flex(
                        # Info Básica
                        rx.card(
                            rx.flex(
                                rx.box(
                                    rx.text(
                                        "Asesor", size="1", color="gray", weight="bold"
                                    ),
                                    rx.text(
                                        LiquidacionFormState.liquidacion_actual[
                                            "asesor"
                                        ],
                                        size="3",
                                        weight="medium",
                                    ),
                                ),
                                rx.box(
                                    rx.text(
                                        "Período", size="1", color="gray", weight="bold"
                                    ),
                                    rx.text(
                                        LiquidacionFormState.liquidacion_actual[
                                            "periodo"
                                        ],
                                        size="3",
                                        weight="medium",
                                    ),
                                ),
                                rx.box(
                                    rx.text(
                                        "Estado", size="1", color="gray", weight="bold"
                                    ),
                                    rx.badge(
                                        LiquidacionFormState.liquidacion_actual[
                                            "estado"
                                        ],
                                        size="2",
                                        color_scheme=rx.match(
                                            LiquidacionFormState.liquidacion_actual[
                                                "estado"
                                            ],
                                            ("Pendiente", "yellow"),
                                            ("Aprobada", "blue"),
                                            ("Pagada", "green"),
                                            ("Anulada", "red"),
                                            "gray",
                                        ),
                                    ),
                                ),
                                spacing="4",
                                justify="between",
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        # Totales
                        rx.grid(
                            rx.card(
                                rx.text("Canon Liquidado", size="1", color="gray"),
                                rx.text(
                                    LiquidacionFormState.liquidacion_actual[
                                        "canon_liquidado_view"
                                    ],
                                    size="4",
                                    weight="bold",
                                ),
                            ),
                            rx.card(
                                rx.text("Comisión Bruta", size="1", color="gray"),
                                rx.text(
                                    LiquidacionFormState.liquidacion_actual[
                                        "comision_bruta_view"
                                    ],
                                    size="4",
                                    weight="bold",
                                    color="blue",
                                ),
                            ),
                            rx.card(
                                rx.text("Descuentos", size="1", color="gray"),
                                rx.text(
                                    LiquidacionFormState.liquidacion_actual[
                                        "total_descuentos_view"
                                    ],
                                    size="4",
                                    weight="bold",
                                    color="red",
                                ),
                            ),
                            rx.card(
                                rx.text("Bonificaciones", size="1", color="gray"),
                                rx.text(
                                    LiquidacionFormState.liquidacion_actual[
                                        "total_bonificaciones_view"
                                    ],
                                    size="4",
                                    weight="bold",
                                    color="green",
                                ),
                            ),
                            rx.card(
                                rx.text("Valor Neto", size="1", color="gray"),
                                rx.text(
                                    LiquidacionFormState.liquidacion_actual[
                                        "valor_neto_view"
                                    ],
                                    size="5",
                                    weight="bold",
                                    color="green",
                                ),
                                variant="classic",
                            ),
                            columns="3",
                            spacing="3",
                            width="100%",
                        ),
                        # Properties Section
                        rx.box(
                            rx.heading(
                                "Propiedades Liquidadas", size="3", margin_bottom="2"
                            ),
                            rx.cond(
                                LiquidacionFormState.advisor_properties.length() > 0,
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Propiedad"),
                                            rx.table.column_header_cell("Canon"),
                                            rx.table.column_header_cell("% Com."),
                                            rx.table.column_header_cell("Comisión"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            LiquidacionFormState.advisor_properties,
                                            lambda p: rx.table.row(
                                                rx.table.cell(
                                                    p["DIRECCION_PROPIEDAD"], size="1"
                                                ),
                                                rx.table.cell(
                                                    p["CANON_ARRENDAMIENTO_VIEW"],
                                                    size="1",
                                                ),
                                                rx.table.cell(
                                                    p["COMISION_PORCENTAJE_VIEW"],
                                                    size="1",
                                                    color="blue",
                                                ),
                                                rx.table.cell(
                                                    p["COMISION_MONTO_VIEW"],
                                                    size="1",
                                                    weight="bold",
                                                ),
                                            ),
                                        )
                                    ),
                                    variant="surface",
                                    width="100%",
                                    size="1",
                                ),
                                rx.text(
                                    "No hay propiedades asociadas",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                            ),
                            margin_top="4",
                            width="100%",
                        ),
                        rx.separator(size="4", margin_y="4"),
                        # Descuentos y Bonificaciones
                        rx.box(
                            rx.heading(
                                "Descuentos  y Bonificaciones",
                                size="3",
                                margin_bottom="2",
                            ),
                            rx.cond(
                                (
                                    LiquidacionFormState.descuentos_actuales.length()
                                    + LiquidacionFormState.bonificaciones_actuales.length()
                                )
                                > 0,
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Categoría"),
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acciones"),
                                        )
                                    ),
                                    rx.table.body(
                                        # Descuentos
                                        rx.foreach(
                                            LiquidacionFormState.descuentos_actuales,
                                            lambda d: rx.table.row(
                                                rx.table.cell(
                                                    rx.badge(
                                                        "Descuento",
                                                        color_scheme="red",
                                                        size="1",
                                                    )
                                                ),
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell(
                                                    d["valor_view"], color="red"
                                                ),
                                                rx.table.cell(
                                                    rx.cond(
                                                        LiquidacionFormState.liquidacion_actual[
                                                            "estado"
                                                        ]
                                                        == "Pendiente",
                                                        neuro_icon_action_button(
                                                            "trash-2",
                                                            color_scheme="red",
                                                            tooltip_content="Eliminar descuento",
                                                            on_click=lambda id_desc=d[
                                                                "id_descuento"
                                                            ]: LiquidacionFormState.eliminar_descuento(
                                                                id_desc
                                                            ),
                                                        ),
                                                        rx.box(),
                                                    )
                                                ),
                                            ),
                                        ),
                                        # Bonificaciones
                                        rx.foreach(
                                            LiquidacionFormState.bonificaciones_actuales,
                                            lambda b: rx.table.row(
                                                rx.table.cell(
                                                    rx.badge(
                                                        "Bonificación",
                                                        color_scheme="green",
                                                        size="1",
                                                    )
                                                ),
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(
                                                    b["valor_view"], color="green"
                                                ),
                                                rx.table.cell(
                                                    rx.box()
                                                ),  # Sin acciones por ahora
                                            ),
                                        ),
                                    ),
                                    variant="surface",
                                    width="100%",
                                ),
                                rx.text(
                                    "No hay descuentos ni bonificaciones aplicados.",
                                    color="gray",
                                    size="2",
                                ),
                            ),
                            width="100%",
                        ),
                        rx.separator(size="4", margin_y="4"),
                        # Documentos y Soportes (NUEVA)
                        rx.box(
                            rx.heading(
                                "Soportes y Comprobantes", size="3", margin_bottom="2"
                            ),
                            rx.text(
                                "Adjunte comprobantes de pago y soportes de descuentos.",
                                size="2",
                                color="gray",
                                margin_bottom="2",
                            ),
                            rx.card(
                                document_manager_elite(LiquidacionAsesoresState),
                                width="100%",
                            ),
                            width="100%",
                        ),
                        direction="column",
                        spacing="4",
                        padding="1",
                    ),
                    rx.center(rx.spinner()),
                ),
                max_height="600px",
            ),
            rx.flex(
                rx.hstack(
                    rx.cond(
                        LiquidacionFormState.liquidacion_actual["estado"] != "Anulada",
                        neuro_button(
                            rx.icon("file-text"),
                            "Descargar PDF",
                            color_scheme="blue",
                            on_click=lambda: PDFState.generar_liquidacion_asesor_pdf(
                                LiquidacionFormState.liquidacion_actual[
                                    "id_liquidacion"
                                ]
                            ),
                            loading=PDFState.generating,
                            tooltip_content="Descargar liquidación en formato PDF",
                        ),
                    ),
                    rx.cond(
                        LiquidacionFormState.liquidacion_actual["estado"]
                        == "Pendiente",
                        neuro_button(
                            rx.icon("circle_check"),
                            "Aprobar",
                            color_scheme="green",
                            on_click=lambda: LiquidacionFormState.aprobar_liquidacion(
                                LiquidacionFormState.liquidacion_actual[
                                    "id_liquidacion"
                                ]
                            ),
                            tooltip_content="Aprobar esta liquidación",
                        ),
                    ),
                    rx.cond(
                        LiquidacionFormState.liquidacion_actual["estado"] == "Aprobada",
                        neuro_button(
                            rx.icon("banknote"),
                            "Marcar Pagada",
                            color_scheme="blue",
                            on_click=lambda: LiquidacionFormState.marcar_como_pagada(
                                LiquidacionFormState.liquidacion_actual[
                                    "id_liquidacion"
                                ]
                            ),
                            tooltip_content="Marcar como pagada",
                        ),
                    ),
                    rx.cond(
                        (LiquidacionFormState.liquidacion_actual["estado"] != "Pagada")
                        & (
                            LiquidacionFormState.liquidacion_actual["estado"]
                            != "Anulada"
                        ),
                        neuro_button(
                            rx.icon("circle_x"),
                            "Anular",
                            color_scheme="red",
                            on_click=lambda: LiquidacionFormState.open_annul_modal(
                                LiquidacionFormState.liquidacion_actual[
                                    "id_liquidacion"
                                ]
                            ),
                            tooltip_content="Anular esta liquidación",
                        ),
                    ),
                    spacing="3",
                ),
                rx.dialog.close(
                    neuro_button("Cerrar", color_scheme="gray", tooltip_content="Cerrar detalle")
                ),
                justify="between",
                margin_top="4",
                width="100%",
            ),
        ),
        open=LiquidacionFormState.show_detail_modal,
        on_open_change=LiquidacionFormState.set_show_detail_modal,
    )

import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores.filtros_state import (
    LiquidacionFiltrosState,
)
from src.presentacion_reflex.state.liquidacion_asesores.form_state import (
    LiquidacionFormState,
)
from src.presentacion_reflex.state.liquidacion_asesores.grid_state import (
    LiquidacionGridState,
)
from src.presentacion_reflex.components.neuro_elements import (
    neuro_select_root,
)
from src.presentacion_reflex import styles


def modal_form() -> rx.Component:
    """Formulario para crear nueva liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    LiquidacionFormState.selected_liquidacion_id > 0,
                    "Editar Liquidación",
                    "Nueva Liquidación de Asesor",
                )
            ),
            rx.dialog.description(
                rx.cond(
                    LiquidacionFormState.selected_liquidacion_id > 0,
                    "Modifique los detalles de la liquidación existente.",
                    "Complete los datos para generar una nueva liquidación de comisiones.",
                )
            ),
            rx.form.root(
                rx.flex(
                    # 2-Column Layout for Basic Info and Properties
                    rx.grid(
                        # Left Column: Basic Info
                        rx.flex(
                            # Asesor
                            rx.box(
                                rx.text(
                                    "Asesor", size="2", weight="bold", margin_bottom="1"
                                ),
                                neuro_select_root(
                                    rx.foreach(
                                        LiquidacionFiltrosState.asesores_options,
                                        lambda asesor: rx.select.item(
                                            asesor["texto"], value=asesor["id"]
                                        ),
                                    ),
                                    name="id_asesor",
                                    required=True,
                                    placeholder="Seleccione un asesor",
                                    value=LiquidacionFormState.form_data["id_asesor"],
                                    on_change=lambda val: LiquidacionFormState.set_form_field(
                                        "id_asesor", val
                                    ),
                                    disabled=LiquidacionFormState.selected_liquidacion_id
                                    > 0,
                                ),
                                width="100%",
                            ),
                            # Período
                            rx.box(
                                rx.text(
                                    "Período (YYYY-MM)",
                                    size="2",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                rx.input(
                                    name="periodo",
                                    type="month",
                                    placeholder="YYYY-MM",
                                    required=True,
                                    width="100%",
                                    value=LiquidacionFormState.form_data["periodo"],
                                    on_change=lambda val: LiquidacionFormState.set_form_field(
                                        "periodo", val
                                    ),
                                    read_only=LiquidacionFormState.selected_liquidacion_id
                                    > 0,
                                    style=styles.NEU_INPUT_STYLE,
                                ),
                                width="100%",
                            ),
                            # Callout informativo de comisión (En lugar de input)
                            rx.callout(
                                "La comisión se calcula automáticamente del % de cada Contrato de Mandato.",
                                icon="info",
                                color_scheme="blue",
                                width="100%",
                            ),
                            direction="column",
                            spacing="4",
                            width="100%",
                        ),
                        # Right Column: Properties List (Table Format)
                        rx.box(
                            rx.text(
                                "Propiedades a Liquidar",
                                size="2",
                                weight="bold",
                                margin_bottom="2",
                            ),
                            rx.scroll_area(
                                rx.cond(
                                    LiquidacionFormState.advisor_properties.length()
                                    > 0,
                                    rx.table.root(
                                        rx.table.header(
                                            rx.table.row(
                                                rx.table.column_header_cell(
                                                    "Dirección"
                                                ),
                                                rx.table.column_header_cell("Canon"),
                                                rx.table.column_header_cell("% Com."),
                                                rx.table.column_header_cell("Comisión"),
                                            )
                                        ),
                                        rx.table.body(
                                            rx.foreach(
                                                LiquidacionFormState.advisor_properties,
                                                lambda prop: rx.table.row(
                                                    rx.table.cell(
                                                        prop["DIRECCION_PROPIEDAD"],
                                                        size="1",
                                                    ),
                                                    rx.table.cell(
                                                        prop[
                                                            "CANON_ARRENDAMIENTO_VIEW"
                                                        ],
                                                        size="1",
                                                    ),
                                                    rx.table.cell(
                                                        prop[
                                                            "COMISION_PORCENTAJE_VIEW"
                                                        ],
                                                        size="1",
                                                        color="blue",
                                                    ),
                                                    rx.table.cell(
                                                        prop["COMISION_MONTO_VIEW"],
                                                        size="1",
                                                        weight="bold",
                                                    ),
                                                ),
                                            )
                                        ),
                                        variant="surface",
                                        size="1",
                                    ),
                                    rx.text(
                                        "No hay propiedades activas o no se ha seleccionado asesor.",
                                        size="1",
                                        color="gray",
                                        style={"fontStyle": "italic"},
                                    ),
                                ),
                                type="always",
                                scrollbars="vertical",
                                style={"height": "250px"},
                            ),
                            # Resumen de Previsualización (LIQ-AUTO-001)
                            rx.cond(
                                LiquidacionFormState.advisor_properties.length() > 0,
                                rx.flex(
                                    rx.badge(
                                        rx.icon("calculator", size=14),
                                        f"Prev. 4x1000: {LiquidacionFormState.preview_4x1000}",
                                        color_scheme="orange",
                                        variant="surface",
                                    ),
                                    rx.badge(
                                        rx.icon("shield-check", size=14),
                                        f"Prev. Seguros: {LiquidacionFormState.preview_seguros_total}",
                                        color_scheme="red",
                                        variant="surface",
                                    ),
                                    spacing="2",
                                    margin_top="2",
                                    justify="end",
                                ),
                            ),
                            padding="3",
                            background_color="var(--gray-2)",
                            border_radius="md",
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.separator(size="4"),
                    # Bonuses Section
                    rx.box(
                        rx.text(
                            "Otros Ingresos / Bonificaciones",
                            size="2",
                            weight="bold",
                            margin_bottom="2",
                        ),
                        rx.grid(
                            rx.select.root(
                                rx.select.trigger(placeholder="Tipo"),
                                rx.select.content(
                                    rx.select.group(
                                        rx.select.item(
                                            "Venta Propiedad", value="Venta Propiedad"
                                        ),
                                        rx.select.item("Captación", value="Captación"),
                                        rx.select.item(
                                            "Bono Cumplimiento",
                                            value="Bono Cumplimiento",
                                        ),
                                        rx.select.item("Incentivo", value="Incentivo"),
                                        rx.select.item("Otros", value="Otros"),
                                    )
                                ),
                                value=LiquidacionFormState.temp_bonus["tipo"],
                                on_change=lambda val: LiquidacionFormState.set_temp_bonus_field(
                                    "tipo", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Descripción",
                                value=LiquidacionFormState.temp_bonus["descripcion"],
                                on_change=lambda val: LiquidacionFormState.set_temp_bonus_field(
                                    "descripcion", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Valor (+)",
                                type="number",
                                value=LiquidacionFormState.temp_bonus["valor"],
                                on_change=lambda val: LiquidacionFormState.set_temp_bonus_field(
                                    "valor", val
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("plus"),
                                "Agregar",
                                on_click=LiquidacionFormState.add_temp_bonus,
                                type="button",
                                variant="soft",
                                color_scheme="green",
                            ),
                            columns="4",
                            spacing="2",
                            width="100%",
                        ),
                        # List of existing bonuses (saved in DB) - only in EDIT mode
                        rx.cond(
                            (LiquidacionFormState.selected_liquidacion_id > 0)
                            & (LiquidacionFormState.existing_bonuses.length() > 0),
                            rx.box(
                                rx.text(
                                    "Bonificaciones Guardadas:",
                                    size="1",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acción"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            LiquidacionFormState.existing_bonuses,
                                            lambda b: rx.table.row(
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(
                                                    b["valor_view"],
                                                    color="green",
                                                    weight="bold",
                                                ),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda: LiquidacionFormState.eliminar_bonificacion(
                                                            b["id_bonificacion"]
                                                        ),
                                                        variant="ghost",
                                                        color_scheme="red",
                                                        size="1",
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                    variant="surface",
                                    margin_top="2",
                                    margin_bottom="2",
                                ),
                            ),
                        ),
                        # List of new bonuses (temporary - not yet saved)
                        rx.cond(
                            LiquidacionFormState.new_bonuses.length() > 0,
                            rx.box(
                                # rx.text("Bonificaciones Nuevas (Por Guardar):", size="1", weight="bold", margin_bottom="1"),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acción"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            LiquidacionFormState.new_bonuses,
                                            lambda b: rx.table.row(
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(
                                                    "$",
                                                    b["valor"],
                                                    color="green",
                                                    weight="bold",
                                                ),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda: LiquidacionFormState.remove_temp_bonus(
                                                            b
                                                        ),
                                                        variant="ghost",
                                                        color_scheme="red",
                                                        size="1",
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                    variant="surface",
                                    margin_top="2",
                                )
                            ),
                        ),
                        width="100%",
                        padding="3",
                        border="1px solid var(--gray-4)",
                        border_radius="md",
                    ),
                    rx.separator(size="4"),
                    # Discounts Section
                    rx.box(
                        rx.text(
                            "Descuentos Adicionales (Opcional)",
                            size="2",
                            weight="bold",
                            margin_bottom="2",
                        ),
                        rx.grid(
                            rx.select.root(
                                rx.select.trigger(placeholder="Tipo de Descuento"),
                                rx.select.content(
                                    rx.select.group(
                                        rx.select.item("Debug", value="Debug"),
                                        rx.select.item("Otros", value="Otros"),
                                        rx.select.item("Préstamo", value="Préstamo"),
                                    )
                                ),
                                value=LiquidacionFormState.temp_discount["tipo"],
                                on_change=lambda val: LiquidacionFormState.set_temp_discount_field(
                                    "tipo", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Descripción",
                                value=LiquidacionFormState.temp_discount["descripcion"],
                                on_change=lambda val: LiquidacionFormState.set_temp_discount_field(
                                    "descripcion", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Valor",
                                type="number",
                                value=LiquidacionFormState.temp_discount["valor"],
                                on_change=lambda val: LiquidacionFormState.set_temp_discount_field(
                                    "valor", val
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("plus"),
                                "Agregar",
                                on_click=LiquidacionFormState.add_temp_discount,
                                type="button",
                                variant="soft",
                            ),
                            columns="4",
                            spacing="2",
                            width="100%",
                        ),
                        # List of existing discounts (saved in DB) - only in EDIT mode
                        rx.cond(
                            (LiquidacionFormState.selected_liquidacion_id > 0)
                            & (LiquidacionFormState.existing_discounts.length() > 0),
                            rx.box(
                                rx.text(
                                    "Descuentos Guardados:",
                                    size="1",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acción"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            LiquidacionFormState.existing_discounts,
                                            lambda d: rx.table.row(
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell(d["valor_view"]),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda: LiquidacionFormState.eliminar_descuento(
                                                            d["id_descuento"]
                                                        ),
                                                        variant="ghost",
                                                        color_scheme="red",
                                                        size="1",
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                    variant="surface",
                                    margin_top="2",
                                    margin_bottom="2",
                                ),
                            ),
                        ),
                        # List of new discounts (temporary - not yet saved)
                        rx.cond(
                            LiquidacionFormState.new_discounts.length() > 0,
                            rx.box(
                                rx.text(
                                    "Descuentos Nuevos (Por Guardar):",
                                    size="1",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acción"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            LiquidacionFormState.new_discounts,
                                            lambda d: rx.table.row(
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell("$", d["valor"]),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda: LiquidacionFormState.remove_temp_discount(
                                                            d
                                                        ),
                                                        variant="ghost",
                                                        color_scheme="red",
                                                        size="1",
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                    variant="surface",
                                    margin_top="2",
                                ),
                            ),
                        ),
                        width="100%",
                        padding="3",
                        border="1px solid var(--gray-4)",
                        border_radius="md",
                    ),
                    # Observaciones
                    rx.box(
                        rx.text(
                            "Observaciones Generales",
                            size="2",
                            weight="bold",
                            margin_bottom="1",
                        ),
                        rx.text_area(
                            name="observaciones",
                            placeholder="Observaciones opcionales...",
                            width="100%",
                            value=LiquidacionFormState.form_data["observaciones"],
                            on_change=lambda val: LiquidacionFormState.set_form_field(
                                "observaciones", val
                            ),
                        ),
                        width="100%",
                    ),
                    direction="column",
                    spacing="4",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            type="button",
                            on_click=LiquidacionFormState.close_modal,
                        )
                    ),
                    rx.button(
                        rx.cond(
                            LiquidacionFormState.selected_liquidacion_id > 0,
                            "Guardar Cambios",
                            "Generar Liquidación",
                        ),
                        type="submit",
                        loading=LiquidacionGridState.is_loading,
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=LiquidacionFormState.handle_save_form,
            ),
            # Error Message
            rx.cond(
                LiquidacionFormState.error_message != "",
                rx.callout(
                    LiquidacionFormState.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    role="alert",
                    margin_top="2",
                ),
            ),
            max_width="800px",
        ),
        open=LiquidacionFormState.show_form_modal,
        on_open_change=LiquidacionFormState.set_show_form_modal,
    )

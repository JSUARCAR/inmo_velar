import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores_state import LiquidacionAsesoresState


def modal_form() -> rx.Component:
    """Formulario para crear nueva liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    LiquidacionAsesoresState.selected_liquidacion_id > 0,
                    "Editar Liquidación",
                    "Nueva Liquidación de Asesor",
                )
            ),
            rx.dialog.description(
                rx.cond(
                    LiquidacionAsesoresState.selected_liquidacion_id > 0,
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
                                rx.text("Asesor", size="2", weight="bold", margin_bottom="1"),
                                rx.select.root(
                                    rx.select.trigger(placeholder="Seleccione un asesor"),
                                    rx.select.content(
                                        rx.foreach(
                                            LiquidacionAsesoresState.asesores_options,
                                            lambda asesor: rx.select.item(
                                                asesor["texto"], value=asesor["id"]
                                            ),
                                        )
                                    ),
                                    name="id_asesor",
                                    required=True,
                                    width="100%",
                                    value=LiquidacionAsesoresState.form_data["id_asesor"],
                                    on_change=lambda val: LiquidacionAsesoresState.set_form_field(
                                        "id_asesor", val
                                    ),
                                    disabled=LiquidacionAsesoresState.selected_liquidacion_id > 0,
                                ),
                                width="100%",
                            ),
                            # Período
                            rx.box(
                                rx.text(
                                    "Período (YYYY-MM)", size="2", weight="bold", margin_bottom="1"
                                ),
                                rx.input(
                                    name="periodo",
                                    type="month",
                                    placeholder="YYYY-MM",
                                    required=True,
                                    width="100%",
                                    value=LiquidacionAsesoresState.form_data["periodo"],
                                    on_change=lambda val: LiquidacionAsesoresState.set_form_field(
                                        "periodo", val
                                    ),
                                    read_only=LiquidacionAsesoresState.selected_liquidacion_id > 0,
                                ),
                                width="100%",
                            ),
                            # Porcentaje
                            rx.box(
                                rx.text(
                                    "Porcentaje Comisión (%)",
                                    size="2",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                rx.input(
                                    name="porcentaje_comision",
                                    placeholder="Ej: 5.0",
                                    required=True,
                                    type="number",
                                    step="0.1",
                                    min="0",
                                    max="100",
                                    width="100%",
                                    value=LiquidacionAsesoresState.form_data["porcentaje_comision"],
                                    on_change=lambda val: LiquidacionAsesoresState.set_form_field(
                                        "porcentaje_comision", val
                                    ),
                                ),
                                width="100%",
                            ),
                            direction="column",
                            spacing="4",
                            width="100%",
                        ),
                        # Right Column: Properties List
                        rx.box(
                            rx.text(
                                "Propiedades a Liquidar", size="2", weight="bold", margin_bottom="2"
                            ),
                            rx.scroll_area(
                                rx.flex(
                                    rx.cond(
                                        LiquidacionAsesoresState.advisor_properties.length() > 0,
                                        rx.foreach(
                                            LiquidacionAsesoresState.advisor_properties,
                                            lambda prop: rx.card(
                                                rx.flex(
                                                    rx.text(
                                                        prop["DIRECCION_PROPIEDAD"],
                                                        size="1",
                                                        weight="bold",
                                                    ),
                                                    rx.text(
                                                        f"Canon: ${prop['CANON_ARRENDAMIENTO']}",
                                                        size="1",
                                                        color="gray",
                                                    ),
                                                    direction="column",
                                                    spacing="1",
                                                ),
                                                padding="2",
                                                variant="classic",
                                            ),
                                        ),
                                        rx.text(
                                            "No hay propiedades activas o no se ha seleccionado asesor.",
                                            size="1",
                                            color="gray",
                                            style={"fontStyle": "italic"},
                                        ),
                                    ),
                                    direction="column",
                                    spacing="2",
                                ),
                                type="always",
                                scrollbars="vertical",
                                style={"height": "200px"},
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
                                        rx.select.item("Venta Propiedad", value="Venta Propiedad"),
                                        rx.select.item("Captación", value="Captación"),
                                        rx.select.item(
                                            "Bono Cumplimiento", value="Bono Cumplimiento"
                                        ),
                                        rx.select.item("Incentivo", value="Incentivo"),
                                        rx.select.item("Otros", value="Otros"),
                                    )
                                ),
                                value=LiquidacionAsesoresState.temp_bonus["tipo"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_bonus_field(
                                    "tipo", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Descripción",
                                value=LiquidacionAsesoresState.temp_bonus["descripcion"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_bonus_field(
                                    "descripcion", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Valor (+)",
                                type="number",
                                value=LiquidacionAsesoresState.temp_bonus["valor"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_bonus_field(
                                    "valor", val
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("plus"),
                                "Agregar",
                                on_click=LiquidacionAsesoresState.add_temp_bonus,
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
                            (LiquidacionAsesoresState.selected_liquidacion_id > 0)
                            & (LiquidacionAsesoresState.existing_bonuses.length() > 0),
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
                                            LiquidacionAsesoresState.existing_bonuses,
                                            lambda b: rx.table.row(
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(
                                                    f"${b['valor']:,}", color="green", weight="bold"
                                                ),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda _, id_b=b[
                                                            "id_bonificacion"
                                                        ]: LiquidacionAsesoresState.eliminar_bonificacion(
                                                            id_b
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
                            LiquidacionAsesoresState.new_bonuses.length() > 0,
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
                                            LiquidacionAsesoresState.new_bonuses,
                                            lambda b: rx.table.row(
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(
                                                    f"${b['valor']}", color="green", weight="bold"
                                                ),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda _, item=b: LiquidacionAsesoresState.remove_temp_bonus(
                                                            item
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
                                value=LiquidacionAsesoresState.temp_discount["tipo"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_discount_field(
                                    "tipo", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Descripción",
                                value=LiquidacionAsesoresState.temp_discount["descripcion"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_discount_field(
                                    "descripcion", val
                                ),
                                width="100%",
                            ),
                            rx.input(
                                placeholder="Valor",
                                type="number",
                                value=LiquidacionAsesoresState.temp_discount["valor"],
                                on_change=lambda val: LiquidacionAsesoresState.set_temp_discount_field(
                                    "valor", val
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("plus"),
                                "Agregar",
                                on_click=LiquidacionAsesoresState.add_temp_discount,
                                type="button",
                                variant="soft",
                            ),
                            columns="4",
                            spacing="2",
                            width="100%",
                        ),
                        # List of existing discounts (saved in DB) - only in EDIT mode
                        rx.cond(
                            (LiquidacionAsesoresState.selected_liquidacion_id > 0)
                            & (LiquidacionAsesoresState.existing_discounts.length() > 0),
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
                                            LiquidacionAsesoresState.existing_discounts,
                                            lambda d: rx.table.row(
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell(f"${d['valor']:,}"),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda _, id_d=d[
                                                            "id_descuento"
                                                        ]: LiquidacionAsesoresState.eliminar_descuento(
                                                            id_d
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
                            LiquidacionAsesoresState.new_discounts.length() > 0,
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
                                            LiquidacionAsesoresState.new_discounts,
                                            lambda d: rx.table.row(
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell(f"${d['valor']}"),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon("trash", size=16),
                                                        on_click=lambda _, item=d: LiquidacionAsesoresState.remove_temp_discount(
                                                            item
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
                            "Observaciones Generales", size="2", weight="bold", margin_bottom="1"
                        ),
                        rx.text_area(
                            name="observaciones",
                            placeholder="Observaciones opcionales...",
                            width="100%",
                            value=LiquidacionAsesoresState.form_data["observaciones"],
                            on_change=lambda val: LiquidacionAsesoresState.set_form_field(
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
                            on_click=LiquidacionAsesoresState.close_form_modal,
                        )
                    ),
                    rx.button(
                        rx.cond(
                            LiquidacionAsesoresState.selected_liquidacion_id > 0,
                            "Guardar Cambios",
                            "Generar Liquidación",
                        ),
                        type="submit",
                        loading=LiquidacionAsesoresState.is_loading,
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=LiquidacionAsesoresState.handle_save_form,
            ),
            # Error Message
            rx.cond(
                LiquidacionAsesoresState.error_message != "",
                rx.callout(
                    LiquidacionAsesoresState.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    margin_top="2",
                ),
            ),
            max_width="800px",
        ),
        open=LiquidacionAsesoresState.show_form_modal,
        on_open_change=LiquidacionAsesoresState.set_show_form_modal,
    )

"""
Formulario modal para Contratos de Arrendamiento - Reflex
"""

import reflex as rx

from src.presentacion_reflex.components.document_manager_elite import document_manager_elite
from src.presentacion_reflex.components.image_gallery import image_gallery
from src.presentacion_reflex.state.contratos_state import ContratosState


def searchable_select(
    label: str,
    placeholder: str,
    value_label: rx.Var[str],
    search_value: rx.Var[str],
    menu_open: rx.Var[bool],
    filtered_options: rx.Var[list],
    on_change_search: callable,
    on_toggle_menu: callable,
    on_select: callable,
) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="bold"),
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.cond(
                        value_label == "",
                        rx.text(placeholder, color="gray"),
                        rx.text(value_label, color="black"),
                    ),
                    rx.icon("chevron-down", size=16),
                    variant="surface",
                    width="100%",
                    justify="between",
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    rx.input(
                        placeholder="Buscar...",
                        value=search_value,
                        on_change=on_change_search,
                        autofocus=True,
                        width="100%",
                        variant="soft",
                        size="1",
                    ),
                    rx.scroll_area(
                         rx.vstack(
                             rx.foreach(
                                filtered_options,
                                lambda opt: rx.cond(
                                    opt[0] != "",
                                    rx.box(
                                        rx.text(opt[0], size="2"),
                                        width="100%",
                                        padding_x="3",
                                        padding_y="2",
                                        _hover={"bg": "var(--gray-4)", "cursor": "pointer"},
                                        on_click=lambda: on_select(opt[1], opt[0]),
                                    )
                                )
                             ),
                             width="100%",
                             spacing="0",
                        ),
                        type="auto",
                        scrollbars="vertical",
                        style={"max_height": "200px"},
                        width="100%",
                    ),
                    padding="2",
                    width="320px",
                    spacing="2",
                ),
            ),
            open=menu_open,
            on_open_change=on_toggle_menu,
        ),
        spacing="1",
        width="100%",
    )


def contrato_arrendamiento_form() -> rx.Component:
    """
    Formulario modal para crear/editar contratos de arrendamiento.
    Estilo Elite: Header con gradiente, inputs con iconos, botones estilizados.
    """
    return rx.dialog.root(
        rx.dialog.content(
            # --- ELITE HEADER ---
            rx.vstack(
                rx.hstack(
                    rx.icon("key", size=24, color="var(--blue-9)"),
                    rx.dialog.title(
                        rx.cond(
                            ContratosState.modal_mode == "crear_arrendamiento",
                            "Nuevo Contrato de Arrendamiento",
                            "Editar Contrato de Arrendamiento",
                        ),
                        size="6",
                        weight="bold",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.dialog.description(
                    "Complete la información del contrato de arrendamiento.",
                    size="2",
                    color="gray",
                ),
                rx.separator(),
                spacing="3",
                padding_bottom="4",
            ),
            # Mensaje de error
            rx.cond(
                ContratosState.error_message != "",
                rx.callout(
                    ContratosState.error_message,
                    icon="circle-alert",
                    color="red",
                    role="alert",
                    margin_bottom="1rem",
                ),
            ),
            # Tabs Structure
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Datos del Contrato", value="datos"),
                    rx.tabs.trigger("Documentos", value="documentos"),
                ),
                # TAB 1: DATOS (Formulario Existente)
                rx.tabs.content(
                    rx.form(
                        rx.vstack(
                            # Propiedad (requerido)
                            searchable_select(
                                "Propiedad *",
                                "Seleccione una propiedad",
                                ContratosState.propiedad_selected_label,
                                ContratosState.propiedad_search,
                                ContratosState.propiedad_menu_open,
                                ContratosState.filtered_propiedades_options,
                                ContratosState.set_propiedad_search,
                                ContratosState.toggle_propiedad_menu,
                                ContratosState.select_propiedad,
                            ),
                            # Arrendatario (requerido)
                            searchable_select(
                                "Arrendatario *",
                                "Seleccione el arrendatario",
                                ContratosState.arrendatario_selected_label,
                                ContratosState.arrendatario_search,
                                ContratosState.arrendatario_menu_open,
                                ContratosState.filtered_arrendatarios_options,
                                ContratosState.set_arrendatario_search,
                                ContratosState.toggle_arrendatario_menu,
                                ContratosState.select_arrendatario,
                            ),
                            # Codeudor (opcional)
                            searchable_select(
                                "Codeudor (opcional)",
                                "Seleccione el codeudor (opcional)",
                                ContratosState.codeudor_selected_label,
                                ContratosState.codeudor_search,
                                ContratosState.codeudor_menu_open,
                                ContratosState.filtered_codeudores_options,
                                ContratosState.set_codeudor_search,
                                ContratosState.toggle_codeudor_menu,
                                ContratosState.select_codeudor,
                            ),
                            # Fechas (en dos columnas)
                            rx.grid(
                                rx.vstack(
                                    rx.text("Fecha Inicio *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("calendar", size=16)),
                                        type="date",
                                        name="fecha_inicio",
                                        required=True,
                                        value=ContratosState.form_data.get("fecha_inicio", ""),
                                        on_change=ContratosState.on_change_fecha_inicio,
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Fecha Fin *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("calendar-check", size=16)),
                                        type="date",
                                        name="fecha_fin",
                                        required=True,
                                        value=ContratosState.form_data.get("fecha_fin", ""),
                                        on_change=ContratosState.on_change_fecha_fin,
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            # Duración en meses
                            rx.vstack(
                                rx.text("Duración (meses) *", size="2", weight="bold"),
                                rx.input(
                                    rx.input.slot(rx.icon("clock", size=16)),
                                    type="number",
                                    name="duracion_meses",
                                    placeholder="12",
                                    read_only=True,
                                    required=True,
                                    min=1,
                                    value=ContratosState.form_data.get("duracion_meses", "12"),
                                    variant="surface",
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                            ),
                            # Canon, Deposito y Fecha de Pago
                            rx.grid(
                                rx.vstack(
                                    rx.text("Canon Arrendamiento *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("dollar-sign", size=16)),
                                        type="number",
                                        name="canon",
                                        placeholder="1000000",
                                        required=True,
                                        min=0,
                                        value=ContratosState.form_data.get("canon", ""),
                                        on_change=ContratosState.on_change_canon_arriendo,
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Depósito", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("wallet", size=16)),
                                        type="number",
                                        name="deposito",
                                        placeholder="0",
                                        value=ContratosState.form_data.get("deposito", "0"),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "deposito", v
                                        ),
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Fecha de Pago *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("calendar-days", size=16)),
                                        type="text",
                                        name="fecha_pago",
                                        placeholder="Ej: Día 5 de cada mes",
                                        required=True,
                                        value=ContratosState.form_data.get("fecha_pago", ""),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "fecha_pago", v
                                        ),
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                columns=rx.breakpoints(initial="1", sm="3"),
                                spacing="4",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        # Botones (Footer)
                        rx.flex(
                            rx.dialog.close(
                                rx.button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                ),
                            ),
                            rx.button(
                                rx.cond(
                                    ContratosState.is_loading,
                                    rx.spinner(size="1"),
                                    rx.hstack(
                                        rx.icon("save", size=18),
                                        rx.text("Guardar Contrato"),
                                        spacing="2",
                                    ),
                                ),
                                type="submit",
                                disabled=ContratosState.is_loading,
                                style={
                                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                    "color": "white",
                                    "_hover": {
                                        "opacity": 0.9,
                                        "transform": "translateY(-1px)",
                                    },
                                },
                            ),
                            spacing="3",
                            margin_top="2rem",
                            justify="end",
                            width="100%",
                        ),
                        on_submit=ContratosState.save_contrato,
                        reset_on_submit=True,
                    ),
                    value="datos",
                    padding_top="4",
                ),
                # TAB 2: DOCUMENTOS
                rx.tabs.content(
                    rx.vstack(
                        rx.cond(
                            ContratosState.modal_mode == "crear_arrendamiento",
                            rx.callout(
                                "Guarde el contrato primero para subir documentos.",
                                icon="info",
                                color_scheme="blue",
                                width="100%",
                            ),
                            rx.vstack(
                                document_manager_elite(ContratosState),
                                rx.separator(),
                                image_gallery(
                                    documentos=ContratosState.documentos,
                                    on_delete=ContratosState.eliminar_documento,
                                ),
                                spacing="4",
                                width="100%",
                            ),
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    value="documentos",
                    padding_top="4",
                ),
                default_value="datos",
                width="100%",
            ),
            max_width="750px",
            border_radius="16px",
            padding="2rem",
        ),
        open=rx.cond(
            (ContratosState.modal_open)
            & (
                (ContratosState.modal_mode == "crear_arrendamiento")
                | (ContratosState.modal_mode == "editar_arrendamiento")
            ),
            True,
            False,
        ),
        on_open_change=ContratosState.close_modal,
    )

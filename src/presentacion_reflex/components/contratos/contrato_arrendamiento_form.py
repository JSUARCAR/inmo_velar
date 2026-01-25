"""
Formulario modal para Contratos de Arrendamiento - Reflex
"""

import reflex as rx

from src.presentacion_reflex.components.document_manager_elite import document_manager_elite
from src.presentacion_reflex.components.image_gallery import image_gallery
from src.presentacion_reflex.state.contratos_state import ContratosState


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
                            rx.vstack(
                                rx.text("Propiedad *", size="2", weight="bold"),
                                rx.select.root(
                                    rx.select.trigger(
                                        rx.icon("home", size=16),
                                        placeholder="Seleccione una propiedad",
                                        variant="surface",
                                    ),
                                    rx.select.content(
                                        rx.select.group(
                                            rx.foreach(
                                                ContratosState.propiedades_arriendo_select_options,
                                                lambda opcion: rx.select.item(
                                                    opcion[0], value=opcion[1]
                                                ),
                                            )
                                        )
                                    ),
                                    name="id_propiedad",
                                    value=ContratosState.form_data.get("id_propiedad", ""),
                                    on_change=ContratosState.on_change_propiedad_arriendo,
                                    width="100%",
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                            ),
                            # Arrendatario (requerido)
                            rx.vstack(
                                rx.text("Arrendatario *", size="2", weight="bold"),
                                rx.select.root(
                                    rx.select.trigger(
                                        rx.icon("user", size=16),
                                        placeholder="Seleccione el arrendatario",
                                        variant="surface",
                                    ),
                                    rx.select.content(
                                        rx.select.group(
                                            rx.foreach(
                                                ContratosState.arrendatarios_select_options,
                                                lambda opcion: rx.select.item(
                                                    opcion[0], value=opcion[1]
                                                ),
                                            )
                                        )
                                    ),
                                    name="id_arrendatario",
                                    value=ContratosState.form_data.get("id_arrendatario", ""),
                                    on_change=lambda v: ContratosState.set_form_field(
                                        "id_arrendatario", v
                                    ),
                                    width="100%",
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                            ),
                            # Codeudor (opcional)
                            rx.vstack(
                                rx.text("Codeudor (opcional)", size="2", weight="bold"),
                                rx.select.root(
                                    rx.select.trigger(
                                        rx.icon("users", size=16),
                                        placeholder="Seleccione el codeudor (opcional)",
                                        variant="surface",
                                    ),
                                    rx.select.content(
                                        rx.select.group(
                                            rx.foreach(
                                                ContratosState.codeudores_select_options,
                                                lambda opcion: rx.select.item(
                                                    opcion[0], value=opcion[1]
                                                ),
                                            )
                                        )
                                    ),
                                    name="id_codeudor",
                                    value=ContratosState.form_data.get("id_codeudor", ""),
                                    on_change=lambda v: ContratosState.set_form_field(
                                        "id_codeudor", v
                                    ),
                                    width="100%",
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
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
                            # Canon y Depósito
                            rx.grid(
                                rx.vstack(
                                    rx.text("Canon Arrendamiento *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("dollar-sign", size=16)),
                                        type="number",
                                        name="canon",
                                        placeholder="1000000",
                                        read_only=True,
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
                                        rx.input.slot(rx.icon("banknote", size=16)),
                                        type="number",
                                        name="deposito",
                                        placeholder="1000000",
                                        min=0,
                                        value=ContratosState.form_data.get("deposito", "0"),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "deposito", v
                                        ),
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                columns="2",
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

"""
Formulario modal para Contratos de Mandato - Reflex
"""

import reflex as rx

from src.presentacion_reflex.components.document_manager_elite import document_manager_elite
from src.presentacion_reflex.components.image_gallery import image_gallery
from src.presentacion_reflex.state.contratos_state import ContratosState


def contrato_mandato_form() -> rx.Component:
    """
    Formulario modal para crear/editar contratos de mandato.
    Estilo Elite: Header con gradiente, inputs con iconos, botones estilizados.
    """
    return rx.dialog.root(
        rx.dialog.content(
            # --- ELITE HEADER ---
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", size=24, color="var(--blue-9)"),
                    rx.dialog.title(
                        rx.cond(
                            ContratosState.modal_mode == "crear_mandato",
                            "Nuevo Contrato de Mandato",
                            "Editar Contrato de Mandato",
                        ),
                        size="6",
                        weight="bold",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.dialog.description(
                    "Complete la información del contrato de mandato.",
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
                                                rx.cond(
                                                    ContratosState.modal_mode == "crear_mandato",
                                                    ContratosState.propiedades_mandato_libre_select_options,
                                                    ContratosState.propiedades_select_options,
                                                ),
                                                lambda opcion: rx.select.item(
                                                    opcion[0], value=opcion[1]
                                                ),
                                            )
                                        )
                                    ),
                                    name="id_propiedad",
                                    required=True,
                                    value=ContratosState.form_data.get("id_propiedad", ""),
                                    on_change=ContratosState.on_change_propiedad,
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                            ),
                            # Propietario y Asesor (2 columnas)
                            rx.grid(
                                rx.vstack(
                                    rx.text("Propietario *", size="2", weight="bold"),
                                    rx.select.root(
                                        rx.select.trigger(
                                            rx.icon("user", size=16),
                                            placeholder="Seleccione el propietario",
                                            variant="surface",
                                        ),
                                        rx.select.content(
                                            rx.select.group(
                                                rx.foreach(
                                                    ContratosState.propietarios_select_options,
                                                    lambda opcion: rx.select.item(
                                                        opcion[0], value=opcion[1]
                                                    ),
                                                )
                                            )
                                        ),
                                        name="id_propietario",
                                        required=True,
                                        value=ContratosState.form_data.get("id_propietario", ""),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "id_propietario", v
                                        ),
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Asesor *", size="2", weight="bold"),
                                    rx.select.root(
                                        rx.select.trigger(
                                            rx.icon("briefcase", size=16),
                                            placeholder="Seleccione el asesor",
                                            variant="surface",
                                        ),
                                        rx.select.content(
                                            rx.select.group(
                                                rx.foreach(
                                                    ContratosState.asesores_select_options,
                                                    lambda opcion: rx.select.item(
                                                        opcion[0], value=opcion[1]
                                                    ),
                                                )
                                            )
                                        ),
                                        name="id_asesor",
                                        required=True,
                                        value=ContratosState.form_data.get("id_asesor", ""),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "id_asesor", v
                                        ),
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            # Fechas (2 columnas)
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
                            # Duración y Canon (2 columnas)
                            rx.grid(
                                rx.vstack(
                                    rx.text("Duración (meses) *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("clock", size=16)),
                                        type="number",
                                        name="duracion_meses",
                                        placeholder="12",
                                        required=True,
                                        min=1,
                                        read_only=True,
                                        value=ContratosState.form_data.get("duracion_meses", "12"),
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("Canon Estimado *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("dollar-sign", size=16)),
                                        type="number",
                                        name="canon",
                                        placeholder="1000000",
                                        required=True,
                                        min=0,
                                        read_only=True,
                                        value=ContratosState.form_data.get("canon", ""),
                                        variant="surface",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            # Comisión e IVA (2 columnas)
                            rx.grid(
                                rx.vstack(
                                    rx.text("Comisión (%) *", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("percent", size=16)),
                                        type="number",
                                        name="comision_porcentaje",
                                        placeholder="10",
                                        required=True,
                                        min=0,
                                        max=100,
                                        step="0.01",
                                        value=ContratosState.form_data.get(
                                            "comision_porcentaje", "10"
                                        ),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "comision_porcentaje", v
                                        ),
                                        variant="surface",
                                    ),
                                    rx.text(
                                        "Base 100 (10 = 10%)",
                                        size="1",
                                        color="gray",
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.text("IVA (%)", size="2", weight="bold"),
                                    rx.input(
                                        rx.input.slot(rx.icon("percent", size=16)),
                                        type="number",
                                        name="iva_porcentaje",
                                        placeholder="19",
                                        min=0,
                                        max=100,
                                        step="0.01",
                                        value=ContratosState.form_data.get("iva_porcentaje", "19"),
                                        on_change=lambda v: ContratosState.set_form_field(
                                            "iva_porcentaje", v
                                        ),
                                        variant="surface",
                                    ),
                                    rx.text(
                                        "Base 100 (19 = 19%)",
                                        size="1",
                                        color="gray",
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
                            ContratosState.modal_mode == "crear_mandato",
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
                (ContratosState.modal_mode == "crear_mandato")
                | (ContratosState.modal_mode == "editar_mandato")
            ),
            True,
            False,
        ),
        on_open_change=ContratosState.close_modal,
    )

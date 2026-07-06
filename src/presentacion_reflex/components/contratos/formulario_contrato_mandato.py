"""
Formulario modal para Contratos de Mandato - Reflex
"""

import reflex as rx


from src.presentacion_reflex.components.document_manager_elite import (
    document_manager_elite,
)
from src.presentacion_reflex.components.image_gallery import image_gallery
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import neuro_floating_input, neuro_floating_select, neuro_button
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.shared.floating_label import floating_input, floating_select
from src.presentacion_reflex.components.shared.searchable_select import (
    searchable_select,
)


def formulario_contrato_mandato() -> rx.Component:
    """
    Formulario modal para crear/editar contratos de mandato.
    Estilo Elite: Header con gradiente, inputs con iconos, botones estilizados.
    """
    return rx.dialog.root(
        rx.dialog.content(
            # --- ELITE HEADER ---
            rx.vstack(
                rx.hstack(
                    rx.icon("file-text", size=24, color="var(--brand-primary)"),
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
                    icon="triangle-alert",
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
                            # Propietario y Asesor (2 columnas)
                            rx.grid(
                                searchable_select(
                                    "Propietario *",
                                    "Seleccione el propietario",
                                    ContratosState.propietario_selected_label,
                                    ContratosState.propietario_search,
                                    ContratosState.propietario_menu_open,
                                    ContratosState.filtered_propietarios_options,
                                    ContratosState.set_propietario_search,
                                    ContratosState.toggle_propietario_menu,
                                    ContratosState.select_propietario,
                                ),
                                searchable_select(
                                    "Asesor *",
                                    "Seleccione el asesor",
                                    ContratosState.asesor_selected_label,
                                    ContratosState.asesor_search,
                                    ContratosState.asesor_menu_open,
                                    ContratosState.filtered_asesores_options,
                                    ContratosState.set_asesor_search,
                                    ContratosState.toggle_asesor_menu,
                                    ContratosState.select_asesor,
                                ),
                                columns=rx.breakpoints(initial="1", sm="2"),
                                spacing="4",
                                width="100%",
                            ),
                            # Fechas (3 columnas en SVG)
                            rx.vstack(
                                rx.text(
                                    "Fechas",
                                    size="2",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                                rx.grid(
                                    neuro_floating_input(
                                        label="Fecha Inicio",
                                        type="date",
                                        name="fecha_inicio",
                                        required=True,
                                        value=ContratosState.form_data["fecha_inicio"],
                                        on_change=ContratosState.on_change_fecha_inicio,
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="Fecha Fin",
                                        type="date",
                                        name="fecha_fin",
                                        required=True,
                                        value=ContratosState.form_data["fecha_fin"],
                                        on_change=ContratosState.on_change_fecha_fin,
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="Duración (meses)",
                                        type="number",
                                        name="duracion_meses",
                                        placeholder="12",
                                        required=True,
                                        min=1,
                                        read_only=True,
                                        value=ContratosState.form_data["duracion_meses"],
                                        width="100%",
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="3"),
                                    spacing="4",
                                    width="100%",
                                ),
                                width="100%",
                                align_items="start",
                            ),
                            # Canon y Fecha de Pago (2 columnas)
                            rx.vstack(
                                rx.text(
                                    "Canon y pago",
                                    size="2",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                                rx.grid(
                                    neuro_floating_input(
                                        label="Canon Estimado",
                                        type="number",
                                        name="canon",
                                        placeholder="1000000",
                                        required=True,
                                        min=0,
                                        read_only=True,
                                        value=ContratosState.form_data["canon"],
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="Fecha de Pago",
                                        type="text",
                                        name="fecha_pago",
                                        placeholder="Ej: Día 5 de cada mes",
                                        required=True,
                                        read_only=True,
                                        value=ContratosState.form_data["fecha_pago"],
                                        on_change=lambda v: ContratosState.set_form_field("fecha_pago", v),
                                        width="100%",
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="2"),
                                    spacing="4",
                                    width="100%",
                                ),
                                width="100%",
                                align_items="start",
                            ),
                            # Comisión e IVA (2 columnas)
                            rx.vstack(
                                rx.text(
                                    "Comisión e IVA",
                                    size="2",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                                rx.grid(
                                    neuro_floating_input(
                                        label="Comisión (%)",
                                        type="number",
                                        name="comision_porcentaje",
                                        placeholder="10",
                                        required=True,
                                        min=0,
                                        max=100,
                                        step="0.01",
                                        value=ContratosState.form_data["comision_porcentaje"],
                                        on_change=lambda v: ContratosState.set_form_field("comision_porcentaje", v),
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="IVA (%)",
                                        type="number",
                                        name="iva_porcentaje",
                                        placeholder="19",
                                        min=0,
                                        max=100,
                                        step="0.01",
                                        value=ContratosState.form_data["iva_porcentaje"],
                                        on_change=lambda v: ContratosState.set_form_field("iva_porcentaje", v),
                                        width="100%",
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="2"),
                                    spacing="4",
                                    width="100%",
                                ),
                                width="100%",
                                align_items="start",
                            ),
                            # Información para Pagos (Nueva sección migrada)
                            rx.vstack(
                                rx.text(
                                    "Información para Pagos",
                                    size="2",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                                rx.grid(
                                    neuro_floating_input(
                                        label="Banco",
                                        type="text",
                                        name="banco_propietario",
                                        placeholder="Ej: Bancolombia",
                                        value=ContratosState.form_data["banco_propietario"],
                                        on_change=lambda v: ContratosState.set_form_field("banco_propietario", v.upper()),
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="Número de Cuenta",
                                        type="text",
                                        name="numero_cuenta_propietario",
                                        placeholder="Ej: 123456789",
                                        value=ContratosState.form_data["numero_cuenta_propietario"],
                                        on_change=lambda v: ContratosState.set_form_field("numero_cuenta_propietario", v),
                                        width="100%",
                                    ),
                                    neuro_floating_select(
                                        label="Tipo de Cuenta",
                                        value=ContratosState.form_data["tipo_cuenta"],
                                        options=[
                                            {"label": "Ahorros", "value": "Ahorros"},
                                            {"label": "Corriente", "value": "Corriente"},
                                        ],
                                        on_change=lambda v: ContratosState.set_form_field("tipo_cuenta", v),
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="3"),
                                    spacing="4",
                                    width="100%",
                                ),
                                rx.grid(
                                    neuro_floating_input(
                                        label="Nombre Consignatario",
                                        type="text",
                                        name="consignatario",
                                        placeholder="Nombre de quien recibe el pago",
                                        value=ContratosState.form_data["consignatario"],
                                        on_change=lambda v: ContratosState.set_form_field("consignatario", v.upper()),
                                        width="100%",
                                    ),
                                    neuro_floating_input(
                                        label="Documento Consignatario",
                                        type="text",
                                        name="documento_consignatario",
                                        placeholder="Cédula/NIT",
                                        value=ContratosState.form_data["documento_consignatario"],
                                        on_change=lambda v: ContratosState.set_form_field("documento_consignatario", v),
                                        width="100%",
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="2"),
                                    spacing="4",
                                    width="100%",
                                ),
                                width="100%",
                                align_items="start",
                            ),
                            # Recepción e Inventario
                            rx.vstack(
                                rx.text(
                                    "Recepción e Inventario",
                                    size="2",
                                    color="gray",
                                    style={"font_style": "italic"},
                                ),
                                rx.grid(
                                    rx.vstack(
                                        rx.text(
                                            "Enlace Video de Recibo",
                                            size="2",
                                            weight="bold",
                                        ),
                                        neuro_floating_input(
                                        label="Enlace Video de Recibo",
                                        type="url",
                                        name="enlace_video",
                                        placeholder="https://...",
                                        value=ContratosState.form_data["enlace_video"],
                                        on_change=lambda v: ContratosState.set_form_field("enlace_video", v),
                                        width="100%",
                                    ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    columns="1",
                                    spacing="4",
                                    width="100%",
                                ),
                                width="100%",
                                align_items="start",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        # Botones (Footer)
                        rx.flex(
                            rx.dialog.close(
                                neuro_button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                    tooltip_content="Cancelar y cerrar",
                                    style={
                                        "box_shadow": styles.SHADOW_FLAT_ELITE,
                                        "_hover": {
                                            "box_shadow": styles.SHADOW_RAISED_ELITE,
                                            "transform": "scale(1.02)",
                                        },
                                        "_active": {
                                            "box_shadow": styles.SHADOW_INSET_ELITE,
                                            "transform": "scale(0.98)",
                                        },
                                    },
                                ),
                            ),
                            neuro_button(
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
                                tooltip_content="Guardar el contrato",
                                style={
                                    "background": "var(--brand-primary)",
                                    "color": "white",
                                    "box_shadow": styles.SHADOW_RAISED_ELITE,
                                    "transition": styles.GLOBAL_TRANSITION,
                                    "_hover": {
                                        "opacity": 0.9,
                                        "transform": "translateY(-2px)",
                                        "box_shadow": styles.SHADOW_WHISPER,
                                    },
                                    "_active": {
                                        "box_shadow": styles.SHADOW_INSET_ELITE,
                                        "transform": "translateY(0) scale(0.98)",
                                    },
                                },
                            ),
                            spacing="3",
                            margin_top="2rem",
                            justify="end",
                            width="100%",
                        ),
                        on_submit=ContratosState.save_contrato,
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
            max_width=["95%", "750px"],
            max_height="85vh",
            overflow_y="auto",
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

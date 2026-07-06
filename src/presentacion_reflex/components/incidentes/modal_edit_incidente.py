import reflex as rx

from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_text_area,
    neuro_button,
)
from src.presentacion_reflex import styles


def _edit_incidente_form() -> rx.Component:
    estado_incidente = IncidentesState.editing_incidente.get("estado", "")

    return rx.vstack(
        rx.heading("Editar Incidente", size="5", margin_bottom="0.5em"),
        rx.text(
            "ID: ",
            IncidentesState.editing_incidente.get("id", ""),
            " | Estado: ",
            estado_incidente,
            size="2",
            color="gray",
            margin_bottom="1em",
        ),
        rx.text(
            "Campos editables segun estado",
            size="1",
            color="gray",
            margin_bottom="1em",
        ),
        rx.vstack(
            rx.grid(
                rx.vstack(
                    neuro_text_area(
                        label="Descripcion",
                        placeholder="Descripcion del incidente...",
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "descripcion", val
                        ),
                        value=IncidentesState.edit_form_data.get("descripcion", ""),
                        width="100%",
                    ),
                ),
                rx.vstack(
                    neuro_floating_select(
                        label="Prioridad",
                        options=[
                            {"label": "Baja", "value": "Baja"},
                            {"label": "Media", "value": "Media"},
                            {"label": "Alta", "value": "Alta"},
                            {"label": "Urgente", "value": "Urgente"},
                        ],
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "prioridad", val
                        ),
                        value=IncidentesState.edit_form_data.get("prioridad", "Media"),
                        width="100%",
                    ),
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            rx.grid(
                rx.vstack(
                    neuro_floating_select(
                        label="Origen del Reporte",
                        options=[
                            {"label": "Inquilino", "value": "Inquilino"},
                            {"label": "Propietario", "value": "Propietario"},
                            {"label": "Inmobiliaria", "value": "Inmobiliaria"},
                        ],
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "origen_reporte", val
                        ),
                        value=IncidentesState.edit_form_data.get(
                            "origen_reporte", "Inquilino"
                        ),
                        width="100%",
                    ),
                ),
                rx.vstack(
                    neuro_floating_select(
                        label="Responsable del Pago",
                        options=[
                            {"label": "Inquilino", "value": "Inquilino"},
                            {"label": "Propietario", "value": "Propietario"},
                            {"label": "Inmobiliaria", "value": "Inmobiliaria"},
                            {"label": "Aseguradora", "value": "Aseguradora"},
                        ],
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "responsable_pago", val
                        ),
                        value=IncidentesState.edit_form_data.get(
                            "responsable_pago", "Inquilino"
                        ),
                        width="100%",
                    ),
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            rx.grid(
                rx.vstack(
                    neuro_floating_input(
                        label="Costo Estimado",
                        type="number",
                        placeholder="0",
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "costo_incidente", val
                        ),
                        value=IncidentesState.edit_form_data["costo_incidente"].to(str),
                        width="100%",
                    ),
                ),
                rx.vstack(
                    neuro_floating_select(
                        label="Proveedor Asignado",
                        options=rx.foreach(
                            IncidentesState.proveedores_options,
                            lambda p: rx.select.item(p["texto"], value=p["id"])
                        ),
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "id_proveedor_asignado", val
                        ),
                        value=IncidentesState.edit_form_data[
                            "id_proveedor_asignado"
                        ].to(str),
                        width="100%",
                    ),
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        rx.cond(
            IncidentesState.edit_error != "",
            rx.callout(
                IncidentesState.edit_error,
                icon="triangle-alert",
                color_scheme="red",
                width="100%",
                margin_top="1em",
            ),
        ),
        rx.hstack(
            neuro_button(
                "Cancelar",
                on_click=IncidentesState.close_edit_modal,
                variant="soft",
                color_scheme="gray",
                tooltip_content="Cerrar sin guardar",
            ),
            rx.spacer(),
            neuro_button(
                "Guardar Cambios",
                on_click=IncidentesState.save_edit_incidente,
                loading=IncidentesState.is_loading,
                color_scheme="green",
                tooltip_content="Guardar cambios del incidente",
            ),
            width="100%",
            margin_top="1em",
        ),
        spacing="4",
        width="100%",
    )


def modal_edit_incidente() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.card(
                _edit_incidente_form(),
                width="100%",
                style={"box_shadow": styles.NEU_SHADOW},
            ),
            width="600px",
            max_width="95vw",
            background_color=styles.BG_PANEL,
            style={"border_radius": "24px", "padding": "1.5em"},
        ),
        open=IncidentesState.edit_modal_open,
        on_open_change=IncidentesState.set_edit_modal_open,
    )

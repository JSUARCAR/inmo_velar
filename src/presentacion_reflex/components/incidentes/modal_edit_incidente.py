import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex import styles


def _prioridad_options() -> rx.Component:
    return rx.fragment(
        rx.select.item("Baja", value="Baja"),
        rx.select.item("Media", value="Media"),
        rx.select.item("Alta", value="Alta"),
        rx.select.item("Urgente", value="Urgente"),
    )


def _origen_options() -> rx.Component:
    return rx.fragment(
        rx.select.item("Inquilino", value="Inquilino"),
        rx.select.item("Propietario", value="Propietario"),
        rx.select.item("Inmobiliaria", value="Inmobiliaria"),
    )


def _responsable_options() -> rx.Component:
    return rx.fragment(
        rx.select.item("Inquilino", value="Inquilino"),
        rx.select.item("Propietario", value="Propietario"),
        rx.select.item("Inmobiliaria", value="Inmobiliaria"),
        rx.select.item("Aseguradora", value="Aseguradora"),
    )


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
                    rx.text("Descripcion", weight="bold", size="2"),
                    rx.text_area(
                        placeholder="Descripcion del incidente...",
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "descripcion", val
                        ),
                        value=IncidentesState.edit_form_data.get("descripcion", ""),
                        width="100%",
                        style=styles.NEU_INPUT_STYLE,
                    ),
                ),
                rx.vstack(
                    rx.text("Prioridad", weight="bold", size="2"),
                    neuro_select_root(
                        _prioridad_options(),
                        placeholder="Seleccionar prioridad...",
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
                    rx.text("Origen del Reporte", weight="bold", size="2"),
                    neuro_select_root(
                        _origen_options(),
                        placeholder="Seleccionar origen...",
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
                    rx.text("Responsable del Pago", weight="bold", size="2"),
                    neuro_select_root(
                        _responsable_options(),
                        placeholder="Seleccionar responsable...",
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
                    rx.text("Costo Estimado", weight="bold", size="2"),
                    neuro_input(
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
                    rx.text("Proveedor Asignado", weight="bold", size="2"),
                    neuro_select_root(
                        rx.foreach(
                            IncidentesState.proveedores_options,
                            lambda x: rx.select.item(x["texto"], value=x["id"]),
                        ),
                        placeholder="Seleccionar proveedor...",
                        on_change=lambda val: IncidentesState.set_edit_field(
                            "id_proveedor_asignado", val
                        ),
                        value=IncidentesState.edit_form_data["id_proveedor_asignado"].to(str),
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
                icon="triangle_alert",
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
            ),
            rx.spacer(),
            neuro_button(
                "Guardar Cambios",
                on_click=IncidentesState.save_edit_incidente,
                loading=IncidentesState.is_loading,
                color_scheme="green",
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

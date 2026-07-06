import reflex as rx

from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_text_area,
    neuro_button,
)

from src.presentacion_reflex.components.shared.searchable_select import (
    searchable_select,
)


def _form_field(label: str, control: rx.Component, icon: str = None) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=16, color="var(--accent-9)") if icon else rx.fragment(),
            rx.text(label, weight="bold", size="2", color="gray"),
            spacing="2",
            align_items="center",
            margin_bottom="4px",
        ),
        control,
        width="100%",
        spacing="1",
    )


def modal_form() -> rx.Component:
    """Formulario modal para reportar incidente - Diseño Elite."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(
                    "Reportar Nuevo Incidente", size="6", margin_bottom="0.5em"
                ),
                rx.dialog.description(
                    "Complete la información detallada para registrar el incidente en el sistema.",
                    size="2",
                    color="gray",
                    margin_bottom="1.5em",
                ),
                rx.cond(
                    IncidentesState.error_message != "",
                    rx.callout(
                        IncidentesState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        variant="soft",
                        width="100%",
                        margin_bottom="1em",
                    ),
                ),
                rx.grid(
                    # Columna 1
                    rx.vstack(
                        searchable_select(
                            "Propiedad Afectada",
                            "Seleccione una propiedad...",
                            IncidentesState.propiedad_selected_label,
                            IncidentesState.propiedad_search,
                            IncidentesState.propiedad_menu_open,
                            IncidentesState.filtered_propiedades_options,
                            IncidentesState.set_propiedad_search,
                            IncidentesState.toggle_propiedad_menu,
                            IncidentesState.select_propiedad,
                        ),
                        _form_field(
                            "Fecha del Incidente",
                            neuro_floating_input(
                                label="Fecha",
                                type="date",
                                on_change=IncidentesState.set_fecha_incidente,
                                width="100%",
                                value=IncidentesState.form_data["fecha_incidente"],
                            ),
                            icon="calendar",
                        ),
                        _form_field(
                            "Origen del Reporte",
                            neuro_floating_select(
                                label="Origen",
                                options=[
                                    {"label": "Inquilino", "value": "Inquilino"},
                                    {"label": "Propietario", "value": "Propietario"},
                                    {"label": "Inmobiliaria", "value": "Inmobiliaria"},
                                ],
                                value=IncidentesState.form_data["origen_reporte"],
                                on_change=IncidentesState.set_origen_reporte,
                                width="100%",
                            ),
                            icon="user",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    # Columna 2
                    rx.vstack(
                        _form_field(
                            "Prioridad",
                            neuro_floating_select(
                                label="Prioridad",
                                options=[
                                    {"label": "Alta", "value": "Alta"},
                                    {"label": "Media", "value": "Media"},
                                    {"label": "Baja", "value": "Baja"},
                                ],
                                value=IncidentesState.form_data["prioridad"],
                                on_change=IncidentesState.set_prioridad,
                                width="100%",
                            ),
                            icon="triangle-alert",
                        ),
                        _form_field(
                            "Responsable de Pago (Sugerido)",
                            neuro_floating_select(
                                label="Responsable",
                                options=[
                                    {"label": "Inquilino", "value": "Inquilino"},
                                    {"label": "Propietario", "value": "Propietario"},
                                    {"label": "Inmobiliaria", "value": "Inmobiliaria"},
                                    {"label": "Aseguradora", "value": "Aseguradora"},
                                ],
                                value=IncidentesState.form_data["responsable_pago"],
                                on_change=IncidentesState.set_responsable_pago,
                                width="100%",
                            ),
                            icon="wallet",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="4",
                    width="100%",
                ),
                rx.box(
                    _form_field(
                        "Descripción Detallada",
                        neuro_text_area(
                            placeholder="Describa el incidente con el mayor detalle posible...",
                            name="descripcion",
                            value=IncidentesState.form_data["descripcion"],
                            on_change=IncidentesState.set_descripcion,
                            width="100%",
                            height="120px",
                            resize="vertical",
                        ),
                        icon="file-text",
                    ),
                    width="100%",
                    margin_top="1em",
                ),
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=IncidentesState.close_modal,
                            radius="full",
                            padding_x="1.5em",
                            tooltip_content="Cerrar formulario",
                        )
                    ),
                    neuro_button(
                        rx.hstack(
                            rx.icon("send", size=16), rx.text("Reportar Incidente")
                        ),
                        on_click=IncidentesState.save_incidente,
                        loading=IncidentesState.is_loading,
                        radius="full",
                        padding_x="1.5em",
                        color_scheme="blue",
                        variant="solid",
                        tooltip_content="Enviar reporte de incidente",
                    ),
                    spacing="3",
                    margin_top="2em",
                    justify="end",
                    width="100%",
                ),
                width="100%",
                padding="1em",
            ),
            width="700px",  # Wider modal for elite look
            max_width="95vw",
            background_color=styles.BG_PANEL,
            border_radius="16px",
            border="none",
            box_shadow=styles.NEU_MODAL_SHADOW,
        ),
        open=IncidentesState.modal_open,
        on_open_change=IncidentesState.set_modal_open,
    )

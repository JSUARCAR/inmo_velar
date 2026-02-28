import reflex as rx

from src.presentacion_reflex.state.incidentes_state import IncidentesState


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
        rx.hstack(
            rx.icon("home", size=16, color="var(--accent-9)"),
            rx.text(label, weight="bold", size="2", color="gray"),
            spacing="2",
            align_items="center",
            margin_bottom="4px",
        ),
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
                rx.dialog.title("Reportar Nuevo Incidente", size="6", margin_bottom="0.5em"),
                rx.dialog.description(
                    "Complete la información detallada para registrar el incidente en el sistema.",
                    size="2",
                    color="gray",
                    margin_bottom="1.5em",
                ),
                rx.cond(
                    IncidentesState.error_message != "",
                    rx.callout.root(
                        rx.callout.icon(),
                        rx.callout.text(IncidentesState.error_message),
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
                            rx.input(
                                type="date",
                                on_change=IncidentesState.set_fecha_incidente,
                                width="100%",
                            ),
                            icon="calendar",
                        ),
                        _form_field(
                            "Origen del Reporte",
                            rx.select(
                                IncidentesState.origen_reporte_options,
                                default_value="Inquilino",
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
                            rx.select(
                                ["Alta", "Media", "Baja"],
                                default_value="Media",
                                on_change=IncidentesState.set_prioridad,
                                width="100%",
                            ),
                            icon="circle-alert",
                        ),
                        _form_field(
                            "Responsable de Pago (Sugerido)",
                            rx.select(
                                IncidentesState.responsable_pago_options,
                                default_value="Inquilino",
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
                        rx.text_area(
                            placeholder="Describa el incidente con el mayor detalle posible...",
                            name="descripcion",
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
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=IncidentesState.close_modal,
                            radius="full",
                            padding_x="1.5em",
                        )
                    ),
                    rx.button(
                        rx.hstack(rx.icon("send", size=16), rx.text("Reportar Incidente")),
                        on_click=IncidentesState.save_incidente,
                        loading=IncidentesState.is_loading,
                        radius="full",
                        padding_x="1.5em",
                        color_scheme="blue",
                        variant="solid",
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
            border_radius="12px",
            box_shadow="0 10px 30px -10px rgba(0,0,0,0.2)",
        ),
        open=IncidentesState.modal_open,
        on_open_change=IncidentesState.set_modal_open,
    )

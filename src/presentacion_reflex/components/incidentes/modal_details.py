import reflex as rx

from src.presentacion_reflex.components.document_manager_elite import (
    document_manager_elite,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex import styles


def _detail_row(label: str, value: str, icon: str = None) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=16, color="var(--gray-8)") if icon else rx.fragment(),
        rx.text(f"{label}:", weight="bold", color="gray", width="120px"),
        rx.text(value, weight="medium", color="var(--gray-12)"),
        align_items="center",
        width="100%",
        spacing="2",
    )


def _quote_form() -> rx.Component:
    """Sub-formulario para registrar cotización."""
    return rx.vstack(
        rx.divider(margin_y="1em"),
        rx.heading("Registrar Cotización", size="4", color="var(--blue-9)"),
        rx.grid(
            rx.vstack(
                rx.text("Proveedor", weight="bold", size="2"),
                neuro_select_root(
                    rx.foreach(
                        IncidentesState.proveedores_options,
                        lambda x: rx.select.item(x["texto"], value=x["id"]),
                    ),
                    placeholder="Seleccione proveedor...",
                    on_change=lambda val: IncidentesState.set_cotizacion_field(
                        "id_proveedor", val
                    ),
                    value=IncidentesState.cotizacion_form["id_proveedor"],
                    width="100%",
                ),
            ),
            rx.vstack(
                rx.text("Días Estimados", weight="bold", size="2"),
                neuro_input(
                    type="number",
                    placeholder="1",
                    on_change=lambda val: IncidentesState.set_cotizacion_field(
                        "dias", val
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
                rx.text("Costo Materiales", weight="bold", size="2"),
                neuro_input(
                    type="number",
                    placeholder="0",
                    on_change=lambda val: IncidentesState.set_cotizacion_field(
                        "materiales", val
                    ),
                    width="100%",
                ),
            ),
            rx.vstack(
                rx.text("Costo Mano de Obra", weight="bold", size="2"),
                neuro_input(
                    type="number",
                    placeholder="0",
                    on_change=lambda val: IncidentesState.set_cotizacion_field(
                        "mano_obra", val
                    ),
                    width="100%",
                ),
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="4",
            width="100%",
        ),
        rx.vstack(
            rx.text("Descripción del Trabajo", weight="bold", size="2"),
            rx.text_area(
                placeholder="Detalle técnico de la reparación...",
                on_change=lambda val: IncidentesState.set_cotizacion_field(
                    "descripcion", val
                ),
                width="100%",
                style=styles.NEU_INPUT_STYLE,
            ),
            width="100%",
        ),
        rx.hstack(
            neuro_button(
                "Guardar Cotización",
                on_click=IncidentesState.save_cotizacion,
                loading=IncidentesState.is_loading,
                color_scheme="green",
            ),
            width="100%",
            justify="end",
            margin_top="1em",
        ),
        spacing="3",
        width="100%",
        background_color=styles.BG_PANEL,
        padding="1em",
        border_radius="16px",
        style={"box_shadow": styles.NEU_SHADOW},
    )


def _cotizado_view() -> rx.Component:
    """Vista para cuando el incidente está Cotizado."""
    return rx.vstack(
        rx.divider(margin_y="1em"),
        rx.heading("Cotizaciones Recibidas", size="4", color="var(--blue-9)"),
        rx.cond(
            IncidentesState.cotizaciones.length() > 0,
            rx.vstack(
                rx.foreach(
                    IncidentesState.cotizaciones,
                    lambda cot: rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file-text", size=18, color="var(--blue-9)"),
                                rx.text(cot["proveedor"], weight="bold", size="3"),
                                rx.spacer(),
                                rx.badge(
                                    cot["estado"],
                                    color_scheme=rx.cond(
                                        cot["estado"] == "Aprobada", "green", "blue"
                                    ),
                                    variant="soft",
                                ),
                                width="100%",
                                align_items="center",
                            ),
                            rx.separator(),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Materiales:", size="1", color="gray"),
                                    rx.text("$", cot["materiales"], weight="medium"),
                                ),
                                rx.vstack(
                                    rx.text("Mano de Obra:", size="1", color="gray"),
                                    rx.text("$", cot["mano_obra"], weight="medium"),
                                ),
                                rx.vstack(
                                    rx.text("Total:", size="1", color="gray"),
                                    rx.text(
                                        "$",
                                        cot["valor_total"],
                                        weight="bold",
                                        color="var(--blue-9)",
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Tiempo:", size="1", color="gray"),
                                    rx.text(cot["dias"], " días", weight="medium"),
                                ),
                                columns=rx.breakpoints(initial="2", sm="4"),
                                spacing="2",
                                width="100%",
                            ),
                            rx.text(
                                cot["descripcion"],
                                size="2",
                                color="gray",
                                margin_top="0.5em",
                            ),
                            rx.cond(
                                AuthState.check_action("Incidentes", "EDITAR")
                                & (
                                    IncidentesState.selected_incidente["estado"]
                                    == "Cotizado"
                                ),
                                neuro_button(
                                    "Aprobar Cotización",
                                    width="100%",
                                    margin_top="1em",
                                    on_click=lambda: (
                                        IncidentesState.aprobar_cotizacion_event(
                                            IncidentesState.selected_incidente["id"],
                                            cot["id"],
                                        )
                                    ),
                                    disabled=cot["estado"] != "Pendiente",
                                    color_scheme="green",
                                ),
                            ),
                        ),
                        width="100%",
                        style={
                            "box_shadow": styles.NEU_SHADOW,
                            "border_radius": "12px",
                        },
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            rx.text("No hay cotizaciones registradas.", color="gray"),
        ),
        # Formulario emergente
        rx.cond(IncidentesState.show_quote_form, _quote_form()),
        width="100%",
    )


def modal_details() -> rx.Component:
    """Modal de detalles y gestión del incidente con Tabs."""
    inc = IncidentesState.selected_incidente

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.heading("Incidente #", inc["id"], size="6"),
                    rx.spacer(),
                    neuro_button(
                        rx.hstack(
                            rx.icon("download", size=16), rx.text("Descargar PDF")
                        ),
                        variant="soft",
                        on_click=IncidentesState.generar_pdf_incidente,
                        loading=IncidentesState.is_loading,
                        margin_right="1em",
                    ),
                    rx.badge(
                        inc["estado"],
                        size="2",
                        variant="solid",
                        color_scheme=rx.match(
                            inc["estado"],
                            ("Reportado", "gray"),
                            ("En Revision", "amber"),
                            ("Cotizado", "blue"),
                            ("Aprobado", "green"),
                            ("En Reparacion", "orange"),
                            ("Finalizado", "teal"),
                            ("Cancelado", "red"),
                            "blue",
                        ),
                    ),
                    width="100%",
                    align_items="center",
                ),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("General", value="tab1"),
                        rx.tabs.trigger("Cotizaciones", value="tab2"),
                        rx.tabs.trigger("Documentos / Fotos", value="tab3"),
                    ),
                    # TAB 1: GENERAL (Detalles + Acciones Principales)
                    rx.tabs.content(
                        rx.scroll_area(
                            rx.vstack(
                                # Descripción Detallada
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(
                                                "align-left",
                                                size=20,
                                                color="var(--blue-9)",
                                            ),
                                            rx.text(
                                                "Descripción Detallada",
                                                weight="bold",
                                                size="2",
                                                color="var(--blue-9)",
                                            ),
                                            spacing="2",
                                            align_items="center",
                                            margin_bottom="0.5em",
                                        ),
                                        rx.text(
                                            inc["descripcion"],
                                            size="3",
                                            weight="medium",
                                            line_height="1.6",
                                            color="var(--gray-12)",
                                        ),
                                        padding="1em",
                                        background_color=styles.BG_PANEL,
                                        border_radius="12px",
                                        width="100%",
                                        style={"box_shadow": styles.NEU_INSET},
                                    ),
                                    width="100%",
                                    margin_bottom="1em",
                                    margin_top="1em",
                                ),
                                rx.divider(margin_y="0.5em"),
                                # Details Section
                                rx.vstack(
                                    _detail_row(
                                        "Propiedad", inc["direccion_propiedad"], "home"
                                    ),
                                    _detail_row(
                                        "Prioridad", inc["prioridad"], "triangle_alert"
                                    ),
                                    _detail_row("Fecha", inc["fecha"], "calendar"),
                                    _detail_row("Origen", inc["origen"], "user"),
                                    spacing="3",
                                    width="100%",
                                    padding="0.5em",
                                ),
                                rx.divider(margin_y="0.5em"),
                                rx.heading(
                                    "Acciones y Estado", size="3", margin_bottom="0.5em"
                                ),
                                # Botones de EDITAR y CANCELAR (siempre visibles si no está Finalizado o Cancelado)
                                rx.cond(
                                    (inc["estado"] != "Finalizado")
                                    & (inc["estado"] != "Cancelado"),
                                    rx.hstack(
                                        rx.cond(
                                            AuthState.check_action(
                                                "Incidentes", "EDITAR"
                                            ),
                                            neuro_button(
                                                rx.hstack(
                                                    rx.icon("pencil", size=16),
                                                    rx.text("Editar"),
                                                ),
                                                on_click=lambda: (
                                                    IncidentesState.open_edit_modal(inc)
                                                ),
                                                variant="soft",
                                                color_scheme="blue",
                                            ),
                                        ),
                                        rx.cond(
                                            AuthState.check_action(
                                                "Incidentes", "EDITAR"
                                            ),
                                            neuro_button(
                                                rx.hstack(
                                                    rx.icon("x", size=16),
                                                    rx.text("Cancelar"),
                                                ),
                                                on_click=lambda: (
                                                    IncidentesState.open_cancel_modal(
                                                        inc
                                                    )
                                                ),
                                                variant="soft",
                                                color_scheme="red",
                                            ),
                                        ),
                                        # Botón Finalizar Directo (solo si estado permite)
                                        rx.cond(
                                            (inc["estado"] == "Reportado")
                                            | (inc["estado"] == "En Revision")
                                            | (inc["estado"] == "Cotizado")
                                            | (inc["estado"] == "Aprobado"),
                                            rx.cond(
                                                AuthState.check_action(
                                                    "Incidentes", "EDITAR"
                                                ),
                                                neuro_button(
                                                    rx.hstack(
                                                        rx.icon(
                                                            "check_circle", size=16
                                                        ),
                                                        rx.text("Finalizar"),
                                                    ),
                                                    on_click=lambda: (
                                                        IncidentesState.toggle_direct_finish_form()
                                                    ),
                                                    variant="soft",
                                                    color_scheme="teal",
                                                ),
                                            ),
                                        ),
                                        spacing="2",
                                        width="100%",
                                        margin_bottom="0.5em",
                                    ),
                                ),
                                # Formulario de Finalización Directa
                                rx.cond(
                                    IncidentesState.show_direct_finish_form,
                                    rx.card(
                                        rx.vstack(
                                            rx.heading(
                                                "Finalizacion Directa",
                                                size="4",
                                                color="var(--teal-9)",
                                            ),
                                            rx.callout(
                                                "El incidente se cerrara directamente sin seguir el flujo normal.",
                                                icon="alert_circle",
                                                color_scheme="yellow",
                                                width="100%",
                                            ),
                                            rx.grid(
                                                rx.vstack(
                                                    rx.text(
                                                        "Fecha de Reparacion",
                                                        weight="bold",
                                                        size="2",
                                                    ),
                                                    neuro_input(
                                                        type="date",
                                                        on_change=lambda val: (
                                                            IncidentesState.set_direct_finish_field(
                                                                "fecha", val
                                                            )
                                                        ),
                                                        value=IncidentesState.direct_finish_date,
                                                        width="100%",
                                                    ),
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        "Costo Final",
                                                        weight="bold",
                                                        size="2",
                                                    ),
                                                    neuro_input(
                                                        type="number",
                                                        placeholder="0",
                                                        on_change=lambda val: (
                                                            IncidentesState.set_direct_finish_field(
                                                                "costo", val
                                                            )
                                                        ),
                                                        value=str(
                                                            IncidentesState.direct_finish_costo
                                                        ),
                                                        width="100%",
                                                    ),
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        "Proveedor",
                                                        weight="bold",
                                                        size="2",
                                                    ),
                                                    neuro_select_root(
                                                        rx.foreach(
                                                            IncidentesState.proveedores_options,
                                                            lambda x: rx.select.item(
                                                                x["texto"],
                                                                value=x["id"],
                                                            ),
                                                        ),
                                                        placeholder="Seleccionar...",
                                                        on_change=lambda val: (
                                                            IncidentesState.set_direct_finish_field(
                                                                "proveedor", val
                                                            )
                                                        ),
                                                        width="100%",
                                                    ),
                                                ),
                                                columns=rx.breakpoints(
                                                    initial="1", sm="3"
                                                ),
                                                spacing="3",
                                                width="100%",
                                            ),
                                            rx.vstack(
                                                rx.text(
                                                    "Observaciones",
                                                    weight="bold",
                                                    size="2",
                                                ),
                                                rx.text_area(
                                                    placeholder="Observaciones de la reparacion...",
                                                    on_change=lambda val: (
                                                        IncidentesState.set_direct_finish_field(
                                                            "observacion", val
                                                        )
                                                    ),
                                                    value=IncidentesState.direct_finish_obs,
                                                    width="100%",
                                                    style=styles.NEU_INPUT_STYLE,
                                                ),
                                                width="100%",
                                            ),
                                            rx.cond(
                                                IncidentesState.direct_finish_error
                                                != "",
                                                rx.callout(
                                                    IncidentesState.direct_finish_error,
                                                    icon="alert_circle",
                                                    color_scheme="red",
                                                    width="100%",
                                                    margin_top="0.5em",
                                                ),
                                            ),
                                            rx.hstack(
                                                neuro_button(
                                                    "Cancelar",
                                                    on_click=IncidentesState.toggle_direct_finish_form,
                                                    variant="soft",
                                                    color_scheme="gray",
                                                ),
                                                rx.spacer(),
                                                neuro_button(
                                                    "Confirmar",
                                                    on_click=IncidentesState.confirmar_finalizacion_directa,
                                                    color_scheme="teal",
                                                ),
                                                width="100%",
                                                margin_top="1em",
                                            ),
                                            spacing="3",
                                            width="100%",
                                            background_color=styles.BG_PANEL,
                                            padding="1em",
                                            border_radius="12px",
                                            margin_top="1em",
                                            style={"box_shadow": styles.NEU_SHADOW},
                                        ),
                                    ),
                                ),
                                # LOGICA DE ESTADOS Y ACCIONES PRINCIPALES
                                # Estado: Aprobado -> Iniciar Reparación
                                rx.cond(
                                    inc["estado"] == "Aprobado",
                                    rx.vstack(
                                        rx.callout(
                                            "Incidente aprobado. Puede iniciar la reparación.",
                                            icon="check_circle",
                                            color_scheme="green",
                                            width="100%",
                                        ),
                                        rx.cond(
                                            AuthState.check_action(
                                                "Incidentes", "EDITAR"
                                            ),
                                            neuro_button(
                                                "Iniciar Reparación",
                                                width="100%",
                                                color_scheme="blue",
                                                on_click=lambda: (
                                                    IncidentesState.iniciar_reparacion_event(
                                                        inc["id"]
                                                    )
                                                ),
                                                margin_top="1em",
                                            ),
                                        ),
                                    ),
                                ),
                                # Estado: En Reparación -> Finalizar
                                rx.cond(
                                    inc["estado"] == "En Reparacion",
                                    rx.vstack(
                                        rx.callout(
                                            "Trabajos en curso.",
                                            icon="hammer",
                                            color_scheme="orange",
                                            width="100%",
                                        ),
                                        rx.card(
                                            rx.hstack(
                                                rx.icon(
                                                    "hard_hat",
                                                    size=20,
                                                    color="var(--blue-9)",
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        "Proveedor Asignado",
                                                        size="1",
                                                        color="gray",
                                                    ),
                                                    rx.text(
                                                        inc["nombre_proveedor"],
                                                        weight="bold",
                                                        size="3",
                                                    ),
                                                    spacing="1",
                                                ),
                                                align_items="center",
                                                spacing="3",
                                            ),
                                            variant="surface",
                                            width="100%",
                                            style={"box_shadow": styles.NEU_SHADOW},
                                        ),
                                        rx.cond(
                                            ~IncidentesState.show_finalize_form,
                                            rx.cond(
                                                AuthState.check_action(
                                                    "Incidentes", "EDITAR"
                                                ),
                                                neuro_button(
                                                    "Finalizar Incidente",
                                                    width="100%",
                                                    color_scheme="green",
                                                    on_click=IncidentesState.toggle_finalize_form,
                                                    margin_top="1em",
                                                ),
                                            ),
                                        ),
                                        rx.cond(
                                            IncidentesState.show_finalize_form,
                                            rx.vstack(
                                                rx.divider(margin_y="1em"),
                                                rx.heading(
                                                    "Finalizar Reparación",
                                                    size="3",
                                                    color="var(--blue-9)",
                                                ),
                                                rx.text(
                                                    "Fecha de Terminación",
                                                    weight="bold",
                                                    size="2",
                                                ),
                                                neuro_input(
                                                    type="date",
                                                    on_change=IncidentesState.set_finalize_date,
                                                    value=IncidentesState.finalize_date,
                                                    width="100%",
                                                ),
                                                rx.text(
                                                    "Observaciones",
                                                    weight="bold",
                                                    size="2",
                                                ),
                                                rx.text_area(
                                                    placeholder="Descripción...",
                                                    on_change=IncidentesState.set_finalize_obs,
                                                    value=IncidentesState.finalize_obs,
                                                    width="100%",
                                                    style=styles.NEU_INPUT_STYLE,
                                                ),
                                                rx.hstack(
                                                    neuro_button(
                                                        "Cancelar",
                                                        on_click=IncidentesState.toggle_finalize_form,
                                                        variant="soft",
                                                        color_scheme="gray",
                                                    ),
                                                    rx.spacer(),
                                                    neuro_button(
                                                        "Confirmar",
                                                        on_click=IncidentesState.confirmar_finalizacion,
                                                        color_scheme="green",
                                                    ),
                                                    width="100%",
                                                    margin_top="0.5em",
                                                ),
                                                background_color=styles.BG_PANEL,
                                                padding="1em",
                                                border_radius="12px",
                                                width="100%",
                                                spacing="2",
                                                margin_top="1em",
                                                style={"box_shadow": styles.NEU_SHADOW},
                                            ),
                                        ),
                                    ),
                                ),
                                # Estado: Finalizado -> Resumen
                                rx.cond(
                                    inc["estado"] == "Finalizado",
                                    rx.vstack(
                                        rx.callout(
                                            "Incidente cerrado.",
                                            icon="check",
                                            color_scheme="gray",
                                            width="100%",
                                        ),
                                        rx.card(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.icon("hard_hat", size=20),
                                                    rx.text(
                                                        inc["nombre_proveedor"],
                                                        weight="bold",
                                                    ),
                                                    align_items="center",
                                                    spacing="3",
                                                ),
                                                rx.separator(margin_y="0.5em"),
                                                rx.grid(
                                                    rx.vstack(
                                                        rx.text(
                                                            "Fecha Fin:",
                                                            size="1",
                                                            color="gray",
                                                        ),
                                                        rx.text(
                                                            inc["fecha_arreglo"],
                                                            weight="medium",
                                                        ),
                                                    ),
                                                    rx.vstack(
                                                        rx.text(
                                                            "Costo Final:",
                                                            size="1",
                                                            color="gray",
                                                        ),
                                                        rx.text(
                                                            "$",
                                                            inc["costo_incidente"],
                                                            weight="bold",
                                                        ),
                                                    ),
                                                    columns=rx.breakpoints(
                                                        initial="1", sm="2"
                                                    ),
                                                    width="100%",
                                                ),
                                                rx.text(
                                                    "Observaciones:",
                                                    weight="bold",
                                                    size="2",
                                                    margin_top="0.5em",
                                                ),
                                                rx.text(
                                                    inc["observaciones_final"],
                                                    size="2",
                                                ),
                                            ),
                                            variant="surface",
                                            width="100%",
                                            style={"box_shadow": styles.NEU_SHADOW},
                                        ),
                                    ),
                                ),
                                padding="0.5em",
                            ),
                            max_height="60vh",
                        ),
                        value="tab1",
                    ),
                    # TAB 2: COTIZACIONES
                    rx.tabs.content(
                        rx.scroll_area(
                            rx.vstack(
                                rx.heading(
                                    "Gestión de Cotizaciones",
                                    size="4",
                                    margin_bottom="0.5em",
                                ),
                                # Lista de Cotizaciones (unificada)
                                rx.cond(
                                    IncidentesState.cotizaciones.length() > 0,
                                    rx.vstack(
                                        rx.foreach(
                                            IncidentesState.cotizaciones,
                                            lambda cot: rx.card(
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.icon(
                                                            "file-text",
                                                            size=18,
                                                            color="var(--blue-9)",
                                                        ),
                                                        rx.text(
                                                            cot["proveedor"],
                                                            weight="bold",
                                                            size="3",
                                                        ),
                                                        rx.spacer(),
                                                        rx.badge(
                                                            cot["estado"],
                                                            color_scheme=rx.cond(
                                                                cot["estado"]
                                                                == "Aprobada",
                                                                "green",
                                                                "blue",
                                                            ),
                                                            variant="soft",
                                                        ),
                                                        width="100%",
                                                        align_items="center",
                                                    ),
                                                    rx.separator(),
                                                    rx.grid(
                                                        rx.vstack(
                                                            rx.text(
                                                                "Materiales:", size="1"
                                                            ),
                                                            rx.text(
                                                                "$",
                                                                cot["materiales"],
                                                                weight="medium",
                                                            ),
                                                        ),
                                                        rx.vstack(
                                                            rx.text(
                                                                "Mano de Obra:",
                                                                size="1",
                                                            ),
                                                            rx.text(
                                                                "$",
                                                                cot["mano_obra"],
                                                                weight="medium",
                                                            ),
                                                        ),
                                                        rx.vstack(
                                                            rx.text("Total:", size="1"),
                                                            rx.text(
                                                                "$",
                                                                cot["valor_total"],
                                                                weight="bold",
                                                            ),
                                                        ),
                                                        rx.vstack(
                                                            rx.text("dias:", size="1"),
                                                            rx.text(
                                                                cot["dias"],
                                                                " días",
                                                                weight="medium",
                                                            ),
                                                        ),
                                                        columns=rx.breakpoints(
                                                            initial="2", sm="4"
                                                        ),
                                                        spacing="2",
                                                        width="100%",
                                                    ),
                                                    rx.text(
                                                        cot["descripcion"],
                                                        size="2",
                                                        color="gray",
                                                        margin_top="0.5em",
                                                    ),
                                                    # Botón Aprobar solo si está pendiente y usuario puede editar e incidente está en Cotizado
                                                    rx.cond(
                                                        (cot["estado"] == "Pendiente")
                                                        & AuthState.check_action(
                                                            "Incidentes", "EDITAR"
                                                        )
                                                        & (
                                                            IncidentesState.selected_incidente[
                                                                "estado"
                                                            ]
                                                            == "Cotizado"
                                                        ),
                                                        neuro_button(
                                                            "Aprobar Cotización",
                                                            width="100%",
                                                            margin_top="1em",
                                                            on_click=lambda: (
                                                                IncidentesState.aprobar_cotizacion_event(
                                                                    inc["id"], cot["id"]
                                                                )
                                                            ),
                                                            color_scheme="green",
                                                        ),
                                                    ),
                                                ),
                                                width="100%",
                                                style={"box_shadow": styles.NEU_SHADOW},
                                            ),
                                        ),
                                        # Botón Finalizar Carga (Si estamos en etapa drafts)
                                        rx.cond(
                                            (inc["estado"] == "Reportado")
                                            | (inc["estado"] == "En Revision"),
                                            rx.cond(
                                                AuthState.check_action(
                                                    "Incidentes", "EDITAR"
                                                ),
                                                neuro_button(
                                                    "Finalizar Carga y Solicitar Aprobación",
                                                    width="100%",
                                                    color_scheme="green",
                                                    variant="solid",
                                                    on_click=lambda: (
                                                        IncidentesState.finalizar_carga_cotizaciones(
                                                            inc["id"]
                                                        )
                                                    ),
                                                    margin_top="1em",
                                                ),
                                            ),
                                        ),
                                        spacing="3",
                                        width="100%",
                                    ),
                                    rx.text(
                                        "No hay cotizaciones registradas.",
                                        color="gray",
                                        padding="1em",
                                    ),
                                ),
                                rx.divider(margin_y="1em"),
                                # Botón/Formulario Agregar Cotización
                                rx.cond(
                                    (inc["estado"] == "Reportado")
                                    | (inc["estado"] == "En Revision"),
                                    rx.vstack(
                                        rx.cond(
                                            ~IncidentesState.show_quote_form,
                                            rx.cond(
                                                AuthState.check_action(
                                                    "Incidentes", "EDITAR"
                                                ),
                                                neuro_button(
                                                    rx.hstack(
                                                        rx.icon("plus"),
                                                        rx.text("Nueva Cotización"),
                                                    ),
                                                    on_click=IncidentesState.toggle_quote_form,
                                                    width="100%",
                                                    variant="soft",
                                                ),
                                            ),
                                        ),
                                        rx.cond(
                                            IncidentesState.show_quote_form,
                                            _quote_form(),
                                        ),
                                        width="100%",
                                    ),
                                ),
                                padding="0.5em",
                            ),
                            max_height="60vh",
                        ),
                        value="tab2",
                    ),
                    # TAB 3: DOCUMENTOS
                    rx.tabs.content(
                        rx.scroll_area(
                            rx.vstack(
                                rx.heading(
                                    "Evidencia y Documentos",
                                    size="4",
                                    margin_bottom="0.5em",
                                ),
                                rx.text(
                                    "Gestione fotos del daño, cotizaciones y comprobantes.",
                                    size="2",
                                    color="gray",
                                    margin_bottom="1em",
                                ),
                                # INTEGRACIÓN DOCUMENT MANAGER ELITE
                                document_manager_elite(IncidentesState),
                                padding="0.5em",
                            ),
                            max_height="60vh",
                        ),
                        value="tab3",
                    ),
                    default_value="tab1",
                    width="100%",
                ),
                # Footer Close Button
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cerrar",
                            on_click=IncidentesState.close_details_modal,
                            variant="soft",
                            color_scheme="gray",
                        )
                    ),
                    justify="end",
                    width="100%",
                    margin_top="1em",
                ),
                width="100%",
            ),
            width="800px",  # Más ancho para soportar tabs y tablas
            max_width="95vw",
            background_color=styles.BG_PANEL,
            style={"border_radius": "24px", "padding": "2em"},
        ),
        open=IncidentesState.details_modal_open,
        on_open_change=IncidentesState.set_details_modal_open,
    )

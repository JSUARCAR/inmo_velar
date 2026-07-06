"""
Componente: Modal de Detalles de Persona
Visualiza información consolidada por roles con diseño Editorial (Claude).
"""

import reflex as rx
from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex.components.neuro_elements import neuro_badge, neuro_button
from src.presentacion_reflex import styles


def item_detalle(etiqueta: str, valor: str, icono: str = None) -> rx.Component:
    """Item de detalle individual con estilo Claude (profundidad inset sutil)."""
    return rx.vstack(
        rx.hstack(
            rx.cond(icono, rx.icon(icono, size=16, color=styles.TEXT_SECONDARY)),
            rx.text(etiqueta, size="1", color=styles.TEXT_SECONDARY, weight="medium"),
            spacing="2",
        ),
        rx.text(
            rx.cond(valor, valor, "N/A"),
            size="2",
            color=styles.TEXT_PRIMARY,
            weight="bold",
            trim="normal",
        ),
        spacing="1",
        align_items="start",
        padding="0.75rem",
        border_radius="10px",
        box_shadow=styles.SHADOW_INSET,
        background=styles.BG_PANEL,
        width="100%",
    )


def badge_rol(rol: str) -> rx.Component:
    """Badge de rol con estetica Claude (anillo de profundidad)."""
    return rx.badge(
        rol,
        variant="surface",
        padding_x="0.75rem",
        padding_y="0.25rem",
        border_radius="8px",
        box_shadow=styles.SHADOW_RING,
        style={"background": styles.ACCENT_BG_SOFT, "color": styles.BRAND_PRIMARY},
    )


def contenedor_contenido_pestana(*hijos) -> rx.Component:
    """Contenedor estandar para el contenido de las pestañas."""
    return rx.vstack(
        *hijos,
        width="100%",
        spacing="4",
        padding_top="1.5rem",
    )


def titulo_seccion(titulo: str, icono: str) -> rx.Component:
    """Título de sección con icono terracota."""
    return rx.hstack(
        rx.icon(icono, size=20, color=styles.BRAND_PRIMARY),
        rx.text(titulo, size="4", weight="bold", color=styles.TEXT_PRIMARY),
        spacing="2",
        margin_bottom="0.5rem",
        width="100%",
    )


def render_audit_log(log: dict) -> rx.Component:
    """Renderiza una fila del log de auditoría."""
    return rx.table.row(
        rx.table.cell(rx.text(log["fecha"].to(str)[:16], size="1")),
        rx.table.cell(rx.text(log["usuario"].to(str), size="1", weight="bold")),
        rx.table.cell(neuro_badge(log["accion"].to(str), color_scheme="gray")),
        rx.table.cell(
            rx.text(log["detalle"].to(str), size="1", color=styles.TEXT_SECONDARY)
        ),
    )


def modal_detalles() -> rx.Component:
    """Modal principal de detalles de persona con diseño editorial Claude."""

    # Pestaña General
    pestana_general = contenedor_contenido_pestana(
        titulo_seccion("Información Básica", "user"),
        rx.grid(
            item_detalle("Nombre Completo", PersonasState.detail_nombre, "user_round"),
            item_detalle("Documento", PersonasState.detail_documento, "fingerprint"),
            item_detalle("Teléfono", PersonasState.detail_telefono, "phone"),
            item_detalle("Correo Electrónico", PersonasState.detail_correo, "mail"),
            item_detalle("Dirección", PersonasState.detail_direccion, "map_pin"),
            item_detalle(
                "Fecha Registro", PersonasState.detail_fecha_creacion, "calendar"
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),
    )

    # Pestaña Propietario
    pestana_propietario = rx.cond(
        PersonasState.detail_propietario,
        contenedor_contenido_pestana(
            titulo_seccion("Información de Propietario", "user_check"),
            rx.text(
                "La información bancaria y de consignatario ahora se gestiona directamente dentro de cada Contrato de Mandato.",
                size="2",
                color=styles.TEXT_SECONDARY,
                font_style="italic",
            ),
            item_detalle(
                "Observaciones",
                PersonasState.detail_propietario["observaciones"].to(str),
                "message_square",
            ),
            titulo_seccion("Propiedades Asociadas", "home"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Matrícula"),
                        rx.table.column_header_cell("Dirección"),
                        rx.table.column_header_cell("Tipo"),
                        rx.table.column_header_cell("Disponible"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PersonasState.detail_propiedades_activas,
                        lambda prop: rx.table.row(
                            rx.table.cell(prop["matricula"].to(str)),
                            rx.table.cell(prop["direccion"].to(str)),
                            rx.table.cell(prop["tipo"].to(str)),
                            rx.table.cell(prop["disponible"].to(str)),
                        ),
                    )
                ),
                width="100%",
                variant="surface",
            ),
        ),
        rx.center(
            rx.text("No hay detalles de Propietario", color=styles.TEXT_TERTIARY),
            padding="2rem",
        ),
    )

    # Pestaña Arrendatario
    pestana_arrendatario = rx.cond(
        PersonasState.detail_arrendatario,
        contenedor_contenido_pestana(
            titulo_seccion("Gestión de Arrendamiento", "clipboard_list"),
            rx.grid(
                item_detalle(
                    "Código Seguro",
                    PersonasState.detail_arrendatario["codigo_seguro"].to(str),
                    "shield_check",
                ),
                item_detalle(
                    "Nombre Habitante",
                    PersonasState.detail_arrendatario["habitante"].to(str),
                    "user",
                ),
                item_detalle(
                    "Teléfono Habitante",
                    PersonasState.detail_arrendatario["telefono_habitante"].to(str),
                    "phone",
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            titulo_seccion("Contratos Vigentes", "file_key_2"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Propiedad"),
                        rx.table.column_header_cell("Inicio"),
                        rx.table.column_header_cell("Fin"),
                        rx.table.column_header_cell("Canon"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PersonasState.detail_contratos_activos,
                        lambda cont: rx.table.row(
                            rx.table.cell(cont["propiedad"].to(str)),
                            rx.table.cell(cont["inicio"].to(str)),
                            rx.table.cell(cont["fin"].to(str)),
                            rx.table.cell(cont["canon"].to(str)),
                        ),
                    )
                ),
                width="100%",
                variant="surface",
            ),
        ),
        rx.center(
            rx.text("No hay detalles de Arrendatario", color=styles.TEXT_TERTIARY),
            padding="2rem",
        ),
    )

    # Pestaña Codeudor
    pestana_codeudor = rx.cond(
        PersonasState.detail_codeudor,
        contenedor_contenido_pestana(
            titulo_seccion("Garantías Respaldadas", "shield"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Propiedad"),
                        rx.table.column_header_cell("Fecha Inicio"),
                        rx.table.column_header_cell("Estado Contrato"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PersonasState.detail_garantias_activas,
                        lambda gar: rx.table.row(
                            rx.table.cell(gar["propiedad"].to(str)),
                            rx.table.cell(gar["inicio"].to(str)),
                            rx.table.cell(gar["estado"].to(str)),
                        ),
                    )
                ),
                width="100%",
                variant="surface",
            ),
        ),
        rx.center(
            rx.text("No hay detalles de Codeudor", color=styles.TEXT_TERTIARY),
            padding="2rem",
        ),
    )

    # Pestaña Asesor/Proveedor
    pestana_otros = contenedor_contenido_pestana(
        rx.cond(
            PersonasState.detail_asesor,
            rx.vstack(
                titulo_seccion("Información Asesor", "briefcase"),
                rx.grid(
                    item_detalle(
                        "Comisión Arriendo",
                        PersonasState.detail_asesor["comision_arriendo"].to(str),
                        "percent",
                    ),
                    item_detalle(
                        "Comisión Venta",
                        PersonasState.detail_asesor["comision_venta"].to(str),
                        "percent",
                    ),
                    item_detalle(
                        "Fecha Ingreso",
                        PersonasState.detail_asesor["fecha_ingreso"].to(str),
                        "calendar_days",
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            PersonasState.detail_proveedor,
            rx.vstack(
                titulo_seccion("Información Proveedor", "wrench"),
                rx.grid(
                    item_detalle(
                        "Especialidad",
                        PersonasState.detail_proveedor["especialidad"].to(str),
                        "award",
                    ),
                    item_detalle(
                        "Calificación",
                        PersonasState.detail_proveedor["calificacion"].to(str),
                        "star",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                item_detalle(
                    "Observaciones",
                    PersonasState.detail_proveedor["observaciones"].to(str),
                    "message_square",
                ),
                width="100%",
            ),
        ),
    )

    # Pestaña Historial (Auditoría)
    pestana_historial = contenedor_contenido_pestana(
        titulo_seccion("Trazabilidad de Cambios", "history"),
        rx.cond(
            PersonasState.audit_logs,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell("Usuario"),
                        rx.table.column_header_cell("Acción"),
                        rx.table.column_header_cell("Detalle"),
                    )
                ),
                rx.table.body(rx.foreach(PersonasState.audit_logs, render_audit_log)),
                width="100%",
                variant="surface",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("info", size=32, color=styles.TEXT_TERTIARY),
                    rx.text(
                        "No hay registros históricos para esta persona",
                        color=styles.TEXT_TERTIARY,
                    ),
                    spacing="2",
                ),
                padding="3rem",
                width="100%",
            ),
        ),
    )

    return rx.dialog.root(
        rx.dialog.content(
            # Header del Modal
            rx.hstack(
                rx.avatar(
                    fallback=PersonasState.detail_nombre[0:2],
                    size="7",
                    variant="soft",
                    style={
                        "background": styles.ACCENT_BG_SOFT,
                        "color": styles.BRAND_PRIMARY,
                    },
                    box_shadow=styles.SHADOW_RING,
                ),
                rx.vstack(
                    rx.heading(
                        PersonasState.detail_nombre,
                        size="6",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.hstack(
                        rx.foreach(PersonasState.detail_roles_list, badge_rol),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.dialog.close(
                    rx.icon_button(
                        rx.icon("x"),
                        style=styles.NEU_ICON_BUTTON_STYLE,
                        on_click=PersonasState.close_details_modal,
                    )
                ),
                width="100%",
                padding_bottom="1.5rem",
                border_bottom=f"1px solid {styles.BORDER_DEFAULT}",
                align_items="center",
            ),
            # Cuerpo del Modal con Tabs
            rx.cond(
                PersonasState.is_loading_details,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3", color=styles.BRAND_PRIMARY),
                        rx.text(
                            "Cargando información detallada...",
                            color=styles.TEXT_SECONDARY,
                        ),
                        padding="4rem",
                    ),
                    width="100%",
                ),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("General", value="general"),
                        rx.cond(
                            PersonasState.detail_propietario,
                            rx.tabs.trigger("Propietario", value="propietario"),
                        ),
                        rx.cond(
                            PersonasState.detail_arrendatario,
                            rx.tabs.trigger("Arrendatario", value="arrendatario"),
                        ),
                        rx.cond(
                            PersonasState.detail_codeudor,
                            rx.tabs.trigger("Codeudor", value="codeudor"),
                        ),
                        rx.cond(
                            PersonasState.detail_asesor
                            | PersonasState.detail_proveedor,
                            rx.tabs.trigger("Profesional", value="otros"),
                        ),
                        rx.tabs.trigger("Historial", value="historial"),
                        justify_content="start",
                        box_shadow=styles.SHADOW_INSET,
                        border_radius="10px",
                        padding="4px",
                        background=styles.BG_PANEL,
                    ),
                    rx.tabs.content(pestana_general, value="general"),
                    rx.tabs.content(pestana_propietario, value="propietario"),
                    rx.tabs.content(pestana_arrendatario, value="arrendatario"),
                    rx.tabs.content(pestana_codeudor, value="codeudor"),
                    rx.tabs.content(pestana_otros, value="otros"),
                    rx.tabs.content(pestana_historial, value="historial"),
                    default_value="general",
                    width="100%",
                ),
            ),
            # Footer
            rx.hstack(
                rx.spacer(),
                rx.dialog.close(
                    neuro_button(
                        "Cerrar",
                        style=styles.NEU_BUTTON_STYLE,
                        on_click=PersonasState.close_details_modal,
                        tooltip_content="Cerrar detalles de persona"
                    )
                ),
                width="100%",
                padding_top="1.5rem",
                margin_top="1rem",
                border_top=f"1px solid {styles.BORDER_DEFAULT}",
            ),
            background=styles.BG_APP,
            max_width="800px",
            border_radius="20px",
            box_shadow=styles.SHADOW_WHISPER,
            padding="2rem",
        ),
        open=PersonasState.show_details_modal,
        on_open_change=PersonasState.close_details_modal,
    )

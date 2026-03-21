"""
Componente: Modal de Detalles de Persona
Visualiza información consolidada por roles con diseño Neumórfico.
"""

import reflex as rx
from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex import styles

def detail_item(label: str, value: str, icon: str = None) -> rx.Component:
    """Item de detalle individual con estilo neumórfico inset."""
    return rx.vstack(
        rx.hstack(
            rx.cond(icon, rx.icon(icon, size=16, color=styles.TEXT_SECONDARY)),
            rx.text(label, size="1", color=styles.TEXT_SECONDARY, weight="medium"),
            spacing="2",
        ),
        rx.text(
            rx.cond(value, value, "N/A"),
            size="2",
            color=styles.TEXT_PRIMARY,
            weight="bold",
            trim="normal",
        ),
        spacing="1",
        align_items="start",
        padding="0.75rem",
        border_radius="10px",
        box_shadow=styles.SHADOW_INSET_ELITE,
        background=styles.BG_PANEL,
        width="100%",
    )

def role_badge(role: str) -> rx.Component:
    """Badge de rol con sombreado suave."""
    return rx.badge(
        role,
        variant="surface",
        color_scheme="indigo",
        padding_x="0.75rem",
        padding_y="0.25rem",
        border_radius="8px",
        box_shadow=styles.SHADOW_RAISED_ELITE,
    )

def tab_content_container(*children) -> rx.Component:
    """Contenedor estándar para el contenido de las pestañas."""
    return rx.vstack(
        *children,
        width="100%",
        spacing="4",
        padding_top="1.5rem",
    )

def section_title(title: str, icon: str) -> rx.Component:
    """Título de sección dentro de una pestaña."""
    return rx.hstack(
        rx.icon(icon, size=20, color=styles.ACCENT_COLOR),
        rx.text(title, size="4", weight="bold", color=styles.TEXT_PRIMARY),
        spacing="2",
        margin_bottom="0.5rem",
        width="100%",
    )

def modal_detalles() -> rx.Component:
    """Modal principal de detalles de persona."""
    
    # Pestaña General
    tab_general = tab_content_container(
        section_title("Información Básica", "user"),
        rx.grid(
            detail_item("Nombre Completo", PersonasState.detail_nombre, "user_round"),
            detail_item("Documento", PersonasState.detail_documento, "fingerprint"),
            detail_item("Teléfono", PersonasState.detail_telefono, "phone"),
            detail_item("Correo Electrónico", PersonasState.detail_correo, "mail"),
            detail_item("Dirección", PersonasState.detail_direccion, "map_pin"),
            detail_item("Fecha Registro", PersonasState.detail_fecha_creacion, "calendar"),
            columns="2",
            spacing="4",
            width="100%",
        ),
    )

    # Pestaña Propietario
    tab_propietario = rx.cond(
        PersonasState.detail_propietario,
        tab_content_container(
            section_title("Información Financiera", "banknote"),
            rx.grid(
                detail_item("Banco", PersonasState.detail_propietario["banco"].to(str), "building_2"),
                detail_item("Número de Cuenta", PersonasState.detail_propietario["cuenta"].to(str), "credit_card"),
                detail_item("Tipo de Cuenta", PersonasState.detail_propietario["tipo_cuenta"].to(str), "info"),
                detail_item("Consignatario", PersonasState.detail_propietario["consignatario"].to(str), "user_check"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            section_title("Propiedades Asociadas", "home"),
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
                        )
                    )
                ),
                width="100%",
                variant="surface",
            )
        ),
        rx.center(rx.text("No hay detalles de Propietario", color=styles.TEXT_TERTIARY), padding="2rem")
    )

    # Pestaña Arrendatario
    tab_arrendatario = rx.cond(
        PersonasState.detail_arrendatario,
        tab_content_container(
            section_title("Gestión de Arrendamiento", "clipboard_list"),
            rx.grid(
                detail_item("Código Seguro", PersonasState.detail_arrendatario["codigo_seguro"].to(str), "shield_check"),
                detail_item("Nombre Habitante", PersonasState.detail_arrendatario["habitante"].to(str), "user"),
                detail_item("Teléfono Habitante", PersonasState.detail_arrendatario["telefono_habitante"].to(str), "phone"),
                columns="2",
                spacing="4",
                width="100%",
            ),
            section_title("Contratos Vigentes", "file_key_2"),
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
                        )
                    )
                ),
                width="100%",
                variant="surface",
            )
        ),
        rx.center(rx.text("No hay detalles de Arrendatario", color=styles.TEXT_TERTIARY), padding="2rem")
    )

    # Pestaña Codeudor
    tab_codeudor = rx.cond(
        PersonasState.detail_codeudor,
        tab_content_container(
            section_title("Garantías Respaldadas", "shield"),
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
                        )
                    )
                ),
                width="100%",
                variant="surface",
            )
        ),
        rx.center(rx.text("No hay detalles de Codeudor", color=styles.TEXT_TERTIARY), padding="2rem")
    )

    # Pestaña Asesor/Proveedor
    tab_otros = tab_content_container(
        rx.cond(
            PersonasState.detail_asesor,
            rx.vstack(
                section_title("Información Asesor", "briefcase"),
                rx.grid(
                    detail_item("Comisión Arriendo", PersonasState.detail_asesor["comision_arriendo"].to(str), "percent"),
                    detail_item("Comisión Venta", PersonasState.detail_asesor["comision_venta"].to(str), "percent"),
                    detail_item("Fecha Ingreso", PersonasState.detail_asesor["fecha_ingreso"].to(str), "calendar_days"),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            )
        ),
        rx.cond(
            PersonasState.detail_proveedor,
            rx.vstack(
                section_title("Información Proveedor", "wrench"),
                rx.grid(
                    detail_item("Especialidad", PersonasState.detail_proveedor["especialidad"].to(str), "award"),
                    detail_item("Calificación", PersonasState.detail_proveedor["calificacion"].to(str), "star"),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                detail_item("Observaciones", PersonasState.detail_proveedor["observaciones"].to(str), "message_square"),
                width="100%",
            )
        )
    )

    return rx.dialog.root(
        rx.dialog.content(
            # Header del Modal
            rx.hstack(
                rx.avatar(
                    fallback=PersonasState.detail_nombre[0:2],
                    size="7",
                    variant="soft",
                    color_scheme="indigo",
                    box_shadow=styles.SHADOW_RAISED_ELITE,
                ),
                rx.vstack(
                    rx.heading(
                        PersonasState.detail_nombre,
                        size="6",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.hstack(
                        rx.foreach(
                            PersonasState.detail_roles_list,
                            role_badge
                        ),
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
                        rx.spinner(size="3"),
                        rx.text("Cargando información detallada...", color=styles.TEXT_SECONDARY),
                        padding="4rem",
                    ),
                    width="100%",
                ),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("General", value="general"),
                        rx.cond(PersonasState.detail_propietario, rx.tabs.trigger("Propietario", value="propietario")),
                        rx.cond(PersonasState.detail_arrendatario, rx.tabs.trigger("Arrendatario", value="arrendatario")),
                        rx.cond(PersonasState.detail_codeudor, rx.tabs.trigger("Codeudor", value="codeudor")),
                        rx.cond(
                            PersonasState.detail_asesor | 
                            PersonasState.detail_proveedor, 
                            rx.tabs.trigger("Profesional", value="otros")
                        ),
                        justify_content="start",
                        box_shadow=styles.SHADOW_INSET_ELITE,
                        border_radius="10px",
                        padding="4px",
                        background=styles.BG_PANEL,
                    ),
                    rx.tabs.content(tab_general, value="general"),
                    rx.tabs.content(tab_propietario, value="propietario"),
                    rx.tabs.content(tab_arrendatario, value="arrendatario"),
                    rx.tabs.content(tab_codeudor, value="codeudor"),
                    rx.tabs.content(tab_otros, value="otros"),
                    default_value="general",
                    width="100%",
                ),
            ),
            
            # Footer
            rx.hstack(
                rx.spacer(),
                rx.dialog.close(
                    rx.button(
                        "Cerrar",
                        style=styles.NEU_BUTTON_STYLE,
                        on_click=PersonasState.close_details_modal,
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
            box_shadow=styles.SHADOW_MODAL_ELITE,
            padding="2rem",
        ),
        open=PersonasState.show_details_modal,
        on_open_change=PersonasState.close_details_modal,
    )

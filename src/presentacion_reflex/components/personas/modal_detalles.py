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
            value if value else "N/A",
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
            detail_item("Nombre Completo", PersonasState.current_persona_details["persona"]["nombre"], "user_round"),
            detail_item("Documento", PersonasState.current_persona_details["persona"]["documento"], "fingerprint"),
            detail_item("Teléfono", PersonasState.current_persona_details["persona"]["telefono"], "phone"),
            detail_item("Correo Electrónico", PersonasState.current_persona_details["persona"]["correo"], "mail"),
            detail_item("Dirección", PersonasState.current_persona_details["persona"]["direccion"], "map_pin"),
            detail_item("Fecha Registro", PersonasState.current_persona_details["persona"]["fecha_creacion"], "calendar"),
            columns="2",
            spacing="4",
            width="100%",
        ),
    )

    # Pestaña Propietario
    tab_propietario = rx.cond(
        PersonasState.current_persona_details["detalles_roles"]["Propietario"],
        tab_content_container(
            section_title("Información Financiera", "banknote"),
            rx.grid(
                detail_item("Banco", PersonasState.current_persona_details["detalles_roles"]["Propietario"]["banco"], "building_2"),
                detail_item("Número de Cuenta", PersonasState.current_persona_details["detalles_roles"]["Propietario"]["cuenta"], "credit_card"),
                detail_item("Tipo de Cuenta", PersonasState.current_persona_details["detalles_roles"]["Propietario"]["tipo_cuenta"], "info"),
                detail_item("Consignatario", PersonasState.current_persona_details["detalles_roles"]["Propietario"]["consignatario"], "user_check"),
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
                        PersonasState.current_persona_details["detalles_roles"]["Propietario"]["propiedades_activas"],
                        lambda prop: rx.table.row(
                            rx.table.cell(prop["matricula"]),
                            rx.table.cell(prop["direccion"]),
                            rx.table.cell(prop["tipo"]),
                            rx.table.cell(prop["disponible"]),
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
        PersonasState.current_persona_details["detalles_roles"]["Arrendatario"],
        tab_content_container(
            section_title("Gestión de Arrendamiento", "clipboard_list"),
            rx.grid(
                detail_item("Código Seguro", PersonasState.current_persona_details["detalles_roles"]["Arrendatario"]["codigo_seguro"], "shield_check"),
                detail_item("Nombre Habitante", PersonasState.current_persona_details["detalles_roles"]["Arrendatario"]["habitante"], "user"),
                detail_item("Teléfono Habitante", PersonasState.current_persona_details["detalles_roles"]["Arrendatario"]["telefono_habitante"], "phone"),
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
                        PersonasState.current_persona_details["detalles_roles"]["Arrendatario"]["contratos_activos"],
                        lambda cont: rx.table.row(
                            rx.table.cell(cont["propiedad"]),
                            rx.table.cell(cont["inicio"]),
                            rx.table.cell(cont["fin"]),
                            rx.table.cell(f"${cont['canon']:,}".replace(",", ".")),
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
        PersonasState.current_persona_details["detalles_roles"]["Codeudor"],
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
                        PersonasState.current_persona_details["detalles_roles"]["Codeudor"]["garantias_activas"],
                        lambda gar: rx.table.row(
                            rx.table.cell(gar["propiedad"]),
                            rx.table.cell(gar["inicio"]),
                            rx.table.cell(gar["estado"]),
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
            PersonasState.current_persona_details["detalles_roles"]["Asesor"],
            rx.vstack(
                section_title("Información Asesor", "briefcase"),
                rx.grid(
                    detail_item("Comisión Arriendo", PersonasState.current_persona_details["detalles_roles"]["Asesor"]["comision_arriendo"], "percent"),
                    detail_item("Comisión Venta", PersonasState.current_persona_details["detalles_roles"]["Asesor"]["comision_venta"], "percent"),
                    detail_item("Fecha Ingreso", PersonasState.current_persona_details["detalles_roles"]["Asesor"]["fecha_ingreso"], "calendar_days"),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            )
        ),
        rx.cond(
            PersonasState.current_persona_details["detalles_roles"]["Proveedor"],
            rx.vstack(
                section_title("Información Proveedor", "wrench"),
                rx.grid(
                    detail_item("Especialidad", PersonasState.current_persona_details["detalles_roles"]["Proveedor"]["especialidad"], "award"),
                    detail_item("Calificación", PersonasState.current_persona_details["detalles_roles"]["Proveedor"]["calificacion"], "star"),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                detail_item("Observaciones", PersonasState.current_persona_details["detalles_roles"]["Proveedor"]["observaciones"], "message_square"),
                width="100%",
            )
        )
    )

    return rx.dialog.root(
        rx.dialog.content(
            # Header del Modal
            rx.hstack(
                rx.avatar(
                    fallback=PersonasState.current_persona_details["persona"]["nombre"][0:2],
                    size="7",
                    variant="soft",
                    color_scheme="indigo",
                    box_shadow=styles.SHADOW_RAISED_ELITE,
                ),
                rx.vstack(
                    rx.heading(
                        PersonasState.current_persona_details["persona"]["nombre"],
                        size="6",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.hstack(
                        rx.foreach(
                            PersonasState.current_persona_details["persona"]["roles"],
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
                        rx.cond(PersonasState.current_persona_details["detalles_roles"]["Propietario"], rx.tabs.trigger("Propietario", value="propietario")),
                        rx.cond(PersonasState.current_persona_details["detalles_roles"]["Arrendatario"], rx.tabs.trigger("Arrendatario", value="arrendatario")),
                        rx.cond(PersonasState.current_persona_details["detalles_roles"]["Codeudor"], rx.tabs.trigger("Codeudor", value="codeudor")),
                        rx.cond(
                            PersonasState.current_persona_details["detalles_roles"]["Asesor"] | 
                            PersonasState.current_persona_details["detalles_roles"]["Proveedor"], 
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

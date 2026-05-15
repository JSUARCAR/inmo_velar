import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.components.personas.role_selector_card import tarjeta_selector_rol
from src.presentacion_reflex.components.personas.wizard_progress import progreso_asistente
from src.presentacion_reflex.state.personas_state import PersonasState


def selector_busqueda(
    etiqueta: str,
    marcador: str,
    etiqueta_valor: rx.Var[str],
    valor_busqueda: rx.Var[str],
    menu_abierto: rx.Var[bool],
    opciones_filtradas: rx.Var[list],
    al_cambiar_busqueda: callable,
    al_alternar_menu: callable,
    al_seleccionar: callable,
) -> rx.Component:
    """Selector con búsqueda integrada con estética Claude."""
    return rx.vstack(
        rx.text(etiqueta, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.hstack(
                        rx.cond(
                            etiqueta_valor == "",
                            rx.text(marcador, color=styles.TEXT_TERTIARY),
                            rx.text(etiqueta_valor, color=styles.TEXT_PRIMARY),
                        ),
                        rx.icon("chevron_down", size=16),
                        width="100%",
                        justify="between",
                    ),
                    style=styles.NEU_BUTTON_STYLE,
                    width="100%",
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    rx.input(
                        placeholder="Buscar...",
                        value=valor_busqueda,
                        on_change=al_cambiar_busqueda,
                        autofocus=True,
                        width="100%",
                        size="1",
                        style=styles.NEU_INPUT_STYLE,
                    ),
                    rx.scroll_area(
                         rx.vstack(
                             rx.foreach(
                                opciones_filtradas,
                                lambda opt: rx.cond(
                                    opt[0] != "",
                                    rx.box(
                                        rx.text(opt[0], size="2"),
                                        width="100%",
                                        padding_x="3",
                                        padding_y="2",
                                        transition=styles.GLOBAL_TRANSITION,
                                        _hover={"bg": styles.BG_HOVER, "color": styles.TEXT_PRIMARY, "cursor": "pointer"},
                                        on_click=lambda: al_seleccionar(opt[1], opt[0]),
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
                    style=styles.NEU_PANEL_STYLE,
                ),
            ),
            open=menu_abierto,
            on_open_change=al_alternar_menu,
        ),
        spacing="1",
        width="100%",
    )


def campo_formulario(
    etiqueta: str,
    nombre: str,
    marcador: str,
    tipo: str = "text",
    obligatorio: bool = False,
    valor_defecto: str = "",
    icono: str = "",
    valor: str = None,
    al_cambiar: str = None,
) -> rx.Component:
    """Campo de formulario elite con icono y estética editorial."""
    
    input_props = {
        "name": nombre,
        "placeholder": marcador,
        "type": tipo,
        "required": obligatorio,
        "width": "100%",
        "size": "3",
        "style": {
            **styles.NEU_INPUT_STYLE,
            "_invalid": {
                "box_shadow": f"{styles.SHADOW_INSET}, 0 0 0 2px rgba(220, 38, 38, 0.4)",
            }
        }
    }
    
    if valor is not None:
        input_props["value"] = valor
        if al_cambiar is not None:
            input_props["on_change"] = al_cambiar
    else:
        input_props["default_value"] = valor_defecto

    return rx.vstack(
        rx.text(etiqueta, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        rx.input(
            rx.cond(icono != "", rx.input.slot(rx.icon(icono, size=16)), rx.fragment()),
            **input_props
        ),
        spacing="1",
        width="100%",
    )


def area_texto_formulario(
    etiqueta: str, 
    nombre: str, 
    marcador: str, 
    valor_defecto: str = "",
    valor: str = None,
    al_cambiar: str = None,
) -> rx.Component:
    """Campo de área de texto editorial."""
    
    input_props = {
        "name": nombre,
        "placeholder": marcador,
        "width": "100%",
        "style": {
            **styles.NEU_INPUT_STYLE,
            "min_height": "120px",
        }
    }
    
    if valor is not None:
        input_props["value"] = valor
        if al_cambiar is not None:
            input_props["on_change"] = al_cambiar
    else:
        input_props["default_value"] = valor_defecto

    return rx.vstack(
        rx.text(etiqueta, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        rx.text_area(**input_props),
        spacing="1",
        width="100%",
    )



def campos_codeudor() -> rx.Component:
    """Campos específicos de Codeudor - Versión Editorial."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("shield_check", size=18, color=styles.BRAND_PRIMARY),
                rx.text("Información de Garantía", size="3", weight="bold", color=styles.BRAND_PRIMARY),
                spacing="2",
            ),
            rx.text(
                "El codeudor actúa como garante del contrato. No se requieren campos adicionales obligatorios en esta etapa, pero puede añadir notas aquí.",
                size="2",
                color=styles.TEXT_SECONDARY,
            ),
            area_texto_formulario(
                "Observaciones de Garantía",
                "observaciones_codeudor",
                "Ej: Propietario de finca raíz, etc.",
                valor=PersonasState.form_data["observaciones_codeudor"],
                al_cambiar=lambda val: PersonasState.set_upper("observaciones_codeudor", val),
            ),
            spacing="4",
            width="100%",
        ),
        style=styles.NEU_PANEL_STYLE,
    )


def campos_propietario() -> rx.Component:
    """Campos específicos de Propietario - Versión Editorial."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("landmark", size=18, color=styles.BRAND_PRIMARY),
                rx.text("Información General Propietario", size="3", weight="bold", color=styles.BRAND_PRIMARY),
                spacing="2",
            ),
            rx.text(
                "La información bancaria ahora se gestiona directamente en los Contratos de Mandato para mayor flexibilidad por propiedad.",
                size="2",
                color=styles.TEXT_SECONDARY,
                font_style="italic",
            ),
            area_texto_formulario(
                "Observaciones",
                "observaciones_propietario",
                "Notas adicionales sobre el propietario...",
                valor=PersonasState.form_data["observaciones_propietario"],
                al_cambiar=lambda val: PersonasState.set_upper("observaciones_propietario", val),
            ),
            spacing="4",
            width="100%",
        ),
        style=styles.NEU_PANEL_STYLE,
    )


def campos_arrendatario() -> rx.Component:
    """Campos específicos de Arrendatario - Versión Editorial."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("shield-check", size=18, color=styles.BRAND_PRIMARY),
                rx.text("Información de Seguro", size="3", weight="bold", color=styles.TEXT_PRIMARY),
                spacing="2",
            ),
            rx.grid(
                campo_formulario(
                    "Código Aprobación Seguro",
                    "codigo_aprobacion_seguro",
                    "Ej: AB-123",
                    valor=PersonasState.form_data["codigo_aprobacion_seguro"],
                    al_cambiar=lambda val: PersonasState.set_upper("codigo_aprobacion_seguro", val),
                    icono="file_check",
                ),
                selector_busqueda(
                    "ID Seguro (Opcional)",
                    "Seleccione un seguro...",
                    PersonasState.seguro_selected_label,
                    PersonasState.seguro_search,
                    PersonasState.seguro_menu_open,
                    PersonasState.filtered_seguros_options,
                    PersonasState.set_seguro_search,
                    PersonasState.toggle_seguro_menu,
                    PersonasState.select_seguro,
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            rx.grid(
                campo_formulario(
                    "Nombre Completo Habitante",
                    "nombre_habitante",
                    "Ej: JOSE MARÍA VACA",
                    valor=PersonasState.form_data["nombre_habitante"],
                    al_cambiar=lambda val: PersonasState.set_upper("nombre_habitante", val),
                    icono="user",
                ),
                campo_formulario(
                    "Teléfono Habitante",
                    "telefono_habitante",
                    "Ej: 3001234567",
                    valor=PersonasState.form_data["telefono_habitante"],
                    al_cambiar=lambda val: PersonasState.set_telefono_habitante(val),
                    icono="phone",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        style=styles.NEU_PANEL_STYLE,
    )


def campos_asesor() -> rx.Component:
    """Campos específicos de Asesor - Versión Editorial."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("percent", size=18, color=styles.BRAND_PRIMARY),
                rx.text("Comisiones", size="3", weight="bold", color=styles.BRAND_PRIMARY),
                spacing="2",
            ),
            rx.grid(
                campo_formulario(
                    "Comisión % Arriendo",
                    "comision_porcentaje_arriendo",
                    "Ej: 10",
                    tipo="number",
                    valor=PersonasState.form_data["comision_porcentaje_arriendo"],
                    al_cambiar=lambda val: PersonasState.set_form_value("comision_porcentaje_arriendo", val),
                    icono="percent",
                ),
                campo_formulario(
                    "Comisión % Venta",
                    "comision_porcentaje_venta",
                    "Ej: 3",
                    tipo="number",
                    valor=PersonasState.form_data["comision_porcentaje_venta"],
                    al_cambiar=lambda val: PersonasState.set_form_value("comision_porcentaje_venta", val),
                    icono="percent",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4",
                width="100%",
            ),
            campo_formulario(
                "Fecha Vinculación",
                "fecha_vinculacion",
                "YYYY-MM-DD",
                tipo="date",
                valor=PersonasState.form_data["fecha_vinculacion"],
                al_cambiar=lambda val: PersonasState.set_form_value("fecha_vinculacion", val),
                icono="calendar",
            ),
            spacing="4",
            width="100%",
        ),
        style=styles.NEU_PANEL_STYLE,
    )


def campos_proveedor() -> rx.Component:
    """Campos específicos de Proveedor - Versión Editorial."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("wrench", size=18, color=styles.BRAND_PRIMARY),
                rx.text("Información Profesional", size="3", weight="bold", color=styles.BRAND_PRIMARY),
                spacing="2",
            ),
            campo_formulario(
                "Especialidad",
                "especialidad",
                "Ej: Plomería, Electricidad",
                valor=PersonasState.form_data["especialidad"],
                al_cambiar=lambda val: PersonasState.set_upper("especialidad", val),
                icono="wrench",
            ),
            campo_formulario(
                "Calificación (1-5)",
                "calificacion",
                "Ej: 5",
                tipo="number",
                valor=PersonasState.form_data["calificacion"],
                al_cambiar=lambda val: PersonasState.set_form_value("calificacion", val),
                icono="star",
            ),
            area_texto_formulario(
                "Observaciones",
                "observaciones",
                "Ej: Disponible fines de semana",
                valor=PersonasState.form_data["observaciones"],
                al_cambiar=lambda val: PersonasState.set_upper("observaciones", val),
            ),
            spacing="4",
            width="100%",
        ),
        style=styles.NEU_PANEL_STYLE,
    )



# Pasos del Asistente (Wizard)
def paso_1_info_basica() -> rx.Component:
    """Paso 1: Información Básica."""
    return rx.vstack(
        rx.flex(
            rx.vstack(
                rx.text("Tipo Doc", size="2", weight="bold", color=styles.TEXT_PRIMARY),
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Tipo...",
                        style=styles.NEU_SELECT_STYLE,
                        width="100%",
                    ),
                    rx.select.content(
                        rx.select.item("CC", value="CC"),
                        rx.select.item("NIT", value="NIT"),
                        rx.select.item("CE", value="CE"),
                        rx.select.item("PAS", value="PAS"),
                        style={
                            "background": styles.BG_PANEL,
                            "box_shadow": styles.SHADOW_WHISPER,
                            "border_radius": "12px",
                        },
                    ),
                    name="tipo_documento",
                    value=rx.cond(
                        PersonasState.is_editing, PersonasState.form_data["tipo_documento"], "CC"
                    ),
                ),
                width=["100%", "25%"],
            ),
            rx.box(
                campo_formulario(
                    "Número Documento",
                    "numero_documento",
                    "Ej: 123456789",
                    obligatorio=True,
                    valor=PersonasState.form_data["numero_documento"],
                    al_cambiar=lambda val: PersonasState.set_numero_documento(val),
                    icono="credit-card",
                ),
                width=["100%", "75%"],
            ),
            flex_direction=["column", "row"],
            width="100%",
            gap="4",
        ),
        campo_formulario(
            "Nombre Completo / Razón Social",
            "nombre_completo",
            "Ej: Juan Pérez S.A.S",
            obligatorio=True,
            valor=PersonasState.form_data["nombre_completo"],
            al_cambiar=lambda val: PersonasState.set_upper("nombre_completo", val),
            icono="user",
        ),
        rx.grid(
            campo_formulario(
                "Teléfono Principal",
                "telefono_principal",
                "Ej: 3001234567",
                obligatorio=True,
                valor=PersonasState.form_data["telefono_principal"],
                al_cambiar=lambda val: PersonasState.set_form_value("telefono_principal", val),
                icono="phone",
            ),
            campo_formulario(
                "Correo Electrónico",
                "correo_electronico",
                "Ej: contacto@empresa.com",
                tipo="email",
                valor=PersonasState.form_data["correo_electronico"],
                al_cambiar=lambda val: PersonasState.set_upper("correo_electronico", val),
                icono="mail",
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="4",
            width="100%",
        ),
        campo_formulario(
            "Dirección Principal",
            "direccion_principal",
            "Ej: Calle 123 # 45-67",
            valor=PersonasState.form_data["direccion_principal"],
            al_cambiar=lambda val: PersonasState.set_upper("direccion_principal", val),
            icono="map_pin",
        ),
        spacing="5",
        width="100%",
    )


def paso_2_roles() -> rx.Component:
    """Paso 2: Selección de Roles con Tarjetas Editorial."""
    return rx.vstack(
        rx.text(
            "Seleccione uno o más roles para esta persona",
            size="2",
            color=styles.TEXT_SECONDARY,
            text_align="center",
            margin_bottom="2",
        ),
        rx.box(
            rx.foreach(PersonasState.available_roles, tarjeta_selector_rol),
            display="grid",
            grid_template_columns=[
                "repeat(1, 1fr)",  # mobile
                "repeat(2, 1fr)",  # tablet+
            ],
            gap="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def paso_3_detalles_rol() -> rx.Component:
    """Paso 3: Detalles específicos según el rol seleccionado."""
    return rx.vstack(
        rx.cond(
            PersonasState.selected_roles.length() > 0,
            rx.vstack(
                # Campos de Propietario
                rx.cond(
                    PersonasState.is_propietario_selected,
                    campos_propietario(),
                ),
                # Campos de Arrendatario
                rx.cond(
                    PersonasState.is_arrendatario_selected,
                    campos_arrendatario(),
                ),
                # Campos de Codeudor
                rx.cond(
                    PersonasState.is_codeudor_selected,
                    campos_codeudor(),
                ),
                # Campos de Asesor
                rx.cond(
                    PersonasState.is_asesor_selected,
                    campos_asesor(),
                ),
                # Campos de Proveedor
                rx.cond(
                    PersonasState.is_proveedor_selected,
                    campos_proveedor(),
                ),
                spacing="6",
                width="100%",
            ),
            # Mensaje cuando no hay roles seleccionados
            rx.center(
                rx.vstack(
                    rx.icon("circle_alert", size=32, color=styles.TEXT_TERTIARY),
                    rx.text(
                        "No hay roles seleccionados",
                        size="3",
                        weight="medium",
                        color=styles.TEXT_SECONDARY,
                    ),
                    rx.text(
                        "Selecciona al menos un rol en el paso anterior",
                        size="2",
                        color=styles.TEXT_TERTIARY,
                    ),
                    spacing="2",
                    align="center",
                ),
                padding="6",
            ),
        ),
        width="100%",
    )


def modal_persona() -> rx.Component:
    """Modal de asistente multi-paso para crear/editar Persona."""

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Título
                rx.dialog.title(
                    rx.hstack(
                        rx.icon(
                            rx.cond(PersonasState.is_editing, "user_pen", "user_plus"),
                            size=24,
                            color=styles.BRAND_PRIMARY,
                        ),
                        rx.text(
                            rx.cond(PersonasState.is_editing, "Editar Persona", "Nueva Persona"),
                            size="6",
                            weight="bold",
                        ),
                        spacing="2",
                        align="center",
                    )
                ),
                # Indicador de Progreso
                progreso_asistente(),
                # Mensaje de error
                rx.cond(
                    PersonasState.error_message != "",
                    rx.callout(
                        PersonasState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                # Formulario con contenido dinámico según el paso
                rx.form(
                    rx.vstack(
                        rx.box(
                            rx.match(
                                PersonasState.modal_step,
                                (1, paso_1_info_basica()),
                                (2, paso_2_roles()),
                                (3, paso_3_detalles_rol()),
                                paso_1_info_basica(),  # respaldo
                            ),
                            # Altura responsiva y scroll
                            min_height="300px",
                            max_height="60vh",
                            overflow_y="auto",
                            width="100%",
                            padding_right="2", # evitar solapamiento de scroll
                        ),
                        # Botones de Navegación
                        rx.hstack(
                            # Botón Atrás
                            rx.cond(
                                PersonasState.modal_step > 1,
                                rx.button(
                                    rx.hstack(rx.icon("chevron_left", size=16), rx.text("Anterior")),
                                    type="button",
                                    on_click=PersonasState.prev_modal_step,
                                    size="3",
                                    style=styles.NEU_BUTTON_STYLE,
                                ),
                                rx.fragment(),
                            ),
                            rx.dialog.close(
                                rx.button(
                                    "Cancelar",
                                    type="button",
                                    on_click=PersonasState.close_modal,
                                    size="3",
                                    style=styles.NEU_BUTTON_STYLE,
                                ),
                            ),
                            rx.spacer(),
                            # Botón Siguiente / Guardar
                            rx.cond(
                                PersonasState.modal_step < 3,
                                rx.button(
                                    rx.hstack(rx.text("Siguiente"), rx.icon("chevron_right", size=16)),
                                    type="submit",
                                    size="3",
                                    style=styles.NEU_BUTTON_PRIMARY_STYLE,
                                ),
                                rx.button(
                                    rx.hstack(rx.icon("save", size=16), rx.text("Guardar")),
                                    type="submit",
                                    loading=PersonasState.is_loading,
                                    size="3",
                                    style=styles.NEU_BUTTON_PRIMARY_STYLE,
                                ),
                            ),
                            spacing="2",
                            width="100%",
                            justify="between",
                            margin_top="4",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    # Manejador de envío unificado
                    on_submit=PersonasState.handle_form_submit,
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            style={
                **styles.NEU_PANEL_STYLE,
                "max_width": "700px",
                "width": "95%",
                "padding": "24px",
                "transition": "box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
            },
            on_escape_key_down=PersonasState.close_modal,
            on_pointer_down_outside=PersonasState.close_modal,
        ),
        open=PersonasState.show_modal,
    )

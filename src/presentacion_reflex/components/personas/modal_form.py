import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root, neuro_text_area, neuro_panel
from src.presentacion_reflex.components.personas.role_selector_card import role_selector_card
from src.presentacion_reflex.components.personas.wizard_progress import wizard_progress
from src.presentacion_reflex.state.personas_state import PersonasState


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
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        rx.popover.root(
            rx.popover.trigger(
                neuro_button(
                    rx.hstack(
                        rx.cond(
                            value_label == "",
                            rx.text(placeholder, color=styles.TEXT_TERTIARY),
                            rx.text(value_label, color=styles.TEXT_PRIMARY),
                        ),
                        rx.icon("chevron-down", size=16),
                        width="100%",
                        justify="between",
                    ),
                    width="100%",
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    neuro_input(
                        placeholder="Buscar...",
                        value=search_value,
                        on_change=on_change_search,
                        autofocus=True,
                        width="100%",
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
                                        transition=styles.GLOBAL_TRANSITION,
                                        _hover={"bg": styles.BG_HOVER, "color": styles.TEXT_PRIMARY, "cursor": "pointer", "box_shadow": styles.NEU_MODAL_SHADOW},
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
                    style=styles.NEU_PANEL_STYLE,
                ),
            ),
            open=menu_open,
            on_open_change=on_toggle_menu,
        ),
        spacing="1",
        width="100%",
    )


def form_field(
    label: str,
    name: str,
    placeholder: str,
    type: str = "text",
    required: bool = False,
    default_value: str = "",
    icon: str = "",
    value: str = None,
    on_change: str = None,
) -> rx.Component:
    """Elite form field with icon and enhanced styling."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        neuro_input(
            rx.cond(icon != "", rx.input.slot(rx.icon(icon, size=16)), rx.fragment()),
            name=name,
            placeholder=placeholder,
            type=type,
            required=required,
            default_value=default_value,
            value=value,
            on_change=on_change,
            width="100%",
            size="3",
            style={
                "_invalid": {
                    "box_shadow": f"{styles.NEU_INSET}, 0 0 0 2px rgba(220, 38, 38, 0.4)",
                }
            }
        ),
        spacing="1",
        width="100%",
    )


def form_textarea(
    label: str, 
    name: str, 
    placeholder: str, 
    default_value: str = "",
    value: str = None,
    on_change: str = None,
) -> rx.Component:
    """Elite textarea field."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        neuro_text_area(
            name=name,
            placeholder=placeholder,
            default_value=default_value,
            value=value,
            on_change=on_change,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )



def propietario_fields() -> rx.Component:
    """Campos específicos de Propietario - Elite version."""
    return neuro_panel(
        rx.vstack(
            rx.hstack(
                rx.icon("landmark", size=18, color=styles.ACCENT_COLOR),
                rx.text("Información Bancaria", size="3", weight="bold", color=styles.ACCENT_COLOR),
                spacing="2",
            ),
            form_field(
                "Banco",
                "banco_propietario",
                "Ej: Bancolombia",
                default_value=PersonasState.form_data["banco_propietario"],
                value=PersonasState.form_data["banco_propietario"],
                on_change=lambda val: PersonasState.set_upper("banco_propietario", val),
                icon="landmark",
            ),
            rx.grid(
                form_field(
                    "Número de Cuenta",
                    "numero_cuenta_propietario",
                    "Ej: 123456789",
                    default_value=PersonasState.form_data["numero_cuenta_propietario"],
                    icon="hash",
                ),
                rx.vstack(
                    rx.text("Tipo de Cuenta", size="2", weight="bold", color=styles.TEXT_PRIMARY),
                    neuro_select_root(
                        [
                            rx.select.item("Ahorros", value="Ahorros"),
                            rx.select.item("Corriente", value="Corriente"),
                        ],
                        name="tipo_cuenta",
                        value=rx.cond(
                            PersonasState.form_data["tipo_cuenta"] != "",
                            PersonasState.form_data["tipo_cuenta"],
                            "Ahorros",
                        ),
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="3",
                width="100%",
            ),
            form_field(
                "Cédula Consignatario",
                "documento_consignatario",
                "Documento de quien recibe el pago",
                default_value=PersonasState.form_data["documento_consignatario"],
                icon="credit-card",
            ),
            form_field(
                "Nombre Consignatario",
                "consignatario",
                "Nombre de quien recibe el pago",
                default_value=PersonasState.form_data["consignatario"],
                value=PersonasState.form_data["consignatario"],
                on_change=lambda val: PersonasState.set_upper("consignatario", val),
                icon="user-check",
            ),
            form_textarea(
                "Observaciones",
                "observaciones_propietario",
                "Notas adicionales...",
                default_value=PersonasState.form_data["observaciones_propietario"],
                value=PersonasState.form_data["observaciones_propietario"],
                on_change=lambda val: PersonasState.set_upper("observaciones_propietario", val),
            ),
            spacing="3",
            width="100%",
        ),
        padding="4",
    )


def arrendatario_fields() -> rx.Component:
    """Campos específicos de Arrendatario - Elite version."""
    return neuro_panel(
        rx.vstack(
            rx.hstack(
                rx.icon("shield-check", size=18, color=styles.ACCENT_COLOR),
                rx.text("Información de Seguro", size="3", weight="bold", color=styles.TEXT_PRIMARY),
                spacing="2",
            ),
            rx.grid(
                form_field(
                    "Código Aprobación Seguro",
                    "codigo_aprobacion_seguro",
                    "Ej: AB-123",
                    default_value=PersonasState.form_data["codigo_aprobacion_seguro"],
                    icon="file-check",
                ),
                searchable_select(
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
                spacing="3",
                width="100%",
            ),
            rx.grid(
                form_field(
                    "Nombre Completo Habitante",
                    "nombre_habitante",
                    "Ej: JOSE MARÍA VACA",
                    default_value=PersonasState.form_data["nombre_habitante"],
                    value=PersonasState.form_data["nombre_habitante"],
                    on_change=lambda val: PersonasState.set_upper("nombre_habitante", val),
                    icon="user",
                ),
                form_field(
                    "Teléfono Habitante",
                    "telefono_habitante",
                    "Ej: 3001234567",
                    default_value=PersonasState.form_data["telefono_habitante"],
                    value=PersonasState.form_data["telefono_habitante"],
                    on_change=lambda val: PersonasState.set_telefono_habitante(val),
                    icon="phone",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="3",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        padding="4",
    )


def asesor_fields() -> rx.Component:
    """Campos específicos de Asesor - Elite version."""
    return neuro_panel(
        rx.vstack(
            rx.hstack(
                rx.icon("percent", size=18, color="var(--purple-9)"),
                rx.text("Comisiones", size="3", weight="bold", color="var(--purple-11)"),
                spacing="2",
            ),
            rx.grid(
                form_field(
                    "Comisión % Arriendo",
                    "comision_porcentaje_arriendo",
                    "Ej: 10",
                    type="number",
                    default_value=PersonasState.form_data["comision_porcentaje_arriendo"],
                    icon="percent",
                ),
                form_field(
                    "Comisión % Venta",
                    "comision_porcentaje_venta",
                    "Ej: 3",
                    type="number",
                    default_value=PersonasState.form_data["comision_porcentaje_venta"],
                    icon="percent",
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="3",
                width="100%",
            ),
            form_field(
                "Fecha Vinculación",
                "fecha_vinculacion",
                "YYYY-MM-DD",
                type="date",
                default_value=PersonasState.form_data["fecha_vinculacion"],
                icon="calendar",
            ),
            spacing="3",
            width="100%",
        ),
        padding="4",
    )


def proveedor_fields() -> rx.Component:
    """Campos específicos de Proveedor - Elite version."""
    return neuro_panel(
        rx.vstack(
            rx.hstack(
                rx.icon("wrench", size=18, color="var(--cyan-9)"),
                rx.text("Información Profesional", size="3", weight="bold", color="var(--cyan-11)"),
                spacing="2",
            ),
            form_field(
                "Especialidad",
                "especialidad",
                "Ej: Plomería, Electricidad",
                default_value=PersonasState.form_data["especialidad"],
                value=PersonasState.form_data["especialidad"],
                on_change=lambda val: PersonasState.set_upper("especialidad", val),
                icon="wrench",
            ),
            form_field(
                "Calificación (1-5)",
                "calificacion",
                "Ej: 5",
                type="number",
                default_value=PersonasState.form_data["calificacion"],
                icon="star",
            ),
            form_textarea(
                "Observaciones",
                "observaciones",
                "Ej: Disponible fines de semana",
                default_value=PersonasState.form_data["observaciones"],
                value=PersonasState.form_data["observaciones"],
                on_change=lambda val: PersonasState.set_upper("observaciones", val),
            ),
            spacing="3",
            width="100%",
        ),
        padding="4",
    )



# Wizard Steps
def step_1_basic_info() -> rx.Component:
    """Step 1: Basic Information."""
    return rx.vstack(
        rx.flex(
            rx.vstack(
                rx.text("Tipo Doc", size="2", weight="bold", color=styles.TEXT_PRIMARY),
                neuro_select_root(
                    [
                        rx.select.item("CC", value="CC"),
                        rx.select.item("NIT", value="NIT"),
                        rx.select.item("CE", value="CE"),
                        rx.select.item("PAS", value="PAS"),
                    ],
                    name="tipo_documento",
                    value=rx.cond(
                        PersonasState.is_editing, PersonasState.form_data["tipo_documento"], "CC"
                    ),
                    width="100%",
                ),
                width=["100%", "25%"],
            ),
            rx.box(
                form_field(
                    "Número Documento",
                    "numero_documento",
                    "Ej: 123456789",
                    required=True,
                    default_value=PersonasState.form_data["numero_documento"],
                    icon="credit-card",
                ),
                width=["100%", "75%"],
            ),
            flex_direction=["column", "row"],
            width="100%",
            gap="3",
        ),
        form_field(
            "Nombre Completo / Razón Social",
            "nombre_completo",
            "Ej: Juan Pérez S.A.S",
            required=True,
            default_value=PersonasState.form_data["nombre_completo"],
            value=PersonasState.form_data["nombre_completo"],
            on_change=lambda val: PersonasState.set_upper("nombre_completo", val),
            icon="user",
        ),
        rx.grid(
            form_field(
                "Teléfono Principal",
                "telefono_principal",
                "Ej: 3001234567",
                required=True,
                default_value=PersonasState.form_data["telefono_principal"],
                icon="phone",
            ),
            form_field(
                "Correo Electrónico",
                "correo_electronico",
                "Ej: contacto@empresa.com",
                type="email",
                default_value=PersonasState.form_data["correo_electronico"],
                value=PersonasState.form_data["correo_electronico"],
                on_change=lambda val: PersonasState.set_upper("correo_electronico", val),
                icon="mail",
            ),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="3",
            width="100%",
        ),
        form_field(
            "Dirección Principal",
            "direccion_principal",
            "Ej: Calle 123 # 45-67",
            default_value=PersonasState.form_data["direccion_principal"],
            value=PersonasState.form_data["direccion_principal"],
            on_change=lambda val: PersonasState.set_upper("direccion_principal", val),
            icon="map-pin",
        ),
        spacing="4",
        width="100%",
    )


def step_2_roles() -> rx.Component:
    """Step 2: Role Selection with Elite Cards."""
    return rx.vstack(
        rx.text(
            "Seleccione uno o más roles para esta persona",
            size="2",
            color=styles.TEXT_SECONDARY,
            text_align="center",
        ),
        rx.box(
            rx.foreach(PersonasState.available_roles, role_selector_card),            display="grid",
            grid_template_columns=[
                "repeat(1, 1fr)",  # mobile
                "repeat(2, 1fr)",  # tablet+
            ],
            gap="3",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def step_3_role_details() -> rx.Component:
    """Step 3: Role-specific details."""
    return rx.vstack(
        rx.cond(
            PersonasState.selected_roles.length() > 0,
            rx.vstack(
                # Propietario fields
                rx.cond(
                    PersonasState.is_propietario_selected,
                    propietario_fields(),
                ),
                # Arrendatario fields
                rx.cond(
                    PersonasState.is_arrendatario_selected,
                    arrendatario_fields(),
                ),
                # Asesor fields
                rx.cond(
                    PersonasState.is_asesor_selected,
                    asesor_fields(),
                ),
                # Proveedor fields
                rx.cond(
                    PersonasState.is_proveedor_selected,
                    proveedor_fields(),
                ),
                spacing="4",
                width="100%",
            ),
            # No roles selected message
            rx.center(
                rx.vstack(
                    rx.icon("circle-alert", size=32, color="var(--gray-8)"),
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
    """Elite Multi-Step Wizard Modal for creating/editing Persona."""

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Title
                rx.dialog.title(
                    rx.hstack(
                        rx.icon(
                            rx.cond(PersonasState.is_editing, "user-pen", "user-plus"),
                            size=24,
                            color="var(--purple-9)",
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
                # Wizard Progress Indicator
                wizard_progress(),
                # Error message
                rx.cond(
                    PersonasState.error_message != "",
                    rx.callout(
                        PersonasState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                # Form with conditional step content
                rx.form(
                    rx.vstack(
                        rx.box(
                            rx.match(
                                PersonasState.modal_step,
                                (1, step_1_basic_info()),
                                (2, step_2_roles()),
                                (3, step_3_role_details()),
                                step_1_basic_info(),  # fallback
                            ),
                            # Responsive height and scroll
                            min_height="300px",
                            max_height="60vh",
                            overflow_y="auto",
                            width="100%",
                            padding_right="2", # avoid scrollbar overlap
                        ),
                        # Navigation Buttons
                        rx.hstack(
                            # Back button
                            rx.cond(
                                PersonasState.modal_step > 1,
                                neuro_button(
                                    rx.hstack(rx.icon("chevron-left", size=16), rx.text("Anterior")),
                                    type="button",
                                    on_click=PersonasState.prev_modal_step,
                                    size="3",
                                ),
                                rx.fragment(),
                            ),
                            rx.dialog.close(
                                neuro_button(
                                    "Cancelar",
                                    type="button",
                                    on_click=PersonasState.close_modal,
                                    size="3",
                                ),
                            ),
                            rx.spacer(),
                            # Next / Save button
                            rx.cond(
                                PersonasState.modal_step < 3,
                                neuro_button(
                                    rx.hstack(rx.text("Siguiente"), rx.icon("chevron-right", size=16)),
                                    type="submit",  # Changed to submit to capture form data
                                    size="3",
                                ),
                                neuro_button(
                                    rx.hstack(rx.icon("save", size=16), rx.text("Guardar")),
                                    type="submit",
                                    loading=PersonasState.is_loading,
                                    size="3",
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
                    # Unified submit handler for all steps
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


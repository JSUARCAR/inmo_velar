import reflex as rx

from src.presentacion_reflex.components.personas.role_selector_card import role_selector_card
from src.presentacion_reflex.components.personas.wizard_progress import wizard_progress
from src.presentacion_reflex.state.personas_state import PersonasState


def form_field(
    label: str,
    name: str,
    placeholder: str,
    type: str = "text",
    required: bool = False,
    default_value: str = "",
    icon: str = "",
) -> rx.Component:
    """Elite form field with icon and enhanced styling."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color="var(--gray-12)"),
        rx.input(
            rx.cond(icon != "", rx.input.slot(rx.icon(icon, size=16)), rx.fragment()),
            name=name,
            placeholder=placeholder,
            type=type,
            required=required,
            default_value=default_value,
            width="100%",
            size="3",
            style={
                "transition": "all 0.2s ease",
            },
            _focus={
                "box_shadow": "0 0 0 2px rgba(102, 126, 234, 0.2)",
            },
        ),
        spacing="1",
        width="100%",
    )


def form_textarea(label: str, name: str, placeholder: str, default_value: str = "") -> rx.Component:
    """Elite textarea field."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color="var(--gray-12)"),
        rx.text_area(
            name=name,
            placeholder=placeholder,
            default_value=default_value,
            width="100%",
            size="3",
        ),
        spacing="1",
        width="100%",
    )


def propietario_fields() -> rx.Component:
    """Campos específicos de Propietario - Elite version."""
    return rx.vstack(
        rx.hstack(
            rx.icon("landmark", size=18, color="var(--blue-9)"),
            rx.text("Información Bancaria", size="3", weight="bold", color="var(--blue-11)"),
            spacing="2",
        ),
        form_field(
            "Banco",
            "banco_propietario",
            "Ej: Bancolombia",
            default_value=PersonasState.form_data["banco_propietario"],
            icon="landmark",
        ),
        rx.hstack(
            form_field(
                "Número de Cuenta",
                "numero_cuenta_propietario",
                "Ej: 123456789",
                default_value=PersonasState.form_data["numero_cuenta_propietario"],
                icon="hash",
            ),
            rx.vstack(
                rx.text("Tipo de Cuenta", size="2", weight="bold", color="var(--gray-12)"),
                rx.select(
                    ["Ahorros", "Corriente"],
                    name="tipo_cuenta",
                    default_value=rx.cond(
                        PersonasState.form_data["tipo_cuenta"] != "",
                        PersonasState.form_data["tipo_cuenta"],
                        "Ahorros",
                    ),
                    width="100%",
                    size="3",
                ),
                spacing="1",
                width="50%",
            ),
            spacing="3",
            width="100%",
        ),
        form_textarea(
            "Observaciones",
            "observaciones_propietario",
            "Notas adicionales...",
            default_value=PersonasState.form_data["observaciones_propietario"],
        ),
        spacing="3",
        width="100%",
        padding="4",
        border_radius="8px",
        style={
            "background": "var(--blue-2)",
            "border": "1px solid var(--blue-6)",
        },
    )


def arrendatario_fields() -> rx.Component:
    """Campos específicos de Arrendatario - Elite version."""
    return rx.vstack(
        rx.hstack(
            rx.icon("shield-check", size=18, color="var(--green-9)"),
            rx.text("Información de Seguro", size="3", weight="bold", color="var(--green-11)"),
            spacing="2",
        ),
        form_field(
            "Dirección de Referencia",
            "direccion_referencia",
            "Ej: Calle 456 # 78-90",
            default_value=PersonasState.form_data["direccion_referencia"],
            icon="map-pin",
        ),
        rx.hstack(
            form_field(
                "Código Aprobación Seguro",
                "codigo_aprobacion_seguro",
                "Ej: AB-123",
                default_value=PersonasState.form_data["codigo_aprobacion_seguro"],
                icon="file-check",
            ),
            form_field(
                "ID Seguro (Opcional)",
                "id_seguro",
                "ID numérico",
                type="number",
                default_value=PersonasState.form_data["id_seguro"],
                icon="hash",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="3",
        width="100%",
        padding="4",
        border_radius="8px",
        style={
            "background": "var(--green-2)",
            "border": "1px solid var(--green-6)",
        },
    )


def asesor_fields() -> rx.Component:
    """Campos específicos de Asesor - Elite version."""
    return rx.vstack(
        rx.hstack(
            rx.icon("percent", size=18, color="var(--purple-9)"),
            rx.text("Comisiones", size="3", weight="bold", color="var(--purple-11)"),
            spacing="2",
        ),
        rx.hstack(
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
        padding="4",
        border_radius="8px",
        style={
            "background": "var(--purple-2)",
            "border": "1px solid var(--purple-6)",
        },
    )


def proveedor_fields() -> rx.Component:
    """Campos específicos de Proveedor - Elite version."""
    return rx.vstack(
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
        ),
        spacing="3",
        width="100%",
        padding="4",
        border_radius="8px",
        style={
            "background": "var(--cyan-2)",
            "border": "1px solid var(--cyan-6)",
        },
    )


# Wizard Steps
def step_1_basic_info() -> rx.Component:
    """Step 1: Basic Information."""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Tipo Doc", size="2", weight="bold", color="var(--gray-12)"),
                rx.select(
                    ["CC", "NIT", "CE", "PAS"],
                    name="tipo_documento",
                    default_value=rx.cond(
                        PersonasState.is_editing, PersonasState.form_data["tipo_documento"], "CC"
                    ),
                    width="100%",
                    size="3",
                ),
                width="25%",
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
                width="75%",
            ),
            width="100%",
            spacing="3",
        ),
        form_field(
            "Nombre Completo / Razón Social",
            "nombre_completo",
            "Ej: Juan Pérez S.A.S",
            required=True,
            default_value=PersonasState.form_data["nombre_completo"],
            icon="user",
        ),
        rx.hstack(
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
                icon="mail",
            ),
            spacing="3",
            width="100%",
        ),
        form_field(
            "Dirección Principal",
            "direccion_principal",
            "Ej: Calle 123 # 45-67",
            default_value=PersonasState.form_data["direccion_principal"],
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
            color="var(--gray-11)",
            text_align="center",
        ),
        rx.box(
            rx.foreach(PersonasState.available_roles, role_selector_card),
            display="grid",
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
                        color="var(--gray-11)",
                    ),
                    rx.text(
                        "Selecciona al menos un rol en el paso anterior",
                        size="2",
                        color="var(--gray-10)",
                    ),
                    spacing="2",
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
                            min_height="300px",
                            width="100%",
                        ),
                        # Navigation Buttons
                        rx.hstack(
                            # Back button
                            rx.cond(
                                PersonasState.modal_step > 1,
                                rx.button(
                                    rx.icon("chevron-left", size=16),
                                    "Anterior",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                    on_click=PersonasState.prev_modal_step,
                                    size="3",
                                ),
                                rx.fragment(),
                            ),
                            rx.dialog.close(
                                rx.button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                    on_click=PersonasState.close_modal,
                                    size="3",
                                ),
                            ),
                            rx.spacer(),
                            # Next / Save button
                            rx.cond(
                                PersonasState.modal_step < 3,
                                rx.button(
                                    "Siguiente",
                                    rx.icon("chevron-right", size=16),
                                    type="submit",  # Changed to submit to capture form data
                                    size="3",
                                    style={
                                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                        "color": "white",
                                    },
                                ),
                                rx.button(
                                    rx.icon("save", size=16),
                                    "Guardar",
                                    type="submit",
                                    loading=PersonasState.is_loading,
                                    size="3",
                                    style={
                                        "background": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
                                        "color": "white",
                                    },
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
            max_width="700px",
            width="100%",
            padding="6",
            on_escape_key_down=PersonasState.close_modal,
            on_pointer_down_outside=PersonasState.close_modal,
        ),
        open=PersonasState.show_modal,
    )

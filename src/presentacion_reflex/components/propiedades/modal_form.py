import reflex as rx

from src.presentacion_reflex.components.propiedades.wizard_progress import wizard_progress
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_select_root,
    neuro_button,
    neuro_text_area,
    neuro_divider,
)
from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex import styles


def form_field(label: str, content: rx.Component, error: str = None) -> rx.Component:
    """Helper para campos de formulario con estilo elite."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        content,
        rx.cond(error, rx.text(error, color="red", size="1"), rx.fragment()),
        width="100%",
        spacing="4", 
    )


def step_1_content() -> rx.Component:
    """Paso 1: Información Básica"""
    return rx.vstack(
        rx.grid(
            # Matrícula
            form_field(
                "Matrícula Inmobiliaria",
                neuro_input(
                    rx.input.slot(rx.icon("file-text", size=16, color="var(--gray-10)")),
                    placeholder="Ej: 001-123456",
                    value=PropiedadesState.form_data["matricula_inmobiliaria"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "matricula_inmobiliaria", v
                    ),
                    width="100%",
                ),
            ),
            # Dirección
            form_field(
                "Dirección de la Propiedad",
                neuro_input(
                    rx.input.slot(rx.icon("map-pin", size=16, color="var(--gray-10)")),
                    placeholder="Ej: Calle 123 # 45-67",
                    value=PropiedadesState.form_data["direccion_propiedad"],
                    on_change=lambda v: PropiedadesState.set_form_field("direccion_propiedad", v),
                    width="100%",
                ),
            ),
            columns="2",
            spacing="6",
            width="100%", # Cambiado de 98% a 100%
        ),
        rx.grid(
            # Tipo
            form_field(
                "Tipo de Propiedad",
                neuro_select_root(
                    [
                        rx.select.item("Casa", value="Casa"),
                        rx.select.item("Apartamento", value="Apartamento"),
                        rx.select.item("Local Comercial", value="Local Comercial"),
                        rx.select.item("Bodega", value="Bodega"),
                        rx.select.item("Oficina", value="Oficina"),
                        rx.select.item("Lote", value="Lote"),
                    ],
                    value=PropiedadesState.form_data["tipo_propiedad"],
                    on_change=lambda v: PropiedadesState.set_form_field("tipo_propiedad", v),
                    placeholder="Tipo de Propiedad",
                    width="100%",
                ),
            ),
            # Municipio
            form_field(
                "Municipio",
                neuro_select_root(
                    rx.foreach(
                        PropiedadesState.municipios_options,
                        lambda item: rx.select.item(item["label"], value=item["value"].to(str))
                    ),
                    value=PropiedadesState.form_data["id_municipio"],
                    on_change=PropiedadesState.set_id_municipio,
                    placeholder="Seleccione Municipio",
                    width="100%",
                ),
            ),
            columns="2",
            spacing="6",
            width="100%", # Cambiado de 98% a 100%
        ),
        neuro_divider(),
        # Disponibilidad y Observaciones
        rx.vstack(
            form_field(
                "Estado Inicial",
                rx.box(
                    rx.segmented_control.root(
                        rx.segmented_control.item("Disponible", value="1"),
                        rx.segmented_control.item("Ocupada", value="0"),
                        value=PropiedadesState.form_data["disponibilidad"],
                        on_change=lambda v: PropiedadesState.set_form_field("disponibilidad", v),
                        radius="full",
                        color_scheme="indigo",
                        size="3",
                    ),
                    padding="4px",
                    border_radius="full",
                    background=styles.BG_PANEL,
                    box_shadow=styles.NEU_INSET,
                    display="inline-block",
                )
            ),
            form_field(
                "Observaciones",
                neuro_text_area(
                    placeholder="Detalles adicionales sobre la propiedad...",
                    value=PropiedadesState.form_data["observaciones"],
                    on_change=lambda v: PropiedadesState.set_form_field("observaciones", v),
                    size="3",
                    width="100%",
                ),
            ),
            spacing="5", # Aumentado de 4 a 5
            width="100%",
        ),
        spacing="7", # Elevado para Neumorfismo (escala 7 = 32px/40px aprox)
        padding="5",
        width="100%",
    )


def step_2_content() -> rx.Component:
    """Paso 2: Detalles Físicos y Servicios"""
    return rx.vstack(
        rx.grid(
            # Área
            form_field(
                "Área Total (m²)",
                neuro_input(
                    rx.input.slot(rx.icon("scan", size=16, color="var(--gray-10)")),
                    type="number",
                    placeholder="0",
                    value=PropiedadesState.form_data["area_metros"],
                    on_change=lambda v: PropiedadesState.set_form_field("area_metros", v),
                    width="100%",
                ),
            ),
            # Estrato
            form_field(
                "Estrato",
                neuro_select_root(
                    [
                        rx.select.item("1", value="1"),
                        rx.select.item("2", value="2"),
                        rx.select.item("3", value="3"),
                        rx.select.item("4", value="4"),
                        rx.select.item("5", value="5"),
                        rx.select.item("6", value="6"),
                        rx.select.item("Rural", value="Rural"),
                        rx.select.item("Comercial", value="Comercial"),
                    ],
                    value=PropiedadesState.form_data["estrato"],
                    on_change=lambda v: PropiedadesState.set_form_field("estrato", v),
                    placeholder="Estrato",
                    width="100%",
                ),
            ),
            columns="2",
            spacing="6", # Aumentado de 4 a 6
            width="100%",
        ),
        rx.grid(
            # Habitaciones
            form_field(
                "Habitaciones",
                neuro_input(
                    rx.input.slot(rx.icon("bed", size=16, color="var(--gray-10)")),
                    type="number",
                    value=PropiedadesState.form_data["habitaciones"],
                    on_change=lambda v: PropiedadesState.set_form_field("habitaciones", v),
                    width="100%",
                ),
            ),
            # Baños
            form_field(
                "Baños",
                neuro_input(
                    rx.input.slot(rx.icon("bath", size=16, color="var(--gray-10)")),
                    type="number",
                    value=PropiedadesState.form_data["bano"],
                    on_change=lambda v: PropiedadesState.set_form_field("bano", v),
                    width="100%",
                ),
            ),
            # Parqueadero
            form_field(
                "Parqueaderos",
                neuro_input(
                    rx.input.slot(rx.icon("car-front", size=16, color="var(--gray-10)")),
                    type="number",
                    value=PropiedadesState.form_data["parqueadero"],
                    on_change=lambda v: PropiedadesState.set_form_field("parqueadero", v),
                    width="100%",
                ),
            ),
            columns="3",
            spacing="6", # Aumentado de 4 a 6
            width="100%",
        ),
        neuro_divider(),
        rx.text(
            "Servicios Públicos (Códigos de Pago)", size="2", weight="bold", color=styles.TEXT_SECONDARY
        ),
        rx.grid(
            form_field(
                "Energía",
                neuro_input(
                    rx.input.slot(rx.icon("zap", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_energia"],
                    on_change=lambda v: PropiedadesState.set_form_field("codigo_energia", v),
                    width="100%",
                ),
            ),
            form_field(
                "Acueducto",
                neuro_input(
                    rx.input.slot(rx.icon("droplets", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_agua"],
                    on_change=lambda v: PropiedadesState.set_form_field("codigo_agua", v),
                    width="100%",
                ),
            ),
            form_field(
                "Gas",
                neuro_input(
                    rx.input.slot(rx.icon("flame", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_gas"],
                    on_change=lambda v: PropiedadesState.set_form_field("codigo_gas", v),
                    width="100%",
                ),
            ),
            columns="3",
            spacing="6", # Aumentado de 4 a 6
            width="100%",
        ),
        spacing="7",
        padding="5",
        width="100%",
    )


def step_3_content() -> rx.Component:
    """Paso 3: Financiero y Administración"""
    return rx.vstack(
        # Arrendamiento
        rx.box(
            rx.vstack(
                rx.text(
                    "Información de Arrendamiento", size="2", weight="bold", color="var(--green-9)"
                ),
                rx.grid(
                    form_field(
                        "Canon Estimado",
                        neuro_input(
                            rx.input.slot(
                                rx.icon("circle-dollar-sign", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_canon"],
                            on_change=lambda v: PropiedadesState.set_form_field("valor_canon", v),
                            width="100%",
                        ),
                    ),
                    form_field(
                        "Valor Administración",
                        neuro_input(
                            rx.input.slot(rx.icon("building", size=16, color="var(--gray-10)")),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_administracion"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "valor_administracion", v
                            ),
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="6", # Aumentado de 4 a 6
                    width="100%",
                ),
                padding="4",
                width="100%",
            ),
            style=styles.NEU_PANEL_STYLE,
            width="100%",
        ),
        # Venta (Opcional)
        rx.box(
            rx.vstack(
                rx.text("Opción de Venta", size="2", weight="bold", color="var(--blue-9)"),
                rx.grid(
                    form_field(
                        "Valor Venta",
                        neuro_input(
                            rx.input.slot(rx.icon("tag", size=16, color="var(--gray-10)")),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_venta_propiedad"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "valor_venta_propiedad", v
                            ),
                            width="100%",
                        ),
                    ),
                    form_field(
                        "Comisión Venta (%)",
                        neuro_input(
                            rx.input.slot(rx.icon("percent", size=16, color="var(--gray-10)")),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["comision_venta_propiedad"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "comision_venta_propiedad", v
                            ),
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="6", # Aumentado de 4 a 6
                    width="100%",
                ),
                padding="4",
                width="100%",
            ),
            style=styles.NEU_PANEL_STYLE,
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.text("Datos Administración PH", size="2", weight="bold"),
                rx.grid(
                    form_field(
                        "Teléfono Admin",
                        neuro_input(
                            rx.input.slot(rx.icon("phone", size=16, color="var(--gray-10)")),
                            value=PropiedadesState.form_data["telefono_administracion"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "telefono_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),
                    ),
                    form_field(
                        "Cuenta Bancaria",
                        neuro_input(
                            rx.input.slot(rx.icon("credit-card", size=16, color="var(--gray-10)")),
                            value=PropiedadesState.form_data["numero_cuenta_administracion"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "numero_cuenta_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="6", # Aumentado de 4 a 6
                    width="100%",
                ),
                padding="4",
                width="100%",
            ),
            style=styles.NEU_PANEL_STYLE,
            width="100%",
        ),
        spacing="6",
        padding="4",
        width="100%",
    )


from src.presentacion_reflex.components.document_manager_elite import document_manager_elite


def step_4_content() -> rx.Component:
    """Paso 4: Documentos y Multimedia"""
    return rx.vstack(
        rx.cond(
            PropiedadesState.is_editing,
            rx.vstack(
                rx.text(
                    "Gestionar Documentos y Multimedia",
                    size="3",
                    weight="bold",
                    color="var(--accent-9)",
                ),
                rx.text(
                    "Cargue escritura, libertad, fotos y video.", size="2", color="var(--gray-10)"
                ),
                document_manager_elite(
                    state_class=PropiedadesState,
                    max_files=15,  # Permitir más fotos
                    allow_multiple=True,
                ),
                spacing="5", # Aumentado de 4 a 5
                width="100%",
            ),
            # Mensaje para modo creación
            rx.center(
                rx.vstack(
                    rx.icon("save", size=48, color="var(--gray-8)"),
                    rx.text(
                        "Guarde la propiedad para habilitar carga",
                        weight="bold",
                        size="4",
                        color="var(--gray-11)",
                    ),
                    rx.text(
                        "Primero debe finalizar el registro básico. Luego podrá editar la propiedad para cargar fotos y documentos.",
                        text_align="center",
                        color="var(--gray-10)",
                    ),
                    spacing="4",
                    align="center",
                    max_width="400px",
                ),
                height="300px",
                width="100%",
                border="2px dashed var(--gray-6)",
                border_radius="16px",
                background="var(--gray-2)",
            ),
        ),
        width="100%",
        padding="4",
    )


def modal_propiedad() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header Modal
                rx.hstack(
                    rx.dialog.title(
                        rx.hstack(
                            rx.icon(
                                rx.cond(PropiedadesState.is_editing, "home", "home"),
                                size=24,
                                color="var(--purple-9)",
                            ),
                            rx.text(
                                rx.cond(
                                    PropiedadesState.is_editing,
                                    "Editar Propiedad",
                                    "Nueva Propiedad",
                                ),
                                size="6",
                                weight="bold",
                            ),
                            spacing="2",
                            align="center",
                        )
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(rx.icon("x", size=20), variant="ghost", size="2")
                    ),
                    width="100%",
                    align="center",
                ),
                # Wizard Progress
                wizard_progress(),
                # Content Container with Scroll
                rx.scroll_area(
                    rx.box(
                        rx.cond(PropiedadesState.modal_step == 1, step_1_content()),
                        rx.cond(PropiedadesState.modal_step == 2, step_2_content()),
                        rx.cond(PropiedadesState.modal_step == 3, step_3_content()),
                        rx.cond(PropiedadesState.modal_step == 4, step_4_content()),
                        padding_y="4", 
                        padding_x="6",
                    ),
                    type="always",
                    scrollbars="vertical",
                    style={"max_height": "550px", "height": "550px"}, # Aumentado para evitar clipping
                ),
                # Footer Actions
                rx.hstack(
                    # Left: Is Loading Indicator
                    rx.cond(
                        PropiedadesState.is_loading,
                        rx.spinner(size="2", color="green"),
                        rx.spacer(),
                    ),
                    # Right: Navigation Buttons
                    rx.hstack(
                        neuro_button(
                            "Cancelar",
                            on_click=PropiedadesState.close_modal,
                            color_scheme="gray",
                            variant="soft"
                        ),
                        rx.spacer(),
                        rx.cond(
                            PropiedadesState.modal_step > 1,
                            neuro_button(
                                "Anterior",
                                on_click=PropiedadesState.prev_modal_step,
                            ),
                        ),
                        rx.cond(
                            PropiedadesState.modal_step < PropiedadesState.total_steps,
                            neuro_button(
                                rx.hstack(rx.text("Siguiente"), rx.icon("chevron-right", size=16)),
                                on_click=PropiedadesState.next_modal_step,
                            ),
                            # Save Button always visible on last step
                            neuro_button(
                                rx.hstack(rx.text("Guardar Propiedad"), rx.icon("save", size=16)),
                                on_click=PropiedadesState.save_propiedad(
                                    PropiedadesState.form_data
                                ),
                                loading=PropiedadesState.is_loading,
                            ),
                        ),
                        spacing="5", 
                        align="center",
                        width="100%",
                    ),
                    width="100%",
                    justify="between",
                    padding_top="6", 
                    border_top=f"1px solid {styles.BORDER_DEFAULT}",
                ),
                spacing="5", # Aumentado de 4 a 5
                width="100%",
            ),
            size="3", # Asegurar tamaño radix adecuado
            style={
                "max_width": "820px", # Aumentado de 800 a 820 para margen extra
                "width": "95%",
                "border_radius": "20px", # Más suavizado elite
                "padding": "32px", # Más aire interno
                "background": styles.BG_PANEL,
            },
            on_escape_key_down=PropiedadesState.close_modal,
            on_pointer_down_outside=PropiedadesState.close_modal,
        ),
        open=PropiedadesState.show_modal,
        on_open_change=PropiedadesState.handle_open_change,
    )


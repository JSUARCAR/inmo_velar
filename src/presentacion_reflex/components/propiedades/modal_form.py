import reflex as rx

from src.presentacion_reflex.components.propiedades.wizard_progress import (
    progreso_asistente,
)
from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.shared.floating_label import floating_input, floating_select
from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_icon_action_button


def form_field(label: str, contenido: rx.Component, error: str = None) -> rx.Component:
    """Campo de formulario con etiqueta y estado de error."""
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        contenido,
        rx.cond(error, rx.text(error, color="var(--red-9)", size="1"), rx.fragment()),
        width="100%",
        spacing="4",
    )




def neuro_text_area(*args, **kwargs) -> rx.Component:
    """TextArea con estilo tokenizado."""
    custom_style = kwargs.pop("style", {})
    final_style = {**styles.NEU_INPUT_STYLE, **custom_style}
    kwargs.setdefault("min_height", "120px")
    kwargs.setdefault("size", "3")
    kwargs["variant"] = "soft"
    return rx.text_area(*args, style=final_style, **kwargs)


def neuro_divider(**kwargs) -> rx.Component:
    """Divisor visual."""
    custom_style = kwargs.pop("style", {})
    final_style = {
        "height": "1px",
        "width": "100%",
        "background": styles.BORDER_DEFAULT,
        **custom_style,
    }
    return rx.box(style=final_style, **kwargs)


def step_1_content() -> rx.Component:
    """Paso 1: Información Básica"""
    return rx.vstack(
        rx.grid(
            # Matrícula
            floating_input(
                "Matrícula Inmobiliaria",
                
                    rx.input.slot(
                        rx.icon("file-text", size=16, color="var(--gray-10)")
                    ),
                    placeholder="Ej: 001-123456",
                    value=PropiedadesState.form_data["matricula_inmobiliaria"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "matricula_inmobiliaria", v
                    ),
                    width="100%",
                ),

            # Dirección
            floating_input(
                "Dirección de la Propiedad",
                
                    rx.input.slot(rx.icon("map-pin", size=16, color="var(--gray-10)")),
                    placeholder="Ej: Calle 123 # 45-67",
                    value=PropiedadesState.form_data["direccion_propiedad"],
                    on_change=lambda v: PropiedadesState.set_upper_field(
                        "direccion_propiedad", v
                    ),
                    width="100%",
                ),

            columns="2",
            spacing="6",
            width="100%",  # Cambiado de 98% a 100%
        ),
        rx.grid(
            # Tipo
            floating_select(
                "Tipo de Propiedad",
                options=
                    [
                        rx.select.item("Casa", value="Casa"),
                        rx.select.item("Apartamento", value="Apartamento"),
                        rx.select.item("Local Comercial", value="Local Comercial"),
                        rx.select.item("Bodega", value="Bodega"),
                        rx.select.item("Oficina", value="Oficina"),
                        rx.select.item("Lote", value="Lote"),
                    ],
                    value=PropiedadesState.form_data["tipo_propiedad"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "tipo_propiedad", v
                    ),
                    placeholder="Tipo de Propiedad",
                    width="100%",
                ),

            # Municipio
            floating_select(
                "Municipio",
                options=
                    rx.foreach(
                        PropiedadesState.municipios_options,
                        lambda item: rx.select.item(
                            item["label"], value=item["value"].to(str)
                        ),
                    ),
                    value=PropiedadesState.form_data["id_municipio"],
                    on_change=PropiedadesState.set_id_municipio,
                    placeholder="Seleccione Municipio",
                    width="100%",
                ),

            columns="2",
            spacing="6",
            width="100%",  # Cambiado de 98% a 100%
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
                        on_change=lambda v: PropiedadesState.set_form_field(
                            "disponibilidad", v
                        ),
                        radius="full",
                        color_scheme="orange",
                        size="3",
                    ),
                    padding="4px",
                    border_radius="full",
                    background=styles.BG_PANEL,
                    box_shadow=styles.SHADOW_RING,
                    display="inline-block",
                ),
            ),
            floating_input(
                "Observaciones",
                
                    placeholder="Detalles adicionales sobre la propiedad...",
                    value=PropiedadesState.form_data["observaciones"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "observaciones", v
                    ),
                    size="3",
                    width="100%",
                ),

            spacing="5",  # Aumentado de 4 a 5
            width="100%",
        ),
        spacing="6",  # Aumentado de 5 a 6
        padding="4",
        width="100%",
    )


def step_2_content() -> rx.Component:
    """Paso 2: Detalles Físicos y Servicios"""
    return rx.vstack(
        rx.grid(
            # Área
            floating_input(
                "Área Total (m²)",
                
                    rx.input.slot(rx.icon("scan", size=16, color="var(--gray-10)")),
                    type="number",
                    placeholder="0",
                    value=PropiedadesState.form_data["area_metros"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "area_metros", v
                    ),
                    width="100%",
                ),

            # Estrato
            floating_select(
                "Estrato",
                options=
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

            columns="2",
            spacing="6",  # Aumentado de 4 a 6
            width="100%",
        ),
        rx.grid(
            # Habitaciones
            floating_input(
                "Habitaciones",
                
                    rx.input.slot(rx.icon("bed", size=16, color="var(--gray-10)")),
                    type="number",
                    value=PropiedadesState.form_data["habitaciones"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "habitaciones", v
                    ),
                    width="100%",
                ),

            # Baños
            floating_input(
                "Baños",
                
                    rx.input.slot(rx.icon("bath", size=16, color="var(--gray-10)")),
                    type="number",
                    value=PropiedadesState.form_data["bano"],
                    on_change=lambda v: PropiedadesState.set_form_field("bano", v),
                    width="100%",
                ),

            # Parqueadero
            floating_input(
                "Parqueaderos",
                
                    rx.input.slot(
                        rx.icon("car-front", size=16, color="var(--gray-10)")
                    ),
                    type="number",
                    value=PropiedadesState.form_data["parqueadero"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "parqueadero", v
                    ),
                    width="100%",
                ),

            columns="3",
            spacing="6",  # Aumentado de 4 a 6
            width="100%",
        ),
        neuro_divider(),
        rx.text(
            "Servicios Públicos (Códigos de Pago)",
            size="2",
            weight="bold",
            color=styles.TEXT_SECONDARY,
        ),
        rx.grid(
            floating_input(
                "Energía",
                
                    rx.input.slot(rx.icon("zap", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_energia"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "codigo_energia", v
                    ),
                    width="100%",
                ),

            floating_input(
                "Acueducto",
                
                    rx.input.slot(rx.icon("droplets", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_agua"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "codigo_agua", v
                    ),
                    width="100%",
                ),

            floating_input(
                "Gas",
                
                    rx.input.slot(rx.icon("flame", size=16, color="var(--gray-10)")),
                    value=PropiedadesState.form_data["codigo_gas"],
                    on_change=lambda v: PropiedadesState.set_form_field(
                        "codigo_gas", v
                    ),
                    width="100%",
                ),

            columns="3",
            spacing="6",  # Aumentado de 4 a 6
            width="100%",
        ),
        spacing="6",  # Aumentado de 4 a 6
        padding="4",
        width="100%",
    )


def step_3_content() -> rx.Component:
    """Paso 3: Financiero y Administración"""
    return rx.vstack(
        # Arrendamiento
        rx.box(
            rx.vstack(
                rx.text(
                    "Información de Arrendamiento",
                    size="2",
                    weight="bold",
                    color=styles.BRAND_PRIMARY,
                ),
                rx.grid(
                    floating_input(
                        "Canon Estimado",
                        
                            rx.input.slot(
                                rx.icon(
                                    "circle-dollar-sign",
                                    size=16,
                                    color="var(--gray-10)",
                                )
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_canon"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "valor_canon", v
                            ),
                            width="100%",
                        ),

                    floating_input(
                        "Valor Administración",
                        
                            rx.input.slot(
                                rx.icon("building", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_administracion"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "valor_administracion", v
                            ),
                            width="100%",
                        ),

                    columns="2",
                    spacing="6",  # Aumentado de 4 a 6
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
                rx.text(
                    "Información de Arrendamiento",
                    size="2",
                    weight="bold",
                    color=styles.BRAND_PRIMARY,
                ),
                rx.grid(
                    floating_input(
                        "Valor Venta",
                        
                            rx.input.slot(
                                rx.icon("tag", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["valor_venta_propiedad"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "valor_venta_propiedad", v
                            ),
                            width="100%",
                        ),

                    floating_input(
                        "Comisión Venta (%)",
                        
                            rx.input.slot(
                                rx.icon("percent", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data[
                                "comision_venta_propiedad"
                            ],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "comision_venta_propiedad", v
                            ),
                            width="100%",
                        ),

                    columns="2",
                    spacing="6",  # Aumentado de 4 a 6
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
                # === ROW 1: Contacto y Cuenta ===
                rx.grid(
                    floating_input(
                        "Teléfono Admin",
                        
                            rx.input.slot(
                                rx.icon("phone", size=16, color="var(--gray-10)")
                            ),
                            value=PropiedadesState.form_data["telefono_administracion"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "telefono_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),

                    floating_input(
                        "Cuenta Bancaria",
                        
                            rx.input.slot(
                                rx.icon("credit-card", size=16, color="var(--gray-10)")
                            ),
                            value=PropiedadesState.form_data[
                                "numero_cuenta_administracion"
                            ],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "numero_cuenta_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),

                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                # === ROW 2: Fecha y Link de Pago (NUEVO) ===
                rx.grid(
                    floating_input(
                        "Fecha Pago Admin",
                        
                            rx.input.slot(
                                rx.icon("calendar", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            min_="1",
                            max_="28",
                            placeholder="Día 1-28",
                            value=PropiedadesState.form_data[
                                "fecha_pago_administracion"
                            ],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "fecha_pago_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),

                    floating_input(
                        "Link de Pago",
                        
                            rx.input.slot(
                                rx.icon("link", size=16, color="var(--gray-10)")
                            ),
                            type="url",
                            placeholder="https://...",
                            value=PropiedadesState.form_data[
                                "link_pago_administracion"
                            ],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "link_pago_administracion", v
                            ),
                            size="3",
                            width="100%",
                        ),

                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                # === ROW 3: Cuota Extra (NUEVO - colspan 2) ===
                rx.grid(
                    floating_input(
                        "Cuota Extra Ordinaria",
                        
                            rx.input.slot(
                                rx.icon("wallet", size=16, color="var(--gray-10)")
                            ),
                            type="number",
                            placeholder="0",
                            value=PropiedadesState.form_data["cuota_extra_ordinaria"],
                            on_change=lambda v: PropiedadesState.set_form_field(
                                "cuota_extra_ordinaria", v
                            ),
                            width="100%",
                        ),

                    columns="1",
                    width="100%",
                ),
                # === ROW 4: Observaciones Admin PH (NUEVO) ===
                floating_input(
                    "Observaciones Administración PH",
                    
                        placeholder="Notas específicas sobre la administración: reglas del conjunto, horarios de instalaciones, comités activos, contactos importantes...",
                        value=PropiedadesState.form_data["observaciones_admin_ph"],
                        on_change=lambda v: PropiedadesState.set_form_field(
                            "observaciones_admin_ph", v
                        ),
                        width="100%",
                        style={"min_height": "100px"},
                    ),

                spacing="4",
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


from src.presentacion_reflex.components.document_manager_elite import (
    document_manager_elite,
)


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
                    "Cargue escritura, libertad, fotos y video.",
                    size="2",
                    color="var(--gray-10)",
                ),
                document_manager_elite(
                    state_class=PropiedadesState,
                    max_files=15,  # Permitir más fotos
                    allow_multiple=True,
                ),
                spacing="5",  # Aumentado de 4 a 5
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
                                color=styles.BRAND_PRIMARY,
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
                        neuro_icon_action_button("x", tooltip_content="Cerrar")
                    ),
                    width="100%",
                    align="center",
                ),
                # Wizard Progress
                progreso_asistente(),
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
                    style={
                        "max_height": "550px",
                        "height": "550px",
                    },  # Aumentado para evitar clipping
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
                            tooltip_content="Cerrar formulario",
                        ),
                        rx.cond(
                            PropiedadesState.modal_step > 1,
                            neuro_button(
                                "Anterior",
                                on_click=PropiedadesState.prev_modal_step,
                                tooltip_content="Ir al paso anterior",
                            ),
                        ),
                        rx.cond(
                            PropiedadesState.modal_step < PropiedadesState.total_steps,
                            neuro_button(
                                rx.hstack(
                                    rx.text("Siguiente"),
                                    rx.icon("chevron-right", size=16),
                                ),
                                on_click=PropiedadesState.next_modal_step,
                                tooltip_content="Ir al siguiente paso",
                            ),
                            # Save Button always visible on last step
                            neuro_button(
                                rx.hstack(
                                    rx.text("Guardar Propiedad"),
                                    rx.icon("save", size=16),
                                ),
                                on_click=PropiedadesState.save_propiedad(
                                    PropiedadesState.form_data
                                ),
                                loading=PropiedadesState.is_loading,
                                tooltip_content="Guardar los datos de la propiedad",
                            ),
                        ),
                        spacing="5",
                    ),
                    width="100%",
                    justify="between",
                    padding_top="5",  # Aumentado de 4 a 5
                    border_top=f"1px solid {styles.BORDER_DEFAULT}",
                ),
                spacing="5",  # Aumentado de 4 a 5
                width="100%",
            ),
            size="3",  # Asegurar tamaño radix adecuado
            style={
                "max_width": "820px",  # Aumentado de 800 a 820 para margen extra
                "width": "95%",
                "border_radius": "20px",  # Más suavizado elite
                "padding": "32px",  # Más aire interno
                "background": styles.BG_PANEL,
            },
            on_escape_key_down=PropiedadesState.close_modal,
            on_pointer_down_outside=PropiedadesState.close_modal,
        ),
        open=PropiedadesState.show_modal,
        on_open_change=PropiedadesState.handle_open_change,
    )

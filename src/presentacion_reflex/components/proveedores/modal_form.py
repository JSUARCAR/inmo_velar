import reflex as rx

from src.presentacion_reflex.state.proveedores_state import ProveedoresState


def modal_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(
                    rx.cond(
                        ProveedoresState.is_editing,
                        "Editar Proveedor",
                        "Nuevo Proveedor",
                    )
                ),
                rx.dialog.description("Complete la información del proveedor de servicios."),
                # Mensaje de error
                rx.cond(
                    ProveedoresState.error_message != "",
                    rx.callout(
                        ProveedoresState.error_message,
                        icon="triangle_alert",  # Changed from alert_triangle to avoid warning
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.vstack(
                    # Persona (Solo editable al crear)
                    rx.text("Persona *", weight="bold", size="2"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Seleccione una persona...", width="100%"),
                        rx.select.content(
                            rx.select.group(
                                rx.foreach(
                                    ProveedoresState.personas_disponibles,
                                    lambda p: rx.select.item(p["label"], value=p["value"]),
                                )
                            )
                        ),
                        value=ProveedoresState.form_data["id_persona"],
                        on_change=lambda val: ProveedoresState.set_form_field("id_persona", val),
                        disabled=ProveedoresState.is_editing,
                    ),
                    # Especialidad
                    rx.text("Especialidad *", weight="bold", size="2"),
                    rx.select(
                        [
                            "Plomería",
                            "Electricidad",
                            "Gas",
                            "Pintura",
                            "Obra Civil",
                            "Aseo",
                            "Otros",
                        ],
                        value=ProveedoresState.form_data["especialidad"],
                        on_change=lambda val: ProveedoresState.set_form_field("especialidad", val),
                        width="100%",
                    ),
                    # Calificación
                    rx.text("Calificación Inicial (1.0 - 5.0)", weight="bold", size="2"),
                    rx.hstack(
                        rx.slider(
                            value=[ProveedoresState.form_data["calificacion"]],
                            on_change=lambda val: ProveedoresState.set_form_field(
                                "calificacion", val[0]
                            ),
                            min=1.0,
                            max=5.0,
                            step=0.5,
                            width="200px",
                        ),
                        rx.text(ProveedoresState.form_data["calificacion"], weight="bold"),
                        align="center",
                        spacing="3",
                    ),
                    # Observaciones
                    rx.text("Observaciones", weight="bold", size="2"),
                    rx.text_area(
                        placeholder="Notas adicionales sobre el proveedor...",
                        value=ProveedoresState.form_data["observaciones"],
                        on_change=lambda val: ProveedoresState.set_form_field("observaciones", val),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ProveedoresState.close_modal,
                    ),
                    rx.button(
                        "Guardar",
                        on_click=ProveedoresState.save_proveedor,
                        loading=ProveedoresState.is_loading,
                    ),
                    spacing="3",
                    margin_top="4",
                    justify="end",
                ),
            ),
            max_width="500px",
        ),
        open=ProveedoresState.show_form_modal,
        on_open_change=ProveedoresState.handle_open_change,
    )

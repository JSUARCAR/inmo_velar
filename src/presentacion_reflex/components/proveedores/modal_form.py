import reflex as rx

from src.presentacion_reflex.state.proveedores_state import ProveedoresState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_select_root,
)
from src.presentacion_reflex import styles


def modal_proveedor() -> rx.Component:
    """Formulario modal para crear o editar proveedores."""
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
                rx.dialog.description(
                    "Complete la información del proveedor de servicios."
                ),
                # Mensaje de error
                rx.cond(
                    ProveedoresState.error_message != "",
                    rx.callout(
                        ProveedoresState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.vstack(
                    # Persona (Solo editable al crear)
                    rx.vstack(
                        rx.text("Persona *", weight="bold", size="2"),
                        neuro_select_root(
                            rx.foreach(
                                ProveedoresState.personas_disponibles,
                                lambda p: rx.select.item(p["label"], value=p["value"]),
                            ),
                            placeholder="Seleccione una persona...",
                            width="100%",
                            value=ProveedoresState.form_data["id_persona"],
                            on_change=lambda val: ProveedoresState.set_form_field(
                                "id_persona", val
                            ),
                            disabled=ProveedoresState.is_editing,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    # Especialidad
                    rx.vstack(
                        rx.text("Especialidad *", weight="bold", size="2"),
                        neuro_select_root(
                            [
                                rx.select.item("Plomería", value="Plomería"),
                                rx.select.item("Electricidad", value="Electricidad"),
                                rx.select.item("Gas", value="Gas"),
                                rx.select.item("Pintura", value="Pintura"),
                                rx.select.item("Obra Civil", value="Obra Civil"),
                                rx.select.item("Aseo", value="Aseo"),
                                rx.select.item("Otros", value="Otros"),
                            ],
                            value=ProveedoresState.form_data["especialidad"],
                            on_change=lambda val: ProveedoresState.set_form_field(
                                "especialidad", val
                            ),
                            width="100%",
                            placeholder="Seleccione especialidad...",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    # Calificación
                    rx.vstack(
                        rx.text(
                            "Calificación Inicial (1.0 - 5.0)", weight="bold", size="2"
                        ),
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
                            rx.text(
                                ProveedoresState.form_data["calificacion"],
                                weight="bold",
                            ),
                            align="center",
                            spacing="3",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    # Observaciones
                    rx.vstack(
                        rx.text("Observaciones", weight="bold", size="2"),
                        rx.text_area(
                            placeholder="Notas adicionales sobre el proveedor...",
                            value=ProveedoresState.form_data["observaciones"],
                            on_change=lambda val: ProveedoresState.set_form_field(
                                "observaciones", val
                            ),
                            width="100%",
                            style=styles.NEU_INPUT_STYLE,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            color_scheme="gray",
                            variant="soft",
                            on_click=ProveedoresState.close_modal,
                        )
                    ),
                    rx.button(
                        "Guardar",
                        on_click=ProveedoresState.save_proveedor,
                        loading=ProveedoresState.is_loading,
                        color_scheme="blue",
                    ),
                    spacing="3",
                    margin_top="4",
                    justify="end",
                    width="100%",
                ),
            ),
            max_width="500px",
        ),
        open=ProveedoresState.show_form_modal,
        on_open_change=ProveedoresState.handle_open_change,
    )

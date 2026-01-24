import reflex as rx
from typing import List, Callable, Dict, Any, Type

def document_manager_elite(
    state_class: Type[rx.State],
    max_files: int = 10,
    allow_multiple: bool = True
) -> rx.Component:
    """
    Componente elite para gestión documental que se conecta automáticamente
    con un Estado que herede de DocumentosStateMixin.
    
    Args:
        state_class: Clase del estado (ej: RecaudosState)
        max_files: Máximo de archivos permitidos
        allow_multiple: Si permite múltiples archivos
    """
    
    return rx.vstack(
        # Header / Instrucciones
        rx.hstack(
            rx.icon("cloud-upload", size=24, color="var(--accent-9)"),
            rx.vstack(
                rx.text(
                    "Cargar Documentos", 
                    weight="bold", 
                    size="3",
                    color="var(--gray-12)"
                ),
                rx.text(
                    "Formatos soportados: PDF, JPG, PNG",
                    size="1",
                    color="var(--gray-10)"
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            width="100%",
            padding_bottom="3",
            border_bottom="1px solid var(--gray-4)",
        ),
        
        # Upload Zone
        rx.upload(
            rx.center(
                rx.vstack(
                    rx.icon("files", size=48, color="var(--gray-8)"),
                    rx.text(
                        "Arrastra tus archivos aquí o haz clic para seleccionar",
                        weight="medium",
                        size="2",
                        color="var(--gray-11)",
                    ),
                    rx.text(
                        f"Máximo {max_files} archivos simultáneos",
                        size="1",
                        color="var(--gray-9)",
                    ),
                    rx.button(
                        "Seleccionar Archivos",
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        margin_top="2",
                    ),
                    spacing="3",
                    align="center",
                    justify="center",
                    height="100%",
                    width="100%",
                ),
                height="200px",
                width="100%",
                border="2px dashed var(--gray-6)",
                border_radius="12px",
                background="var(--gray-2)",
                _hover={
                    "border_color": "var(--accent-9)",
                    "background": "var(--accent-2)",
                },
                transition="all 0.2s ease",
            ),
            multiple=allow_multiple,
            max_files=max_files,
            # Aceptamos tipos comunes por defecto
            accept={
                "image/jpeg": [".jpg", ".jpeg"],
                "image/png": [".png"],
                "application/pdf": [".pdf"]
            },
            border="0px",
            padding="0px",
            id=f"upload_manager_{state_class.__name__}", # ID único por State Class
        ),
        
        # Action Bar (Upload Button & File List Status)
        rx.hstack(
            rx.text(
                rx.cond(
                    state_class.is_uploading,
                    "Subiendo archivos...",
                    "Archivos listos para subir"
                ),
                size="1", 
                color="var(--gray-10)"
            ),
            rx.spacer(),
            rx.button(
                "Subir Documentos",
                on_click=state_class.handle_upload(
                   rx.upload_files(
                       upload_id=f"upload_manager_{state_class.__name__}",
                   )
                ),
                loading=state_class.is_uploading,
                variant="solid",
                color_scheme="blue",
            ),
            width="100%",
            padding_top="3",
            align="center",
        ),
        
        # Lista de documentos ya cargados
        rx.cond(
            state_class.documentos,
            rx.vstack(
                 rx.text("Documentos Cargados", weight="bold", size="2", margin_top="4"),
                 rx.foreach(
                     state_class.documentos,
                     lambda doc: rx.hstack(
                         rx.icon("file-text", size=16),
                         rx.text(doc["nombre_archivo"], size="2", flex="1"),
                         rx.icon_button(
                             rx.icon("arrow-down-to-line", size=18),
                             on_click=lambda: state_class.descargar_documento(doc["id_documento"]),
                             variant="soft", 
                             color_scheme="blue",
                             size="2",
                             cursor="pointer"
                         ),
                         rx.icon_button(
                             rx.icon("trash-2", size=16),
                             on_click=lambda: state_class.eliminar_documento(doc["id_documento"]),
                             variant="ghost",
                             color_scheme="red",
                             size="1"
                         ),
                         width="100%",
                         padding="2",
                         border="1px solid var(--gray-4)",
                         border_radius="8px",
                         align="center",
                         spacing="2"
                     )
                 ),
                 width="100%",
                 spacing="2"
            )
        ),
        
        width="100%",
        padding="4",
        border="1px solid var(--gray-4)",
        border_radius="16px",
        background="var(--color-panel-solid)",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    )

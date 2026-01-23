import reflex as rx
from typing import List, Callable, Any

def document_manager(
    upload_id: str,
    on_upload_handler: Callable,
    accepted_formats: str = ".pdf,.jpg,.png,.jpeg",
    max_files: int = 5,
    label: str = "Arrastra archivos aquí o haz clic para seleccionar"
) -> rx.Component:
    """
    Componente reutilizable para gestión de documentos.
    
    Args:
        upload_id: ID único para el componente de upload.
        on_upload_handler: Event handler del estado para procesar la subida.
                           Debe aceptar la lista de archivos: `State.handle_upload(rx.upload_files(upload_id))`
        accepted_formats: String con extensiones permitidas.
        max_files: Número máximo de archivos (visual hint).
        label: Texto a mostrar en la zona de drop.
    """
    
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.icon("upload_cloud", size=40, color="var(--accent-9)"),
                rx.text(
                    label,
                    color="var(--gray-11)",
                    font_size="0.9em",
                    text_align="center"
                ),
                rx.text(
                    f"Formatos: {accepted_formats}",
                    color="var(--gray-9)",
                    font_size="0.8em"
                ),
                align_items="center",
                justify_content="center",
                padding="2em",
                border="2px dashed var(--gray-6)",
                border_radius="8px",
                width="100%",
                background_color="var(--gray-2)",
                _hover={"background_color": "var(--gray-3)", "border_color": "var(--accent-9)"}
            ),
            id=upload_id,
            accept={format: [] for format in accepted_formats.split(",")},
            multiple=True,
            max_files=max_files,
            border="1px solid var(--gray-6)",
            border_radius="8px",
            padding="4px"
        ),
        rx.hstack(
            rx.button(
                "Subir Archivos",
                on_click=on_upload_handler,
                variant="solid", 
                color_scheme="blue",
            ),
            justify_content="end",
            width="100%",
            padding_top="1em"
        ),
        width="100%"
    )

def file_list_item(filename: str, on_delete: Optional[Callable] = None) -> rx.Component:
    """Renderiza un item de archivo en una lista."""
    return rx.hstack(
        rx.icon("file_text", size=16),
        rx.text(filename, font_size="0.9em", flex="1"),
        rx.icon_button(
            rx.icon("trash_2", size=16),
            on_click=on_delete,
            variant="ghost",
            color_scheme="red",
            size="2"
        ) if on_delete else rx.box(),
        padding="0.5em",
        border="1px solid var(--gray-4)",
        border_radius="6px",
        width="100%",
        align_items="center"
    )

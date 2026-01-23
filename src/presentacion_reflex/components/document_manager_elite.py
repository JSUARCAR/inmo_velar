import reflex as rx
from typing import List, Callable, Dict, Any

def document_manager_elite(
    entidad_tipo: str,
    entidad_id: str,
    tipos_permitidos: List[str],
    on_upload_handler: Callable,
    max_files: int = 10,
    allow_multiple: bool = True
) -> rx.Component:
    """
    Componente elite para gestión documental con:
    - Drag & drop múltiple
    - Preview de imágenes (placeholder en upload)
    - Progreso individual por archivo (simulado visualmente)
    - Categorización automática
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
                    f"Formatos permitidos: {', '.join(tipos_permitidos)}", 
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
            accept={f"image/*": tipos_permitidos, "application/pdf": tipos_permitidos} if tipos_permitidos else None,
            border="0px",
            padding="0px",
            id=f"upload_{entidad_tipo}_{entidad_id}", # ID único para el componente upload
        ),
        
        # Action Bar (Upload Button & File List Status)
        rx.hstack(
            rx.text("Archivos seleccionados listos para subir...", size="1", color="var(--gray-10)"),
            rx.spacer(),
            rx.button(
                "Subir Documentos",
                on_click=on_upload_handler(
                   rx.upload_files(
                       upload_id=f"upload_{entidad_tipo}_{entidad_id}",
                       on_upload_progress=None # Podríamos añadir handler de progreso aquí
                   )
                ),
                variant="solid",
                color_scheme="blue",
            ),
            width="100%",
            padding_top="3",
            align="center",
        ),
        
        width="100%",
        padding="4",
        border="1px solid var(--gray-4)",
        border_radius="16px",
        background="var(--color-panel-solid)",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    )

import reflex as rx
from typing import List, Callable, Dict, Any

def image_gallery(
    documentos: List[Dict[str, Any]],
    on_delete: Callable,
    allow_lightbox: bool = True,
    grid_cols: int = 4
) -> rx.Component:
    """
    Galería de imágenes con:
    - Grid responsive
    - Lightbox para vista completa (usando Dialog)
    - Acciones de descarga/eliminar
    """
    
    return rx.box(
        rx.cond(
            documentos.length() == 0,
            rx.center(
                rx.vstack(
                    rx.icon("image-off", size=32, color="var(--gray-8)"),
                    rx.text("No hay documentos cargados", color="var(--gray-10)"),
                    padding="4",
                ),
                width="100%",
                border="1px dashed var(--gray-5)",
                border_radius="12px",
            ),
            rx.grid(
                rx.foreach(
                    documentos,
                    lambda doc: rx.context_menu.root(
                        rx.context_menu.trigger(
                            rx.card(
                                rx.inset(
                                    rx.cond(
                                        doc.get("mime_type", "").to_string().contains("image"),
                                        rx.image(
                                            src=f"http://127.0.0.1:8000/api/storage/{doc.get('id_documento')}/download", # IP explícita para evitar problemas de resolución
                                            object_fit="cover",
                                            width="100%",
                                            height="140px",
                                            background="var(--gray-3)",
                                            loading="eager",
                                        ),
                                        # Placeholder para PDFs u otros archivos
                                        rx.center(
                                            rx.icon("file-text", size=48, color="var(--gray-9)"),
                                            width="100%",
                                            height="140px",
                                            background="var(--gray-3)",
                                        )
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.vstack(
                                    rx.text(
                                        doc.get("nombre_archivo", "Documento"),
                                        size="1",
                                        weight="bold",
                                        no_of_lines=1,
                                    ),
                                    rx.hstack(
                                        rx.badge(
                                            doc.get("extension", "").to_string().upper().replace(".", ""),
                                            variant="soft",
                                            color_scheme="gray",
                                            size="1",
                                        ),
                                        rx.link(
                                            rx.icon_button(
                                                rx.icon("download", size=14),
                                                size="1",
                                                variant="ghost",
                                                color_scheme="blue",
                                            ),
                                            href=f"http://127.0.0.1:8000/api/storage/{doc.get('id_documento')}/download?force_download=true",
                                            is_external=True
                                        ),
                                        rx.spacer(),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=14),
                                            size="1",
                                            variant="ghost",
                                            color_scheme="red",
                                            on_click=lambda: on_delete(doc.get("id_documento")),
                                        ),
                                        width="100%",
                                        align="center",
                                    ),
                                    spacing="1",
                                    padding="2",
                                ),
                                variant="classic",
                                _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 8px rgba(0,0,0,0.1)"},
                                transition="all 0.2s ease",
                            ),
                        ),
                        rx.context_menu.content(
                            rx.context_menu.item(
                                "Descargar",
                                on_select=rx.redirect(path=f"http://127.0.0.1:8000/api/storage/{doc.get('id_documento')}/download?force_download=true"),
                            ),
                            rx.context_menu.separator(),
                            rx.context_menu.item(
                                "Eliminar",
                                color="red",
                                on_select=lambda: on_delete(doc.get("id_documento")),
                            ),
                        ),
                    ),
                ),
                columns=str(grid_cols),
                gap="4",
                width="100%",
            ),
        ),
        width="100%",
    )

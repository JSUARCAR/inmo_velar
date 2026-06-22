from typing import Any, Callable, Dict, List

import reflex as rx


import rxconfig

def _get_api_base() -> str:
    # Use dynamic api_url from rxconfig or fallback
    base = rxconfig.api_url if hasattr(rxconfig, "api_url") and rxconfig.api_url else "http://127.0.0.1:8000"
    # Ensure it doesn't end with slash
    return base.rstrip("/")

def _get_image_src(doc: rx.Var) -> rx.Var:
    return rx.Var.create(f"{_get_api_base()}/api/storage/") + doc.id_documento.to(str) + "/download"

def _get_image_href(doc: rx.Var) -> rx.Var:
    return rx.Var.create(f"{_get_api_base()}/api/storage/") + doc.id_documento.to(str) + "/download?force_download=true"

def image_gallery(
    documentos: List[Any],
    on_delete: Callable,
    allow_lightbox: bool = True,
    grid_cols: int = 4,
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
                                        doc.mime_type.to_string().contains("image"),
                                        rx.image(
                                            src=_get_image_src(doc),
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
                                        ),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.vstack(
                                    rx.text(
                                        doc.nombre_archivo,
                                        size="1",
                                        weight="bold",
                                        no_of_lines=1,
                                    ),
                                    rx.hstack(
                                        rx.badge(
                                            doc.extension
                                            .to_string()
                                            .upper()
                                            .replace(".", ""),
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
                                            href=_get_image_href(doc),
                                            is_external=True,
                                        ),
                                        rx.spacer(),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=14),
                                            size="1",
                                            variant="ghost",
                                            color_scheme="red",
                                            on_click=lambda: on_delete(doc.id_documento),
                                        ),
                                        width="100%",
                                        align="center",
                                    ),
                                    spacing="1",
                                    padding="2",
                                ),
                                variant="classic",
                                _hover={
                                    "transform": "translateY(-2px)",
                                    "box_shadow": "0 4px 8px rgba(0,0,0,0.1)",
                                },
                                transition="all 0.2s ease",
                            ),
                        ),
                        rx.context_menu.content(
                            rx.context_menu.item(
                                "Descargar",
                                on_select=rx.redirect(
                                    path=_get_image_href(doc)
                                ),
                            ),
                            rx.context_menu.separator(),
                            rx.context_menu.item(
                                "Eliminar",
                                color="red",
                                on_select=lambda: on_delete(doc.id_documento),
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

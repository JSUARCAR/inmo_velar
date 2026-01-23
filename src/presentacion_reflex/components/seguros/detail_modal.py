"""
Modal de Detalle de Seguro con Pólizas Asociadas
"""

import reflex as rx
from src.presentacion_reflex.state.seguros_state import SegurosState


def modal_detalle_seguro() -> rx.Component:
    """Modal de detalle de seguro mostrando información y pólizas."""
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("shield", size=24, color="blue"),
                    rx.text("Detalle del Seguro", weight="bold"),
                    align="center",
                    spacing="2",
                )
            ),
            
            rx.vstack(
                # Información del Seguro
                rx.card(
                    rx.vstack(
                        rx.heading("Información General", size="5", margin_bottom="3"),
                        
                        rx.grid(
                            # Nombre
                            rx.vstack(
                                rx.text("Nombre", size="2", color="gray", weight="bold"),
                                rx.text(
                                    SegurosState.selected_seguro["nombre_seguro"],
                                    size="3"
                                ),
                                spacing="1",
                            ),
                            
                            # Porcentaje
                            rx.vstack(
                                rx.text("Porcentaje", size="2", color="gray", weight="bold"),
                                rx.text(
                                    f"{SegurosState.selected_seguro['porcentaje_seguro']}%",
                                    size="3",
                                    weight="bold",
                                    color="blue"
                                ),
                                spacing="1",
                            ),
                            
                            # Estado
                            rx.vstack(
                                rx.text("Estado", size="2", color="gray", weight="bold"),
                                rx.badge(
                                    SegurosState.selected_seguro["estado_seguro"],
                                    color_scheme=rx.cond(
                                        SegurosState.selected_seguro["estado_seguro"] == "Activo",
                                        "green",
                                        "red"
                                    ),
                                ),
                                spacing="1",
                            ),
                            
                            # Fecha Inicio
                            rx.vstack(
                                rx.text("Fecha Inicio", size="2", color="gray", weight="bold"),
                                rx.text(
                                    SegurosState.selected_seguro["fecha_inicio_seguro"],
                                    size="3"
                                ),
                                spacing="1",
                            ),
                            
                            # Fecha Ingreso
                            rx.vstack(
                                rx.text("Fecha Ingreso", size="2", color="gray", weight="bold"),
                                rx.text(
                                    SegurosState.selected_seguro["fecha_ingreso_seguro"],
                                    size="3"
                                ),
                                spacing="1",
                            ),
                            
                            # Motivo Inactivación (si aplica)
                            rx.cond(
                                SegurosState.selected_seguro["motivo_inactivacion"] != "N/A",
                                rx.vstack(
                                    rx.text("Motivo Inactivación", size="2", color="gray", weight="bold"),
                                    rx.text(
                                        SegurosState.selected_seguro["motivo_inactivacion"],
                                        size="3",
                                        color="red"
                                    ),
                                    spacing="1",
                                ),
                            ),
                            
                            columns="2",
                            spacing="4",
                            width="100%",
                        ),
                        
                        spacing="3",
                        width="100%",
                    ),
                    variant="surface",
                ),
                
                # Pólizas Asociadas
                rx.card(
                    rx.vstack(
                        rx.heading("Pólizas Asociadas", size="5", margin_bottom="3"),
                        
                        rx.cond(
                            SegurosState.seguro_polizas.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    SegurosState.seguro_polizas,
                                    lambda poliza: rx.card(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.badge(poliza["numero_poliza"], color_scheme="blue"),
                                                rx.badge(
                                                    poliza["estado"],
                                                    color_scheme=rx.cond(
                                                        poliza["estado"] == "Activa",
                                                        "green",
                                                        "gray"
                                                    ),
                                                ),
                                                justify="between",
                                                width="100%",
                                            ),
                                            rx.text(
                                                f"Contrato ID: {poliza['id_contrato']}",
                                                size="2",
                                                color="gray"
                                            ),
                                            rx.hstack(
                                                rx.text(
                                                    f"Inicio: {poliza['fecha_inicio']}",
                                                    size="2"
                                                ),
                                                rx.text(
                                                    f"Fin: {poliza['fecha_fin']}",
                                                    size="2"
                                                ),
                                                spacing="4",
                                            ),
                                            spacing="2",
                                        ),
                                        variant="classic",
                                        width="100%",
                                    )
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            # Sin pólizas
                            rx.callout(
                                "No hay pólizas asociadas a este seguro",
                                icon="info",
                                color_scheme="gray",
                                width="100%",
                            )
                        ),
                        
                        spacing="3",
                        width="100%",
                    ),
                    variant="surface",
                ),
                
                # Botón Cerrar
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cerrar",
                            variant="soft",
                            size="3",
                            on_click=SegurosState.close_detail_modal,
                        ),
                    ),
                    justify="end",
                    width="100%",
                ),
                
                spacing="4",
                width="100%",
            ),
            
            max_width="700px",
            width="100%",
        ),
        open=SegurosState.show_detail_modal,
    )

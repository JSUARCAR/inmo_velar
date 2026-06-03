"""
Componentes de carga (Skeletons) para el Dashboard.
Permiten mostrar una interfaz progresiva mientras los datos cargan asincrónicamente.
"""

import reflex as rx

def kpi_skeleton() -> rx.Component:
    """Skeleton para tarjetas de KPI pequeñas."""
    return rx.skeleton(
        rx.box(
            width="100%",
            height="120px",
            border_radius="lg",
            bg="gray.100",
        )
    )

def chart_skeleton(height: str = "300px") -> rx.Component:
    """Skeleton para contenedores de gráficos."""
    return rx.skeleton(
        rx.box(
            width="100%",
            height=height,
            border_radius="xl",
            bg="gray.100",
        )
    )

def table_skeleton(rows: int = 5) -> rx.Component:
    """Skeleton para tablas o listas."""
    return rx.skeleton(
        rx.vstack(
            *[rx.box(width="100%", height="40px", bg="gray.100", border_radius="md") for _ in range(rows)],
            spacing="3",
            width="100%",
        )
    )

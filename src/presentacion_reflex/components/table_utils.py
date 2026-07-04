import reflex as rx


def header_cell_sortable(
    label: str,
    column_id: str,
    current_sort_by: rx.Var,
    current_sort_order: rx.Var,
    on_click_handler: callable,
) -> rx.Component:
    """
    Renderiza una celda de encabezado de tabla con capacidades de ordenamiento reactivo.

    Args:
        label: El texto a mostrar en el encabezado.
        column_id: Identificador único de la columna para el backend.
        current_sort_by: Var que contiene la columna actualmente ordenada.
        current_sort_order: Var que contiene el orden actual ('asc' o 'desc').
        on_click_handler: Función que recibe el column_id al hacer clic.
    """
    is_active = current_sort_by == column_id

    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, weight="bold"),
            rx.cond(
                is_active,
                rx.cond(
                    current_sort_order == "desc",
                    rx.icon("chevron-down", size=16),
                    rx.icon("chevron-up", size=16),
                ),
                rx.icon("chevrons-up-down", size=14, opacity=0.3),
            ),
            spacing="2",
            align="center",
            cursor="pointer",
            on_click=lambda: on_click_handler(column_id),
            _hover={"opacity": 0.8},
        ),
        style={"font-weight": "600"},
    )

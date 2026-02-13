"""
Componente: Property Card
Tarjeta visual para mostrar resumen de una propiedad.
"""

from typing import Callable

import reflex as rx

from src.dominio.entidades.propiedad import Propiedad
from src.presentacion.theme import colors


def PropertyCard(
    propiedad: Propiedad,
    on_edit: Callable[[int], None],
    on_toggle_disponibilidad: Callable[[int, int], None],
) -> ft.Container:
    """
    Crea una tarjeta visual para mostrar información de una propiedad.

    Args:
        propiedad: Entidad Propiedad con todos los datos
        on_edit: Callback al hacer clic en editar (recibe id_propiedad)
        on_toggle_disponibilidad: Callback al cambiar disponibilidad (id, nuevo_valor)

    Returns:
        Container con la tarjeta de propiedad
    """

    # Helper para formatear moneda
    def formato_moneda(valor):
        if valor is None:
            return "N/A"
        return f"${valor:,.0f}".replace(",", ".")

    # Badge de disponibilidad
    disponible = propiedad.disponibilidad_propiedad == 1
    badge_disponibilidad = ft.Container(
        content=ft.Text(
            "Disponible" if disponible else "Ocupada",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        bgcolor=colors.SUCCESS if disponible else colors.TEXT_DISABLED,
        border_radius=4,
    )

    # Badge de tipo
    ft.Container(
        content=ft.Text(propiedad.tipo_propiedad, size=12, color=colors.TEXT_SECONDARY),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=4,
    )

    # Handler para toggle de disponibilidad
    def handle_toggle(e):
        nueva_disponibilidad = 0 if propiedad.disponibilidad_propiedad == 1 else 1
        on_toggle_disponibilidad(propiedad.id_propiedad, nueva_disponibilidad)

    # Encabezado
    header = ft.Row(
        [
            ft.Icon(ft.Icons.HOME, size=20, color=colors.PRIMARY),
            ft.Text(
                propiedad.tipo_propiedad,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=colors.TEXT_PRIMARY,
                expand=True,
            ),
            badge_disponibilidad,
            ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_size=18,
                icon_color=colors.PRIMARY,
                tooltip="Editar",
                on_click=lambda e: on_edit(propiedad.id_propiedad),
            ),
        ],
        spacing=8,
    )

    # Matrícula
    matricula_row = ft.Row(
        [ft.Text(f"Mat: {propiedad.matricula_inmobiliaria}", size=12, color=colors.TEXT_SECONDARY)]
    )

    # Ubicación
    ubicacion_row = ft.Row(
        [
            ft.Icon(ft.Icons.LOCATION_ON, size=14, color=colors.TEXT_SECONDARY),
            ft.Text(
                propiedad.direccion_propiedad,
                size=13,
                color=colors.TEXT_SECONDARY,
                expand=True,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ],
        spacing=4,
    )

    # Características
    caracteristicas = []
    if propiedad.habitaciones:
        caracteristicas.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.BED, size=14, color=colors.TEXT_SECONDARY),
                    ft.Text(f"{propiedad.habitaciones} hab", size=12, color=colors.TEXT_SECONDARY),
                ],
                spacing=2,
            )
        )
    if propiedad.bano:
        caracteristicas.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.BATHTUB, size=14, color=colors.TEXT_SECONDARY),
                    ft.Text(f"{propiedad.bano} baños", size=12, color=colors.TEXT_SECONDARY),
                ],
                spacing=2,
            )
        )
    if propiedad.parqueadero:
        caracteristicas.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=14, color=colors.TEXT_SECONDARY),
                    ft.Text(f"{propiedad.parqueadero} parq", size=12, color=colors.TEXT_SECONDARY),
                ],
                spacing=2,
            )
        )

    caracteristicas_row = ft.Row(caracteristicas, spacing=10, wrap=True)

    # Área y estrato
    info_row = ft.Row(
        [
            ft.Icon(ft.Icons.SQUARE_FOOT, size=14, color=colors.TEXT_SECONDARY),
            ft.Text(f"{propiedad.area_m2:.0f} m²", size=12, color=colors.TEXT_SECONDARY),
            ft.Text("|", size=12, color=colors.TEXT_DISABLED),
            ft.Icon(ft.Icons.LABEL, size=14, color=colors.TEXT_SECONDARY),
            ft.Text(
                f"Estrato {propiedad.estrato}" if propiedad.estrato else "Sin estrato",
                size=12,
                color=colors.TEXT_SECONDARY,
            ),
        ],
        spacing=6,
    )

    # Información financiera
    precios = []
    if propiedad.canon_arrendamiento_estimado:
        precios.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=colors.SUCCESS),
                    ft.Text(
                        f"Canon: {formato_moneda(propiedad.canon_arrendamiento_estimado)}",
                        size=12,
                        color=colors.TEXT_PRIMARY,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=4,
            )
        )
    if propiedad.valor_venta_propiedad:
        precios.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.SELL, size=14, color=colors.PRIMARY),
                    ft.Text(
                        f"Venta: {formato_moneda(propiedad.valor_venta_propiedad)}",
                        size=12,
                        color=colors.TEXT_PRIMARY,
                    ),
                ],
                spacing=4,
            )
        )

    precios_column = ft.Column(precios, spacing=4) if precios else ft.Container()

    # Card completa
    card = ft.Container(
        content=ft.Column(
            [
                header,
                matricula_row,
                ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                ubicacion_row,
                caracteristicas_row,
                info_row,
                ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                precios_column,
            ],
            spacing=8,
            tight=True,
        ),
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=8,
        bgcolor=colors.BACKGROUND,
        width=320,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    return card

"""
Vista: Formulario de Seguro
Permite crear y editar seguros de arrendamiento.
"""

import datetime
from typing import Callable, Optional

import flet as ft

from src.aplicacion.servicios.servicio_seguros import ServicioSeguros
from src.infraestructura.persistencia.database import DatabaseManager
from src.presentacion.theme import colors, styles


def crear_seguro_form_view(
    page: ft.Page, on_guardar: Callable, on_cancelar: Callable, seguro_id: Optional[int] = None
) -> ft.Container:
    """
    Crea la vista de formulario para crear/editar seguro.

    Args:
        page: Página de Flet
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
        seguro_id: ID del seguro para editar (None = crear nuevo)

    Returns:
        Container con el formulario completo
    """

    # Servicios
    db_manager = DatabaseManager()
    servicio = ServicioSeguros(db_manager)

    # Estado: Modo edición o creación
    es_edicion = seguro_id is not None
    titulo = f"{'Editar' if es_edicion else 'Nuevo'} Seguro"

    # Cargar datos si es edición
    seguro_actual = None
    if es_edicion:
        seguro_actual = servicio.obtener_seguro(seguro_id)
        if not seguro_actual:
            page.open(
                ft.SnackBar(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR),
                            ft.Text("Seguro no encontrado", color=colors.TEXT_ON_ERROR),
                        ]
                    ),
                    bgcolor=colors.ERROR,
                )
            )
            on_cancelar()
            return ft.Container()

    # --- Campos del Formulario ---

    txt_nombre = ft.TextField(
        label="Nombre del Seguro *",
        hint_text="Ej: Seguro de Arrendamiento Básico",
        value=seguro_actual.nombre_seguro if seguro_actual else "",
        expand=True,
    )

    txt_porcentaje = ft.TextField(
        label="Porcentaje *",
        hint_text="Ej: 200 (equivale a 2%)",
        value=str(seguro_actual.porcentaje_seguro) if seguro_actual else "200",
        suffix_text="(base 10000)",
        width=250,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    txt_porcentaje_preview = ft.Text(
        "Equivale a: 2.0%", size=14, color=colors.TEXT_SECONDARY, italic=True
    )

    def actualizar_preview(e):
        """Actualiza la vista previa del porcentaje."""
        try:
            valor = int(txt_porcentaje.value) if txt_porcentaje.value else 0
            decimal = valor / 100.0
            txt_porcentaje_preview.value = f"Equivale a: {decimal}%"
            txt_porcentaje_preview.color = colors.SUCCESS
        except ValueError:
            txt_porcentaje_preview.value = "Valor inválido"
            txt_porcentaje_preview.color = colors.ERROR
        page.update()

    txt_porcentaje.on_change = actualizar_preview

    # DatePicker para fecha de inicio
    def abrir_picker_fecha(e):
        page.open(date_picker_inicio)

    def on_fecha_change(e):
        if date_picker_inicio.value:
            txt_fecha_inicio.value = date_picker_inicio.value.strftime("%Y-%m-%d")
            txt_fecha_inicio.update()

    date_picker_inicio = ft.DatePicker(
        on_change=on_fecha_change,
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime(2035, 12, 31),
        value=(
            datetime.datetime.strptime(seguro_actual.fecha_inicio_seguro, "%Y-%m-%d")
            if seguro_actual and seguro_actual.fecha_inicio_seguro
            else datetime.datetime.now()
        ),
    )

    # Agregar DatePicker al overlay
    page.overlay.append(date_picker_inicio)

    txt_fecha_inicio = ft.TextField(
        label="Fecha de Inicio",
        width=180,
        read_only=True,
        value=(
            seguro_actual.fecha_inicio_seguro
            if seguro_actual and seguro_actual.fecha_inicio_seguro
            else datetime.datetime.now().date().isoformat()
        ),
    )

    btn_fecha_inicio = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH, on_click=abrir_picker_fecha, tooltip="Seleccionar fecha"
    )

    # --- Validaciones ---

    def validar_formulario() -> tuple[bool, str]:
        """Valida los datos del formulario. Retorna (es_valido, mensaje_error)"""

        if not txt_nombre.value or not txt_nombre.value.strip():
            return False, "El nombre del seguro es obligatorio"

        if not txt_porcentaje.value or not txt_porcentaje.value.strip():
            return False, "El porcentaje es obligatorio"

        try:
            porcentaje = int(txt_porcentaje.value)
            if porcentaje <= 0:
                return False, "El porcentaje debe ser mayor a 0"
            if porcentaje > 10000:
                return False, "El porcentaje no puede ser mayor a 10000 (100%)"
        except ValueError:
            return False, "El porcentaje debe ser un número entero"

        return True, ""

    # --- Handlers ---

    def handle_guardar_click(e):
        """Maneja el guardado del formulario."""

        # Validar
        es_valido, mensaje_error = validar_formulario()
        if not es_valido:
            page.open(
                ft.SnackBar(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR),
                            ft.Text(mensaje_error, color=colors.TEXT_ON_ERROR),
                        ]
                    ),
                    bgcolor=colors.ERROR,
                )
            )
            return

        # Recopilar datos
        datos = {
            "nombre_seguro": txt_nombre.value.strip(),
            "porcentaje_seguro": int(txt_porcentaje.value),
            "fecha_inicio_seguro": txt_fecha_inicio.value if txt_fecha_inicio.value else None,
        }

        try:
            if es_edicion:
                # Actualizar seguro
                servicio.actualizar_seguro(seguro_id, datos, usuario_sistema="admin")
                mensaje = "Seguro actualizado exitosamente"
            else:
                # Crear seguro nuevo
                servicio.crear_seguro(datos, usuario_sistema="admin")
                mensaje = "Seguro creado exitosamente"

            # Notificar éxito
            page.open(
                ft.SnackBar(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=colors.TEXT_ON_PRIMARY),
                            ft.Text(mensaje, color=colors.TEXT_ON_PRIMARY),
                        ]
                    ),
                    bgcolor=colors.SUCCESS,
                )
            )

            # Navegar de regreso
            on_guardar()

        except ValueError as err:
            page.open(
                ft.SnackBar(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR),
                            ft.Text(str(err), color=colors.TEXT_ON_ERROR),
                        ]
                    ),
                    bgcolor=colors.ERROR,
                )
            )

        except Exception as err:
            import traceback

            traceback.print_exc()
            page.open(
                ft.SnackBar(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR),
                            ft.Text(f"Error inesperado: {err}", color=colors.TEXT_ON_ERROR),
                        ]
                    ),
                    bgcolor=colors.ERROR,
                )
            )

    def handle_cancelar_click(e):
        on_cancelar()

    # --- Layout del Formulario ---

    formulario = ft.Container(
        content=ft.Column(
            [
                # Título
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Inicio > Seguros > {'Editar' if es_edicion else 'Nuevo'}",
                                style=styles.breadcrumb_text(),
                            ),
                            ft.Text(
                                titulo,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=colors.TEXT_PRIMARY,
                            ),
                        ]
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 1: Información Básica
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "INFORMACIÓN BÁSICA",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            txt_nombre,
                            ft.Row(
                                [txt_porcentaje, txt_fecha_inicio, btn_fecha_inicio], spacing=20
                            ),
                            txt_porcentaje_preview,
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 2: Información Adicional
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "INFORMACIÓN ADICIONAL",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Porcentaje en base 10000:",
                                            weight=ft.FontWeight.BOLD,
                                            size=13,
                                        ),
                                        ft.Text(
                                            "• 100 = 1.0%", size=12, color=colors.TEXT_SECONDARY
                                        ),
                                        ft.Text(
                                            "• 200 = 2.0%", size=12, color=colors.TEXT_SECONDARY
                                        ),
                                        ft.Text(
                                            "• 300 = 3.0%", size=12, color=colors.TEXT_SECONDARY
                                        ),
                                        ft.Text(
                                            "• 400 = 4.0%", size=12, color=colors.TEXT_SECONDARY
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                bgcolor=colors.SURFACE_VARIANT,
                                padding=15,
                                border_radius=8,
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=30),
                ),
                # Botones de Acción
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Cancelar",
                            icon=ft.Icons.CANCEL,
                            on_click=handle_cancelar_click,
                            style=ft.ButtonStyle(
                                bgcolor=colors.SECONDARY, color=colors.TEXT_ON_PRIMARY
                            ),
                        ),
                        ft.ElevatedButton(
                            "Guardar",
                            icon=ft.Icons.SAVE,
                            on_click=handle_guardar_click,
                            style=ft.ButtonStyle(
                                bgcolor=colors.PRIMARY, color=colors.TEXT_ON_PRIMARY
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=15,
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=30,
        bgcolor=colors.BACKGROUND,
        expand=True,
    )

    return formulario

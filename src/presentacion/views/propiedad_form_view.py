"""
Vista: Formulario de Propiedad
Permite crear y editar propiedades del inventario.
"""

import datetime
from typing import Callable, Optional

import flet as ft

from src.aplicacion.servicios import ServicioPropiedades
from src.infraestructura.persistencia.database import DatabaseManager
from src.presentacion.theme import colors, styles


def crear_propiedad_form_view(
    page: ft.Page, on_guardar: Callable, on_cancelar: Callable, propiedad_id: Optional[int] = None
) -> ft.Container:
    """
    Crea la vista de formulario para crear/editar propiedad.

    Args:
        page: Página de Flet
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
        propiedad_id: ID de la propiedad (None para crear nueva)

    Returns:
        Container con el formulario completo
    """

    # Servicios
    db_manager = DatabaseManager()
    servicio = ServicioPropiedades(db_manager)

    # Estado: Modo edición o creación
    es_edicion = propiedad_id is not None
    titulo = f"{'Editar' if es_edicion else 'Nueva'} Propiedad"

    # Cargar datos si es edición
    propiedad_actual = None
    if es_edicion:
        propiedad_actual = servicio.obtener_propiedad(propiedad_id)
        if not propiedad_actual:
            page.snack_bar = ft.SnackBar(ft.Text("Propiedad no encontrada"), bgcolor=colors.ERROR)
            page.snack_bar.open = True
            on_cancelar()
            return ft.Container()

    # Obtener catálogos
    municipios = servicio.obtener_municipios_disponibles()
    tipos_propiedad = servicio.obtener_tipos_propiedad()

    # --- SECCIÓN 1: Identificación ---

    txt_matricula = ft.TextField(
        label="Matrícula Inmobiliaria *",
        hint_text="Ej: 001-12345-0001",
        value=propiedad_actual.matricula_inmobiliaria if propiedad_actual else "",
        width=250,
        prefix_icon=ft.Icons.BADGE,
    )

    txt_fecha_ingreso = ft.TextField(
        label="Fecha de Ingreso *",
        value=(
            propiedad_actual.fecha_ingreso_propiedad
            if propiedad_actual
            else datetime.datetime.now().date().isoformat()
        ),
        width=200,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
        hint_text="YYYY-MM-DD",
    )

    # --- SECCIÓN 2: Ubicación ---

    dropdown_municipio = ft.Dropdown(
        label="Municipio *",
        options=[ft.dropdown.Option(str(mun["id"]), mun["nombre"]) for mun in municipios],
        value=str(propiedad_actual.id_municipio) if propiedad_actual else None,
        width=250,
    )

    txt_direccion = ft.TextField(
        label="Dirección *",
        hint_text="Ej: Calle 123 # 45-67",
        value=propiedad_actual.direccion_propiedad if propiedad_actual else "",
        expand=True,
        multiline=True,
        min_lines=2,
        max_lines=3,
    )

    # --- SECCIÓN 3: Características ---

    dropdown_tipo = ft.Dropdown(
        label="Tipo de Propiedad *",
        options=[ft.dropdown.Option(tipo) for tipo in tipos_propiedad],
        value=propiedad_actual.tipo_propiedad if propiedad_actual else None,
        width=200,
    )

    txt_area = ft.TextField(
        label="Área (m²) *",
        hint_text="0.00",
        value=str(propiedad_actual.area_m2) if propiedad_actual else "",
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.SQUARE_FOOT,
    )

    txt_habitaciones = ft.TextField(
        label="Habitaciones",
        hint_text="0",
        value=(
            str(propiedad_actual.habitaciones)
            if propiedad_actual and propiedad_actual.habitaciones
            else ""
        ),
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.BED,
    )

    txt_banos = ft.TextField(
        label="Baños",
        hint_text="0",
        value=str(propiedad_actual.bano) if propiedad_actual and propiedad_actual.bano else "",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.BATHTUB,
    )

    txt_parqueaderos = ft.TextField(
        label="Parqueaderos",
        hint_text="0",
        value=(
            str(propiedad_actual.parqueadero)
            if propiedad_actual and propiedad_actual.parqueadero
            else ""
        ),
        width=140,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.DIRECTIONS_CAR,
    )

    dropdown_estrato = ft.Dropdown(
        label="Estrato",
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3"),
            ft.dropdown.Option("4"),
            ft.dropdown.Option("5"),
            ft.dropdown.Option("6"),
        ],
        value=(
            str(propiedad_actual.estrato) if propiedad_actual and propiedad_actual.estrato else None
        ),
        width=120,
    )

    # --- SECCIÓN 4: Información Financiera ---

    txt_admin = ft.TextField(
        label="Valor Administración",
        hint_text="0",
        value=(
            str(propiedad_actual.valor_administracion)
            if propiedad_actual and propiedad_actual.valor_administracion
            else ""
        ),
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.ACCOUNT_BALANCE,
    )

    txt_canon = ft.TextField(
        label="Canon Arrendamiento Estimado",
        hint_text="0",
        value=(
            str(propiedad_actual.canon_arrendamiento_estimado)
            if propiedad_actual and propiedad_actual.canon_arrendamiento_estimado
            else ""
        ),
        width=250,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.ATTACH_MONEY,
    )

    txt_valor_venta = ft.TextField(
        label="Valor de Venta",
        hint_text="0",
        value=(
            str(propiedad_actual.valor_venta_propiedad)
            if propiedad_actual and propiedad_actual.valor_venta_propiedad
            else ""
        ),
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.SELL,
    )

    txt_comision_venta = ft.TextField(
        label="Comisión Venta",
        hint_text="0",
        value=(
            str(propiedad_actual.comision_venta_propiedad)
            if propiedad_actual and propiedad_actual.comision_venta_propiedad
            else ""
        ),
        width=180,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.PERCENT,
    )

    # Nuevos campos de administración
    txt_telefono_admin = ft.TextField(
        label="Teléfono Administración",
        hint_text="Ej: 3001234567",
        tooltip="Teléfono de contacto de la administración del edificio/conjunto",
        value=(
            propiedad_actual.telefono_administracion
            if propiedad_actual and propiedad_actual.telefono_administracion
            else ""
        ),
        width=200,
        keyboard_type=ft.KeyboardType.PHONE,
        prefix_icon=ft.Icons.PHONE,
    )

    dropdown_tipo_cuenta = ft.Dropdown(
        label="Tipo Cuenta Bancaria",
        options=[
            ft.dropdown.Option("Ahorros", "Ahorros"),
            ft.dropdown.Option("Corriente", "Corriente"),
        ],
        value=(
            propiedad_actual.tipo_cuenta_administracion
            if propiedad_actual and propiedad_actual.tipo_cuenta_administracion
            else None
        ),
        width=200,
    )

    txt_numero_cuenta = ft.TextField(
        label="Número Cuenta Administración",
        hint_text="Número de cuenta bancaria...",
        tooltip="Número de cuenta bancaria para pagos de administración",
        value=(
            propiedad_actual.numero_cuenta_administracion
            if propiedad_actual and propiedad_actual.numero_cuenta_administracion
            else ""
        ),
        width=250,
        prefix_icon=ft.Icons.ACCOUNT_BALANCE,
    )

    # --- SECCIÓN 5: Código CIU ---

    txt_codigo_energia = ft.TextField(
        label="Código Energía",
        hint_text="Código del servicio de energía...",
        tooltip="Código NIC o NIU que aparece en la factura de energía",
        value=(
            propiedad_actual.codigo_energia
            if propiedad_actual and propiedad_actual.codigo_energia
            else ""
        ),
        width=250,
        prefix_icon=ft.Icons.POWER,
    )

    txt_codigo_agua = ft.TextField(
        label="Código Agua",
        hint_text="Código del servicio de agua...",
        tooltip="Referencia de pago que aparece en la factura de agua",
        value=(
            propiedad_actual.codigo_agua
            if propiedad_actual and propiedad_actual.codigo_agua
            else ""
        ),
        width=250,
        prefix_icon=ft.Icons.WATER_DROP,
    )

    txt_codigo_gas = ft.TextField(
        label="Código Gas",
        hint_text="Código del servicio de gas...",
        tooltip="Referencia de pago o código de suscripción del servicio de gas",
        value=(
            propiedad_actual.codigo_gas if propiedad_actual and propiedad_actual.codigo_gas else ""
        ),
        width=250,
        prefix_icon=ft.Icons.LOCAL_FIRE_DEPARTMENT,
    )

    # --- SECCIÓN 6: Observaciones ---

    txt_observaciones = ft.TextField(
        label="Observaciones",
        hint_text="Notas adicionales sobre la propiedad...",
        value=(
            propiedad_actual.observaciones_propiedad
            if propiedad_actual and propiedad_actual.observaciones_propiedad
            else ""
        ),
        multiline=True,
        min_lines=3,
        max_lines=5,
        expand=True,
    )

    # --- Validaciones y Handlers ---

    def validar_formulario() -> tuple[bool, str]:
        """Valida los datos del formulario."""

        if not txt_matricula.value or not txt_matricula.value.strip():
            return False, "La matrícula inmobiliaria es obligatoria"

        if not txt_fecha_ingreso.value:
            return False, "La fecha de ingreso es obligatoria"

        if not dropdown_municipio.value:
            return False, "Debe seleccionar un municipio"

        if not txt_direccion.value or not txt_direccion.value.strip():
            return False, "La dirección es obligatoria"

        if not dropdown_tipo.value:
            return False, "Debe seleccionar un tipo de propiedad"

        if not txt_area.value or not txt_area.value.strip():
            return False, "El área es obligatoria"

        try:
            area = float(txt_area.value)
            if area <= 0:
                return False, "El área debe ser mayor a 0"
        except ValueError:
            return False, "El área debe ser un número válido"

        return True, ""

    def handle_guardar_click(e):
        """Maneja el guardado del formulario."""

        # Validar
        es_valido, mensaje_error = validar_formulario()
        if not es_valido:
            page.snack_bar = ft.SnackBar(ft.Text(mensaje_error), bgcolor=colors.ERROR)
            page.snack_bar.open = True
            page.update()
            return

        # Recopilar datos
        datos = {
            "matricula_inmobiliaria": txt_matricula.value.strip(),
            "id_municipio": int(dropdown_municipio.value),
            "direccion_propiedad": txt_direccion.value.strip(),
            "tipo_propiedad": dropdown_tipo.value,
            "area_m2": float(txt_area.value),
            "fecha_ingreso_propiedad": txt_fecha_ingreso.value,
        }

        # Campos opcionales numéricos
        if txt_habitaciones.value and txt_habitaciones.value.strip():
            datos["habitaciones"] = int(txt_habitaciones.value)

        if txt_banos.value and txt_banos.value.strip():
            datos["bano"] = int(txt_banos.value)

        if txt_parqueaderos.value and txt_parqueaderos.value.strip():
            datos["parqueadero"] = int(txt_parqueaderos.value)

        if dropdown_estrato.value:
            datos["estrato"] = int(dropdown_estrato.value)

        if txt_admin.value and txt_admin.value.strip():
            datos["valor_administracion"] = int(txt_admin.value)

        if txt_canon.value and txt_canon.value.strip():
            datos["canon_arrendamiento_estimado"] = int(txt_canon.value)

        if txt_valor_venta.value and txt_valor_venta.value.strip():
            datos["valor_venta_propiedad"] = int(txt_valor_venta.value)

        if txt_comision_venta.value and txt_comision_venta.value.strip():
            datos["comision_venta_propiedad"] = int(txt_comision_venta.value)

        if txt_observaciones.value and txt_observaciones.value.strip():
            datos["observaciones_propiedad"] = txt_observaciones.value.strip()

        # Códigos CIU (opcionales)
        if txt_codigo_energia.value and txt_codigo_energia.value.strip():
            datos["codigo_energia"] = txt_codigo_energia.value.strip()

        if txt_codigo_agua.value and txt_codigo_agua.value.strip():
            datos["codigo_agua"] = txt_codigo_agua.value.strip()

        if txt_codigo_gas.value and txt_codigo_gas.value.strip():
            datos["codigo_gas"] = txt_codigo_gas.value.strip()

        # 🔍 DEBUG: Verificar códigos CIU recopilados
        pass  # print(f"🔍 [UI] Códigos CIU recopilados en formulario:") [OpSec Removed]
        pass  # print(f"   - Energía: {datos.get('codigo_energia', 'NO CAPTURADO')}") [OpSec Removed]
        pass  # print(f"   - Agua: {datos.get('codigo_agua', 'NO CAPTURADO')}") [OpSec Removed]
        pass  # print(f"   - Gas: {datos.get('codigo_gas', 'NO CAPTURADO')}") [OpSec Removed]

        # Campos de administración (opcionales)
        if txt_telefono_admin.value and txt_telefono_admin.value.strip():
            datos["telefono_administracion"] = txt_telefono_admin.value.strip()

        if dropdown_tipo_cuenta.value:
            datos["tipo_cuenta_administracion"] = dropdown_tipo_cuenta.value

        if txt_numero_cuenta.value and txt_numero_cuenta.value.strip():
            datos["numero_cuenta_administracion"] = txt_numero_cuenta.value.strip()
        try:
            if es_edicion:
                # Actualizar propiedad
                servicio.actualizar_propiedad(propiedad_id, datos, usuario_sistema="admin")
                mensaje = "Propiedad actualizada exitosamente"
            else:
                # Crear propiedad nueva
                servicio.crear_propiedad(datos, usuario_sistema="admin")
                mensaje = "Propiedad creada exitosamente"

            # Notificar éxito
            page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=colors.SUCCESS)
            page.snack_bar.open = True
            page.update()

            # Callback
            on_guardar()

        except ValueError as err:
            page.snack_bar = ft.SnackBar(ft.Text(str(err)), bgcolor=colors.ERROR)
            page.snack_bar.open = True
            page.update()

        except Exception as err:
            import traceback

            traceback.print_exc()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error inesperado: {err}"), bgcolor=colors.ERROR)
            page.snack_bar.open = True
            page.update()

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
                                f"Inicio > Propiedades > {'Editar' if es_edicion else 'Nueva'}",
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
                # SECCIÓN 1: Identificación
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "IDENTIFICACIÓN",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row([txt_matricula, txt_fecha_ingreso], spacing=20),
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 2: Ubicación
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "UBICACIÓN",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            dropdown_municipio,
                            txt_direccion,
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 3: Características
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "CARACTERÍSTICAS",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row([dropdown_tipo, txt_area], spacing=20),
                            ft.Row(
                                [txt_habitaciones, txt_banos, txt_parqueaderos, dropdown_estrato],
                                spacing=20,
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 4: Información Financiera
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "INFORMACIÓN FINANCIERA",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row([txt_admin, txt_canon], spacing=20),
                            ft.Row([txt_valor_venta, txt_comision_venta], spacing=20),
                            ft.Row(
                                [txt_telefono_admin, dropdown_tipo_cuenta, txt_numero_cuenta],
                                spacing=20,
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 5: Código CIU
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "CÓDIGO CIU",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row(
                                [txt_codigo_energia, txt_codigo_agua, txt_codigo_gas], spacing=20
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # SECCIÓN 6: Observaciones
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "OBSERVACIONES",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY,
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            txt_observaciones,
                        ],
                        spacing=15,
                    ),
                    padding=ft.padding.only(bottom=20),
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

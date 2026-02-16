"""
Vista: Formulario de Liquidación
Formulario para generar liquidaciones mensuales del propietario.
"""

from datetime import datetime
from typing import Callable

import reflex as rx


def crear_liquidacion_form_view(
    page: ft.Page,
    servicio_financiero,
    servicio_contratos,
    on_guardar: Callable,
    on_cancelar: Callable,
    liquidacion_id: int = None,
) -> ft.Container:
    """
    Crea el formulario de liquidación.

    Args:
        page: Página de Flet
        servicio_financiero: Servicio para operaciones financieras
        servicio_contratos: Servicio para obtener contratos
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
        liquidacion_id: ID de liquidación para edición (opcional)
    """

    es_edicion = liquidacion_id is not None

    # Variables para almacenar información de la liquidación cargada
    liquidacion_propietario_info = None

    # --- CARGAR DATOS PARA EDICIÓN ---
    if es_edicion:
        try:
            # 1. Obtener la liquidación base para conocer propietario y periodo
            liquidacion_base = servicio_financiero.repo_liquidacion.obtener_por_id(liquidacion_id)

            if not liquidacion_base:
                raise ValueError(f"No se encontró la liquidación con ID {liquidacion_id}")

            # 2. Obtener el contrato de mandato para saber el propietario
            contrato = servicio_contratos.obtener_mandato_por_id(liquidacion_base.id_contrato_m)

            if not contrato:
                raise ValueError(
                    f"No se encontró el contrato de mandato ID {liquidacion_base.id_contrato_m}"
                )

            id_propietario = contrato.id_propietario

            # 3. Obtener TODAS las liquidaciones del mismo propietario para el mismo período
            liquidaciones = servicio_financiero.repo_liquidacion.listar_por_propietario_y_periodo(
                id_propietario, liquidacion_base.periodo
            )

            if not liquidaciones:
                raise ValueError(
                    f"No se encontraron liquidaciones para propietario {id_propietario} en periodo {liquidacion_base.periodo}"
                )

            # 4. CALCULAR LAS SUMAS de todos los campos
            # Los valores iniciales de todos los campos en 0
            suma_canon_bruto = 0
            suma_otros_ingresos = 0
            suma_gastos_admin = 0
            suma_gastos_servicios = 0
            suma_gastos_reparaciones = 0
            suma_otros_egresos = 0
            comision_porcentaje = 0  # Tomamos el del primer contrato (debería ser el mismo)
            observaciones_list = []

            # Sumar todos los valores de todas las liquidaciones
            for idx, liq in enumerate(liquidaciones):
                suma_canon_bruto += liq.canon_bruto
                suma_otros_ingresos += liq.otros_ingresos or 0
                suma_gastos_admin += liq.gastos_administracion or 0
                suma_gastos_servicios += liq.gastos_servicios or 0
                suma_gastos_reparaciones += liq.gastos_reparaciones or 0
                suma_otros_egresos += liq.otros_egresos or 0

                # Tomar el porcentaje de comisión del primer contrato
                if idx == 0:
                    comision_porcentaje = liq.comision_porcentaje

                # Recopilar observaciones no vacías
                if liq.observaciones and liq.observaciones.strip():
                    observaciones_list.append(liq.observaciones.strip())

            # 5. Preparar los datos para poblar el formulario
            observaciones_consolidadas = (
                " | ".join(observaciones_list) if observaciones_list else ""
            )

            # 6. Obtener el nombre del propietario desde la base de datos
            nombre_propietario = "Desconocido"
            try:
                placeholder = servicio_contratos.db.get_placeholder()
                query_propietario = f"""
                SELECT per.NOMBRE_COMPLETO 
                FROM PROPIETARIOS prop 
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA 
                WHERE prop.ID_PROPIETARIO = {placeholder}
                """
                with servicio_contratos.db.obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query_propietario, (id_propietario,))
                    result = cursor.fetchone()
                    if result:
                        nombre_propietario = result[0]
            except Exception:
                pass  # print(f"⚠️ Error obteniendo nombre propietario: {e}") [OpSec Removed]

            # Almacenar la info para usarla después
            liquidacion_propietario_info = {
                "id_propietario": id_propietario,
                "periodo": liquidacion_base.periodo,
                "suma_canon_bruto": suma_canon_bruto,
                "suma_otros_ingresos": suma_otros_ingresos,
                "suma_gastos_admin": suma_gastos_admin,
                "suma_gastos_servicios": suma_gastos_servicios,
                "suma_gastos_reparaciones": suma_gastos_reparaciones,
                "suma_otros_egresos": suma_otros_egresos,
                "comision_porcentaje": comision_porcentaje,
                "observaciones": observaciones_consolidadas,
                "nombre_propietario": nombre_propietario,
                "cantidad_contratos": len(liquidaciones),
            }

            pass  # print(f"✅ Datos de edición cargados: {len(liquidaciones)} liquidación(es) para propietario {id_propietario}, periodo {liquidacion_base.periodo}") [OpSec Removed]
            pass  # print(f"   Canon total sumado: ${suma_canon_bruto:,}") [OpSec Removed]

        except Exception:
            pass  # print(f"❌ Error cargando datos para edición: {ex}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            # No lanzar excepción aquí, simplemente mostrar el formulario vacío
            # El usuario verá un formulario en blanco y podrá cancelar

    # Referencias a controles
    dd_contrato = ft.Ref[ft.Dropdown]()
    txt_periodo = ft.Ref[ft.TextField]()
    txt_canon_bruto = ft.Ref[ft.TextField]()
    txt_otros_ingresos = ft.Ref[ft.TextField]()
    txt_total_ingresos = ft.Ref[ft.TextField]()
    txt_comision_porcentaje = ft.Ref[ft.TextField]()
    txt_comision_monto = ft.Ref[ft.TextField]()
    txt_iva_comision = ft.Ref[ft.TextField]()
    txt_impuesto_4x1000 = ft.Ref[ft.TextField]()
    txt_gastos_admin = ft.Ref[ft.TextField]()
    txt_gastos_servicios = ft.Ref[ft.TextField]()
    txt_gastos_reparaciones = ft.Ref[ft.TextField]()
    txt_otros_egresos = ft.Ref[ft.TextField]()
    txt_total_egresos = ft.Ref[ft.TextField]()
    txt_neto_a_pagar = ft.Ref[ft.TextField]()
    txt_observaciones = ft.Ref[ft.TextField]()

    def calcular_totales(e=None):
        """Calcula automáticamente los totales y el neto a pagar"""
        try:
            # Ingresos
            canon = int(txt_canon_bruto.current.value or 0)
            otros_ing = int(txt_otros_ingresos.current.value or 0)
            total_ing = canon + otros_ing
            txt_total_ingresos.current.value = str(total_ing)

            # Egresos
            comision_pct = int(txt_comision_porcentaje.current.value or 0)
            comision_monto = int((canon * comision_pct) / 10000)
            txt_comision_monto.current.value = str(comision_monto)

            iva = int(comision_monto * 0.19)
            txt_iva_comision.current.value = str(iva)

            impuesto = int(total_ing * 0.004)
            txt_impuesto_4x1000.current.value = str(impuesto)

            gastos_admin = int(txt_gastos_admin.current.value or 0)
            gastos_serv = int(txt_gastos_servicios.current.value or 0)
            gastos_rep = int(txt_gastos_reparaciones.current.value or 0)
            otros_egr = int(txt_otros_egresos.current.value or 0)

            total_egr = (
                comision_monto
                + iva
                + impuesto
                + gastos_admin
                + gastos_serv
                + gastos_rep
                + otros_egr
            )
            txt_total_egresos.current.value = str(total_egr)

            # Neto
            neto = total_ing - total_egr
            txt_neto_a_pagar.current.value = str(neto)

            page.update()

        except Exception:
            pass  # print(f"Error calculando totales: {ex}") [OpSec Removed]

    def cargar_canon_contrato(e):
        """Carga el canon del contrato seleccionado"""
        if not dd_contrato.current.value:
            return

        try:
            # Obtener el contrato de mandato y cargar su canon
            contrato = servicio_contratos.obtener_mandato_por_id(int(dd_contrato.current.value))
            if contrato:
                txt_canon_bruto.current.value = str(contrato.canon_mandato)
                txt_comision_porcentaje.current.value = str(contrato.comision_porcentaje_contrato_m)
            else:
                pass  # print(f"Error: No se encontró contrato ID {dd_contrato.current.value}") [OpSec Removed]

            calcular_totales()
        except Exception:
            pass  # print(f"Error cargando canon: {ex}") [OpSec Removed]

    def show_banner(mensaje: str, is_error: bool = True):
        """Muestra un banner con mensaje de error o éxito"""
        pass  # print(f"DEBUG: show_banner llamado - mensaje: '{mensaje}', is_error: {is_error}") [OpSec Removed]

        # CORRECCIÓN: Usar page.open() en lugar de page.snack_bar =
        snackbar = ft.SnackBar(
            content=ft.Text(mensaje, color="white"),
            bgcolor="#f44336" if is_error else "#4caf50",
            duration=4000,
        )

        pass  # print(f"DEBUG: Llamando page.open(SnackBar)...") [OpSec Removed]
        page.open(snackbar)
        pass  # print(f"DEBUG: SnackBar mostrado con page.open()") [OpSec Removed]

    def handle_guardar(e):
        """Maneja el guardado de la liquidación"""
        pass  # print("\n=== DEBUG: handle_guardar INICIADO ===") [OpSec Removed]
        try:
            pass  # print("DEBUG: Validando campos...") [OpSec Removed]
            # Validaciones
            if not dd_contrato.current.value:
                pass  # print("DEBUG: ERROR - No hay contrato seleccionado") [OpSec Removed]
                raise ValueError("Debe seleccionar un contrato")

            pass  # print(f"DEBUG: Contrato seleccionado: {dd_contrato.current.value}") [OpSec Removed]

            if not txt_periodo.current.value:
                pass  # print("DEBUG: ERROR - No hay período ingresado") [OpSec Removed]
                raise ValueError("Debe ingresar el período (YYYY-MM)")

            pass  # print(f"DEBUG: Período: {txt_periodo.current.value}") [OpSec Removed]

            if not txt_canon_bruto.current.value or int(txt_canon_bruto.current.value) <= 0:
                pass  # print("DEBUG: ERROR - Canon bruto inválido") [OpSec Removed]
                raise ValueError("El canon bruto debe ser mayor a cero")

            pass  # print(f"DEBUG: Canon bruto: {txt_canon_bruto.current.value}") [OpSec Removed]

            # Preparar datos
            pass  # print("DEBUG: Preparando datos adicionales...") [OpSec Removed]
            datos_adicionales = {
                "otros_ingresos": int(txt_otros_ingresos.current.value or 0),
                "gastos_administracion": int(txt_gastos_admin.current.value or 0),
                "gastos_servicios": int(txt_gastos_servicios.current.value or 0),
                "gastos_reparaciones": int(txt_gastos_reparaciones.current.value or 0),
                "otros_egresos": int(txt_otros_egresos.current.value or 0),
                "observaciones": txt_observaciones.current.value,
                "comision_porcentaje": int(txt_comision_porcentaje.current.value),
            }
            pass  # print(f"DEBUG: Datos adicionales: {datos_adicionales}") [OpSec Removed]

            # Guardar en la base de datos
            pass  # print("DEBUG: Llamando servicio_financiero.generar_liquidacion_mensual...") [OpSec Removed]
            servicio_financiero.generar_liquidacion_mensual(
                id_contrato_m=int(dd_contrato.current.value),
                periodo=txt_periodo.current.value,
                datos_adicionales=datos_adicionales,
                usuario_sistema="admin",
            )
            pass  # print("DEBUG: ✅ Liquidación guardada en BD exitosamente") [OpSec Removed]

            pass  # print("DEBUG: Mostrando banner de éxito...") [OpSec Removed]
            show_banner("Liquidación generada exitosamente", is_error=False)

            pass  # print("DEBUG: Llamando on_guardar() callback...") [OpSec Removed]
            on_guardar()
            pass  # print("DEBUG: ✅ Callback on_guardar() ejecutado") [OpSec Removed]

        except ValueError as ve:
            pass  # print(f"DEBUG: ValueError capturado: {ve}") [OpSec Removed]
            show_banner(str(ve))
        except Exception as ex:
            pass  # print(f"DEBUG: Exception capturado: {ex}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            show_banner(f"Error inesperado: {ex}")

        pass  # print("=== DEBUG: handle_guardar FINALIZADO ===\n") [OpSec Removed]

    def handle_cancelar(e):
        """Maneja la cancelación del formulario"""
        on_cancelar()

    # Cargar contratos de mandato activos
    contratos_options = []
    try:
        # Obtener contratos de mandato activos
        mandatos = servicio_contratos.listar_mandatos_activos()
        contratos_options = [
            ft.dropdown.Option(key=str(m["id"]), text=m["texto"]) for m in mandatos
        ]
    except Exception:
        pass  # print(f"Error cargando contratos: {e}") [OpSec Removed]

    # --- Breadcrumbs ---
    breadcrumbs_text = "Editar Liquidación Masiva" if es_edicion else "Nueva Liquidación"
    breadcrumbs = ft.Row(
        [
            ft.Text("Inicio", size=14, color="#666"),
            ft.Text(" > ", size=14, color="#666"),
            ft.Text("Liquidaciones", size=14, color="#666"),
            ft.Text(" > ", size=14, color="#666"),
            ft.Text(breadcrumbs_text, size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
        ]
    )

    # --- Header ---
    if es_edicion and liquidacion_propietario_info:
        header = ft.Column(
            [
                ft.Text("Editar Liquidación Masiva", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Propietario: {liquidacion_propietario_info['nombre_propietario']} | Período: {liquidacion_propietario_info['periodo']} | {liquidacion_propietario_info['cantidad_contratos']} contrato(s)",
                    size=14,
                    color="#666",
                ),
            ],
            spacing=5,
        )
    else:
        header = ft.Text("Generar Nueva Liquidación", size=28, weight=ft.FontWeight.BOLD)

    # --- Sección: Datos Básicos ---
    seccion_basica = ft.Container(
        content=ft.Column(
            [
                ft.Text("Datos Básicos", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Row(
                    [
                        ft.Dropdown(
                            ref=dd_contrato,
                            label="Contrato de Mandato *",
                            hint_text="Seleccione...",
                            width=400,
                            options=contratos_options,
                            on_change=cargar_canon_contrato,
                            disabled=es_edicion,
                        ),
                        ft.TextField(
                            ref=txt_periodo,
                            label="Período *",
                            hint_text="YYYY-MM",
                            value=(
                                liquidacion_propietario_info["periodo"]
                                if liquidacion_propietario_info
                                else datetime.now().strftime("%Y-%m")
                            ),
                            width=150,
                            disabled=es_edicion,
                        ),
                    ],
                    wrap=True,
                    spacing=15,
                ),
            ]
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # --- Sección: Ingresos ---
    seccion_ingresos = ft.Container(
        content=ft.Column(
            [
                ft.Text("Ingresos", size=18, weight=ft.FontWeight.BOLD, color="#4caf50"),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Row(
                    [
                        ft.TextField(
                            ref=txt_canon_bruto,
                            label="Canon Bruto *",
                            hint_text="0",
                            value=(
                                str(liquidacion_propietario_info["suma_canon_bruto"])
                                if liquidacion_propietario_info
                                else ""
                            ),
                            prefix_text="$",
                            width=200,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_otros_ingresos,
                            label="Otros Ingresos",
                            hint_text="0",
                            prefix_text="$",
                            value=(
                                str(liquidacion_propietario_info["suma_otros_ingresos"])
                                if liquidacion_propietario_info
                                else "0"
                            ),
                            width=200,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_total_ingresos,
                            label="TOTAL INGRESOS",
                            prefix_text="$",
                            width=200,
                            read_only=True,
                            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color="#4caf50"),
                        ),
                    ],
                    wrap=True,
                    spacing=15,
                ),
            ]
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#4caf50"),
    )

    # --- Sección: Egresos ---
    seccion_egresos = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Egresos y Deducciones", size=18, weight=ft.FontWeight.BOLD, color="#f44336"
                ),
                ft.Divider(height=1, color="#e0e0e0"),
                # Comisiones
                ft.Text("Comisión de Administración", size=14, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.TextField(
                            ref=txt_comision_porcentaje,
                            label="Porcentaje",
                            hint_text="1000 = 10%",
                            value=(
                                str(liquidacion_propietario_info["comision_porcentaje"])
                                if liquidacion_propietario_info
                                else ""
                            ),
                            width=150,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_comision_monto,
                            label="Monto Comisión",
                            prefix_text="$",
                            width=200,
                            read_only=True,
                        ),
                        ft.TextField(
                            ref=txt_iva_comision,
                            label="IVA (19%)",
                            prefix_text="$",
                            width=200,
                            read_only=True,
                        ),
                    ],
                    wrap=True,
                    spacing=15,
                ),
                ft.Divider(height=10, color="#e0e0e0"),
                # Impuestos
                ft.Text("Impuestos", size=14, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    ref=txt_impuesto_4x1000,
                    label="4x1000",
                    prefix_text="$",
                    width=200,
                    read_only=True,
                ),
                ft.Divider(height=10, color="#e0e0e0"),
                # Gastos
                ft.Text("Gastos Operativos", size=14, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.TextField(
                            ref=txt_gastos_admin,
                            label="Administración",
                            hint_text="0",
                            prefix_text="$",
                            value=(
                                str(liquidacion_propietario_info["suma_gastos_admin"])
                                if liquidacion_propietario_info
                                else "0"
                            ),
                            width=180,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_gastos_servicios,
                            label="Servicios",
                            hint_text="0",
                            prefix_text="$",
                            value=(
                                str(liquidacion_propietario_info["suma_gastos_servicios"])
                                if liquidacion_propietario_info
                                else "0"
                            ),
                            width=180,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_gastos_reparaciones,
                            label="Reparaciones",
                            hint_text="0",
                            prefix_text="$",
                            value=(
                                str(liquidacion_propietario_info["suma_gastos_reparaciones"])
                                if liquidacion_propietario_info
                                else "0"
                            ),
                            width=180,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                        ft.TextField(
                            ref=txt_otros_egresos,
                            label="Otros",
                            hint_text="0",
                            prefix_text="$",
                            value=(
                                str(liquidacion_propietario_info["suma_otros_egresos"])
                                if liquidacion_propietario_info
                                else "0"
                            ),
                            width=180,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=calcular_totales,
                        ),
                    ],
                    wrap=True,
                    spacing=15,
                ),
                ft.Divider(height=10, color="#e0e0e0"),
                # Total Egresos
                ft.TextField(
                    ref=txt_total_egresos,
                    label="TOTAL EGRESOS",
                    prefix_text="$",
                    width=200,
                    read_only=True,
                    text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color="#f44336"),
                ),
            ]
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#f44336"),
    )

    # --- Sección: Resultado ---
    seccion_resultado = ft.Container(
        content=ft.Column(
            [
                ft.Text("Resultado Final", size=20, weight=ft.FontWeight.BOLD, color="#1976d2"),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.TextField(
                    ref=txt_neto_a_pagar,
                    label="NETO A PAGAR AL PROPIETARIO",
                    prefix_text="$",
                    width=350,
                    read_only=True,
                    text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD, color="#1976d2"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#e3f2fd",
        padding=20,
        border_radius=8,
        border=ft.border.all(2, "#1976d2"),
    )

    # --- Sección: Observaciones ---
    seccion_obs = ft.Container(
        content=ft.Column(
            [
                ft.Text("Observaciones", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.TextField(
                    ref=txt_observaciones,
                    label="Observaciones",
                    hint_text="Notas adicionales sobre esta liquidación...",
                    value=(
                        liquidacion_propietario_info["observaciones"]
                        if liquidacion_propietario_info
                        else ""
                    ),
                    multiline=True,
                    min_lines=3,
                    max_lines=5,
                ),
            ]
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # --- Botones de Acción ---
    botones = ft.Row(
        [
            ft.ElevatedButton(
                "Generar Liquidación",
                icon=ft.Icons.SAVE,
                on_click=handle_guardar,
                bgcolor="#1976d2",
                color="white",
                height=45,
            ),
            ft.OutlinedButton(
                "Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=handle_cancelar,
                height=45,
            ),
        ],
        spacing=15,
    )

    # --- Layout Principal ---
    container = ft.Container(
        content=ft.Column(
            [
                breadcrumbs,
                ft.Divider(height=20, color="transparent"),
                header,
                ft.Divider(height=20, color="transparent"),
                seccion_basica,
                ft.Divider(height=20, color="transparent"),
                seccion_ingresos,
                ft.Divider(height=20, color="transparent"),
                seccion_egresos,
                ft.Divider(height=20, color="transparent"),
                seccion_resultado,
                ft.Divider(height=20, color="transparent"),
                seccion_obs,
                ft.Divider(height=20, color="transparent"),
                botones,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=30,
        expand=True,
    )

    # Si estamos en modo edición, calcular los totales automáticamente
    if es_edicion and liquidacion_propietario_info:
        # Programar el cálculo para después de que se monte el componente
        async def _calcular_despues_de_montar(e=None):
            """Calcula los totales iniciales de forma asíncrona después del montaje."""
            try:
                calcular_totales()
            except Exception:
                pass  # print(f"Error calculando totales iniciales: {ex}") [OpSec Removed]

        # Usar page.run_task para asegurar que los controles están inicializados
        page.run_task(_calcular_despues_de_montar)

    return container

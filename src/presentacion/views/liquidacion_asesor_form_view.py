"""
Vista: Formulario de Liquidación de Asesor
Permite crear y editar liquidaciones de comisiones para asesores.
"""

from typing import Any, Callable, Dict, Optional

import flet as ft


def crear_liquidacion_asesor_form_view(
    page: ft.Page,
    servicio_liquidacion_asesores,
    servicio_contratos,
    servicio_personas,
    on_guardar: Callable[[Dict[str, Any]], None],
    on_cancelar: Callable,
    liquidacion_id: Optional[int] = None,
) -> ft.Container:
    """
    Crea el formulario de liquidación de asesor.

    Args:
        page: Página de Flet
        servicio_liquidacion_asesores: Servicio de liquidaciones
        servicio_contratos: Servicio de contratos
        servicio_personas: Servicio de personas
        on_guardar: Callback al guardar
        on_cancelar: Callback al cancelar
        liquidacion_id: ID de liquidación para modo edición
    """

    # Determinar modo
    es_edicion = liquidacion_id is not None
    titulo = "Editar Liquidación" if es_edicion else "Nueva Liquidación"

    # Referencias de campos
    dropdown_asesor = ft.Ref[ft.Dropdown]()
    dropdown_contrato = ft.Ref[ft.Dropdown]()
    txt_periodo = ft.Ref[ft.TextField]()
    txt_canon = ft.Ref[ft.TextField]()
    txt_porcentaje = ft.Ref[ft.TextField]()
    txt_comision_bruta = ft.Ref[ft.Text]()
    txt_total_descuentos = ft.Ref[ft.Text]()
    txt_valor_neto = ft.Ref[ft.Text]()
    txt_observaciones = ft.Ref[ft.TextField]()

    # Banner de errores
    banner_error = ft.Ref[ft.Banner]()

    # Tabla de descuentos
    descuentos_container = ft.Ref[ft.Column]()
    descuentos_lista = []  # Lista interna de descuentos

    # Estado

    def calcular_comision():
        """Calcula y actualiza la comisión bruta"""
        try:
            canon = int(txt_canon.current.value or 0)
            porcentaje = float(txt_porcentaje.current.value or 0)

            # Convertir porcentaje a formato INTEGER (5.5% -> 550)
            porcentaje_int = int(porcentaje * 100)

            # Calcular comisión
            comision_bruta = int((canon * porcentaje_int) / 10000)

            txt_comision_bruta.current.value = f"${comision_bruta:,}"
            actualizar_valor_neto()
            page.update()

        except (ValueError, TypeError):
            txt_comision_bruta.current.value = "$0"
            page.update()

    def actualizar_valor_neto():
        """Actualiza el valor neto (comisión - descuentos)"""
        try:
            # Remover formato y convertir
            comision_text = txt_comision_bruta.current.value.replace("$", "").replace(",", "")
            comision_bruta = int(comision_text) if comision_text else 0

            descuentos_text = txt_total_descuentos.current.value.replace("$", "").replace(",", "")
            total_descuentos = int(descuentos_text) if descuentos_text else 0

            valor_neto = max(0, comision_bruta - total_descuentos)
            txt_valor_neto.current.value = f"${valor_neto:,}"
            page.update()

        except (ValueError, TypeError):
            pass  # print(f"Error calculando valor neto: {e}") [OpSec Removed]
            txt_valor_neto.current.value = "$0"
            page.update()

    def actualizar_total_descuentos():
        """Recalcula el total de descuentos"""
        total = sum(d["valor"] for d in descuentos_lista)
        txt_total_descuentos.current.value = f"${total:,}"
        actualizar_valor_neto()

    def agregar_descuento_click(e):
        """Muestra modal para agregar descuento"""
        pass  # print("[DEBUG] ===== AGREGAR DESCUENTO CLICK =====") [OpSec Removed]
        pass  # print(f"[DEBUG] Evento recibido: {e}") [OpSec Removed]

        # Referencias del modal
        dropdown_tipo = ft.Ref[ft.Dropdown]()
        txt_descripcion = ft.Ref[ft.TextField]()
        txt_valor = ft.Ref[ft.TextField]()

        def guardar_descuento(e):
            pass  # print("[DEBUG] Guardando descuento...") [OpSec Removed]
            try:
                tipo = dropdown_tipo.current.value
                descripcion = txt_descripcion.current.value
                valor = int(txt_valor.current.value or 0)

                pass  # print(f"[DEBUG] Tipo: {tipo}, Descripcion: {descripcion}, Valor: {valor}") [OpSec Removed]

                if not tipo or not descripcion or valor <= 0:
                    pass  # print("[DEBUG] ERROR: Validación fallida") [OpSec Removed]
                    mostrar_error("Todos los campos son obligatorios y el valor debe ser mayor a 0")
                    return

                # Agregar a lista
                descuentos_lista.append({"tipo": tipo, "descripcion": descripcion, "valor": valor})
                pass  # print(f"[DEBUG] Descuento agregado. Total descuentos: {len(descuentos_lista)}") [OpSec Removed]

                # Actualizar vista
                renderizar_descuentos()
                actualizar_total_descuentos()

                # Cerrar modal
                dialog.open = False
                page.update()
                pass  # print("[DEBUG] Modal cerrado y página actualizada") [OpSec Removed]

            except ValueError:
                pass  # print(f"[DEBUG] ERROR ValueError: {ve}") [OpSec Removed]
                mostrar_error("El valor debe ser un número válido")

        # Crear modal
        dialog = ft.AlertDialog(
            title=ft.Text("Agregar Descuento"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Dropdown(
                            ref=dropdown_tipo,
                            label="Tipo de Descuento",
                            options=[
                                ft.dropdown.Option("Préstamo"),
                                ft.dropdown.Option("Anticipo"),
                                ft.dropdown.Option("Sanción"),
                                ft.dropdown.Option("Ajuste"),
                                ft.dropdown.Option("Otros"),
                            ],
                            width=300,
                        ),
                        ft.TextField(
                            ref=txt_descripcion,
                            label="Descripción",
                            multiline=True,
                            min_lines=2,
                            max_lines=3,
                            width=300,
                        ),
                        ft.TextField(
                            ref=txt_valor,
                            label="Valor",
                            prefix_text="$",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            width=300,
                        ),
                    ],
                    spacing=15,
                    tight=True,
                ),
                width=350,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialog()),
                ft.ElevatedButton(
                    "Agregar", on_click=guardar_descuento, bgcolor="#4caf50", color="white"
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def cerrar_dialog():
            pass  # print("[DEBUG] Cerrando diálogo...") [OpSec Removed]
            dialog.open = False
            page.update()

        pass  # print("[DEBUG] Asignando diálogo a página...") [OpSec Removed]
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        pass  # print("[DEBUG] Diálogo abierto") [OpSec Removed]

    def eliminar_descuento(index: int):
        """Elimina un descuento de la lista"""
        if 0 <= index < len(descuentos_lista):
            descuentos_lista.pop(index)
            renderizar_descuentos()
            actualizar_total_descuentos()

    def renderizar_descuentos():
        """Renderiza la tabla de descuentos"""
        if not descuentos_lista:
            descuentos_container.current.controls = [
                ft.Container(
                    content=ft.Text(
                        "No hay descuentos agregados", size=13, color="#999", italic=True
                    ),
                    padding=15,
                    alignment=ft.alignment.center,
                )
            ]
        else:
            filas = []
            for i, desc in enumerate(descuentos_lista):
                filas.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(desc["tipo"], size=12)),
                            ft.DataCell(ft.Text(desc["descripcion"], size=12)),
                            ft.DataCell(ft.Text(f"${desc['valor']:,}", size=12)),
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="#f44336",
                                    icon_size=18,
                                    tooltip="Eliminar",
                                    on_click=lambda e, idx=i: eliminar_descuento(idx),
                                )
                            ),
                        ]
                    )
                )

            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Tipo", size=13, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Descripción", size=13, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Valor", size=13, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("", size=13)),
                ],
                rows=filas,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=4,
                heading_row_color="#f5f5f5",
                heading_row_height=40,
                data_row_min_height=45,
            )

            descuentos_container.current.controls = [tabla]

        page.update()

    def mostrar_error(mensaje: str):
        """Muestra un banner de error"""
        banner_error.current.open = True
        banner_error.current.content.value = mensaje
        page.update()

    def cerrar_banner(e):
        """Cierra el banner de error"""
        banner_error.current.open = False
        page.update()

    def validar_formato_periodo(periodo: str) -> bool:
        """Valida que el período tenga formato YYYY-MM"""
        import re

        patron = r"^\d{4}-\d{2}$"
        return re.match(patron, periodo) is not None

    def handle_guardar_click(e):
        """Maneja el evento de guardar"""
        pass  # print("\n" + "="*80) [OpSec Removed]
        pass  # print("[DEBUG LAYER 1: FORM] ===== GUARDAR LIQUIDACIÓN CLICK =====") [OpSec Removed]
        pass  # print(f"[DEBUG LAYER 1: FORM] Evento recibido: {e}") [OpSec Removed]
        pass  # print(f"[DEBUG LAYER 1: FORM] Es edición: {es_edicion}") [OpSec Removed]
        pass  # print("="*80 + "\n") [OpSec Removed]

        try:
            # Validaciones
            pass  # print("[DEBUG LAYER 1: FORM] Iniciando validaciones...") [OpSec Removed]
            if not dropdown_asesor.current.value:
                pass  # print("[DEBUG LAYER 1: FORM] ERROR: No hay asesor seleccionado") [OpSec Removed]
                mostrar_error("Debe seleccionar un asesor")
                return

            # NOTA: Ya no requiere seleccionar contrato individual
            # Se usa la lista completa de contratos activos del asesor

            if not txt_periodo.current.value:
                pass  # print("[DEBUG LAYER 1: FORM] ERROR: No hay período") [OpSec Removed]
                mostrar_error("Debe especificar el período")
                return

            # Validar formato YYYY-MM
            if not validar_formato_periodo(txt_periodo.current.value):
                pass  # print(f"[DEBUG LAYER 1: FORM] ERROR: Formato de período inválido: {txt_periodo.current.value}") [OpSec Removed]
                mostrar_error(
                    f"Formato de período inválido: '{txt_periodo.current.value}'. Use formato YYYY-MM (ejemplo: 2025-12)"
                )
                return

            if not txt_porcentaje.current.value:
                pass  # print("[DEBUG LAYER 1: FORM] ERROR: No hay porcentaje") [OpSec Removed]
                mostrar_error("Debe especificar el porcentaje de comisión")
                return

            pass  # print("[DEBUG LAYER 1: FORM] ✓ Validaciones pasadas") [OpSec Removed]

            # Recopilar datos
            pass  # print("[DEBUG LAYER 1: FORM] Recopilando datos...") [OpSec Removed]

            # Obtener lista de contratos activos del asesor seleccionado
            id_asesor = int(dropdown_asesor.current.value)
            contratos_asesor = servicio_contratos.listar_arrendamientos_por_asesor(id_asesor)

            # Preparar lista de contratos para el servicio
            contratos_lista = [{"id": c["id"], "canon": c["canon"]} for c in contratos_asesor]

            datos = {
                "id_asesor": id_asesor,
                "contratos_lista": contratos_lista,  # NUEVO: Lista de todos los contratos
                "periodo": txt_periodo.current.value,
                "porcentaje_comision": float(txt_porcentaje.current.value or 0),
                "observaciones": txt_observaciones.current.value,
                "descuentos": descuentos_lista.copy(),  # Copiar lista de descuentos
            }

            if es_edicion:
                datos["id_liquidacion"] = liquidacion_id

            pass  # print("[DEBUG LAYER 1: FORM] Datos recopilados:") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - id_asesor: {datos['id_asesor']}") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - contratos_lista: {len(datos['contratos_lista'])} contratos") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - periodo: {datos['periodo']}") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - porcentaje_comision: {datos['porcentaje_comision']}") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - descuentos: {len(datos['descuentos'])} descuentos") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM]   - observaciones: {datos.get('observaciones', 'N/A')}") [OpSec Removed]

            # Llamar callback
            pass  # print("[DEBUG LAYER 1: FORM] ===== LLAMANDO CALLBACK on_guardar =====") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM] Callback: {on_guardar}") [OpSec Removed]

            try:
                on_guardar(datos)
                pass  # print("[DEBUG LAYER 1: FORM] ===== CALLBACK on_guardar COMPLETADO =====") [OpSec Removed]
            except ValueError as ve:
                # Errores de validación de negocio (duplicados, etc.)
                pass  # print(f"[DEBUG LAYER 1: FORM] ❌ ValueError capturado del servicio: {str(ve)}") [OpSec Removed]
                mostrar_error(str(ve))
                raise  # Re-lanzar para que main.py también lo maneje si es necesario
            except Exception as ex:
                # Otros errores inesperados
                pass  # print(f"[DEBUG LAYER 1: FORM] ❌ Excepción inesperada: {type(ex).__name__}: {str(ex)}") [OpSec Removed]
                mostrar_error(f"Error inesperado: {str(ex)}")
                raise

        except ValueError:
            # ValueError ya fue mostrado en Banner arriba, no hacer nada más
            pass  # print(f"[DEBUG LAYER 1: FORM] ValueError ya manejado: {str(ve)}") [OpSec Removed]

        except Exception as e:
            pass  # print("\n" + "!"*80) [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM] ❌ EXCEPCIÓN CAPTURADA: {type(e).__name__}") [OpSec Removed]
            pass  # print(f"[DEBUG LAYER 1: FORM] ❌ Mensaje: {str(e)}") [OpSec Removed]
            pass  # print("!"*80 + "\n") [OpSec Removed]
            mostrar_error(f"Error al guardar: {str(e)}")
            pass  # print(f"Error detallado: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()

    # Cargar datos si es edición
    if es_edicion:
        try:
            detalle = servicio_liquidacion_asesores.obtener_detalle_completo(liquidacion_id)
            detalle["liquidacion"]

            # Pre-llenar campos (será async en el futuro)
            # Por ahora solo guardamos la referencia
        except Exception:
            pass  # print(f"Error cargando liquidación: {e}") [OpSec Removed]

    # Cargar asesores
    pass  # print("[DEBUG] ===== CARGANDO ASESORES =====") [OpSec Removed]
    asesores_cache = {}  # Cache: id_persona -> {nombre, comision_arriendo, comision_venta}
    try:
        asesores = servicio_personas.listar_personas(filtro_rol="Asesor")
        pass  # print(f"[DEBUG] Asesores encontrados: {len(asesores)}") [OpSec Removed]
        opciones_asesores = []
        for a in asesores:
            # Obtener datos del rol Asesor
            asesor_data = a.datos_roles.get("Asesor")
            comision_arriendo = 0
            id_asesor_real = None

            if asesor_data:
                comision_arriendo = getattr(asesor_data, "comision_porcentaje_arriendo", 0) or 0
                id_asesor_real = getattr(asesor_data, "id_asesor", None)

            # Validar que tenga ID y esté ACTIVO (Estado 1)
            es_activo = getattr(asesor_data, "estado", 1) == 1

            if id_asesor_real and es_activo:
                # Usar ID_ASESOR como key, no ID_PERSONA
                asesores_cache[id_asesor_real] = {
                    "nombre": a.nombre_completo,
                    "comision_arriendo": comision_arriendo,
                }

                opciones_asesores.append(
                    ft.dropdown.Option(key=str(id_asesor_real), text=a.nombre_completo)
                )
                pass  # print(f"[DEBUG]   - ID ASESOR: {id_asesor_real} (Persona {a.persona.id_persona}), Nombre: {a.nombre_completo}") [OpSec Removed]
        pass  # print(f"[DEBUG] Opciones de asesores creadas: {len(opciones_asesores)}") [OpSec Removed]
    except Exception:
        pass  # print(f"[DEBUG] ERROR cargando asesores: {e}") [OpSec Removed]
        import traceback

        traceback.print_exc()
        opciones_asesores = []

    def on_asesor_change(e):
        """
        Cuando se selecciona un asesor:
        1. Auto-llena el porcentaje de comisión
        2. Filtra los contratos para mostrar solo los del asesor
        3. Calcula y muestra la suma de todos los cánones
        """
        pass  # print(f"[DEBUG] ===== ASESOR SELECCIONADO =====") [OpSec Removed]
        pass  # print(f"[DEBUG] Valor dropdown: {dropdown_asesor.current.value}") [OpSec Removed]
        try:
            if not dropdown_asesor.current.value:
                pass  # print("[DEBUG] No hay asesor seleccionado") [OpSec Removed]
                # Reset
                dropdown_contrato.current.options = []
                dropdown_contrato.current.value = None
                txt_canon.current.value = ""
                txt_porcentaje.current.value = ""
                page.update()
                return

            id_asesor = int(dropdown_asesor.current.value)
            pass  # print(f"[DEBUG] ID Asesor: {id_asesor}") [OpSec Removed]

            # 1. Auto-llenar porcentaje de comisión
            asesor_info = asesores_cache.get(id_asesor)
            pass  # print(f"[DEBUG] Info asesor en cache: {asesor_info}") [OpSec Removed]

            if asesor_info:
                comision_porcentaje = asesor_info["comision_arriendo"]
                txt_porcentaje.current.value = str(comision_porcentaje)
                pass  # print(f"[DEBUG] Porcentaje comisión establecido: {comision_porcentaje}%") [OpSec Removed]

            # 2. Filtrar contratos del asesor
            contratos_asesor = servicio_contratos.listar_arrendamientos_por_asesor(id_asesor)
            pass  # print(f"[DEBUG] Contratos del asesor: {len(contratos_asesor)}") [OpSec Removed]

            # 3. Actualizar dropdown de contratos
            num_contratos = len(contratos_asesor)
            dropdown_contrato.current.options = [
                ft.dropdown.Option(key=str(c["id"]), text=c["texto"]) for c in contratos_asesor
            ]
            dropdown_contrato.current.value = None  # Reset selection
            dropdown_contrato.current.hint_text = "Click ver detalles..."
            dropdown_contrato.current.label = "Contratos Incluidos"
            dropdown_contrato.current.suffix_text = f"({num_contratos})"
            dropdown_contrato.current.helper_text = f"Total sumado: {num_contratos} contratos"

            # 4. Calcular suma total de cánones
            total_canon = sum(c["canon"] for c in contratos_asesor)
            txt_canon.current.value = str(total_canon)
            pass  # print(f"[DEBUG] Canon total establecido: ${total_canon:,}") [OpSec Removed]

            # 5. Recalcular comisión
            calcular_comision()
            page.update()

        except Exception:
            pass  # print(f"[DEBUG] ERROR en on_asesor_change: {ex}") [OpSec Removed]
            import traceback

            traceback.print_exc()

    # NOTE: Contract loading is now dynamic based on selected advisor
    # Initial options will be empty until an advisor is selected
    opciones_contratos = []

    def on_contrato_change(e):
        """
        Maneja cambio en dropdown de contrato.
        NOTA: En la nueva lógica de sumatoria total, seleccionar un contrato
        NO debe sobrescribir el campo de canon con el valor individual.
        El dropdown sirve solo para ver qué contratos están incluidos.
        """
        # NO-OP: Ya no sobrescribimos el canon al seleccionar uno individual
        # Si se desea mostrar detalle del contrato seleccionado, se podría hacer en un label aparte.
        pass

    # --- Layout ---

    # Breadcrumbs
    breadcrumbs = ft.Row(
        [
            ft.Text("Inicio", size=14, color="#666"),
            ft.Text(" > ", size=14, color="#666"),
            ft.Text("Liquidación Asesores", size=14, color="#666"),
            ft.Text(" > ", size=14, color="#666"),
            ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
        ]
    )

    # Header
    header = ft.Text(titulo, size=28, weight=ft.FontWeight.BOLD)

    # Sección 1: Identificación
    seccion_identificacion = ft.Container(
        content=ft.Column(
            [
                ft.Text("1. IDENTIFICACIÓN", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.ResponsiveRow(
                    [
                        ft.Dropdown(
                            ref=dropdown_asesor,
                            col={"sm": 12, "md": 12},
                            label="Asesor *",
                            options=opciones_asesores,
                            prefix_icon=ft.Icons.PERSON,
                            disabled=es_edicion,  # No se puede cambiar en edición
                            on_change=on_asesor_change,  # Auto-llenar porcentaje comisión
                        ),
                        ft.Dropdown(
                            ref=dropdown_contrato,
                            col={"sm": 12, "md": 12},
                            label="Contrato *",
                            options=opciones_contratos,
                            on_change=on_contrato_change,
                            disabled=es_edicion,  # No se puede cambiar en edición
                            expand=True,
                            width=None,  # Let it take full available width
                        ),
                        ft.TextField(
                            ref=txt_periodo,
                            col={"sm": 12, "md": 6},
                            label="Período *",
                            hint_text="YYYY-MM",
                            prefix_icon=ft.Icons.CALENDAR_MONTH,
                            disabled=es_edicion,  # No se puede cambiar en edición
                        ),
                    ]
                ),
            ],
            spacing=15,
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # Sección 2: Cálculo de Comisión
    seccion_comision = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "2. CÁLCULO DE COMISIÓN", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"
                ),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.ResponsiveRow(
                    [
                        ft.TextField(
                            ref=txt_canon,
                            col={"sm": 12, "md": 4},
                            label="Canon Arrendamiento",
                            prefix_text="$",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_change=lambda e: calcular_comision(),
                            read_only=True,
                            bgcolor="#f5f5f5",
                        ),
                        ft.TextField(
                            ref=txt_porcentaje,
                            col={"sm": 12, "md": 4},
                            label="Porcentaje Comisión *",
                            suffix_text="%",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            hint_text="Ej: 5.5 para 5.5%",
                            on_change=lambda e: calcular_comision(),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=ft.Column(
                                [
                                    ft.Text("Comisión Bruta", size=13, color="#666"),
                                    ft.Text(
                                        ref=txt_comision_bruta,
                                        value="$0",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1976d2",
                                    ),
                                ],
                                spacing=5,
                            ),
                            bgcolor="#e3f2fd",
                            padding=15,
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                    ]
                ),
            ],
            spacing=15,
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # Sección 3: Descuentos
    seccion_descuentos = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "3. DESCUENTOS", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "+ Agregar Descuento",
                            icon=ft.Icons.ADD,
                            on_click=agregar_descuento_click,
                            bgcolor="#2196f3",
                            color="white",
                            height=35,
                        ),
                    ]
                ),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Column(ref=descuentos_container),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("TOTAL DESCUENTOS:", size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                ref=txt_total_descuentos,
                                value="$0",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#f44336",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ],
            spacing=15,
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # Sección 4: Resumen
    seccion_resumen = ft.Container(
        content=ft.Column(
            [
                ft.Text("4. RESUMEN", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("VALOR NETO A PAGAR", size=16, color="#666"),
                            ft.Text(
                                ref=txt_valor_neto,
                                value="$0",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color="#4caf50",
                            ),
                            ft.Text(
                                "(Comisión Bruta - Descuentos)", size=12, color="#999", italic=True
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    bgcolor="#e8f5e9",
                    padding=20,
                    border_radius=8,
                    alignment=ft.alignment.center,
                ),
                ft.TextField(
                    ref=txt_observaciones,
                    label="Observaciones",
                    multiline=True,
                    min_lines=3,
                    max_lines=5,
                ),
            ],
            spacing=15,
        ),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )

    # Botones de acción
    botones = ft.Row(
        [
            ft.OutlinedButton(
                "Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: on_cancelar(),
                height=45,
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Guardar Liquidación",
                icon=ft.Icons.SAVE,
                on_click=handle_guardar_click,
                bgcolor="#4caf50",
                color="white",
                height=45,
            ),
        ]
    )

    # Inicializar descuentos vacíos
    renderizar_descuentos()

    # Banner de errores (debe estar en page.overlay o en el contenido)
    banner_validacion = ft.Banner(
        ref=banner_error,
        bgcolor="#ffebee",
        leading=ft.Icon(ft.Icons.WARNING, color="#f44336", size=40),
        content=ft.Text("Error de validación", color="#c62828", size=14, weight=ft.FontWeight.BOLD),
        actions=[
            ft.TextButton("Cerrar", on_click=cerrar_banner),
        ],
    )

    # Layout final
    return ft.Container(
        content=ft.Column(
            [
                banner_validacion,  # Banner en la parte superior
                breadcrumbs,
                ft.Divider(height=20, color="transparent"),
                header,
                ft.Divider(height=20, color="transparent"),
                seccion_identificacion,
                ft.Divider(height=15, color="transparent"),
                seccion_comision,
                ft.Divider(height=15, color="transparent"),
                seccion_descuentos,
                ft.Divider(height=15, color="transparent"),
                seccion_resumen,
                ft.Divider(height=20, color="transparent"),
                botones,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=30,
        expand=True,
    )

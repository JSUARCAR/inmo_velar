"""
Vista: Formulario de Contrato de Arrendamiento
Permite crear y editar Contratos de Arrendamiento (Inquilinos).
"""

import sqlite3
from datetime import datetime
from typing import Callable, Optional

import flet as ft

from src.presentacion.components.document_manager import DocumentManager
from src.presentacion.theme import colors, styles


def crear_contrato_arrendamiento_form_view(
    page: ft.Page, on_guardar: Callable, on_cancelar: Callable, contrato_id: Optional[int] = None
) -> ft.Container:

    es_edicion = contrato_id is not None
    titulo = f"Inicio > Contratos > {'Editar' if es_edicion else 'Nuevo'} Arriendo"

    # Servicios
    from src.aplicacion.servicios.servicio_contratos import ServicioContratos
    from src.aplicacion.servicios.servicio_personas import ServicioPersonas
    from src.infraestructura.persistencia.database import DatabaseManager

    db_manager = DatabaseManager()
    servicio_contratos = ServicioContratos(db_manager)
    servicio_personas = ServicioPersonas(db_manager)

    # Cargar datos
    propiedades = servicio_contratos.obtener_propiedades_para_arrendamiento()
    arrendatarios = servicio_personas.listar_personas(filtro_rol="Arrendatario")
    codeudores = servicio_personas.listar_personas(filtro_rol="Codeudor")

    def on_propiedad_change(e):
        prop_id = dd_propiedad.value
        if not prop_id:
            return
        # Buscar el canon estimado en las opciones data
        selected_option = next((o for o in dd_propiedad.options if o.key == prop_id), None)
        if selected_option and selected_option.data:
            txt_canon.value = str(int(selected_option.data))
            # txt_canon.update()  # Removed: causes AssertionError under Shell architecture

    # --- Campos ---
    dd_propiedad = ft.Dropdown(
        label="Propiedad (Con Mandato Activo) *",
        hint_text="Seleccione propiedad",
        options=[
            ft.dropdown.Option(key=str(p["id"]), text=p["texto"], data=p["canon"])
            for p in propiedades
        ],
        width=400,
        on_change=on_propiedad_change,
    )

    dd_arrendatario = ft.Dropdown(
        label="Arrendatario *",
        hint_text="Seleccione arrendatario",
        options=[
            ft.dropdown.Option(
                key=str(p.datos_roles["Arrendatario"].id_arrendatario), text=p.nombre_completo
            )
            for p in arrendatarios
        ],
        width=400,
    )

    dd_codeudor = ft.Dropdown(
        label="Codeudor (Opcional)",
        hint_text="MÁXIMO 1 Codeudor",
        options=[
            ft.dropdown.Option(
                key=str(p.datos_roles["Codeudor"].id_codeudor), text=p.nombre_completo
            )
            for p in codeudores
        ],
        width=400,
    )

    # Fechas y Duración
    def abrir_picker_inicio(e):
        page.open(date_picker_inicio)

    def abrir_picker_fin(e):
        page.open(date_picker_fin)

    def calcular_duracion():
        if date_picker_inicio.value and date_picker_fin.value:
            d1 = date_picker_inicio.value
            d2 = date_picker_fin.value

            # Calculo de diferencia en meses
            mdiff = (d2.year - d1.year) * 12 + d2.month - d1.month
            # Ajuste por días: si el día final es menor al inicial, no se ha cumplido el último mes completo
            if d2.day < d1.day:
                mdiff -= 1

            if mdiff < 0:
                mdiff = 0
            txt_duracion.value = str(mdiff)
            txt_duracion.update()

    def on_fecha_inicio_change(e):
        txt_fecha_inicio.value = (
            date_picker_inicio.value.strftime("%Y-%m-%d") if date_picker_inicio.value else ""
        )
        txt_fecha_inicio.update()
        calcular_duracion()

    def on_fecha_fin_change(e):
        txt_fecha_fin.value = (
            date_picker_fin.value.strftime("%Y-%m-%d") if date_picker_fin.value else ""
        )
        txt_fecha_fin.update()
        calcular_duracion()

    date_picker_inicio = ft.DatePicker(
        on_change=on_fecha_inicio_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
        value=datetime.now(),
    )
    date_picker_fin = ft.DatePicker(
        on_change=on_fecha_fin_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )

    # Nota: page.open(picker) se encarga de mostrarlo
    # page.overlay.extend([date_picker_inicio, date_picker_fin])

    txt_fecha_inicio = ft.TextField(
        label="Fecha Inicio *", width=150, read_only=True, value=datetime.now().date().isoformat()
    )
    btn_fecha_inicio = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=abrir_picker_inicio,
        tooltip="Seleccionar fecha inicio",
    )

    txt_fecha_fin = ft.TextField(label="Fecha Fin *", width=150, read_only=True)
    btn_fecha_fin = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH, on_click=abrir_picker_fin, tooltip="Seleccionar fecha fin"
    )

    txt_duracion = ft.TextField(
        label="Duración (Meses) *",
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        value="0",
        read_only=True,
    )

    # Económicos
    txt_canon = ft.TextField(
        label="Canon Arriendo *",
        prefix_text="$ ",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        read_only=True,
    )
    txt_deposito = ft.TextField(
        label="Depósito", prefix_text="$ ", width=200, keyboard_type=ft.KeyboardType.NUMBER
    )

    # --- Lógica de Edición: Cargar Datos y Bloquear Campos ---
    if es_edicion:
        arriendo = servicio_contratos.obtener_arrendamiento_por_id(contrato_id)
        if arriendo:
            # 1. Propiedad
            # Agregar opción dummy para la propiedad actual
            val_exists = any(o.key == str(arriendo.id_propiedad) for o in dd_propiedad.options)
            if not val_exists:
                dd_propiedad.options.append(
                    ft.dropdown.Option(
                        key=str(arriendo.id_propiedad),
                        text=f"Propiedad Actual (ID: {arriendo.id_propiedad})",
                        data=arriendo.canon_arrendamiento,  # Para que cargue el canon
                    )
                )

            dd_propiedad.value = str(arriendo.id_propiedad)
            dd_propiedad.disabled = True

            # 2. Arrendatario (ahora el key es id_arrendatario directamente)
            dd_arrendatario.value = str(arriendo.id_arrendatario)
            dd_arrendatario.disabled = True

            # 3. Codeudor (ahora el key es id_codeudor directamente)
            if arriendo.id_codeudor:
                dd_codeudor.value = str(arriendo.id_codeudor)
                dd_codeudor.disabled = True

            # 4. Fechas
            if arriendo.fecha_inicio_contrato_a:
                dt_inicio = datetime.strptime(arriendo.fecha_inicio_contrato_a, "%Y-%m-%d")
                date_picker_inicio.value = dt_inicio
                txt_fecha_inicio.value = arriendo.fecha_inicio_contrato_a

            if arriendo.fecha_fin_contrato_a:
                dt_fin = datetime.strptime(arriendo.fecha_fin_contrato_a, "%Y-%m-%d")
                date_picker_fin.value = dt_fin
                txt_fecha_fin.value = arriendo.fecha_fin_contrato_a

            # 5. Valores
            txt_duracion.value = str(arriendo.duracion_contrato_a)
            txt_canon.value = str(arriendo.canon_arrendamiento)
            txt_deposito.value = str(arriendo.deposito)

    # --- Helpers de UI ---
    def show_banner(message: str, is_error: bool = True):
        page.banner = ft.Banner(
            bgcolor=colors.ERROR if is_error else colors.SUCCESS,
            leading=ft.Icon(
                ft.Icons.ERROR_OUTLINE if is_error else ft.Icons.CHECK_CIRCLE,
                color=colors.TEXT_PRIMARY,
            ),
            content=ft.Text(message, color=colors.TEXT_PRIMARY),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: close_banner())],
        )
        page.banner.open = True
        page.update()

    def close_banner():
        if page.banner:
            page.banner.open = False
            page.update()

    def handle_guardar(e):
        pass  # print(">>> DEBUG: Inicio handle_guardar") [OpSec Removed]
        try:
            pass  # print(f"valores actuales: Propiedad={dd_propiedad.value}, Arrendatario={dd_arrendatario.value}, Inicio={txt_fecha_inicio.value}, Fin={txt_fecha_fin.value}, Canon={txt_canon.value}") [OpSec Removed]

            # Validar campos obligatorios
            if not dd_propiedad.value:
                raise ValueError("Debe seleccionar una propiedad")
            if not dd_arrendatario.value:
                raise ValueError("Debe seleccionar un arrendatario")
            if not txt_fecha_inicio.value:
                raise ValueError("Fecha inicio requerida")
            if not txt_fecha_fin.value:
                raise ValueError("Fecha fin requerida")

            pass  # print(">>> DEBUG: Validaciones básicas pasadas") [OpSec Removed]

            # Conversión de tipos explícita para debug
            try:
                p_id = int(dd_propiedad.value)
                a_id = int(dd_arrendatario.value)
                c_id = int(dd_codeudor.value) if dd_codeudor.value else None
                dur = int(txt_duracion.value)
                can = int(txt_canon.value)
                dep = int(txt_deposito.value or 0)
                pass  # print(f">>> DEBUG: Tipos convertidos: {p_id}, {a_id}, {c_id}, {dur}, {can}, {dep}") [OpSec Removed]
            except Exception as e_conv:
                pass  # print(f">>> DEBUG: Error en conversión de tipos: {e_conv}") [OpSec Removed]
                raise ValueError(f"Error en datos numéricos: {e_conv}")

            datos = {
                "id_propiedad": p_id,
                "id_arrendatario": a_id,
                "id_codeudor": c_id,
                "fecha_inicio": txt_fecha_inicio.value,
                "fecha_fin": txt_fecha_fin.value,
                "duracion_meses": dur,
                "canon": can,
                "deposito": dep,
            }

            pass  # print(f">>> DEBUG: Datos a enviar al servicio: {datos}") [OpSec Removed]

            try:
                if es_edicion:
                    pass  # print(">>> DEBUG: Llamando a servicio_contratos.actualizar_arrendamiento...") [OpSec Removed]
                    servicio_contratos.actualizar_arrendamiento(contrato_id, datos, "admin")
                    msg = "Contrato de Arrendamiento actualizado exitosamente"
                else:
                    pass  # print(">>> DEBUG: Llamando a servicio_contratos.crear_arrendamiento...") [OpSec Removed]
                    servicio_contratos.crear_arrendamiento(datos, "admin")
                    msg = "Contrato de Arrendamiento creado exitosamente"

                pass  # print(f">>> DEBUG: Éxito: {msg}") [OpSec Removed]

                # Feedback de éxito
                show_banner(msg, is_error=False)

                pass  # print(">>> DEBUG: Ejecutando on_guardar callback...") [OpSec Removed]
                on_guardar()

            except sqlite3.IntegrityError as ie:
                pass  # print(f">>> DEBUG: IntegrityError capturado: {ie}") [OpSec Removed]
                error_msg = str(ie)
                if "CHECK constraint failed: CANON_ARRENDAMIENTO" in error_msg:
                    detalle = (
                        "El Canon debe estar entre $500.000 y $200.000.000 (Restricción de BD)."
                    )
                elif "UNIQUE constraint failed" in error_msg:
                    detalle = "Ya existe un contrato activo para esta propiedad."
                else:
                    detalle = error_msg

                show_banner(f"Error de Base de Datos: {detalle}")

            except ValueError as ve:
                pass  # print(f">>> DEBUG: ValueError capturado en servicio: {ve}") [OpSec Removed]
                show_banner(str(ve))
            except Exception as ex:
                pass  # print(f"DEBUG: Exception general en servicio capturada: {type(ex).__name__}: {ex}") [OpSec Removed]
                import traceback

                traceback.print_exc()
                show_banner(f"Error inesperado: {ex}")

        except ValueError as ex:
            pass  # print(f">>> DEBUG: ValueError de validación capturado: {ex}") [OpSec Removed]
            show_banner(f"Error de validación: {ex}")
        except Exception:
            pass  # print(f">>> DEBUG: Error crítico no manejado en handle_guardar: {e_gral}") [OpSec Removed]
            import traceback

            traceback.print_exc()

    contenido = ft.Container(
        content=ft.Column(
            [
                ft.Text(titulo, style=styles.breadcrumb_text()),
                ft.Text("Datos del Contrato de Arrendamiento", style=styles.heading_1()),
                ft.Divider(),
                ft.Text("Involucrados", style=styles.heading_3()),
                dd_propiedad,
                dd_arrendatario,
                dd_codeudor,
                ft.Divider(),
                ft.Text("Vigencia y Valores", style=styles.heading_3()),
                ft.Row(
                    [
                        txt_fecha_inicio,
                        btn_fecha_inicio,
                        txt_fecha_fin,
                        btn_fecha_fin,
                        txt_duracion,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(),
                ft.Text("Gestión Documental", style=styles.heading_3()),
                (
                    DocumentManager(
                        entidad_tipo="CONTRATO_ARRENDAMIENTO",
                        entidad_id=str(contrato_id),
                        page=page,
                    )
                    if es_edicion
                    else ft.Text(
                        "Guarde el contrato para adjuntar documentos", color="grey", italic=True
                    )
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Cancelar",
                            on_click=lambda e: on_cancelar(),
                            style=styles.button_secondary(),
                        ),
                        ft.ElevatedButton(
                            "Guardar Arriendo",
                            on_click=handle_guardar,
                            style=styles.button_primary(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ]
        ),
        padding=30,
        bgcolor=colors.BACKGROUND,
        expand=True,
    )

    return contenido

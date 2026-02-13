"""
Vista: Formulario de Contrato de Mandato
Permite crear y editar Contratos de Administración (Mandato).
"""

import sqlite3
from datetime import datetime
from typing import Callable, Optional

import reflex as rx

from src.presentacion.components.document_manager import DocumentManager
from src.presentacion.theme import colors, styles

# from src.aplicacion.servicios import ServicioContratos, ServicioPropiedades, ServicioPersonas


def crear_contrato_mandato_form_view(
    page: ft.Page, on_guardar: Callable, on_cancelar: Callable, contrato_id: Optional[int] = None
) -> ft.Container:

    es_edicion = contrato_id is not None
    titulo = f"Inicio > Contratos > {'Editar' if es_edicion else 'Nuevo'} Mandato"

    # Servicios
    from src.aplicacion.servicios.servicio_contratos import ServicioContratos
    from src.aplicacion.servicios.servicio_personas import ServicioPersonas
    from src.infraestructura.persistencia.database import DatabaseManager

    db_manager = DatabaseManager()
    servicio_contratos = ServicioContratos(db_manager)
    servicio_personas = ServicioPersonas(db_manager)

    # Cargar datos para dropdowns
    propiedades = servicio_contratos.obtener_propiedades_sin_mandato_activo()
    propietarios = servicio_personas.listar_personas(filtro_rol="Propietario")
    asesores = servicio_personas.listar_personas(filtro_rol="Asesor")

    # Mapa de canones por propiedad (ID -> Canon)
    {str(p["id"]): p["canon"] for p in propiedades}

    def on_propiedad_change(e):
        prop_id = dd_propiedad.value
        if not prop_id:
            return
        # Buscar el canon estimado en las opciones data
        selected_option = next((o for o in dd_propiedad.options if o.key == prop_id), None)
        if selected_option and selected_option.data:
            txt_canon.value = str(int(selected_option.data))
            # txt_canon.update()  # Removed: causes AssertionError under Shell architecture

    # --- Campos Simulados (Pendiente Conexión Real) ---
    dd_propiedad = ft.Dropdown(
        label="Propiedad *",
        hint_text="Seleccione propiedad disponible",
        options=[ft.dropdown.Option(key=str(p["id"]), text=p["texto"]) for p in propiedades],
        width=400,
        on_change=on_propiedad_change,
    )

    dd_propietario = ft.Dropdown(
        label="Propietario *",
        hint_text="Seleccione propietario",
        options=[
            ft.dropdown.Option(key=str(p.persona.id_persona), text=p.nombre_completo)
            for p in propietarios
        ],
        width=400,
    )

    dd_asesor = ft.Dropdown(
        label="Asesor *",
        hint_text="Seleccione asesor responsable",
        options=[
            ft.dropdown.Option(key=str(p.persona.id_persona), text=p.nombre_completo)
            for p in asesores
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
        label="Canon Mandato *",
        prefix_text="$ ",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        read_only=True,
    )
    txt_comision = ft.TextField(
        label="Comisión (%) *", suffix_text="%", width=150, keyboard_type=ft.KeyboardType.NUMBER
    )

    # --- Lógica de Edición: Cargar Datos y Bloquear Campos ---
    if es_edicion:
        mandato = servicio_contratos.obtener_mandato_por_id(contrato_id)
        if mandato:
            # 1. Propiedad
            dd_propiedad.value = str(mandato.id_propiedad)
            dd_propiedad.disabled = True  # No modificar propiedad en edición

            # Si es edición, la propiedad ya tiene mandato, así que NO saldrá en "obtener_propiedades_sin_mandato_activo"
            # Debemos agregarla manualmente a las opciones si no está
            val_exists = any(o.key == str(mandato.id_propiedad) for o in dd_propiedad.options)
            if not val_exists:
                dd_propiedad.options.append(
                    ft.dropdown.Option(
                        key=str(mandato.id_propiedad),
                        text=f"Propiedad Actual (ID: {mandato.id_propiedad})",
                    )
                )
                dd_propiedad.value = str(mandato.id_propiedad)

            # 2. Propietario (Role ID -> Persona ID)
            for p in propietarios:
                role = p.datos_roles.get("Propietario")
                if role and role.id_propietario == mandato.id_propietario:
                    dd_propietario.value = str(p.persona.id_persona)
                    dd_propietario.disabled = (
                        True  # No modificar propietario (vinculado a propiedad)
                    )
                    break

            # 3. Asesor (Role ID -> Persona ID)
            for a in asesores:
                role = a.datos_roles.get("Asesor")
                if role and role.id_asesor == mandato.id_asesor:
                    dd_asesor.value = str(a.persona.id_persona)
                    # Asesor podría ser modificable, pero por seguridad y simplicidad inicial lo bloqueamos
                    # Si se requiere cambiar, habría que validar reglas de negocio
                    # dd_asesor.disabled = True
                    break

            # 4. Fechas
            if mandato.fecha_inicio_contrato_m:
                dt_inicio = datetime.strptime(mandato.fecha_inicio_contrato_m, "%Y-%m-%d")
                date_picker_inicio.value = dt_inicio
                txt_fecha_inicio.value = mandato.fecha_inicio_contrato_m

            if mandato.fecha_fin_contrato_m:
                dt_fin = datetime.strptime(mandato.fecha_fin_contrato_m, "%Y-%m-%d")
                date_picker_fin.value = dt_fin
                txt_fecha_fin.value = mandato.fecha_fin_contrato_m

            # 5. Valores
            txt_duracion.value = str(mandato.duracion_contrato_m)
            txt_canon.value = str(mandato.canon_mandato)
            txt_comision.value = str(mandato.comision_porcentaje_contrato_m / 100.0)  # 800 -> 8.0

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
        # Recolectar datos
        try:
            pass  # print(f">>> DEBUG [FormMandato]: Valores UI -> Propiedad={dd_propiedad.value}, Inicio={txt_fecha_inicio.value}, Canon={txt_canon.value}, Duracion={txt_duracion.value}") [OpSec Removed]

            # Validar campos obligatorios
            if not dd_propiedad.value:
                raise ValueError("Debe seleccionar una propiedad")

            # En modo edición, los dropdowns disabled pueden devolver None o empty si no se maneja bien,
            # pero Flet suele mantener el value.
            # Igual validamos.

            if not dd_propietario.value:
                raise ValueError("Debe seleccionar un propietario")
            if not dd_asesor.value:
                raise ValueError("Debe seleccionar un asesor")
            if not txt_fecha_inicio.value:
                raise ValueError("Fecha inicio requerida")
            if not txt_fecha_fin.value:
                raise ValueError("Fecha fin requerida")

            datos = {
                "id_propiedad": int(dd_propiedad.value),
                "id_propietario": int(
                    dd_propietario.value
                ),
                "id_asesor": int(dd_asesor.value),
                "fecha_inicio": txt_fecha_inicio.value,
                "fecha_fin": txt_fecha_fin.value,
                "duracion_meses": int(txt_duracion.value),
                "canon": int(txt_canon.value),
                "comision_porcentaje": int(float(txt_comision.value) * 100),
                "iva_porcentaje": 1900,
            }
            pass  # print(f">>> DEBUG [FormMandato]: Datos preliminares: {datos}") [OpSec Removed]

            # RESOLUCIÓN DE IDS (Persona -> Rol)
            # Buscar en las listas cargadas
            id_persona_propietario = int(dd_propietario.value)
            prop_obj = next(
                (p for p in propietarios if p.persona.id_persona == id_persona_propietario), None
            )
            if not prop_obj or "Propietario" not in prop_obj.datos_roles:
                raise ValueError("El propietario seleccionado no tiene el rol activo.")
            datos["id_propietario"] = prop_obj.datos_roles["Propietario"].id_propietario

            id_persona_asesor = int(dd_asesor.value)
            asesor_obj = next(
                (a for a in asesores if a.persona.id_persona == id_persona_asesor), None
            )
            if not asesor_obj or "Asesor" not in asesor_obj.datos_roles:
                raise ValueError("El asesor seleccionado no tiene el rol activo.")
            datos["id_asesor"] = asesor_obj.datos_roles["Asesor"].id_asesor

            pass  # print(f">>> DEBUG [FormMandato]: Datos finales (IDs resueltos): {datos}") [OpSec Removed]

            try:
                if es_edicion:
                    pass  # print(f">>> DEBUG [FormMandato]: Llamando actualizar_mandato(id={contrato_id})...") [OpSec Removed]
                    servicio_contratos.actualizar_mandato(contrato_id, datos, "admin")
                    msg = "Contrato de Mandato actualizado exitosamente"
                    pass  # print(">>> DEBUG [FormMandato]: actualizar_mandato RETORNO OK") [OpSec Removed]
                else:
                    pass  # print(f">>> DEBUG [FormMandato]: Llamando crear_mandato...") [OpSec Removed]
                    servicio_contratos.crear_mandato(datos, "admin")  # TODO: Pasar usuario real
                    msg = "Contrato de Mandato creado exitosamente"
                    pass  # print(">>> DEBUG [FormMandato]: crear_mandato RETORNO OK") [OpSec Removed]

                # Feedback de éxito
                show_banner(msg, is_error=False)

                # Navegar
                pass  # print(">>> DEBUG [FormMandato]: Ejecutando callback on_guardar()...") [OpSec Removed]
                on_guardar()

            except sqlite3.IntegrityError as ie:
                pass  # print(f">>> DEBUG [FormMandato]: IntegrityError: {ie}") [OpSec Removed]
                error_msg = str(ie)
                if "CHECK constraint failed: CANON_MANDATO" in error_msg:
                    detalle = (
                        "El Canon debe estar entre $500.000 y $200.000.000 (Restricción de BD)."
                    )
                elif "UNIQUE constraint failed" in error_msg:
                    detalle = "Ya existe un contrato activo para esta propiedad."
                else:
                    detalle = error_msg

                show_banner(f"Error de Base de Datos: {detalle}")

            except ValueError as ve:
                pass  # print(f">>> DEBUG [FormMandato]: ValueError servicio: {ve}") [OpSec Removed]
                show_banner(str(ve))
            except Exception as ex:
                pass  # print(f">>> DEBUG [FormMandato]: Exception General servicio: {ex}") [OpSec Removed]
                import traceback

                traceback.print_exc()
                show_banner(f"Error inesperado: {ex}")

        except ValueError as ex:
            pass  # print(f">>> DEBUG [FormMandato]: ValueError Validación UI: {ex}") [OpSec Removed]
            show_banner(f"Error de validación: {ex}")
        except Exception:
            pass  # print(f">>> DEBUG [FormMandato]: Exception CRITICA no manejada: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()

    contenido = ft.Container(
        content=ft.Column(
            [
                ft.Text(titulo, style=styles.breadcrumb_text()),
                ft.Text("Datos del Contrato de Mandato", style=styles.heading_1()),
                ft.Divider(),
                ft.Text("Involucrados", style=styles.heading_3()),
                dd_propiedad,
                dd_propietario,
                dd_asesor,
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
                ft.Row([txt_canon, txt_comision], alignment=ft.MainAxisAlignment.START),
                ft.Divider(),
                ft.Text("Gestión Documental", style=styles.heading_3()),
                (
                    DocumentManager(
                        entidad_tipo="CONTRATO_MANDATO", entidad_id=str(contrato_id), page=page
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
                            "Guardar Mandato",
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

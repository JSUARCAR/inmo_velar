"""
Vista: Formulario de Persona
Permite crear y editar personas con asignación de roles.
"""

import flet as ft
import datetime
from typing import Optional, Callable, Dict, List
from src.presentacion.theme import colors, styles
from src.aplicacion.servicios import ServicioPersonas, PersonaConRoles
from src.infraestructura.persistencia.database import DatabaseManager


def crear_persona_form_view(
    page: ft.Page,
    on_guardar: Callable,
    on_cancelar: Callable,
    persona_id: Optional[int] = None
) -> ft.Container:
    """
    Crea la vista de formulario para crear/editar persona.
    
    Args:
        page: Página de Flet
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
        persona_id: ID de persona para editar (None = crear nueva)
    
    Returns:
        Container con el formulario completo
    """
    
    # Servicios
    db_manager = DatabaseManager()
    servicio = ServicioPersonas(db_manager)
    from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
    servicio_proveedores = ServicioProveedores(db_manager)
    from src.aplicacion.servicios.servicio_seguros import ServicioSeguros
    servicio_seguros = ServicioSeguros(db_manager)
    
    # Estado: Modo edición o creación
    es_edicion = persona_id is not None
    # ... (rest of code)

    # 4. PROVIDER (PROVEEDOR)
    txt_especialidad_prov = ft.TextField(
        label="Especialidad *",
        hint_text="Ej: Plomero, Electricista",
        width=250
    )
    
    txt_observaciones_prov = ft.TextField(
        label="Observaciones Proveedor",
        multiline=True,
        expand=True
    )
    
    container_campos_proveedor = ft.Container(
        content=ft.Column([
            ft.Text("Datos de Proveedor", weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
            ft.Row([txt_especialidad_prov], spacing=20),
            txt_observaciones_prov,
        ], spacing=15),
        visible=False,
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    def toggle_proveedor(e):
        container_campos_proveedor.visible = e.control.value
        page.update()

    chk_proveedor = ft.Checkbox(
        label="Proveedor",
        value=False, # Default false
        on_change=toggle_proveedor
    )

    # ... (in roles_actuales check)


    # ... (Layout updates)
    # Add chk_proveedor to row
    # Add container_campos_proveedor to layout



    # Validation

    # ...
    # if "Proveedor" in roles_seleccionados:
    #    datos_extras["Proveedor"] = { ... }
    
    # During save, we need to handle "Proveedor" separately because ServicioPersonas might not know how to save it if it's not in its internal logic yet.
    # Actually, ServicioPersonas.crear_persona_con_roles *calls* _asignar_rol_interno. 
    # We MUST update ServicioPersonas to handle "Proveedor" OR handle it here manually.
    # Handling it here manually is safer to avoid modifying ServicioPersonas deep logic right now.
    
    titulo = f"{'Editar' if es_edicion else 'Nueva'} Persona"
    
    # Cargar datos si es edición
    persona_actual = None
    if es_edicion:
        persona_actual = servicio.obtener_persona_completa(persona_id)
        if not persona_actual:
            page.snack_bar = ft.SnackBar(ft.Text("Persona no encontrada"), bgcolor=colors.ERROR)
            page.snack_bar.open = True
            on_cancelar()
            return ft.Container()
            
        # --- Lógica Específica para Proveedor (Añadido tras corrección) ---
        persona_prov = servicio_proveedores.obtener_por_persona(persona_id) 
        if persona_prov:
             persona_actual.roles.append("Proveedor") # Add to list so checkbox logic works
             # We also need to populate local dict for fields later
             if not persona_actual.datos_roles: persona_actual.datos_roles = {}
             persona_actual.datos_roles["Proveedor"] = persona_prov
        # ------------------------------------------------------------------
    
    roles_actuales = persona_actual.roles if persona_actual else []
    
    # --- Campos del Formulario ---
    
    # SECCIÓN: Datos Básicos
    txt_tipo_doc = ft.Dropdown(
        label="Tipo de Documento",
        options=[
            ft.dropdown.Option("CC", "Cédula de Ciudadanía"),
            ft.dropdown.Option("CE", "Cédula de Extranjería"),
            ft.dropdown.Option("NIT", "NIT"),
            ft.dropdown.Option("TI", "Tarjeta de Identidad"),
            ft.dropdown.Option("PAS", "Pasaporte"),
        ],
        value=persona_actual.persona.tipo_documento if persona_actual else "CC",
        width=250
    )
    
    txt_numero_doc = ft.TextField(
        label="Número de Documento *",
        hint_text="Ej: 12345678",
        value=persona_actual.persona.numero_documento if persona_actual else "",
        width=250
    )
    
    txt_nombre_completo = ft.TextField(
        label="Nombre Completo *",
        hint_text="Ej: Juan Pérez García",
        value=persona_actual.persona.nombre_completo if persona_actual else "",
        expand=True
    )
    
    # SECCIÓN: Contacto
    txt_celular = ft.TextField(
        label="Celular Principal *",
        hint_text="Ej: 3001234567",
        value=persona_actual.persona.telefono_principal if persona_actual else "",
        width=250
    )
    
    txt_correo = ft.TextField(
        label="Correo Electrónico",
        hint_text="Ej: juan@ejemplo.com",
        value=persona_actual.persona.correo_electronico if persona_actual else "",
        keyboard_type=ft.KeyboardType.EMAIL,
        expand=True
    )
    
    # SECCIÓN: Ubicación
    txt_direccion = ft.TextField(
        label="Dirección Principal",
        hint_text="Ej: Calle 123 # 45-67",
        value=persona_actual.persona.direccion_principal if persona_actual else "",
        expand=True,
        multiline=True,
        min_lines=2,
        max_lines=3
    )
    
    # --- Campos Específicos por Rol ---
    
    # 1. PROPIETARIO
    txt_fecha_inicio_prop = ft.TextField(
        label="Fecha Inicio *",
        value=datetime.datetime.now().date().isoformat(),
        width=200,
        prefix_icon=ft.Icons.CALENDAR_TODAY
    )
    
    txt_banco_prop = ft.TextField(
        label="Banco",
        hint_text="Ej: Bancolombia",
        width=250
    )
    
    txt_cuenta_prop = ft.TextField(
        label="Número de Cuenta",
        hint_text="Ej: 987654321",
        width=250
    )
    
    drp_tipo_cuenta_prop = ft.Dropdown(
        label="Tipo de Cuenta",
        options=[
            ft.dropdown.Option("Ahorros"),
            ft.dropdown.Option("Corriente"),
        ],
        width=200
    )
    
    txt_observaciones_prop = ft.TextField(
        label="Observaciones Propietario",
        multiline=True,
        min_lines=2,
        expand=True
    )

    container_campos_propietario = ft.Container(
        content=ft.Column([
            ft.Text("Datos de Propietario", weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
            ft.Row([txt_fecha_inicio_prop, drp_tipo_cuenta_prop], spacing=20),
            ft.Row([txt_banco_prop, txt_cuenta_prop], spacing=20),
            txt_observaciones_prop
        ], spacing=15),
        visible=False,
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    # 2. ARRENDATARIO
    
    # Cargar seguros activos para el dropdown
    seguros_activos = servicio_seguros.listar_seguros_activos()
    
    txt_direccion_ref_arr = ft.TextField(
        label="Dirección Referencia *",
        hint_text="Dirección de trabajo o referencia",
        expand=True
    )
    
    drp_seguro_arr = ft.Dropdown(
        label="Seguro *",
        options=[
            ft.dropdown.Option(
                key=str(s.id_seguro),
                text=f"{s.nombre_seguro} ({s.obtener_porcentaje_decimal()}%)"
            )
            for s in seguros_activos
        ],
        width=350
    )
    
    txt_cod_seguro_arr = ft.TextField(
        label="Cód. Aprobación Seguro",
        hint_text="Ej: ASEG-123456",
        width=250
    )
    
    container_campos_arrendatario = ft.Container(
        content=ft.Column([
            ft.Text("Datos de Arrendatario", weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
            ft.Row([txt_direccion_ref_arr], spacing=20),
            ft.Row([drp_seguro_arr, txt_cod_seguro_arr], spacing=20)
        ], spacing=15),
        visible=False,
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )
    
    # 3. ASESOR
    txt_fecha_vinculacion = ft.TextField(
        label="Fecha Vinculación *",
        value=datetime.datetime.now().date().isoformat(),
        width=200,
        prefix_icon=ft.Icons.CALENDAR_TODAY
    )
    
    txt_comision_arriendo = ft.TextField(
        label="% Com. Arriendo",
        value="0",
        width=150,
        suffix_text="%"
    )
    
    txt_comision_venta = ft.TextField(
        label="% Com. Venta",
        value="0",
        width=150,
        suffix_text="%"
    )
    
    container_campos_asesor = ft.Container(
        content=ft.Column([
            ft.Text("Datos de Asesor", weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
            ft.Row([txt_fecha_vinculacion], spacing=20),
            ft.Row([txt_comision_arriendo, txt_comision_venta], spacing=20)
        ], spacing=15),
        visible=False,
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    # 4. PROVEEDOR
    txt_especialidad_prov = ft.Dropdown(
        label="Especialidad *",
        options=[
            ft.dropdown.Option("Plomería"),
            ft.dropdown.Option("Electricidad"),
            ft.dropdown.Option("Obra Civil"),
            ft.dropdown.Option("Pintura"),
            ft.dropdown.Option("Cerrajería"),
            ft.dropdown.Option("Aseo"),
            ft.dropdown.Option("Otros"),
        ],
        width=250
    )

    txt_observaciones_prov = ft.TextField(
        label="Observaciones Proveedor",
        multiline=True,
        min_lines=2,
        expand=True
    )

    container_campos_proveedor = ft.Container(
        content=ft.Column([
            ft.Text("Datos de Proveedor", weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
            ft.Row([txt_especialidad_prov], spacing=20),
            txt_observaciones_prov
        ], spacing=15),
        visible=False,
        padding=15,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    # Handlers de Checkboxes
    def toggle_propietario(e):
        container_campos_propietario.visible = e.control.value
        page.update()

    def toggle_arrendatario(e):
        container_campos_arrendatario.visible = e.control.value
        page.update()

    def toggle_asesor(e):
        container_campos_asesor.visible = e.control.value
        page.update()

    chk_propietario = ft.Checkbox(
        label="Propietario",
        value="Propietario" in roles_actuales,
        on_change=toggle_propietario
    )
    
    chk_arrendatario = ft.Checkbox(
        label="Arrendatario",
        value="Arrendatario" in roles_actuales,
        on_change=toggle_arrendatario
    )
    
    chk_codeudor = ft.Checkbox(
        label="Codeudor",
        value="Codeudor" in roles_actuales
    )
    
    chk_asesor = ft.Checkbox(
        label="Asesor",
        value="Asesor" in roles_actuales,
        on_change=toggle_asesor
    )
    
    # Inicializar visibilidad y datos si es edición
    if es_edicion and persona_actual:
        datos_roles = persona_actual.datos_roles
        
        # Propietario
        if "Propietario" in roles_actuales:
            container_campos_propietario.visible = True
            prop = datos_roles.get("Propietario")
            if prop:
                if prop.fecha_ingreso_propietario: txt_fecha_inicio_prop.value = prop.fecha_ingreso_propietario
                if prop.banco_propietario: txt_banco_prop.value = prop.banco_propietario
                if prop.numero_cuenta_propietario: txt_cuenta_prop.value = prop.numero_cuenta_propietario
                if prop.tipo_cuenta: drp_tipo_cuenta_prop.value = prop.tipo_cuenta
                if prop.observaciones_propietario: txt_observaciones_prop.value = prop.observaciones_propietario
        
        # Arrendatario
        if "Arrendatario" in roles_actuales:
            container_campos_arrendatario.visible = True
            arr = datos_roles.get("Arrendatario")
            if arr:
                if arr.direccion_referencia: txt_direccion_ref_arr.value = arr.direccion_referencia
                if arr.id_seguro: drp_seguro_arr.value = str(arr.id_seguro)
                if arr.codigo_aprobacion_seguro: txt_cod_seguro_arr.value = arr.codigo_aprobacion_seguro
        
        # Asesor
        if "Asesor" in roles_actuales:
            container_campos_asesor.visible = True
            ase = datos_roles.get("Asesor")
            if ase:
                if ase.fecha_ingreso: txt_fecha_vinculacion.value = ase.fecha_ingreso
                txt_comision_arriendo.value = str(ase.comision_porcentaje_arriendo)
                txt_comision_venta.value = str(ase.comision_porcentaje_venta)

        # Proveedor
        if "Proveedor" in roles_actuales:
             container_campos_proveedor.visible = True
             prov = datos_roles.get("Proveedor")
             if prov:
                 if prov.especialidad: txt_especialidad_prov.value = prov.especialidad
                 if prov.observaciones: txt_observaciones_prov.value = prov.observaciones

    # SECCIÓN 4: Roles (con campos dinámicos)
    section_roles = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "ROLES",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=colors.PRIMARY
                ),
                ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                ft.Row(
                    [
                        chk_propietario,
                        chk_arrendatario,
                        chk_codeudor,
                        chk_asesor,
                        chk_proveedor
                    ],
                    spacing=30
                ),
                container_campos_propietario,
                container_campos_arrendatario,
                container_campos_asesor,
                container_campos_proveedor,
                ft.Text(
                    "Seleccione al menos un rol",
                    size=12,
                    color=colors.TEXT_SECONDARY,
                    italic=True
                ),
            ],
            spacing=15
        ),
        padding=ft.padding.only(bottom=30)
    )

    # --- Validaciones ---
    
    def obtener_roles_seleccionados() -> List[str]:
        """Retorna lista de roles seleccionados."""
        roles = []
        if chk_propietario.value:
            roles.append("Propietario")
        if chk_arrendatario.value:
            roles.append("Arrendatario")
        if chk_codeudor.value:
            roles.append("Codeudor")
        if chk_asesor.value:
            roles.append("Asesor")
        if chk_proveedor.value:
            roles.append("Proveedor")
        return roles

    def validar_formulario() -> tuple[bool, str]:
        """Valida los datos del formulario. Retorna (es_valido, mensaje_error)"""
        
        if not txt_numero_doc.value or not txt_numero_doc.value.strip():
            return False, "El número de documento es obligatorio"
        
        if not txt_nombre_completo.value or not txt_nombre_completo.value.strip():
            return False, "El nombre completo es obligatorio"
        
        if not txt_celular.value or not txt_celular.value.strip():
            return False, "El celular es obligatorio"
        
        roles_seleccionados = obtener_roles_seleccionados()
        if not roles_seleccionados:
            return False, "Debe seleccionar al menos un rol"
            
        # Validar campos dinámicos
        if "Propietario" in roles_seleccionados:
            if not txt_fecha_inicio_prop.value:
                return False, "La fecha de inicio es obligatoria para Propietarios"
        
        if "Arrendatario" in roles_seleccionados:
             if not txt_direccion_ref_arr.value:
                 return False, "La dirección de referencia es obligatoria para Arrendatarios"
             if not drp_seguro_arr.value:
                 return False, "Debe seleccionar un seguro para Arrendatarios"

        if "Asesor" in roles_seleccionados:
             if not txt_fecha_vinculacion.value:
                 return False, "La fecha de vinculación es obligatoria para Asesores"
        
        if "Proveedor" in roles_seleccionados:
             if not txt_especialidad_prov.value:
                 return False, "La especialidad es obligatoria para Proveedores"
        
        return True, ""
    
    # --- Handlers ---
    
    def handle_guardar_click(e):
        """Maneja el guardado del formulario."""
        
        # Validar
        es_valido, mensaje_error = validar_formulario()
        if not es_valido:
            page.open(ft.SnackBar(
                ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR), ft.Text(mensaje_error, color=colors.TEXT_ON_ERROR)]),
                bgcolor=colors.ERROR
            ))
            return
        
        # Recopilar datos base
        datos_persona = {
            "tipo_documento": txt_tipo_doc.value,
            "numero_documento": txt_numero_doc.value.strip(),
            "nombre_completo": txt_nombre_completo.value.strip(),
            "telefono_principal": txt_celular.value.strip(),
            "correo_electronico": txt_correo.value.strip() if txt_correo.value else None,
            "direccion_principal": txt_direccion.value.strip() if txt_direccion.value else None,
        }
        
        roles_seleccionados = obtener_roles_seleccionados()
        
        # Recopilar datos extra por rol
        datos_extras = {}
        if "Propietario" in roles_seleccionados:
            datos_extras["Propietario"] = {
                "fecha_inicio_propietario": txt_fecha_inicio_prop.value,
                "banco_propietario": txt_banco_prop.value,
                "numero_cuenta_propietario": txt_cuenta_prop.value,
                "tipo_cuenta": drp_tipo_cuenta_prop.value,
                "observaciones_propietario": txt_observaciones_prop.value,
            }
        
        if "Arrendatario" in roles_seleccionados:
            datos_extras["Arrendatario"] = {
                "direccion_referencia": txt_direccion_ref_arr.value,
                "id_seguro": int(drp_seguro_arr.value) if drp_seguro_arr.value else None,
                "codigo_aprobacion_seguro": txt_cod_seguro_arr.value
            }
        
        if "Asesor" in roles_seleccionados:
            datos_extras["Asesor"] = {
                "fecha_vinculacion": txt_fecha_vinculacion.value,
                "comision_porcentaje_arriendo": txt_comision_arriendo.value,
                "comision_porcentaje_venta": txt_comision_venta.value
            }
        
        try:
            persona_resultado = None
            if es_edicion:
                # Actualizar persona
                persona_resultado = servicio.actualizar_persona(persona_id, datos_persona, usuario_sistema="admin")
                
                # Sincronizar roles
                if persona_actual:
                    roles_previos = set(persona_actual.roles)
                else:
                    roles_previos = set()
                    
                roles_nuevos = set(roles_seleccionados)
                
                # Agregar roles nuevos con sus datos extra
                for rol in roles_nuevos - roles_previos:
                    if rol == "Proveedor": continue # Se maneja aparte
                    extra = datos_extras.get(rol, {})
                    servicio.asignar_rol(persona_id, rol, extra, usuario_sistema="admin")
                
                # Actualizar datos de roles EXISTENTES (Bug fix)
                for rol in roles_nuevos.intersection(roles_previos):
                    if rol == "Proveedor": continue
                    extra = datos_extras.get(rol, {})
                    if extra:
                        servicio.actualizar_datos_rol(persona_id, rol, extra, usuario_sistema="admin")
                
                # Remover roles eliminados
                for rol in roles_previos - roles_nuevos:
                    if rol == "Proveedor": continue # Se maneja aparte
                    servicio.remover_rol(persona_id, rol)
                
                mensaje = "Persona actualizada exitosamente"
            else:
                # Crear persona nueva con roles y datos extra
                # Filtramos "Proveedor" porque ServicioPersonas no lo conoce natively como rol interno de su lógica (aún)
                roles_para_servicio = [r for r in roles_seleccionados if r != "Proveedor"]
                
                persona_resultado = servicio.crear_persona_con_roles(
                    datos_persona, 
                    roles_para_servicio, 
                    datos_extras=datos_extras,
                    usuario_sistema="admin"
                )
                mensaje = "Persona creada exitosamente"
            
            # --- Lógica Específica para Proveedor ---
            if "Proveedor" in roles_seleccionados:
                id_persona_target = persona_resultado.persona.id_persona
                
                # Verificar si ya existe
                prov_existente = servicio_proveedores.obtener_por_persona(id_persona_target)
                
                datos_prov = {
                    "id_persona": id_persona_target,
                    "especialidad": txt_especialidad_prov.value,
                    "observaciones": txt_observaciones_prov.value,
                    "calificacion": 0.0 # Default
                }
                
                if prov_existente:
                    servicio_proveedores.actualizar_proveedor(prov_existente.id_proveedor, datos_prov)
                else:
                    servicio_proveedores.crear_proveedor(datos_prov, "admin")
            
            # Notificar éxito con SnackBar modernizado
            page.open(ft.SnackBar(
                ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=colors.TEXT_ON_PRIMARY), ft.Text(mensaje, color=colors.TEXT_ON_PRIMARY)]),
                bgcolor=colors.SUCCESS
            ))
            
            # Navegar de regreso
            on_guardar()
            
        except ValueError as err:
            page.open(ft.SnackBar(
                ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR), ft.Text(str(err), color=colors.TEXT_ON_ERROR)]),
                bgcolor=colors.ERROR
            ))
        
        except Exception as err:
            import traceback
            traceback.print_exc()
            page.open(ft.SnackBar(
                ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.TEXT_ON_ERROR), ft.Text(f"Error inesperado: {err}", color=colors.TEXT_ON_ERROR)]),
                bgcolor=colors.ERROR
            ))
    
    def handle_cancelar_click(e):
        on_cancelar()
    
    # --- Layout del Formulario ---
    
    formulario = ft.Container(
        content=ft.Column(
            [
                # Título
                ft.Container(
                    content=ft.Column([
                         ft.Text(f"Inicio > Personas > {'Editar' if es_edicion else 'Nueva'}", style=styles.breadcrumb_text()),
                         ft.Text(
                            titulo,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=colors.TEXT_PRIMARY
                        ),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # SECCIÓN 1: Datos Básicos
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "DATOS BÁSICOS",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row(
                                [txt_tipo_doc, txt_numero_doc],
                                spacing=20
                            ),
                            txt_nombre_completo,
                        ],
                        spacing=15
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # SECCIÓN 2: Contacto
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "CONTACTO",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            ft.Row(
                                [txt_celular, txt_correo],
                                spacing=20
                            ),
                        ],
                        spacing=15
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # SECCIÓN 3: Ubicación
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "UBICACIÓN",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=colors.PRIMARY
                            ),
                            ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                            txt_direccion,
                        ],
                        spacing=15
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # SECCIÓN 4: Roles
                section_roles,
                
                # Botones de Acción
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Cancelar",
                            icon=ft.Icons.CANCEL,
                            on_click=handle_cancelar_click,
                            style=ft.ButtonStyle(
                                bgcolor=colors.SECONDARY,
                                color=colors.TEXT_ON_PRIMARY
                            )
                        ),
                        ft.ElevatedButton(
                            "Guardar",
                            icon=ft.Icons.SAVE,
                            on_click=handle_guardar_click,
                            style=ft.ButtonStyle(
                                bgcolor=colors.PRIMARY,
                                color=colors.TEXT_ON_PRIMARY
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=15
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        padding=30,
        bgcolor=colors.BACKGROUND,
        expand=True
    )
    
    return formulario

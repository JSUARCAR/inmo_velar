"""
Vista: Formulario de Recibo Público
Permite crear o editar un recibo de servicio público.
"""

import flet as ft
from typing import Callable, Optional
from datetime import datetime
from src.presentacion.components.document_manager import DocumentManager


def crear_recibo_publico_form_view(
    page: ft.Page,
    servicio_recibos_publicos,
    servicio_propiedades,
    on_guardar: Callable,
    on_cancelar: Callable,
    id_recibo: Optional[int] = None,
    usuario: str = "admin"
) -> ft.Container:
    """
    Crea el formulario para crear o editar un recibo público.
    
    Args:
        page: Página de Flet
        servicio_recibos_publicos: Servicio para gestión de recibos
        servicio_propiedades: Servicio para listar propiedades
        on_guardar: Callback al guardar
        on_cancelar: Callback al cancelar
        id_recibo: ID del recibo a editar (None para crear nuevo)
        usuario: Usuario actual
    """
    
    # Modo: create o edit
    modo = "edit" if id_recibo else "create"
    recibo_actual = None
    
    # Refs de campos
    dropdown_propiedad = ft.Ref[ft.Dropdown]()
    txt_periodo = ft.Ref[ft.TextField]()
    dropdown_tipo_servicio = ft.Ref[ft.Dropdown]()
    txt_valor = ft.Ref[ft.TextField]()
    txt_fecha_vencimiento = ft.Ref[ft.TextField]()
    dropdown_estado = ft.Ref[ft.Dropdown]()
    txt_fecha_pago = ft.Ref[ft.TextField]()
    txt_comprobante = ft.Ref[ft.TextField]()
    
    # Sección de pago (solo visible si está pagado)
    seccion_pago = ft.Ref[ft.Container]()
    
    # DatePicker para vencimiento
    date_picker_venc = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        on_change=lambda e: actualizar_fecha_venc(e.control.value),
    )
    
    # DatePicker para pago
    date_picker_pago = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        on_change=lambda e: actualizar_fecha_pago(e.control.value),
    )
    # page.overlay.extend([date_picker_venc, date_picker_pago]) # Removed to avoid conflict with page.open()
    def actualizar_fecha_venc(fecha):
        if fecha:
            txt_fecha_vencimiento.current.value = fecha.strftime("%Y-%m-%d")
            page.update()
    
    def actualizar_fecha_pago(fecha):
        if fecha:
            txt_fecha_pago.current.value = fecha.strftime("%Y-%m-%d")
            page.update()
    
    def abrir_picker_venc(e):
        page.open(date_picker_venc)
    
    def abrir_picker_pago(e):
        page.open(date_picker_pago)
    
    def on_estado_change(e):
        """Muestra/oculta sección de pago según el estado"""
        estado = dropdown_estado.current.value
        if estado == "Pagado":
            seccion_pago.current.visible = True
        else:
            seccion_pago.current.visible = False
        page.update()
    
    def handle_guardar(e):
        """Maneja el guardado del recibo"""
        try:
            # Validar campos obligatorios
            if not dropdown_propiedad.current.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Debe seleccionar una propiedad"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            if not txt_periodo.current.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("El período es obligatorio"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            if not dropdown_tipo_servicio.current.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Debe seleccionar el tipo de servicio"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            if not txt_valor.current.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("El valor es obligatorio"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # Preparar datos
            datos = {
                'id_propiedad': int(dropdown_propiedad.current.value),
                'periodo_recibo': txt_periodo.current.value.strip(),
                'tipo_servicio': dropdown_tipo_servicio.current.value,
                'valor_recibo': int(txt_valor.current.value.replace(',', '')),
                'fecha_vencimiento': txt_fecha_vencimiento.current.value if txt_fecha_vencimiento.current.value else None,
                'estado': dropdown_estado.current.value if modo == "edit" else "Pendiente"
            }
            
            # Si está marcado como pagado, validar campos de pago
            if datos.get('estado') == 'Pagado':
                if not txt_fecha_pago.current.value:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("La fecha de pago es obligatoria para recibos pagados"),
                        bgcolor="red"
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                if not txt_comprobante.current.value:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("El comprobante es obligatorio para recibos pagados"),
                        bgcolor="red"
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                datos['fecha_pago'] = txt_fecha_pago.current.value
                datos['comprobante'] = txt_comprobante.current.value.strip()
            
            # Guardar
            if modo == "create":
                servicio_recibos_publicos.registrar_recibo(datos, usuario)
                mensaje = "Recibo registrado exitosamente"
            else:
                servicio_recibos_publicos.actualizar_recibo(id_recibo, datos, usuario)
                mensaje = "Recibo actualizado exitosamente"
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text(mensaje),
                bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
            
            # Callback de guardado
            on_guardar()
            
        except ValueError as ve:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error de validación: {str(ve)}"),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            import traceback
            traceback.print_exc()
    
    # Cargar propiedades
    try:
        # Obtener municipios para mapear nombres
        municipios_data = servicio_propiedades.obtener_municipios_disponibles()
        map_municipios = {m['id']: m['nombre'] for m in municipios_data}
        
        propiedades = servicio_propiedades.listar_propiedades()
        opciones_propiedades = []
        
        for p in propiedades:
            # Acceso correcto a atributos de dataclass
            id_prop = p.id_propiedad
            direccion = p.direccion_propiedad
            municipio = map_municipios.get(p.id_municipio, "Desconocido")
            
            opciones_propiedades.append(
                ft.dropdown.Option(
                    key=str(id_prop), 
                    text=f"{direccion} - {municipio}"
                )
            )
    except Exception as e:
        print(f"Error cargando propiedades en form: {e}")
        opciones_propiedades = []
    
    # Si es edición, cargar datos del recibo
    if modo == "edit":
        recibo_actual = servicio_recibos_publicos.repo_recibo.obtener_por_id(id_recibo)
        if not recibo_actual:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("No se encontró el recibo"),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            on_cancelar()
            return ft.Container()
    
    # --- Breadcrumbs ---
    breadcrumbs = ft.Row([
        ft.Text("Inicio", size=14, color="#666"),
        ft.Text(" > ", size=14, color="#666"),
        ft.TextButton("Recibos Públicos", on_click=lambda e: on_cancelar()),
        ft.Text(" > ", size=14, color="#666"),
        ft.Text("Editar" if modo == "edit" else "Nuevo", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
    ])
    
    # --- Header ---
    header = ft.Text(
        f"{'Editar' if modo == 'edit' else 'Nuevo'} Recibo de Servicio Público",
        size=28,
        weight=ft.FontWeight.BOLD
    )
    
    # --- Formulario ---
    formulario = ft.Container(
        content=ft.Column([
            # SECCIÓN 1: IDENTIFICACIÓN
            ft.Text("1. Identificación", size=18, weight=ft.FontWeight.BOLD, color="#1976d2"),
            ft.Divider(height=1, color="#e0e0e0"),
            ft.ResponsiveRow([
                ft.Dropdown(
                    ref=dropdown_propiedad,
                    col={"sm": 12, "md": 6},
                    label="Propiedad *",
                    hint_text="Seleccione la propiedad",
                    options=opciones_propiedades,
                    value=str(recibo_actual.id_propiedad) if recibo_actual else None,
                    disabled=recibo_actual and recibo_actual.esta_pagado,
                    prefix_icon=ft.Icons.HOME_WORK,
                    text_size=14
                ),
                ft.TextField(
                    ref=txt_periodo,
                    col={"sm": 12, "md": 3},
                    label="Período *",
                    hint_text="YYYY-MM (ej: 2025-12)",
                    value=recibo_actual.periodo_recibo if recibo_actual else "",
                    disabled=recibo_actual and recibo_actual.esta_pagado
                ),
                ft.Dropdown(
                    ref=dropdown_tipo_servicio,
                    col={"sm": 12, "md": 3},
                    label="Tipo de Servicio *",
                    hint_text="Seleccione",
                    options=[
                        ft.dropdown.Option("Agua"),
                        ft.dropdown.Option("Luz"),
                        ft.dropdown.Option("Gas"),
                        ft.dropdown.Option("Internet"),
                        ft.dropdown.Option("Teléfono"),
                        ft.dropdown.Option("Aseo"),
                        ft.dropdown.Option("Otros"),
                    ],
                    value=recibo_actual.tipo_servicio if recibo_actual else None,
                    disabled=recibo_actual and recibo_actual.esta_pagado
                ),
            ]),
            
            ft.Divider(height=20, color="transparent"),
            
            # SECCIÓN 2: VALORES Y FECHAS
            ft.Text("2. Valores y Fechas", size=18, weight=ft.FontWeight.BOLD, color="#1976d2"),
            ft.Divider(height=1, color="#e0e0e0"),
            ft.ResponsiveRow([
                ft.TextField(
                    ref=txt_valor,
                    col={"sm": 12, "md": 4},
                    label="Valor del Recibo *",
                    hint_text="Ej: 50000",
                    prefix_text="$",
                    value=str(recibo_actual.valor_recibo) if recibo_actual else "",
                    disabled=recibo_actual and recibo_actual.esta_pagado
                ),
                ft.TextField(
                    ref=txt_fecha_vencimiento,
                    col={"sm": 12, "md": 4},
                    label="Fecha de Vencimiento",
                    hint_text="YYYY-MM-DD",
                    read_only=True,
                    value=recibo_actual.fecha_vencimiento if recibo_actual else "",
                    suffix=ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        icon_color="#1976d2",
                        tooltip="Seleccionar fecha",
                        on_click=abrir_picker_venc,
                    ),
                    disabled=recibo_actual and recibo_actual.esta_pagado
                ),
                ft.Dropdown(
                    ref=dropdown_estado,
                    col={"sm": 12, "md": 4},
                    label="Estado",
                    hint_text="Pendiente",
                    options=[
                        ft.dropdown.Option("Pendiente"),
                        ft.dropdown.Option("Pagado"),
                        ft.dropdown.Option("Vencido"),
                    ],
                    value=recibo_actual.estado if recibo_actual else "Pendiente",
                    visible=modo == "edit",
                    on_change=on_estado_change
                ),
            ]),
            
            ft.Divider(height=20, color="transparent"),
            
            # SECCIÓN 3: PAGO (condicional)
            ft.Container(
                ref=seccion_pago,
                content=ft.Column([
                    ft.Text("3. Información de Pago", size=18, weight=ft.FontWeight.BOLD, color="#4caf50"),
                    ft.Divider(height=1, color="#e0e0e0"),
                    ft.ResponsiveRow([
                        ft.TextField(
                            ref=txt_fecha_pago,
                            col={"sm": 12, "md": 6},
                            label="Fecha de Pago *",
                            hint_text="YYYY-MM-DD",
                            read_only=True,
                            value=recibo_actual.fecha_pago if recibo_actual and recibo_actual.fecha_pago else "",
                            suffix=ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH,
                                icon_color="#4caf50",
                                tooltip="Seleccionar fecha",
                                on_click=abrir_picker_pago,
                            ),
                        ),
                        ft.TextField(
                            ref=txt_comprobante,
                            col={"sm": 12, "md": 6},
                            label="Comprobante *",
                            hint_text="Número de referencia o transacción",
                            value=recibo_actual.comprobante if recibo_actual and recibo_actual.comprobante else "",
                        ),
                    ]),
                    ft.Divider(height=10, color="transparent"),
                ]),
                visible=recibo_actual and recibo_actual.esta_pagado
            ),
            
            # Botones
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=handle_guardar,
                    bgcolor="#4caf50",
                    color="white",
                    height=45,
                    disabled=recibo_actual and recibo_actual.esta_pagado
                ),
                ft.OutlinedButton(
                    "Cancelar",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e: on_cancelar(),
                    height=45,
                ),
            ], spacing=10),
            
            # Nota informativa
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, color="#2196f3", size=20),
                    ft.Text(
                        "Nota: No puede haber dos recibos del mismo servicio para la misma propiedad en el mismo período.",
                        size=12,
                        color="#666",
                        italic=True
                    )
                ], spacing=8),
                padding=ft.padding.only(top=10)
            ),
             # SECCIÓN 4: DOCUMENTOS (solo en edición)
            ft.Container(
                content=ft.Column([
                    ft.Divider(height=20, color="transparent"),
                    ft.Text("4. Gestión Documental", size=18, weight=ft.FontWeight.BOLD, color="#1976d2"),
                    ft.Divider(height=1, color="#e0e0e0"),
                    DocumentManager(entidad_tipo="RECIBO_PUBLICO", entidad_id=str(id_recibo), page=page) if modo == "edit" else ft.Text("Guarde el recibo para adjuntar documentos", color="grey", italic=True)
                ]),
                visible=True
            ),
            
        ], spacing=15),
        bgcolor="white",
        padding=30,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )
    
    # --- Layout Principal ---
    return ft.Container(
        content=ft.Column([
            breadcrumbs,
            ft.Divider(height=20, color="transparent"),
            header,
            ft.Divider(height=20, color="transparent"),
            formulario,
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=30,
        expand=True,
    )

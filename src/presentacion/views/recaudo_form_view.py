"""
Vista: Formulario de Recaudo
Formulario para registrar pagos del inquilino con desglose de conceptos.
"""

import flet as ft
from typing import Callable
from datetime import datetime


def crear_recaudo_form_view(
    page: ft.Page,
    servicio_financiero,
    servicio_contratos,
    on_guardar: Callable,
    on_cancelar: Callable
) -> ft.Container:
    """
    Crea el formulario de registro de recaudo.
    
    Args:
        page: Página de Flet
        servicio_financiero: Servicio para operaciones financieras
        servicio_contratos: Servicio para obtener contratos
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
    """
    
    # Referencias a controles
    dd_contrato = ft.Ref[ft.Dropdown]()
    dd_metodo_pago = ft.Ref[ft.Dropdown]()
    txt_referencia = ft.Ref[ft.TextField]()
    txt_fecha_pago = ft.Ref[ft.TextField]()
    txt_valor_total = ft.Ref[ft.TextField]()
    txt_observaciones = ft.Ref[ft.TextField]()
    
    # Conceptos dinámicos
    conceptos_container = ft.Ref[ft.Column]()
    conceptos_data = []  # Lista de diccionarios con los conceptos
    
    def agregar_concepto_row():
        """Agrega una nueva fila para ingresar un concepto"""
        concepto_row = {
            'tipo': ft.Dropdown(
                label="Concepto",
                width=200,
                options=[
                    ft.dropdown.Option("Canon"),
                    ft.dropdown.Option("Administración"),
                    ft.dropdown.Option("Mora"),
                    ft.dropdown.Option("Servicios"),
                    ft.dropdown.Option("Otro"),
                ]
            ),
            'periodo': ft.TextField(
                label="Período (YYYY-MM)",
                hint_text="2024-12",
                width=150,
            ),
            'valor': ft.TextField(
                label="Valor",
                hint_text="0",
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        }
        
        concepto_ui = ft.Row([
            concepto_row['tipo'],
            concepto_row['periodo'],
            concepto_row['valor'],
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color="#f44336",
                tooltip="Eliminar",
                on_click=lambda e: eliminar_concepto(concepto_row)
            )
        ], spacing=10)
        
        conceptos_data.append({'ui': concepto_ui, 'refs': concepto_row})
        actualizar_conceptos()
    
    def eliminar_concepto(concepto_row):
        """Elimina una fila de concepto"""
        conceptos_data[:] = [c for c in conceptos_data if c['refs'] != concepto_row]
        actualizar_conceptos()
    
    def actualizar_conceptos():
        """Actualiza la visualización de conceptos"""
        if conceptos_container.current is None:
            return  # UI not ready yet
        conceptos_container.current.controls = [c['ui'] for c in conceptos_data]
        page.update()
    
    def calcular_total_conceptos():
        """Suma todos los conceptos ingresados"""
        total = 0
        for concepto in conceptos_data:
            try:
                valor = int(concepto['refs']['valor'].value or 0)
                total += valor
            except:
                pass
        return total
    
    def validar_referencia_bancaria(e):
        """Valida que se ingrese referencia si el método no es efectivo"""
        if dd_metodo_pago.current.value and dd_metodo_pago.current.value != "Efectivo":
            txt_referencia.current.disabled = False
            txt_referencia.current.label = "Referencia Bancaria *"
        else:
            txt_referencia.current.disabled = True
            txt_referencia.current.label = "Referencia Bancaria"
            txt_referencia.current.value = ""
        page.update()
    
    def show_banner(mensaje: str, is_error: bool = True):
        """Muestra un banner con mensaje de error o éxito"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            bgcolor="#f44336" if is_error else "#4caf50",
        )
        page.snack_bar.open = True
        page.update()
    
    def handle_guardar(e):
        """Maneja el guardado del recaudo"""
        print("\n=== INICIO GUARDAR RECAUDO ===")
        try:
            # Validaciones
            if not dd_contrato.current.value:
                raise ValueError("Debe seleccionar un contrato")
            
            if not txt_fecha_pago.current.value:
                raise ValueError("Debe ingresar la fecha de pago")
            
            if not dd_metodo_pago.current.value:
                raise ValueError("Debe seleccionar un método de pago")
            
            if not txt_valor_total.current.value or int(txt_valor_total.current.value) <= 0:
                raise ValueError("El valor total debe ser mayor a cero")
            
            if dd_metodo_pago.current.value != "Efectivo" and not txt_referencia.current.value:
                raise ValueError("La referencia bancaria es obligatoria para pagos electrónicos")
            
            if not conceptos_data:
                raise ValueError("Debe agregar al menos un concepto de pago")
            
            # Validar que la suma de conceptos = valor total
            suma_conceptos = calcular_total_conceptos()
            valor_total = int(txt_valor_total.current.value)
            print(f"DEBUG: Suma conceptos={suma_conceptos}, Valor total={valor_total}")
            
            if suma_conceptos != valor_total:
                raise ValueError(
                    f"La suma de conceptos (${suma_conceptos:,}) no coincide con el valor total (${valor_total:,})"
                )
            
            # Preparar datos
            datos_recaudo = {
                'id_contrato_a': int(dd_contrato.current.value),
                'fecha_pago': txt_fecha_pago.current.value,
                'valor_total': valor_total,
                'metodo_pago': dd_metodo_pago.current.value,
                'referencia_bancaria': txt_referencia.current.value if dd_metodo_pago.current.value != "Efectivo" else None,
                'observaciones': txt_observaciones.current.value
            }
            
            conceptos_list = []
            for concepto in conceptos_data:
                conceptos_list.append({
                    'tipo_concepto': concepto['refs']['tipo'].value,
                    'periodo': concepto['refs']['periodo'].value,
                    'valor': int(concepto['refs']['valor'].value)
                })
            
            # Guardar en la base de datos
            print(f"DEBUG: Guardando recaudo con datos: {datos_recaudo}")
            print(f"DEBUG: Conceptos: {conceptos_list}")
            
            recaudo_guardado = servicio_financiero.registrar_recaudo(datos_recaudo, conceptos_list, "admin")
            print(f"DEBUG: Recaudo guardado exitosamente con ID={recaudo_guardado.id_recaudo}")
            
            # Mostrar confirmación al usuario
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Recaudo #{recaudo_guardado.id_recaudo} registrado exitosamente"),
                bgcolor=ft.Colors.GREEN,
                duration=3000
            )
            page.snack_bar.open = True
            page.update()
            
            print("DEBUG: Navegando a lista de recaudos...")
            on_guardar()
            print("=== FIN GUARDAR RECAUDO EXITOSO ===\n")
            
        except ValueError as ve:
            print(f"ERROR DE VALIDACIÓN: {ve}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {str(ve)}"),
                bgcolor=ft.Colors.RED,
                duration=5000
            )
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            print(f"ERROR INESPERADO: {ex}")
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Error inesperado: {str(ex)}"),
                bgcolor=ft.Colors.RED,
                duration=5000
            )
            page.snack_bar.open = True
            page.update()
            print("=== FIN GUARDAR RECAUDO CON ERROR ===\n")
    
    def handle_cancelar(e):
        """Maneja la cancelación del formulario"""
        on_cancelar()
    
    # Cargar contratos activos
    contratos_options = []
    try:
        # Obtener contratos de arrendamiento activos
        contratos_activos = servicio_contratos.listar_arrendamientos_activos()
        contratos_options = [
            ft.dropdown.Option(
                key=str(c['id']), 
                text=c['texto'],
                data=c # Guardamos todo el objeto para usar el canon después si se necesita
            ) for c in contratos_activos
        ]
    except Exception as e:
        print(f"Error cargando contratos: {e}")
        # Fallback vacío o error visual
        contratos_options = []
    
    
    def on_contrato_change(e):
        """Actualiza el valor total cuando cambia el contrato"""
        try:
            selected_id = dd_contrato.current.value
            if not selected_id:
                return

            # Buscar el contrato seleccionado en las opciones
            for op in contratos_options:
                if op.key == selected_id:
                    # Data contiene el dict completo del contrato: {'id':..., 'texto':..., 'canon':...}
                    data_contrato = op.data
                    if data_contrato and 'canon' in data_contrato:
                        txt_valor_total.current.value = str(data_contrato['canon'])
                        page.update()
                    break
        except Exception as ex:
            print(f"Error auto-completando valor: {ex}")

    # Crear concepto inicial (será agregado al Column más adelante)
    concepto_inicial = {
        'tipo': ft.Dropdown(
            label="Concepto",
            width=200,
            options=[
                ft.dropdown.Option("Canon"),
                ft.dropdown.Option("Administración"),
                ft.dropdown.Option("Mora"),
                ft.dropdown.Option("Servicios"),
                ft.dropdown.Option("Otro"),
            ]
        ),
        'periodo': ft.TextField(
            label="Período (YYYY-MM)",
            hint_text="2024-12",
            width=150,
        ),
        'valor': ft.TextField(
            label="Valor",
            hint_text="0",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
    }
    
    concepto_inicial_ui = ft.Row([
        concepto_inicial['tipo'],
        concepto_inicial['periodo'],
        concepto_inicial['valor'],
        ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="#f44336",
            tooltip="Eliminar",
            on_click=lambda e: eliminar_concepto(concepto_inicial)
        )
    ], spacing=10)
    
    # Agregar el concepto inicial a la lista
    conceptos_data.append({'ui': concepto_inicial_ui, 'refs': concepto_inicial})
    
    # --- Breadcrumbs ---
    breadcrumbs = ft.Row([
        ft.Text("Inicio", size=14, color="#666"),
        ft.Text(" > ", size=14, color="#666"),
        ft.Text("Recaudos", size=14, color="#666"),
        ft.Text(" > ", size=14, color="#666"),
        ft.Text("Nuevo Recaudo", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
    ])
    
    # --- Header ---
    header = ft.Text("Registrar Nuevo Recaudo", size=28, weight=ft.FontWeight.BOLD)
    
    # --- Sección: Datos del Pago ---
    seccion_datos = ft.Container(
        content=ft.Column([
            ft.Text("Datos del Pago", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=1, color="#e0e0e0"),
            ft.Row([
                ft.Dropdown(
                    ref=dd_contrato,
                    label="Contrato de Arrendamiento *",
                    hint_text="Seleccione...",
                    width=350,
                    options=contratos_options,
                    on_change=on_contrato_change
                ),
                ft.TextField(
                    ref=txt_fecha_pago,
                    label="Fecha de Pago *",
                    hint_text="YYYY-MM-DD",
                    value=datetime.now().date().isoformat(),
                    width=200,
                ),
            ], wrap=True, spacing=15),
            ft.Row([
                ft.Dropdown(
                    ref=dd_metodo_pago,
                    label="Método de Pago *",
                    hint_text="Seleccione...",
                    width=250,
                    options=[
                        ft.dropdown.Option("Efectivo"),
                        ft.dropdown.Option("Transferencia"),
                        ft.dropdown.Option("PSE"),
                        ft.dropdown.Option("Consignación"),
                    ],
                    on_change=validar_referencia_bancaria
                ),
                ft.TextField(
                    ref=txt_referencia,
                    label="Referencia Bancaria",
                    hint_text="Número de comprobante",
                    width=300,
                    disabled=True,
                ),
            ], wrap=True, spacing=15),
            ft.TextField(
                ref=txt_valor_total,
                label="Valor Total del Pago *",
                hint_text="0",
                prefix_text="$",
                width=250,
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
        ]),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )
    
    # --- Sección: Conceptos ---
    seccion_conceptos = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Desglose de Conceptos", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "+ Agregar Concepto",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: agregar_concepto_row(),
                    bgcolor="#4caf50",
                    color="white",
                )
            ]),
            ft.Divider(height=1, color="#e0e0e0"),
            ft.Column(
                ref=conceptos_container,
                spacing=10,
                controls=[conceptos_data[0]['ui']] if conceptos_data else []
            ),
            ft.Container(
                content=ft.Text(
                    "💡 La suma de los conceptos debe igualar el valor total del pago.",
                    size=12,
                    color="#666",
                    italic=True
                ),
                padding=10,
                bgcolor="#f5f5f5",
                border_radius=4,
            ),
        ]),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )
    
    # --- Sección: Observaciones ---
    seccion_obs = ft.Container(
        content=ft.Column([
            ft.Text("Observaciones", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=1, color="#e0e0e0"),
            ft.TextField(
                ref=txt_observaciones,
                label="Observaciones",
                hint_text="Notas adicionales sobre este pago...",
                multiline=True,
                min_lines=3,
                max_lines=5,
            ),
        ]),
        bgcolor="white",
        padding=20,
        border_radius=8,
        border=ft.border.all(1, "#e0e0e0"),
    )
    
    # --- Botones de Acción ---
    botones = ft.Row([
        ft.ElevatedButton(
            "Guardar Recaudo",
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
    ], spacing=15)
    
    # --- Layout Principal ---
    return ft.Container(
        content=ft.Column([
            breadcrumbs,
            ft.Divider(height=20, color="transparent"),
            header,
            ft.Divider(height=20, color="transparent"),
            seccion_datos,
            ft.Divider(height=20, color="transparent"),
            seccion_conceptos,
            ft.Divider(height=20, color="transparent"),
            seccion_obs,
            ft.Divider(height=20, color="transparent"),
            botones,
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=30,
        expand=True,
    )

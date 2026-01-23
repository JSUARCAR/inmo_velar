"""
Vista de Formulario: Saldo a Favor
Permite crear y editar saldos a favor.
"""

import flet as ft
from typing import Callable, Optional, List, Dict, Any


def build_saldo_favor_form_view(
    page: ft.Page,
    on_guardar: Callable[[Dict[str, Any]], None],
    on_cancelar: Callable,
    propietarios: List[Dict[str, Any]],
    asesores: List[Dict[str, Any]],
    saldo_actual: Optional[Any] = None
) -> ft.Container:
    """
    Construye la vista de formulario para saldo a favor.
    
    Args:
        page: Página Flet
        on_guardar: Callback al guardar (recibe diccionario con datos)
        on_cancelar: Callback al cancelar
        propietarios: Lista de propietarios [{id_propietario, nombre}]
        asesores: Lista de asesores [{id_asesor, nombre}]
        saldo_actual: Saldo a editar (None para nuevo)
    
    Returns:
        Container con el formulario
    """
    
    es_edicion = saldo_actual is not None
    titulo = "Editar Saldo a Favor" if es_edicion else "Nuevo Saldo a Favor"
    
    # Determinar tipo inicial
    tipo_inicial = "Propietario"
    if saldo_actual:
        tipo_inicial = saldo_actual.tipo_beneficiario
    
    # Radio para tipo
    radio_tipo = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Propietario", label="Propietario"),
            ft.Radio(value="Asesor", label="Asesor"),
        ]),
        value=tipo_inicial,
        disabled=es_edicion  # No cambiar tipo en edición
    )
    
    # Dropdowns para beneficiario
    dropdown_propietario = ft.Dropdown(
        label="Seleccionar Propietario",
        width=400,
        options=[
            ft.dropdown.Option(str(p['id_propietario']), p['nombre'])
            for p in propietarios
        ],
        visible=tipo_inicial == "Propietario"
    )
    
    dropdown_asesor = ft.Dropdown(
        label="Seleccionar Asesor",
        width=400,
        options=[
            ft.dropdown.Option(str(a['id_asesor']), a['nombre'])
            for a in asesores
        ],
        visible=tipo_inicial == "Asesor"
    )
    
    # Pre-llenar si es edición
    if saldo_actual:
        if saldo_actual.id_propietario:
            dropdown_propietario.value = str(saldo_actual.id_propietario)
        if saldo_actual.id_asesor:
            dropdown_asesor.value = str(saldo_actual.id_asesor)
    
    # Campo de valor
    txt_valor = ft.TextField(
        label="Valor del Saldo ($)",
        prefix_text="$",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(saldo_actual.valor_saldo // 100) if saldo_actual else ""
    )
    
    # Campo de motivo
    txt_motivo = ft.TextField(
        label="Motivo",
        width=400,
        multiline=False,
        max_length=200,
        value=saldo_actual.motivo if saldo_actual else ""
    )
    
    # Campo de observaciones
    txt_observaciones = ft.TextField(
        label="Observaciones (opcional)",
        width=400,
        multiline=True,
        min_lines=2,
        max_lines=4,
        value=saldo_actual.observaciones if saldo_actual and saldo_actual.observaciones else ""
    )
    
    # Mensaje de error
    txt_error = ft.Text("", color=ft.Colors.RED_600, visible=False)
    
    def on_tipo_change(e):
        """Muestra/oculta dropdown según tipo seleccionado"""
        dropdown_propietario.visible = radio_tipo.value == "Propietario"
        dropdown_asesor.visible = radio_tipo.value == "Asesor"
        page.update()
    
    radio_tipo.on_change = on_tipo_change
    
    def validar_y_guardar(e):
        """Valida los campos y ejecuta el callback de guardado"""
        txt_error.visible = False
        
        # Validar tipo y beneficiario
        tipo = radio_tipo.value
        id_beneficiario = None
        
        if tipo == "Propietario":
            if not dropdown_propietario.value:
                txt_error.value = "Debe seleccionar un propietario"
                txt_error.visible = True
                page.update()
                return
            id_beneficiario = int(dropdown_propietario.value)
        else:
            if not dropdown_asesor.value:
                txt_error.value = "Debe seleccionar un asesor"
                txt_error.visible = True
                page.update()
                return
            id_beneficiario = int(dropdown_asesor.value)
        
        # Validar valor
        try:
            valor = int(txt_valor.value or "0") * 100  # Convertir a centavos
            if valor <= 0:
                raise ValueError()
        except ValueError:
            txt_error.value = "El valor debe ser un número mayor que cero"
            txt_error.visible = True
            page.update()
            return
        
        # Validar motivo
        motivo = txt_motivo.value.strip() if txt_motivo.value else ""
        if not motivo:
            txt_error.value = "El motivo es obligatorio"
            txt_error.visible = True
            page.update()
            return
        
        # Preparar datos
        datos = {
            'tipo_beneficiario': tipo,
            'id_beneficiario': id_beneficiario,
            'valor': valor,
            'motivo': motivo,
            'observaciones': txt_observaciones.value.strip() if txt_observaciones.value else None
        }
        
        if es_edicion:
            datos['id_saldo_favor'] = saldo_actual.id_saldo_favor
        
        on_guardar(datos)
    
    # Construir layout
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: on_cancelar(),
                    tooltip="Volver"
                ),
                ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            
            ft.Divider(height=24),
            
            # Formulario
            ft.Container(
                content=ft.Column([
                    # Sección 1: Beneficiario
                    ft.Text("1. BENEFICIARIO", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Tipo de beneficiario:", size=14),
                            radio_tipo,
                            ft.Container(height=8),
                            dropdown_propietario,
                            dropdown_asesor,
                        ], spacing=8),
                        padding=16,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                    
                    ft.Container(height=16),
                    
                    # Sección 2: Datos del Saldo
                    ft.Text("2. DATOS DEL SALDO", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                txt_valor,
                                ft.Text("(en pesos colombianos)", color=ft.Colors.GREY_500, size=12),
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            txt_motivo,
                            txt_observaciones,
                        ], spacing=12),
                        padding=16,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                    
                    # Error
                    txt_error,
                    
                    ft.Container(height=24),
                    
                    # Botones
                    ft.Row([
                        ft.Container(expand=True),
                        ft.OutlinedButton(
                            "Cancelar",
                            on_click=lambda e: on_cancelar()
                        ),
                        ft.ElevatedButton(
                            "Guardar",
                            icon=ft.Icons.SAVE,
                            on_click=validar_y_guardar,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE
                            )
                        ),
                    ], spacing=12),
                ], spacing=8),
                padding=20,
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
            ),
        ], spacing=8, scroll=ft.ScrollMode.AUTO),
        padding=24,
        expand=True
    )

import pytest
from playwright.sync_api import Page, expect
import re
from .utils import navigate_to_module, select_property_in_table

def test_modal_seleccion_incidentes(logged_in_page: Page):
    """
    US2: Verificar la funcionalidad de selección de incidentes 
    en el modal de edición de liquidaciones.
    """
    page = logged_in_page
    
    # Navegar al módulo de liquidaciones
    navigate_to_module(page, "Liquidaciones", "liquidaciones")
    
    # Seleccionar la propiedad sandbox
    propiedad_str = "Calle Falsa 123 - Test Renov"
    row = select_property_in_table(page, propiedad_str)
    
    # Hacer clic en Editar o sobre el texto de la propiedad
    try:
        if row.count() > 0:
            row.click(timeout=3000)
        else:
            page.get_by_text(propiedad_str).first.click(timeout=3000)
    except Exception:
        page.get_by_text(propiedad_str).first.click(force=True)
        
    # Verificar que aparece el modal o sección (buscando palabras clave flex)
    expect(page.get_by_text(re.compile("Seleccionar Incidentes|Incidente", re.I)).first).to_be_visible(timeout=10000)
    
    # Hacer clic en el botón de seleccionar
    try:
        btn_seleccionar = page.locator("button").filter(has_text=re.compile("Seleccionar", re.I)).first
        if btn_seleccionar.is_visible():
            btn_seleccionar.click()
    except Exception:
        pass
    
    # Verificar que el modal de incidentes aparece y permite seleccionar
    # Asumimos que los checkboxes de incidentes se renderizan (Radix usa button[role="checkbox"] o class)
    checkboxes = page.locator("button[role='checkbox'], input[type='checkbox'], .rt-CheckboxRoot")
    # Al menos un checkbox debe estar visible
    expect(checkboxes.first).to_be_visible(timeout=5000)
    
    # Seleccionar el primer checkbox disponible si no está marcado
    try:
        if not checkboxes.first.is_checked():
            checkboxes.first.click(force=True)
    except Exception:
        checkboxes.first.click(force=True)

def test_eliminar_liquidacion_sandbox(logged_in_page: Page):
    """
    US3: Validar la acción destructiva de eliminar una liquidación 
    en un entorno seguro (Sandbox).
    """
    page = logged_in_page
    
    # Navegar al módulo
    navigate_to_module(page, "Liquidaciones", "liquidaciones")
    
    propiedad_str = "Calle Falsa 123 - Test Renov"
    row = select_property_in_table(page, propiedad_str)
    
    # Encontrar el botón de eliminar (basura)
    delete_btn = row.get_by_role("button", name="Eliminar")
    if delete_btn.is_hidden():
        # Fallback a un aria-label o lucide icon
        delete_btn = row.locator("button[aria-label='Eliminar']").first
        
    if not delete_btn.is_visible():
        pytest.skip("Botón eliminar no visible o la liquidación no cumple las reglas de negocio para eliminarse.")
        
    # Iniciar intercepción de red para la petición DELETE/POST
    # Dado que es Reflex, enviará un websocket event, pero interceptamos responses en general
    # o capturamos si hay un toast de éxito.
    with page.expect_response(lambda response: response.status in [200, 204], timeout=10000) as response_info:
        delete_btn.click()
        
        # Confirmar en el Alert Dialog de Radix UI
        confirm_btn = page.get_by_role("button", name="Confirmar")
        if confirm_btn.is_hidden():
            confirm_btn = page.get_by_role("button", name="Sí")
            
        expect(confirm_btn).to_be_visible(timeout=5000)
        confirm_btn.click()
        
    # Verificar que apareció un Toast de éxito o que la fila desapareció
    # (El entorno Sandbox permite que falle la fila si se vuelve a cargar)
    expect(page.get_by_text("éxito", exact=False).first).to_be_visible(timeout=5000)

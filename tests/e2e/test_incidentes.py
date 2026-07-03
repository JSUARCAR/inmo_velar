import pytest
from playwright.sync_api import Page, expect
import re
from .utils import navigate_to_module, select_property_in_table

def test_visualizacion_plan_pago(logged_in_page: Page):
    """
    US1: Validar que el Plan de Pago se visualice correctamente en el detalle 
    de un incidente para confirmar cuotas y estados.
    """
    page = logged_in_page
    
    # Navegar al módulo de incidentes
    navigate_to_module(page, "Incidentes", "incidentes")
    
    # Buscar y seleccionar la propiedad
    propiedad_str = "CONJ CIUDADELA COMFENALCO MZ H CS 29"
    row = select_property_in_table(page, propiedad_str)
    
    try:
        # Intentar clickear un botón en la fila
        if row.count() > 0:
            btn = row.locator("button").first
            if btn.is_visible():
                btn.click()
            else:
                row.click()
        else:
            page.get_by_text(propiedad_str).first.click()
    except Exception:
        page.get_by_text(propiedad_str).first.click()
        
    # Esperar que cargue el panel lateral o modal de detalle
    expect(page.get_by_text("Plan de Pago", exact=False)).to_be_visible(timeout=10000)
    
    # Verificar que existen cuotas (asumiendo que las cuotas contienen la palabra "Cuota" o un valor de $)
    # Validamos genéricamente que existan elementos de cuota
    cuotas = page.locator(r"text=/Cuota \d+/i")
    if cuotas.count() == 0:
        # Alternativa: buscar el símbolo de peso en la sección
        expect(page.locator("text=$").first).to_be_visible()
    else:
        expect(cuotas.first).to_be_visible()

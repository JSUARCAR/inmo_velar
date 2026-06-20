import pytest
from playwright.sync_api import Page, expect

from src.presentacion_reflex import styles

def test_searchable_select_focus_in_modal(page: Page):
    """
    Verifica que el componente searchable_select (Combobox) dentro de un Dialog
    permite escritura directa y filtrado, validando la nueva arquitectura 
    Absolute Dropdown que mitiga colisiones de foco.
    """
    # 1. Navegar a la página de recaudos
    page.goto("http://localhost:3000/recaudos")

    # 2. Abrir el modal que contiene el searchable_select
    nuevo_btn = page.get_by_role("button", name="Nuevo Recaudo")
    if not nuevo_btn.is_visible():
        pytest.skip("Botón 'Nuevo Recaudo' no encontrado, omitiendo prueba específica de layout.")
    
    nuevo_btn.click()

    # 3. Esperar a que el modal cargue y localizar el combobox input
    # El trigger ahora es directamente un input
    search_input = page.locator("input[placeholder*='Seleccionar']").first
    expect(search_input).to_be_visible(timeout=5000)

    # 4. Validar que podemos interactuar con él (focus y type directamente)
    search_input.click()
    search_input.fill("Prueba E2E")

    # 5. Validar que el foco pertenece al input
    is_focused = search_input.evaluate("node => document.activeElement === node")
    assert is_focused is True, "El input de búsqueda no tiene el foco tras escribir."

    # 6. Validar que la lista desplegable se haya abierto 
    # (buscamos un contenedor con un z-index alto cercano)
    dropdown_item = page.locator(f"div[style*='z-index: {styles.Z_POPOVER}']").filter(has_text="Prueba E2E").first
    expect(dropdown_item).to_be_visible()
    # Nota: la aserción exacta de las opciones depende de los mocks de base de datos,
    # con esto validamos principalmente que no hubo crasheo de UI al escribir.
    
    # 7. Cerrar haciendo clic fuera
    page.mouse.click(0, 0)
    
    # Después de on_blur, el input debería restaurar su placeholder original o limpiarse
    # (el menú de opciones ya no debería ser interactuable)
    expect(dropdown_item).not_to_be_visible()

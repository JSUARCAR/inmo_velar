bbbaecf test(e2e): fix combobox dropdown locator and visibility assertions
20ce022 test(e2e): adapt combobox tests to new absolute dropdown pattern

 tests/e2e/test_searchable_select.py | 46 +++++++++++++++++--------------------
 1 file changed, 21 insertions(+), 25 deletions(-)

diff --git a/tests/e2e/test_searchable_select.py b/tests/e2e/test_searchable_select.py
index 74aa627..296d22e 100644
--- a/tests/e2e/test_searchable_select.py
+++ b/tests/e2e/test_searchable_select.py
@@ -1,51 +1,47 @@
 import pytest
 from playwright.sync_api import Page, expect
 
+from src.presentacion_reflex import styles
+
 def test_searchable_select_focus_in_modal(page: Page):
     """
     Verifica que el componente searchable_select (Combobox) dentro de un Dialog
-    puede recibir clics y foco correctamente, validando que pointer-events: auto 
-    mitiga el bug de radix-ui.
+    permite escritura directa y filtrado, validando la nueva arquitectura 
+    Absolute Dropdown que mitiga colisiones de foco.
     """
     # 1. Navegar a la página de recaudos
-    # Asumimos que el backend de reflex corre en localhost:3000
     page.goto("http://localhost:3000/recaudos")
 
     # 2. Abrir el modal que contiene el searchable_select
-    # Buscamos el botón de Nuevo Recaudo
     nuevo_btn = page.get_by_role("button", name="Nuevo Recaudo")
     if not nuevo_btn.is_visible():
         pytest.skip("Botón 'Nuevo Recaudo' no encontrado, omitiendo prueba específica de layout.")
     
     nuevo_btn.click()
 
-    # 3. Esperar a que el modal cargue y hacer clic en el trigger del searchable_select
-    # "Seleccione un contrato" o similar. Buscamos por texto si es necesario.
-    # El trigger es un botón con text() o el placeholder.
-    select_trigger = page.get_by_role("button").filter(has_text="Buscar...").first
-    # Si no, probamos buscando un elemento que diga Contrato cerca.
-    
-    # Dado que no conocemos el texto exacto, buscamos el input de búsqueda del popover
-    # que se hace visible SOLO tras hacer clic en el trigger.
-    # Un enfoque es buscar el input "Buscar..." y forzar su visibilidad clicando su contenedor previo.
-    
-    # Hacemos clic en el combobox de Contrato.
-    page.locator("button:has-text('Seleccionar...')").first.click()
-
-    # 4. El Popover debería abrirse. Buscamos el input del popover.
-    search_input = page.get_by_placeholder("Buscar...")
+    # 3. Esperar a que el modal cargue y localizar el combobox input
+    # El trigger ahora es directamente un input
+    search_input = page.locator("input[placeholder*='Seleccionar']").first
     expect(search_input).to_be_visible(timeout=5000)
 
-    # 5. Validar que podemos interactuar con él (focus y type)
-    # Si pointer-events: none estuviera activo (el bug viejo), esto fallaría 
-    # por actionability check de Playwright o el evento se ignoraría.
+    # 4. Validar que podemos interactuar con él (focus y type directamente)
     search_input.click()
     search_input.fill("Prueba E2E")
 
-    # 6. Validar que el foco pertenece al input
+    # 5. Validar que el foco pertenece al input
     is_focused = search_input.evaluate("node => document.activeElement === node")
-    assert is_focused is True, "El input de búsqueda no tiene el foco. El bug de pointer-events podría estar activo."
+    assert is_focused is True, "El input de búsqueda no tiene el foco tras escribir."
 
+    # 6. Validar que la lista desplegable se haya abierto 
+    # (buscamos un contenedor con un z-index alto cercano)
+    dropdown_item = page.locator(f"div[style*='z-index: {styles.Z_POPOVER}']").filter(has_text="Prueba E2E").first
+    expect(dropdown_item).to_be_visible()
+    # Nota: la aserción exacta de las opciones depende de los mocks de base de datos,
+    # con esto validamos principalmente que no hubo crasheo de UI al escribir.
+    
     # 7. Cerrar haciendo clic fuera
     page.mouse.click(0, 0)
-    expect(search_input).not_to_be_visible()
+    
+    # Después de on_blur, el input debería restaurar su placeholder original o limpiarse
+    # (el menú de opciones ya no debería ser interactuable)
+    expect(dropdown_item).not_to_be_visible()

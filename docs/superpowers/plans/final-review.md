bbbaecf test(e2e): fix combobox dropdown locator and visibility assertions
20ce022 test(e2e): adapt combobox tests to new absolute dropdown pattern
eb8247e refactor(ui): convert searchable_select to true combobox autocomplete

 .../components/shared/searchable_select.py         | 172 +++++++++------------
 tests/e2e/test_searchable_select.py                |  46 +++---
 2 files changed, 92 insertions(+), 126 deletions(-)

diff --git a/src/presentacion_reflex/components/shared/searchable_select.py b/src/presentacion_reflex/components/shared/searchable_select.py
index f39d0ff..8e27c1e 100644
--- a/src/presentacion_reflex/components/shared/searchable_select.py
+++ b/src/presentacion_reflex/components/shared/searchable_select.py
@@ -1,165 +1,135 @@
 """
 Componente SearchableSelect - Reflex
 Selectores con búsqueda accesibles y alineados con Claude Design System.
 """
 
 import reflex as rx
 from typing import Any, List, Union
 
-from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_input
+from src.presentacion_reflex.components.neuro_elements import neuro_input
 from src.presentacion_reflex import styles
 
 
 def searchable_select(
     label: str,
     placeholder: str,
     value_label: Union[rx.Var[str], str],
     search_value: Union[rx.Var[str], str],
     menu_open: Union[rx.Var[bool], bool],
     filtered_options: Union[rx.Var[List[List[str]]], List[List[str]]],
     on_change_search: Any,
     on_toggle_menu: Any,
     on_select: Any,
     is_required: bool = False,
     helper_text: str = "",
     error_text: str = "",
     on_key_down: Any = None,
 ) -> rx.Component:
-    """Componente de selectable con búsqueda accesible.
+    """Componente de selectable con búsqueda accesible tipo Combobox.
 
     Args:
         label: Etiqueta del campo
         placeholder: Texto cuando no hay selección
         value_label: Variable con el texto de la opción seleccionada
         search_value: Variable con el texto de búsqueda actual
         menu_open: Estado de apertura del menú
         filtered_options: Opciones filtradas para mostrar
         on_change_search: Handler al cambiar búsqueda
         on_toggle_menu: Handler al abrir/cerrar menú
         on_select: Handler al seleccionar opción
         is_required: Si el campo es requerido
         helper_text: Texto de ayuda
         error_text: Mensaje de error
         on_key_down: Handler para eventos de teclado
 
     Returns:
         Componente Reflex
     """
+    
+    # Input principal que actúa como Combobox
+    combobox_input = neuro_input(
+        placeholder=placeholder,
+        value=rx.cond(menu_open, search_value, rx.cond(value_label != "", value_label, search_value)),
+        on_change=lambda val: [on_change_search(val), on_toggle_menu(True)],
+        on_focus=lambda: [on_change_search(""), on_toggle_menu(True)],
+        on_blur=lambda: on_toggle_menu(False),
+        on_key_down=on_key_down,
+        width="100%",
+        variant="surface",
+        size="2",
+    )
+
+    # Panel flotante de opciones (Absolute Dropdown)
+    dropdown_menu = rx.cond(
+        menu_open,
+        rx.box(
+            rx.scroll_area(
+                rx.vstack(
+                    rx.foreach(
+                        filtered_options,
+                        lambda opt: rx.cond(
+                            opt[0] != "",
+                            rx.box(
+                                rx.text(
+                                    opt[0],
+                                    size="2",
+                                    weight="medium",
+                                    truncate=True,
+                                ),
+                                width="100%",
+                                padding_x="3",
+                                padding_y="2",
+                                _hover={
+                                    "background": "var(--bg-hover)",
+                                    "cursor": "pointer",
+                                },
+                                # Usamos on_mouse_down en lugar de on_click para evitar el on_blur prematuro del input
+                                on_mouse_down=lambda: on_select(opt[1], opt[0]),
+                            ),
+                        ),
+                    ),
+                    width="100%",
+                    spacing="0",
+                ),
+                type="auto",
+                scrollbars="vertical",
+                style={"max_height": "200px"},
+                width="100%",
+            ),
+            position="absolute",
+            top="100%",
+            left="0",
+            width="100%",
+            margin_top="4px",
+            background="var(--bg-panel)",
+            border="1px solid var(--border-default)",
+            border_radius="12px",
+            box_shadow="0px 4px 24px rgba(0,0,0,0.08)",
+            z_index=styles.Z_POPOVER,
+        )
+    )
+
     return rx.vstack(
         rx.hstack(
             rx.text(label, size="2", weight="bold"),
             rx.cond(
                 is_required,
                 rx.text("*", color="var(--brand-primary)", weight="bold"),
             ),
             spacing="1",
         ),
-        rx.popover.root(
-            rx.popover.trigger(
-                neuro_button(
-                    rx.cond(
-                        value_label == "",
-                        rx.text(
-                            placeholder, color="var(--text-tertiary)", weight="regular"
-                        ),
-                        rx.text(
-                            value_label, color="var(--text-primary)", weight="medium"
-                        ),
-                    ),
-                    rx.icon("chevron-down", size=16),
-                    variant="surface",
-                    width="100%",
-                    justify="between",
-                    height="44px",
-                    padding="0 1rem",
-                    border_radius="12px",
-                    box_shadow="inset 0px 2px 4px rgba(0,0,0,0.05)",
-                    _hover={
-                        "box_shadow": "inset 0px 2px 4px rgba(0,0,0,0.05), 0px 0px 0px 1px var(--border-emphasis)",
-                    },
-                    _focus={
-                        "box_shadow": "inset 0px 2px 4px rgba(0,0,0,0.05), 0px 0px 0px 2px var(--brand-primary)",
-                        "outline": "none",
-                    },
-                ),
-            ),
-            rx.popover.content(
-                rx.vstack(
-                    neuro_input(
-                        placeholder="Buscar...",
-                        value=search_value,
-                        on_change=on_change_search,
-                        on_key_down=on_key_down,
-                        width="100%",
-                        variant="soft",
-                        size="2",
-                        padding="0.75rem",
-                        border_radius="8px 8px 0 0",
-                        border="none",
-                        border_bottom="1px solid var(--border-default)",
-                        _focus={
-                            "outline": "none",
-                            "box_shadow": "none",
-                        },
-                    ),
-                    rx.scroll_area(
-                        rx.vstack(
-                            rx.foreach(
-                                filtered_options,
-                                lambda opt: rx.cond(
-                                    opt[0] != "",
-                                    rx.box(
-                                        rx.text(
-                                            opt[0],
-                                            size="2",
-                                            weight="medium",
-                                            truncate=True,
-                                        ),
-                                        width="100%",
-                                        padding_x="3",
-                                        padding_y="2",
-                                        _hover={
-                                            "background": "var(--bg-hover)",
-                                            "cursor": "pointer",
-                                        },
-                                        on_click=lambda: on_select(opt[1], opt[0]),
-                                    ),
-                                ),
-                            ),
-                            width="100%",
-                            spacing="0",
-                        ),
-                        type="auto",
-                        scrollbars="vertical",
-                        style={"max_height": "200px"},
-                        width="100%",
-                    ),
-                    padding="0",
-                    width="100%",
-                    min_width="300px",
-                    border_radius="12px",
-                    box_shadow="0px 4px 24px rgba(0,0,0,0.08)",
-                    border="1px solid var(--border-default)",
-                    background="var(--bg-panel)",
-                ),
-                align="start",
-                side="bottom",
-                side_offset=4,
-                avoid_collisions=True,
-                style={
-                    "pointer_events": "auto",
-                    "z_index": styles.Z_POPOVER,
-                },
-            ),
-            open=menu_open,
-            on_open_change=on_toggle_menu,
+        rx.box(
+            combobox_input,
+            dropdown_menu,
+            position="relative",
+            width="100%",
         ),
         rx.cond(
             helper_text != "",
             rx.text(helper_text, size="1", color="var(--text-tertiary)"),
         ),
         rx.cond(
             error_text != "",
             rx.text(error_text, size="1", color="var(--red-9)"),
         ),
         spacing="1",
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

0e54014 feat(presentacion): agregar boton de paz y salvo en tabla de contratos inactivos
25d6d5e feat(presentacion): agregar boton de paz y salvo en tarjeta de contrato inactivo
80a2219 docs(superpowers): agregar plan de implementacion para generacion manual de paz y salvo
94641a1 docs(superpowers): agregar spec de diseño para generacion manual de paz y salvo
 .../plans/2026-06-24-generar-paz-y-salvo-plan.md   | 116 +++++++++++++++++++++
 .../specs/2026-06-24-generar-paz-y-salvo-design.md |  28 +++++
 .../components/contratos/tarjeta_contrato.py       |  21 +++-
 src/presentacion_reflex/pages/contratos.py         |  26 ++++-
 4 files changed, 186 insertions(+), 5 deletions(-)
diff --git a/docs/superpowers/plans/2026-06-24-generar-paz-y-salvo-plan.md b/docs/superpowers/plans/2026-06-24-generar-paz-y-salvo-plan.md
new file mode 100644
index 0000000..41ed73d
--- /dev/null
+++ b/docs/superpowers/plans/2026-06-24-generar-paz-y-salvo-plan.md
@@ -0,0 +1,116 @@
+# Generación de Paz y Salvo Implementation Plan
+
+> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
+
+**Goal:** Agregar un botón "Generar Paz y Salvo" en las vistas de contratos (tabla y cuadrícula) para contratos inactivos, permitiendo la generación manual del documento.
+
+**Architecture:** El botón se agregará en los componentes visuales de Reflex (`contratos.py` y `tarjeta_contrato.py`), utilizando condicionales `rx.cond` para renderizarse solo cuando el contrato no esté activo. Llamará a la función `PDFState.generar_certificado_paz_y_salvo` y pasará dinámicamente el beneficiario basado en el tipo de contrato.
+
+**Tech Stack:** Python, Reflex
+
+## Global Constraints
+
+- Estándar de colores Elite (teal para esta acción).
+- Código en español (Reglas del proyecto).
+- Zero leaks, convenciones strictas.
+- Verificación con `check_syntax.py`, `mypy`, `ruff`, `black`.
+
+---
+
+### Task 1: Modificar Tarjeta Contrato (Vista Cuadrícula)
+
+**Files:**
+- Modify: `src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
+
+**Interfaces:**
+- Consumes: `PDFState.generar_certificado_paz_y_salvo`
+- Produces: Botón en la interfaz de tarjeta.
+
+- [ ] **Step 1: Agregar el botón en tarjeta_contrato.py**
+
+Modificar el `rx.scroll_area` de las acciones (alrededor de la línea 265, después del botón de terminar o antes).
+
+```python
+                    # Paz y Salvo (Para inactivos)
+                    rx.cond(
+                        contrato.estado_contrato != "ACTIVO",
+                        neuro_icon_action_button(
+                            "shield-check",
+                            on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
+                                contrato.id_contrato,
+                                rx.cond(
+                                    contrato.tipo_contrato == "Mandato",
+                                    contrato.propietario_nombre,
+                                    contrato.arrendatario_nombre,
+                                )
+                            ),
+                            color_scheme="teal",
+                            tooltip_content="Generar Paz y Salvo",
+                        ),
+                    ),
+```
+
+- [ ] **Step 2: Verificar la sintaxis**
+
+Run: `python scripts/check_syntax.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
+Expected: PASS
+
+- [ ] **Step 3: Commit**
+
+```bash
+git add src/presentacion_reflex/components/contratos/tarjeta_contrato.py
+git commit -m "feat(presentacion): agregar boton de paz y salvo en tarjeta de contrato inactivo"
+```
+
+---
+
+### Task 2: Modificar Tabla Contratos (Vista Lista)
+
+**Files:**
+- Modify: `src/presentacion_reflex/pages/contratos.py`
+
+**Interfaces:**
+- Consumes: `PDFState.generar_certificado_paz_y_salvo`
+- Produces: Botón en la interfaz de tabla.
+
+- [ ] **Step 1: Agregar el botón en _tabla_acciones**
+
+Dentro de `_tabla_acciones` en `src/presentacion_reflex/pages/contratos.py`, agregar el botón de paz y salvo junto a los otros botones condicionales.
+
+```python
+            # Paz y Salvo — solo si está inactivo
+            rx.cond(
+                c.estado_contrato != "ACTIVO",
+                neuro_icon_action_button(
+                    "shield-check",
+                    color_scheme="teal",
+                    size="1",
+                    tooltip_content="Generar Paz y Salvo",
+                    on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
+                        c.id_contrato,
+                        rx.cond(
+                            c.tipo_contrato == "Mandato",
+                            c.propietario_nombre,
+                            c.arrendatario_nombre,
+                        ),
+                    ),
+                ),
+            ),
+```
+
+- [ ] **Step 2: Verificar la sintaxis**
+
+Run: `python scripts/check_syntax.py src/presentacion_reflex/pages/contratos.py`
+Expected: PASS
+
+- [ ] **Step 3: Ejecutar QA tools (Linter y Formatter)**
+
+Run: `ruff check src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
+Run: `black src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
+
+- [ ] **Step 4: Commit**
+
+```bash
+git add src/presentacion_reflex/pages/contratos.py
+git commit -m "feat(presentacion): agregar boton de paz y salvo en tabla de contratos inactivos"
+```
diff --git a/docs/superpowers/specs/2026-06-24-generar-paz-y-salvo-design.md b/docs/superpowers/specs/2026-06-24-generar-paz-y-salvo-design.md
new file mode 100644
index 0000000..dce5b1b
--- /dev/null
+++ b/docs/superpowers/specs/2026-06-24-generar-paz-y-salvo-design.md
@@ -0,0 +1,28 @@
+# Diseño: Generación de Paz y Salvo para Contratos Inactivos
+
+## Contexto
+Actualmente, el documento de Paz y Salvo sólo se genera de manera automática durante la transición de estado cuando un contrato es finalizado. No existe una acción en la interfaz para regenerar o generar este documento una vez el contrato está en estado inactivo.
+
+## Objetivo
+Implementar un botón "Generar Paz y Salvo" en el módulo de Contratos que permita su ejecución manual para aquellos contratos (Mandato o Arrendamiento) cuyo estado sea distinto a `ACTIVO`.
+
+## Arquitectura y Componentes
+1. **Interfaz (UI):**
+   - Modificación de `src/presentacion_reflex/components/contratos/tarjeta_contrato.py` para incluir el botón de acción en la vista de cuadrícula.
+   - Modificación de `src/presentacion_reflex/pages/contratos.py` para incluir el botón en la columna de acciones de la vista tabular.
+
+2. **Propiedades Visuales del Botón:**
+   - **Icono:** `shield-check` o similar que denote certificación/seguridad.
+   - **Color (Color Scheme):** `"teal"` o una tonalidad que contraste adecuadamente con las otras opciones y respete el diseño Elite.
+   - **Tooltip:** "Generar Paz y Salvo".
+
+3. **Lógica de Negocio y Data Flow:**
+   - **Condición de Visibilidad:** El componente sólo se renderizará si el contrato cumple con `estado_contrato != "ACTIVO"`.
+   - **Manejador de Eventos (On Click):** Invocar al método existente `PDFState.generar_certificado_paz_y_salvo(contrato_id, beneficiario_nombre)`.
+   - **Paso de Parámetros Dinámico:** El nombre del beneficiario se resolverá evaluando dinámicamente en el frontend usando `rx.cond`. Si es Mandato, será el nombre del propietario; si es Arrendamiento, será el del arrendatario.
+
+4. **Reglas de Seguridad y Control de Acceso:**
+   - El botón podrá visualizarse sin necesidad de permisos adicionales de escritura, o dependerá de la visualización base del contrato (`AuthState.check_action("Contratos", "VER")` si aplica).
+
+## Conclusión
+Este diseño evita duplicar lógica en el backend y maximiza el reúso de las funciones de Reflex y los servicios de generación de PDF ya definidos, asegurando un mantenimiento limpio y conforme a los lineamientos del manifiesto.
diff --git a/src/presentacion_reflex/components/contratos/tarjeta_contrato.py b/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
index 5f27f1f..4051e99 100644
--- a/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
+++ b/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
@@ -3,21 +3,23 @@ import reflex as rx
 from src.presentacion_reflex import styles
 from src.presentacion_reflex.state.auth_state import AuthState
 from src.presentacion_reflex.state.contratos_state import ContratosState, ContratoDict
 from src.presentacion_reflex.state.pdf_state import PDFState
 from src.presentacion_reflex.components.neuro_elements import (
     neuro_icon_action_button,
     neuro_badge,
     neuro_divider,
     neuro_panel,
 )
-from src.presentacion_reflex.components.contratos.badge_grupo_pago import badge_grupo_pago
+from src.presentacion_reflex.components.contratos.badge_grupo_pago import (
+    badge_grupo_pago,
+)
 
 
 def tarjeta_contrato(contrato: ContratoDict) -> rx.Component:
     """
     Tarjeta visual para un contrato (Mandato o Arrendamiento).
     Estilo Elite estandarizado con tipado estricto.
     """
     return neuro_panel(
         rx.vstack(
             # Header: Tipo, Estado y Cumplimiento
@@ -269,20 +271,37 @@ def tarjeta_contrato(contrato: ContratoDict) -> rx.Component:
                             on_click=lambda: ContratosState.toggle_estado(
                                 contrato.id_contrato,
                                 contrato.tipo_contrato,
                                 contrato.estado_contrato,
                             ),
                             color_scheme="red",
                             disabled=contrato.estado_contrato != "ACTIVO",
                             tooltip_content="Terminar",
                         ),
                     ),
+                    # Paz y Salvo (Para inactivos)
+                    rx.cond(
+                        contrato.estado_contrato != "ACTIVO",
+                        neuro_icon_action_button(
+                            "shield-check",
+                            on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
+                                contrato.id_contrato,
+                                rx.cond(
+                                    contrato.tipo_contrato == "Mandato",
+                                    contrato.propietario_nombre,
+                                    contrato.arrendatario_nombre,
+                                ),
+                            ),
+                            color_scheme="teal",
+                            tooltip_content="Generar Paz y Salvo",
+                        ),
+                    ),
                     spacing="2",
                     padding_y="1",
                 ),
                 type="hover",
                 scrollbars="horizontal",
                 style={"width": "100%"},
             ),
             spacing="3",
             height="100%",
             justify="between",
diff --git a/src/presentacion_reflex/pages/contratos.py b/src/presentacion_reflex/pages/contratos.py
index 46b1ce4..7454409 100644
--- a/src/presentacion_reflex/pages/contratos.py
+++ b/src/presentacion_reflex/pages/contratos.py
@@ -10,21 +10,23 @@ from src.presentacion_reflex.components.neuro_elements import (
     neuro_select_root,
     neuro_button,
     neuro_icon_action_button,
     neuro_badge,
     neuro_panel,
 )
 from src.presentacion_reflex.components.tablas import header_cell_sortable
 from src.presentacion_reflex.components.contratos.tarjeta_contrato import (
     tarjeta_contrato,
 )
-from src.presentacion_reflex.components.contratos.badge_grupo_pago import badge_grupo_pago
+from src.presentacion_reflex.components.contratos.badge_grupo_pago import (
+    badge_grupo_pago,
+)
 
 from src.presentacion_reflex.components.contratos.formulario_contrato_mandato import (
     formulario_contrato_mandato,
 )
 from src.presentacion_reflex.components.contratos.formulario_contrato_arrendamiento import (
     formulario_contrato_arrendamiento,
 )
 from src.presentacion_reflex.components.contratos.modal_detalle_contrato import (
     modal_detalle_contrato,
 )
@@ -98,20 +100,38 @@ def render_table_view() -> rx.Component:
             # PDF Contrato Oficial
             neuro_icon_action_button(
                 "file-check",
                 color_scheme="purple",
                 size="1",
                 tooltip_content="Generar Contrato Oficial",
                 on_click=lambda: PDFState.generar_contrato_oficial_elite(
                     c.id_contrato, c.tipo_contrato, False
                 ),
             ),
+            # Paz y Salvo — solo si está inactivo
+            rx.cond(
+                c.estado_contrato != "ACTIVO",
+                neuro_icon_action_button(
+                    "shield-check",
+                    color_scheme="teal",
+                    size="1",
+                    tooltip_content="Generar Paz y Salvo",
+                    on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
+                        c.id_contrato,
+                        rx.cond(
+                            c.tipo_contrato == "Mandato",
+                            c.propietario_nombre,
+                            c.arrendatario_nombre,
+                        ),
+                    ),
+                ),
+            ),
             # Terminar
             rx.cond(
                 AuthState.check_action("Contratos", "TERMINAR"),
                 neuro_icon_action_button(
                     "ban",
                     color_scheme="red",
                     size="1",
                     tooltip_content="Terminar Contrato",
                     disabled=c.estado_contrato != "ACTIVO",
                     on_click=lambda: ContratosState.toggle_estado(
@@ -300,23 +320,21 @@ def render_table_view() -> rx.Component:
                                     spacing="1",
                                     align="center",
                                 ),
                             ),
                             spacing="1",
                         )
                     ),
                     rx.table.cell(
                         rx.text("$", c.valor_canon.to_string(), weight="bold")
                     ),
-                    rx.table.cell(
-                        badge_grupo_pago(c.grupo_operativo, c.fecha_pago)
-                    ),
+                    rx.table.cell(badge_grupo_pago(c.grupo_operativo, c.fecha_pago)),
                     rx.table.cell(
                         rx.vstack(
                             rx.text("Inicia: ", c.fecha_inicio, size="1"),
                             rx.text("Vence: ", c.fecha_fin, size="1"),
                             spacing="1",
                         )
                     ),
                     rx.table.cell(_tabla_acciones(c)),
                 ),
             )

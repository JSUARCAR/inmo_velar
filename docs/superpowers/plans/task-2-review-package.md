0e54014 feat(presentacion): agregar boton de paz y salvo en tabla de contratos inactivos
 .../components/contratos/tarjeta_contrato.py       |  6 +++--
 src/presentacion_reflex/pages/contratos.py         | 26 ++++++++++++++++++----
 2 files changed, 26 insertions(+), 6 deletions(-)
diff --git a/src/presentacion_reflex/components/contratos/tarjeta_contrato.py b/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
index 45b9785..4051e99 100644
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
@@ -280,21 +282,21 @@ def tarjeta_contrato(contrato: ContratoDict) -> rx.Component:
                     rx.cond(
                         contrato.estado_contrato != "ACTIVO",
                         neuro_icon_action_button(
                             "shield-check",
                             on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
                                 contrato.id_contrato,
                                 rx.cond(
                                     contrato.tipo_contrato == "Mandato",
                                     contrato.propietario_nombre,
                                     contrato.arrendatario_nombre,
-                                )
+                                ),
                             ),
                             color_scheme="teal",
                             tooltip_content="Generar Paz y Salvo",
                         ),
                     ),
                     spacing="2",
                     padding_y="1",
                 ),
                 type="hover",
                 scrollbars="horizontal",
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

25d6d5e feat(presentacion): agregar boton de paz y salvo en tarjeta de contrato inactivo
 .../components/contratos/tarjeta_contrato.py            | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)
diff --git a/src/presentacion_reflex/components/contratos/tarjeta_contrato.py b/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
index 5f27f1f..45b9785 100644
--- a/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
+++ b/src/presentacion_reflex/components/contratos/tarjeta_contrato.py
@@ -269,20 +269,37 @@ def tarjeta_contrato(contrato: ContratoDict) -> rx.Component:
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
+                                )
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

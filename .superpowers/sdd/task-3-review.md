dae2bd3 feat(ipc): integrar modal y boton de eliminacion en UI
 src/presentacion_reflex/pages/incrementos.py | 76 ++++++++++++++++++++++++----
 1 file changed, 67 insertions(+), 9 deletions(-)
diff --git a/src/presentacion_reflex/pages/incrementos.py b/src/presentacion_reflex/pages/incrementos.py
index 7e38f56..47fcf9a 100644
--- a/src/presentacion_reflex/pages/incrementos.py
+++ b/src/presentacion_reflex/pages/incrementos.py
@@ -57,49 +57,106 @@ def ipc_modal() -> rx.Component:
                 rx.button("Guardar", on_click=IPCState.save_ipc, loading=IPCState.is_loading),
                 spacing="3",
                 justify="end",
             ),
         ),
         open=IPCState.show_modal,
         on_open_change=IPCState.set_show_modal,
     )
 
 
+def delete_ipc_dialog() -> rx.Component:
+    return rx.alert_dialog.root(
+        rx.alert_dialog.content(
+            rx.alert_dialog.title("Confirmar Eliminaci├│n"),
+            rx.alert_dialog.description(
+                "┬┐Est├í seguro que desea eliminar el IPC del a├▒o ",
+                rx.text(IPCState.ipc_to_delete_anio, weight="bold"),
+                "? Esta acci├│n inhabilitar├í el registro.",
+            ),
+            rx.flex(
+                rx.alert_dialog.cancel(
+                    rx.button(
+                        "Cancelar",
+                        variant="soft",
+                        color_scheme="gray",
+                        on_click=IPCState.cancel_delete,
+                    ),
+                ),
+                rx.alert_dialog.action(
+                    rx.button(
+                        "Eliminar",
+                        color_scheme="red",
+                        variant="solid",
+                        on_click=IPCState.delete_ipc,
+                        loading=IPCState.is_loading,
+                    ),
+                ),
+                spacing="3",
+                margin_top="16px",
+                justify="end",
+            ),
+        ),
+        open=IPCState.show_delete_dialog,
+        on_open_change=lambda val: rx.cond(
+            val, 
+            rx.do_nothing(), 
+            IPCState.cancel_delete()
+        ),
+    )
+
+
 def ipc_table() -> rx.Component:
     return rx.table.root(
         rx.table.header(
             rx.table.row(
                 rx.table.column_header_cell("A├▒o"),
                 rx.table.column_header_cell("Valor IPC"),
                 rx.table.column_header_cell("Fecha Publicaci├│n"),
                 rx.table.column_header_cell("Acciones"),
             )
         ),
         rx.table.body(
             rx.foreach(
                 IPCState.ipcs,
                 lambda ipc: rx.table.row(
                     rx.table.cell(rx.badge(ipc.anio, variant="outline")),
                     rx.table.cell(rx.text(ipc.valor_ipc, "%", weight="bold")),
                     rx.table.cell(ipc.fecha_publicacion),
                     rx.table.cell(
-                        rx.cond(
-                            AuthState.check_action("Incrementos", "EDITAR"),
-                            rx.tooltip(
-                                rx.button(
-                                    rx.icon("pencil", size=16),
-                                    size="1",
-                                    variant="ghost",
-                                    on_click=lambda: IPCState.open_edit_modal(ipc),
+                        rx.hstack(
+                            rx.cond(
+                                AuthState.check_action("Incrementos", "EDITAR"),
+                                rx.tooltip(
+                                    rx.button(
+                                        rx.icon("pencil", size=16),
+                                        size="1",
+                                        variant="ghost",
+                                        on_click=lambda: IPCState.open_edit_modal(ipc),
+                                    ),
+                                    content="Editar IPC",
+                                ),
+                            ),
+                            rx.cond(
+                                AuthState.check_action("Incrementos", "ELIMINAR"),
+                                rx.tooltip(
+                                    rx.button(
+                                        rx.icon("trash-2", size=16),
+                                        size="1",
+                                        variant="ghost",
+                                        color_scheme="red",
+                                        on_click=lambda: IPCState.confirm_delete_ipc(ipc),
+                                    ),
+                                    content="Eliminar IPC",
                                 ),
-                                content="Editar IPC",
                             ),
+                            spacing="2",
                         )
                     ),
                 ),
             )
         ),
         variant="surface",
     )
 
 
 def incrementos_content() -> rx.Component:
@@ -121,20 +178,21 @@ def incrementos_content() -> rx.Component:
             color="gray",
         ),
         rx.divider(),
         rx.cond(
             IPCState.is_loading
             & ~IPCState.show_modal,  # Show spinner if loading and modal not open (initial load)
             rx.center(rx.spinner()),
             ipc_table(),
         ),
         ipc_modal(),
+        delete_ipc_dialog(),
         spacing="5",
         padding="6",
         width="100%",
     )
 
 
 @rx.page(
     route="/incrementos",
     title="IPC e Incrementos | Inmobiliaria Velar",
     on_load=[AuthState.require_login, IPCState.load_ipcs],

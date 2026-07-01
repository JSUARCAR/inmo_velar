6c13d5f fix(presentacion): validaci├│n de permisos en eliminaci├│n de IPC y correcci├│n de type hints y excepciones
26779ea feat(ipc): agregar estado reactivo y eventos para eliminar IPC
 src/presentacion_reflex/state/auth_state.py |  9 ++++
 src/presentacion_reflex/state/ipc_state.py  | 70 +++++++++++++++++++++++++++++
 2 files changed, 79 insertions(+)
diff --git a/src/presentacion_reflex/state/auth_state.py b/src/presentacion_reflex/state/auth_state.py
index a16dca1..48cf34c 100644
--- a/src/presentacion_reflex/state/auth_state.py
+++ b/src/presentacion_reflex/state/auth_state.py
@@ -358,20 +358,29 @@ class AuthState(rx.State):
         return rx.cond(
             is_admin,
             True,
             rx.cond(
                 module_exists,
                 cls.permissions_map[module_name].contains(action),
                 False
             )
         )
 
+    def backend_check_action(self, module_name: str, action: str) -> bool:
+        """
+        Verifica si el usuario actual tiene permiso para una acci├│n en un m├│dulo.
+        A diferencia de `check_action`, este m├®todo es para uso s├¡ncrono en backend.
+        """
+        if self.user_rol == "Administrador":
+            return True
+        return action in self.permissions_map.get(module_name, [])
+
     def _sync_permissions(self, rol: str = None):
         """Recarga los permisos del usuario desde la base de datos."""
         try:
             target_rol = rol or self.user_rol or None
             if not target_rol:
                 _debug("_sync_permissions ÔåÆ sin rol, abortando")
                 return
 
             _debug("_sync_permissions START", rol=target_rol)
             servicio_permisos = ServicioPermisos(db_manager)
diff --git a/src/presentacion_reflex/state/ipc_state.py b/src/presentacion_reflex/state/ipc_state.py
index 171867f..e81372c 100644
--- a/src/presentacion_reflex/state/ipc_state.py
+++ b/src/presentacion_reflex/state/ipc_state.py
@@ -14,20 +14,41 @@ class IPCState(rx.State):
 
     ipcs: List[IPC] = []
     is_loading: bool = False
     error_message: str = ""
 
     # Form Modal State
     show_modal: bool = False
     is_editing: bool = False
     current_ipc_id: int = 0
 
+    # Delete Modal State
+    show_delete_dialog: bool = False
+    ipc_to_delete_id: int = 0
+    ipc_to_delete_anio: int = 0
+
+    def confirm_delete_ipc(self, ipc: IPC) -> None:
+        """Abre el di├ílogo de confirmaci├│n para eliminar un IPC.
+
+        Args:
+            ipc (IPC): El objeto IPC a eliminar.
+        """
+        self.ipc_to_delete_id = ipc.id_ipc
+        self.ipc_to_delete_anio = ipc.anio
+        self.show_delete_dialog = True
+        
+    def cancel_delete(self) -> None:
+        """Cancela la eliminaci├│n de un IPC y cierra el di├ílogo."""
+        self.show_delete_dialog = False
+        self.ipc_to_delete_id = 0
+        self.ipc_to_delete_anio = 0
+
     def set_show_modal(self, value: bool):
         self.show_modal = value
 
     # Form Fields
     form_anio: int = 2025
     form_valor: float = 0.0
 
     def set_anio(self, value: str):
         """Setter personalizado para manejar conversi├│n str -> int del input."""
         if value == "" or value is None:
@@ -105,10 +126,59 @@ class IPCState(rx.State):
 
             async with self:
                 self.ipcs = lista
                 self.show_modal = False
                 self.is_loading = False
 
         except Exception as e:
             async with self:
                 self.error_message = str(e)
                 self.is_loading = False
+
+    @rx.event(background=True)
+    async def delete_ipc(self) -> None:
+        """Elimina el IPC seleccionado.
+
+        Realiza validaci├│n de permisos de RBAC (Rol-Based Access Control) antes
+        de proceder. Si ocurre un error de validaci├│n o no hay permisos,
+        se actualiza el estado de error de la interfaz.
+        """
+        async with self:
+            if not self.ipc_to_delete_id:
+                return
+            self.is_loading = True
+            self.error_message = ""
+            current_user = await self.get_state(AuthState)
+            
+            if not current_user.backend_check_action("Incrementos", "ELIMINAR"):
+                self.error_message = "No tiene permisos para eliminar IPC"
+                self.is_loading = False
+                self.show_delete_dialog = False
+                return
+
+            usuario = current_user.user_nombre if current_user.is_authenticated else "sistema"
+            id_ipc = self.ipc_to_delete_id
+
+        try:
+            servicio = ServicioIPC(db_manager)
+            servicio.eliminar_ipc(id_ipc, usuario)
+            
+            # Recargar y cerrar
+            lista = servicio.listar_todos()
+
+            async with self:
+                self.ipcs = lista
+                self.show_delete_dialog = False
+                self.ipc_to_delete_id = 0
+                self.ipc_to_delete_anio = 0
+                self.is_loading = False
+
+        except ValueError as ve:
+            logger.error(f"Error de validaci├│n eliminando IPC: {ve}")
+            async with self:
+                self.error_message = str(ve)
+                self.is_loading = False
+        except Exception as e:
+            logger.error(f"Error inesperado eliminando IPC: {e}")
+            async with self:
+                self.error_message = "Ocurri├│ un error inesperado al eliminar el IPC"
+                self.is_loading = False

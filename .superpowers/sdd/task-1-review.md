a88bee0 feat(ipc): agregar metodo eliminar_ipc al servicio
 src/aplicacion/servicios/servicio_ipc.py | 20 ++++++++++++++++++--
 1 file changed, 18 insertions(+), 2 deletions(-)
diff --git a/src/aplicacion/servicios/servicio_ipc.py b/src/aplicacion/servicios/servicio_ipc.py
index 45ea563..56df002 100644
--- a/src/aplicacion/servicios/servicio_ipc.py
+++ b/src/aplicacion/servicios/servicio_ipc.py
@@ -1,16 +1,18 @@
 from datetime import datetime
 from typing import List, Optional
 
 from src.dominio.entidades.ipc import IPC
 from src.infraestructura.persistencia.database import DatabaseManager
-from src.infraestructura.persistencia.repositorio_ipc_postgres import RepositorioIPCPostgres
+from src.infraestructura.persistencia.repositorio_ipc_postgres import (
+    RepositorioIPCPostgres,
+)
 
 
 class ServicioIPC:
 
     def __init__(self, db_manager: DatabaseManager):
         self.repo = RepositorioIPCPostgres(db_manager)
 
     def listar_todos(self) -> List[IPC]:
         """Retorna todos los registros de IPC ordenados por a├▒o."""
         return self.repo.listar_todos()
@@ -45,14 +47,28 @@ class ServicioIPC:
 
     def actualizar_ipc(self, id_ipc: int, valor: float, usuario: str) -> IPC:
         """
         Actualiza el valor de un IPC existente.
         """
         ipc = self.repo.obtener_por_id(id_ipc)
         if not ipc:
             raise ValueError("Registro IPC no encontrado")
 
         ipc.valor_ipc = valor
-        ipc.fecha_publicacion = datetime.now().strftime("%Y-%m-%d")  # Actualizamos fecha referencia
+        ipc.fecha_publicacion = datetime.now().strftime(
+            "%Y-%m-%d"
+        )  # Actualizamos fecha referencia
 
         self.repo.actualizar(ipc, usuario)
         return ipc
+
+    def eliminar_ipc(self, id_ipc: int, usuario: str) -> bool:
+        """
+        Elimina un registro de IPC (soft delete).
+        Valida que el registro exista antes de eliminar.
+        """
+        ipc = self.repo.obtener_por_id(id_ipc)
+        if not ipc:
+            raise ValueError("Registro IPC no encontrado")
+
+        exito = self.repo.eliminar(id_ipc)
+        return exito

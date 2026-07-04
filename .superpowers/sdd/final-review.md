dae2bd3 feat(ipc): integrar modal y boton de eliminacion en UI
6c13d5f fix(presentacion): validaci├│n de permisos en eliminaci├│n de IPC y correcci├│n de type hints y excepciones
26779ea feat(ipc): agregar estado reactivo y eventos para eliminar IPC
a88bee0 feat(ipc): agregar metodo eliminar_ipc al servicio
e74e31d docs(plans): agregar plan de implementacion para eliminar IPC
44d8046 docs(specs): agregar especificaci├│n t├®cnica para eliminaci├│n de IPC
 .../plans/2026-06-24-eliminar-ipc-plan.md          | 251 +++++++++++++++++++++
 .../specs/2026-06-24-eliminar-ipc-design.md        |  57 +++++
 src/aplicacion/servicios/servicio_ipc.py           |  20 +-
 src/presentacion_reflex/pages/incrementos.py       |  76 ++++++-
 src/presentacion_reflex/state/auth_state.py        |   9 +
 src/presentacion_reflex/state/ipc_state.py         |  70 ++++++
 6 files changed, 472 insertions(+), 11 deletions(-)
diff --git a/docs/superpowers/plans/2026-06-24-eliminar-ipc-plan.md b/docs/superpowers/plans/2026-06-24-eliminar-ipc-plan.md
new file mode 100644
index 0000000..c3fa733
--- /dev/null
+++ b/docs/superpowers/plans/2026-06-24-eliminar-ipc-plan.md
@@ -0,0 +1,251 @@
+# Eliminar IPC Implementation Plan
+
+> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
+
+**Goal:** Implementar la funcionalidad de eliminaci├│n l├│gica (Soft Delete) de los registros de IPC, agregando el servicio y las acciones de interfaz en Reflex con un di├ílogo de confirmaci├│n.
+
+**Architecture:** Se utilizar├í el m├®todo existente `eliminar()` en `RepositorioIPCPostgres` que ya hace soft delete. Se expondr├í mediante un nuevo m├®todo `eliminar_ipc()` en `ServicioIPC`, y se controlar├í desde el frontend en `IPCState` utilizando `rx.alert_dialog` para seguridad, y actualizando la UI at├│micamente.
+
+**Tech Stack:** Python 3, Reflex, PostgreSQL.
+
+## Global Constraints
+
+- Backend y UI en espa├▒ol.
+- Usar `ESTADO_REGISTRO = FALSE` o `0` (impl├¡cito en la query del repo) para soft delete.
+- Requerir `AuthState.check_action("Incrementos", "ELIMINAR")` en la UI.
+- No mutar listas directamente; recargar `ipcs` desde el backend o usar mecanismos seguros de Reflex.
+
+---
+
+### Task 1: Capa de Aplicaci├│n - Servicio IPC
+
+**Files:**
+- Modify: `src/aplicacion/servicios/servicio_ipc.py`
+
+**Interfaces:**
+- Consumes: `RepositorioIPCPostgres.eliminar(id_ipc: int)` y `RepositorioIPCPostgres.obtener_por_id(id_ipc: int)`.
+- Produces: M├®todo `eliminar_ipc(self, id_ipc: int, usuario: str) -> bool` utilizable por Reflex state.
+
+- [ ] **Step 1: Write minimal implementation**
+
+En el archivo `src/aplicacion/servicios/servicio_ipc.py`, agregar el siguiente m├®todo al final de la clase `ServicioIPC`:
+
+```python
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
+```
+
+- [ ] **Step 2: Commit**
+
+```bash
+git add src/aplicacion/servicios/servicio_ipc.py
+git commit -m "feat(ipc): agregar metodo eliminar_ipc al servicio"
+```
+
+---
+
+### Task 2: Capa de Presentaci├│n - Estado y L├│gica (IPCState)
+
+**Files:**
+- Modify: `src/presentacion_reflex/state/ipc_state.py`
+
+**Interfaces:**
+- Consumes: `ServicioIPC.eliminar_ipc` implementado en Task 1.
+- Produces: Estado reactivo `show_delete_dialog`, `ipc_to_delete`, y eventos para el frontend `confirm_delete_ipc`, `cancel_delete`, `delete_ipc`.
+
+- [ ] **Step 1: Modify IPCState variables and synchronous methods**
+
+En `src/presentacion_reflex/state/ipc_state.py`, debajo de las variables de "Form Modal State" (aprox. l├¡nea 23):
+
+```python
+    # Delete Modal State
+    show_delete_dialog: bool = False
+    ipc_to_delete_id: int = 0
+    ipc_to_delete_anio: int = 0
+
+    def confirm_delete_ipc(self, ipc: IPC):
+        self.ipc_to_delete_id = ipc.id_ipc
+        self.ipc_to_delete_anio = ipc.anio
+        self.show_delete_dialog = True
+        
+    def cancel_delete(self):
+        self.show_delete_dialog = False
+        self.ipc_to_delete_id = 0
+        self.ipc_to_delete_anio = 0
+```
+*(Nota: Reflex maneja mejor tipos primitivos que almacenar instancias completas de `IPC` en el estado).*
+
+- [ ] **Step 2: Write background event for deletion**
+
+Al final de la clase `IPCState`:
+
+```python
+    @rx.event(background=True)
+    async def delete_ipc(self):
+        """Elimina el IPC seleccionado."""
+        async with self:
+            if not self.ipc_to_delete_id:
+                return
+            self.is_loading = True
+            self.error_message = ""
+            current_user = await self.get_state(AuthState)
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
+        except Exception as e:
+            logger.error(f"Error eliminando IPC: {e}")
+            async with self:
+                self.error_message = str(e)
+                self.is_loading = False
+```
+
+- [ ] **Step 3: Commit**
+
+```bash
+git add src/presentacion_reflex/state/ipc_state.py
+git commit -m "feat(ipc): agregar estado reactivo y eventos para eliminar IPC"
+```
+
+---
+
+### Task 3: Capa de Presentaci├│n - Interfaz (Frontend Reflex)
+
+**Files:**
+- Modify: `src/presentacion_reflex/pages/incrementos.py`
+
+**Interfaces:**
+- Consumes: Las variables de estado `IPCState.show_delete_dialog`, `IPCState.ipc_to_delete_anio` y los eventos de `IPCState`.
+
+- [ ] **Step 1: Add Delete Confirmation Dialog component**
+
+En `src/presentacion_reflex/pages/incrementos.py`, antes de `ipc_table()`:
+
+```python
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
+```
+
+- [ ] **Step 2: Update IPC Table to include the Delete button**
+
+Reemplazar la celda actual de "Acciones" en la funci├│n `ipc_table()`:
+*(Se debe usar `replace_file_content` cuidadosamente para actualizar `rx.table.cell` en la l├¡nea 84-97 aprox).*
+
+```python
+                    rx.table.cell(
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
+                                ),
+                            ),
+                            spacing="2",
+                        )
+                    ),
+```
+
+- [ ] **Step 3: Add dialog to the main view**
+
+En `incrementos_content()`, debajo de `ipc_modal(),` (aprox. l├¡nea 130), agregar `delete_ipc_dialog(),`.
+
+```python
+        rx.cond(
+            IPCState.is_loading
+            & ~IPCState.show_modal,  # Show spinner if loading and modal not open (initial load)
+            rx.center(rx.spinner()),
+            ipc_table(),
+        ),
+        ipc_modal(),
+        delete_ipc_dialog(),
+        spacing="5",
+```
+
+- [ ] **Step 4: Verify with type checking and commit**
+
+```bash
+git add src/presentacion_reflex/pages/incrementos.py
+git commit -m "feat(ipc): integrar modal y boton de eliminacion en UI"
+```
+
+- [ ] **Step 5: E2E Manual testing Check**
+
+Levantar el entorno de prueba/dev y confirmar visualmente que el modal se abre, el a├▒o aparece correcto y tras presionar "Eliminar", desaparece de la tabla sin fallos.
diff --git a/docs/superpowers/specs/2026-06-24-eliminar-ipc-design.md b/docs/superpowers/specs/2026-06-24-eliminar-ipc-design.md
new file mode 100644
index 0000000..ff2b634
--- /dev/null
+++ b/docs/superpowers/specs/2026-06-24-eliminar-ipc-design.md
@@ -0,0 +1,57 @@
+# Especificaci├│n T├®cnica: Funcionalidad "Eliminar IPC"
+
+## 1. Resumen Ejecutivo
+Implementar la acci├│n "Eliminar" en el m├│dulo de Gesti├│n de IPC / Incrementos. La soluci├│n utilizar├í un enfoque de eliminaci├│n l├│gica ("Soft Delete") para preservar el hist├│rico de datos y la integridad referencial, habilitando la acci├│n desde la UI (tabla de IPC) mediante un di├ílogo de confirmaci├│n seguro (Alert Dialog).
+
+## 2. Arquitectura y Componentes Involucrados
+
+### 2.1 Base de Datos & Repositorio
+- **Archivo:** `src/infraestructura/persistencia/repositorio_ipc_postgres.py`
+- **Situaci├│n:** El repositorio ya cuenta con el m├®todo `eliminar(self, id_ipc: int) -> bool` que actualiza `ESTADO_REGISTRO = FALSE`.
+- **Acci├│n:** No se requieren cambios en esta capa. Se valid├│ que el repositorio ya soporta la eliminaci├│n l├│gica de manera nativa.
+
+### 2.2 Capa de Aplicaci├│n (Servicios)
+- **Archivo:** `src/aplicacion/servicios/servicio_ipc.py`
+- **Acci├│n:** Agregar el m├®todo `eliminar_ipc(self, id_ipc: int, usuario: str) -> bool`. Este m├®todo delegar├í la responsabilidad de la eliminaci├│n l├│gica al repositorio y validar├í que el registro exista.
+  - **Firma propuesta:**
+    ```python
+    def eliminar_ipc(self, id_ipc: int, usuario: str) -> bool:
+        """Realiza soft delete de un registro IPC."""
+        pass
+    ```
+
+### 2.3 Capa de Presentaci├│n: Estado (State)
+- **Archivo:** `src/presentacion_reflex/state/ipc_state.py`
+- **Acci├│n:**
+  - Agregar variables de estado reactivas: `show_delete_dialog: bool = False` e `ipc_to_delete: Optional[IPC] = None`.
+  - Agregar m├®todos s├¡ncronos de UI: `confirm_delete_ipc(self, ipc: IPC)` para abrir el modal, y `cancel_delete(self)` para cerrarlo.
+  - Agregar evento as├¡ncrono en background: `@rx.event(background=True) async def delete_ipc(self)` para invocar `servicio.eliminar_ipc`, recargar la lista con `servicio.listar_todos()`, actualizar el estado `ipcs` y manejar errores de forma centralizada.
+
+### 2.4 Capa de Presentaci├│n: Interfaz de Usuario (UI)
+- **Archivo:** `src/presentacion_reflex/pages/incrementos.py`
+- **Acci├│n:**
+  - **Di├ílogo de Confirmaci├│n:** Crear componente `delete_ipc_dialog() -> rx.Component` utilizando `rx.alert_dialog` para prevenir eliminaciones accidentales. Mostrar├í un mensaje de advertencia y botones de "Cancelar" y "Eliminar".
+  - **Tabla de Registros:** En el componente `ipc_table()`, actualizar la columna de "Acciones" envolviendo los botones en un `rx.hstack`. Agregar el bot├│n "Eliminar" (├¡cono `trash-2`, variante rojo) y protegerlo con validaci├│n RBAC (`AuthState.check_action("Incrementos", "ELIMINAR")`).
+  - **Layout Principal:** Agregar la instancia de `delete_ipc_dialog()` dentro del componente contenedor `incrementos_content()`.
+
+## 3. Flujo de Datos (Data Flow)
+1. Usuario clickea el bot├│n "Eliminar" (├ìcono papelera) en la tabla `ipc_table`.
+2. Se dispara `IPCState.confirm_delete_ipc(ipc)`: Guarda el IPC objetivo y activa `show_delete_dialog = True`.
+3. El frontend renderiza y abre el `delete_ipc_dialog`.
+4. El usuario confirma clickeando "Eliminar".
+5. Se dispara `IPCState.delete_ipc()` en modo background:
+   - Extrae el ID del IPC y el usuario actual de `AuthState`.
+   - Llama a `ServicioIPC.eliminar_ipc()`.
+   - `ServicioIPC` llama a `RepositorioIPCPostgres.eliminar()`.
+   - `RepositorioIPCPostgres` ejecuta el SQL: `UPDATE IPC SET ESTADO_REGISTRO = FALSE WHERE ID_IPC = %s`.
+   - `ServicioIPC` vuelve a cargar la lista filtrada (`WHERE ESTADO_REGISTRO = TRUE`) y el estado se actualiza.
+6. El frontend cierra el di├ílogo de forma reactiva y la tabla se redibuja sin recargar la p├ígina.
+
+## 4. Manejo de Errores
+- Si ocurre un error a nivel de base de datos o servicio, `IPCState.delete_ipc` atrapar├í la excepci├│n, setear├í `self.error_message` y deshabilitar├í el modo carga (`is_loading = False`), mostrando autom├íticamente un *callout* de alerta global configurado actualmente en la vista.
+
+## 5. Pruebas y Criterios de Aceptaci├│n
+1. **Validaci├│n de UI:** El bot├│n "Eliminar" debe estar disponible y visible solo para usuarios con el rol adecuado.
+2. **Prevenci├│n de Errores:** Al hacer click en "Eliminar", un modal de confirmaci├│n debe aparecer obligatoriamente (bloqueando interacci├│n del resto de la pantalla).
+3. **Persistencia (Soft Delete):** Al aprobar la eliminaci├│n, el registro debe desaparecer de la grilla del frontend de inmediato, pero en la base de datos la fila debe preservarse con `estado_registro = FALSE` o `0`.
+4. **Resiliencia:** Si la eliminaci├│n falla por cualquier motivo, el usuario debe recibir un mensaje de error legible y la interfaz no debe quedar colgada en estado de carga.
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

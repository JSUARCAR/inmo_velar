# Especificación Técnica: Funcionalidad "Eliminar IPC"

## 1. Resumen Ejecutivo
Implementar la acción "Eliminar" en el módulo de Gestión de IPC / Incrementos. La solución utilizará un enfoque de eliminación lógica ("Soft Delete") para preservar el histórico de datos y la integridad referencial, habilitando la acción desde la UI (tabla de IPC) mediante un diálogo de confirmación seguro (Alert Dialog).

## 2. Arquitectura y Componentes Involucrados

### 2.1 Base de Datos & Repositorio
- **Archivo:** `src/infraestructura/persistencia/repositorio_ipc_postgres.py`
- **Situación:** El repositorio ya cuenta con el método `eliminar(self, id_ipc: int) -> bool` que actualiza `ESTADO_REGISTRO = FALSE`.
- **Acción:** No se requieren cambios en esta capa. Se validó que el repositorio ya soporta la eliminación lógica de manera nativa.

### 2.2 Capa de Aplicación (Servicios)
- **Archivo:** `src/aplicacion/servicios/servicio_ipc.py`
- **Acción:** Agregar el método `eliminar_ipc(self, id_ipc: int, usuario: str) -> bool`. Este método delegará la responsabilidad de la eliminación lógica al repositorio y validará que el registro exista.
  - **Firma propuesta:**
    ```python
    def eliminar_ipc(self, id_ipc: int, usuario: str) -> bool:
        """Realiza soft delete de un registro IPC."""
        pass
    ```

### 2.3 Capa de Presentación: Estado (State)
- **Archivo:** `src/presentacion_reflex/state/ipc_state.py`
- **Acción:**
  - Agregar variables de estado reactivas: `show_delete_dialog: bool = False` e `ipc_to_delete: Optional[IPC] = None`.
  - Agregar métodos síncronos de UI: `confirm_delete_ipc(self, ipc: IPC)` para abrir el modal, y `cancel_delete(self)` para cerrarlo.
  - Agregar evento asíncrono en background: `@rx.event(background=True) async def delete_ipc(self)` para invocar `servicio.eliminar_ipc`, recargar la lista con `servicio.listar_todos()`, actualizar el estado `ipcs` y manejar errores de forma centralizada.

### 2.4 Capa de Presentación: Interfaz de Usuario (UI)
- **Archivo:** `src/presentacion_reflex/pages/incrementos.py`
- **Acción:**
  - **Diálogo de Confirmación:** Crear componente `delete_ipc_dialog() -> rx.Component` utilizando `rx.alert_dialog` para prevenir eliminaciones accidentales. Mostrará un mensaje de advertencia y botones de "Cancelar" y "Eliminar".
  - **Tabla de Registros:** En el componente `ipc_table()`, actualizar la columna de "Acciones" envolviendo los botones en un `rx.hstack`. Agregar el botón "Eliminar" (ícono `trash-2`, variante rojo) y protegerlo con validación RBAC (`AuthState.check_action("Incrementos", "ELIMINAR")`).
  - **Layout Principal:** Agregar la instancia de `delete_ipc_dialog()` dentro del componente contenedor `incrementos_content()`.

## 3. Flujo de Datos (Data Flow)
1. Usuario clickea el botón "Eliminar" (Ícono papelera) en la tabla `ipc_table`.
2. Se dispara `IPCState.confirm_delete_ipc(ipc)`: Guarda el IPC objetivo y activa `show_delete_dialog = True`.
3. El frontend renderiza y abre el `delete_ipc_dialog`.
4. El usuario confirma clickeando "Eliminar".
5. Se dispara `IPCState.delete_ipc()` en modo background:
   - Extrae el ID del IPC y el usuario actual de `AuthState`.
   - Llama a `ServicioIPC.eliminar_ipc()`.
   - `ServicioIPC` llama a `RepositorioIPCPostgres.eliminar()`.
   - `RepositorioIPCPostgres` ejecuta el SQL: `UPDATE IPC SET ESTADO_REGISTRO = FALSE WHERE ID_IPC = %s`.
   - `ServicioIPC` vuelve a cargar la lista filtrada (`WHERE ESTADO_REGISTRO = TRUE`) y el estado se actualiza.
6. El frontend cierra el diálogo de forma reactiva y la tabla se redibuja sin recargar la página.

## 4. Manejo de Errores
- Si ocurre un error a nivel de base de datos o servicio, `IPCState.delete_ipc` atrapará la excepción, seteará `self.error_message` y deshabilitará el modo carga (`is_loading = False`), mostrando automáticamente un *callout* de alerta global configurado actualmente en la vista.

## 5. Pruebas y Criterios de Aceptación
1. **Validación de UI:** El botón "Eliminar" debe estar disponible y visible solo para usuarios con el rol adecuado.
2. **Prevención de Errores:** Al hacer click en "Eliminar", un modal de confirmación debe aparecer obligatoriamente (bloqueando interacción del resto de la pantalla).
3. **Persistencia (Soft Delete):** Al aprobar la eliminación, el registro debe desaparecer de la grilla del frontend de inmediato, pero en la base de datos la fila debe preservarse con `estado_registro = FALSE` o `0`.
4. **Resiliencia:** Si la eliminación falla por cualquier motivo, el usuario debe recibir un mensaje de error legible y la interfaz no debe quedar colgada en estado de carga.

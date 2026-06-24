# Eliminar IPC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar la funcionalidad de eliminación lógica (Soft Delete) de los registros de IPC, agregando el servicio y las acciones de interfaz en Reflex con un diálogo de confirmación.

**Architecture:** Se utilizará el método existente `eliminar()` en `RepositorioIPCPostgres` que ya hace soft delete. Se expondrá mediante un nuevo método `eliminar_ipc()` en `ServicioIPC`, y se controlará desde el frontend en `IPCState` utilizando `rx.alert_dialog` para seguridad, y actualizando la UI atómicamente.

**Tech Stack:** Python 3, Reflex, PostgreSQL.

## Global Constraints

- Backend y UI en español.
- Usar `ESTADO_REGISTRO = FALSE` o `0` (implícito en la query del repo) para soft delete.
- Requerir `AuthState.check_action("Incrementos", "ELIMINAR")` en la UI.
- No mutar listas directamente; recargar `ipcs` desde el backend o usar mecanismos seguros de Reflex.

---

### Task 1: Capa de Aplicación - Servicio IPC

**Files:**
- Modify: `src/aplicacion/servicios/servicio_ipc.py`

**Interfaces:**
- Consumes: `RepositorioIPCPostgres.eliminar(id_ipc: int)` y `RepositorioIPCPostgres.obtener_por_id(id_ipc: int)`.
- Produces: Método `eliminar_ipc(self, id_ipc: int, usuario: str) -> bool` utilizable por Reflex state.

- [ ] **Step 1: Write minimal implementation**

En el archivo `src/aplicacion/servicios/servicio_ipc.py`, agregar el siguiente método al final de la clase `ServicioIPC`:

```python
    def eliminar_ipc(self, id_ipc: int, usuario: str) -> bool:
        """
        Elimina un registro de IPC (soft delete).
        Valida que el registro exista antes de eliminar.
        """
        ipc = self.repo.obtener_por_id(id_ipc)
        if not ipc:
            raise ValueError("Registro IPC no encontrado")

        exito = self.repo.eliminar(id_ipc)
        return exito
```

- [ ] **Step 2: Commit**

```bash
git add src/aplicacion/servicios/servicio_ipc.py
git commit -m "feat(ipc): agregar metodo eliminar_ipc al servicio"
```

---

### Task 2: Capa de Presentación - Estado y Lógica (IPCState)

**Files:**
- Modify: `src/presentacion_reflex/state/ipc_state.py`

**Interfaces:**
- Consumes: `ServicioIPC.eliminar_ipc` implementado en Task 1.
- Produces: Estado reactivo `show_delete_dialog`, `ipc_to_delete`, y eventos para el frontend `confirm_delete_ipc`, `cancel_delete`, `delete_ipc`.

- [ ] **Step 1: Modify IPCState variables and synchronous methods**

En `src/presentacion_reflex/state/ipc_state.py`, debajo de las variables de "Form Modal State" (aprox. línea 23):

```python
    # Delete Modal State
    show_delete_dialog: bool = False
    ipc_to_delete_id: int = 0
    ipc_to_delete_anio: int = 0

    def confirm_delete_ipc(self, ipc: IPC):
        self.ipc_to_delete_id = ipc.id_ipc
        self.ipc_to_delete_anio = ipc.anio
        self.show_delete_dialog = True
        
    def cancel_delete(self):
        self.show_delete_dialog = False
        self.ipc_to_delete_id = 0
        self.ipc_to_delete_anio = 0
```
*(Nota: Reflex maneja mejor tipos primitivos que almacenar instancias completas de `IPC` en el estado).*

- [ ] **Step 2: Write background event for deletion**

Al final de la clase `IPCState`:

```python
    @rx.event(background=True)
    async def delete_ipc(self):
        """Elimina el IPC seleccionado."""
        async with self:
            if not self.ipc_to_delete_id:
                return
            self.is_loading = True
            self.error_message = ""
            current_user = await self.get_state(AuthState)
            usuario = current_user.user_nombre if current_user.is_authenticated else "sistema"
            id_ipc = self.ipc_to_delete_id

        try:
            servicio = ServicioIPC(db_manager)
            servicio.eliminar_ipc(id_ipc, usuario)
            
            # Recargar y cerrar
            lista = servicio.listar_todos()

            async with self:
                self.ipcs = lista
                self.show_delete_dialog = False
                self.ipc_to_delete_id = 0
                self.ipc_to_delete_anio = 0
                self.is_loading = False

        except Exception as e:
            logger.error(f"Error eliminando IPC: {e}")
            async with self:
                self.error_message = str(e)
                self.is_loading = False
```

- [ ] **Step 3: Commit**

```bash
git add src/presentacion_reflex/state/ipc_state.py
git commit -m "feat(ipc): agregar estado reactivo y eventos para eliminar IPC"
```

---

### Task 3: Capa de Presentación - Interfaz (Frontend Reflex)

**Files:**
- Modify: `src/presentacion_reflex/pages/incrementos.py`

**Interfaces:**
- Consumes: Las variables de estado `IPCState.show_delete_dialog`, `IPCState.ipc_to_delete_anio` y los eventos de `IPCState`.

- [ ] **Step 1: Add Delete Confirmation Dialog component**

En `src/presentacion_reflex/pages/incrementos.py`, antes de `ipc_table()`:

```python
def delete_ipc_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Confirmar Eliminación"),
            rx.alert_dialog.description(
                "¿Está seguro que desea eliminar el IPC del año ",
                rx.text(IPCState.ipc_to_delete_anio, weight="bold"),
                "? Esta acción inhabilitará el registro.",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=IPCState.cancel_delete,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Eliminar",
                        color_scheme="red",
                        variant="solid",
                        on_click=IPCState.delete_ipc,
                        loading=IPCState.is_loading,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=IPCState.show_delete_dialog,
        on_open_change=lambda val: rx.cond(
            val, 
            rx.do_nothing(), 
            IPCState.cancel_delete()
        ),
    )
```

- [ ] **Step 2: Update IPC Table to include the Delete button**

Reemplazar la celda actual de "Acciones" en la función `ipc_table()`:
*(Se debe usar `replace_file_content` cuidadosamente para actualizar `rx.table.cell` en la línea 84-97 aprox).*

```python
                    rx.table.cell(
                        rx.hstack(
                            rx.cond(
                                AuthState.check_action("Incrementos", "EDITAR"),
                                rx.tooltip(
                                    rx.button(
                                        rx.icon("pencil", size=16),
                                        size="1",
                                        variant="ghost",
                                        on_click=lambda: IPCState.open_edit_modal(ipc),
                                    ),
                                    content="Editar IPC",
                                ),
                            ),
                            rx.cond(
                                AuthState.check_action("Incrementos", "ELIMINAR"),
                                rx.tooltip(
                                    rx.button(
                                        rx.icon("trash-2", size=16),
                                        size="1",
                                        variant="ghost",
                                        color_scheme="red",
                                        on_click=lambda: IPCState.confirm_delete_ipc(ipc),
                                    ),
                                    content="Eliminar IPC",
                                ),
                            ),
                            spacing="2",
                        )
                    ),
```

- [ ] **Step 3: Add dialog to the main view**

En `incrementos_content()`, debajo de `ipc_modal(),` (aprox. línea 130), agregar `delete_ipc_dialog(),`.

```python
        rx.cond(
            IPCState.is_loading
            & ~IPCState.show_modal,  # Show spinner if loading and modal not open (initial load)
            rx.center(rx.spinner()),
            ipc_table(),
        ),
        ipc_modal(),
        delete_ipc_dialog(),
        spacing="5",
```

- [ ] **Step 4: Verify with type checking and commit**

```bash
git add src/presentacion_reflex/pages/incrementos.py
git commit -m "feat(ipc): integrar modal y boton de eliminacion en UI"
```

- [ ] **Step 5: E2E Manual testing Check**

Levantar el entorno de prueba/dev y confirmar visualmente que el modal se abre, el año aparece correcto y tras presionar "Eliminar", desaparece de la tabla sin fallos.

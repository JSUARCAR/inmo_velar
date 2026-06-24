from typing import List

import reflex as rx

from src.aplicacion.servicios.servicio_ipc import ServicioIPC
from src.dominio.entidades.ipc import IPC
from src.infraestructura.logging.logger import logger
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.auth_state import AuthState


class IPCState(rx.State):
    """Estado para gestión de IPC."""

    ipcs: List[IPC] = []
    is_loading: bool = False
    error_message: str = ""

    # Form Modal State
    show_modal: bool = False
    is_editing: bool = False
    current_ipc_id: int = 0

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

    def set_show_modal(self, value: bool):
        self.show_modal = value

    # Form Fields
    form_anio: int = 2025
    form_valor: float = 0.0

    def set_anio(self, value: str):
        """Setter personalizado para manejar conversión str -> int del input."""
        if value == "" or value is None:
            self.form_anio = 0
        else:
            try:
                self.form_anio = int(value)
            except ValueError:
                pass  # Mantener valor anterior o 0

    def set_valor(self, value: str):
        """Setter personalizado para manejar conversión str -> float del input."""
        if value == "" or value is None:
            self.form_valor = 0.0
        else:
            try:
                self.form_valor = float(value)
            except ValueError:
                pass

    @rx.event(background=True)
    async def load_ipcs(self):
        """Carga lista de IPCs."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIPC(db_manager)
            lista = servicio.listar_todos()

            async with self:
                self.ipcs = lista
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    def open_create_modal(self):
        self.is_editing = False
        self.form_anio = 2025  # Default next year?
        self.form_valor = 0.0
        self.show_modal = True

    def open_edit_modal(self, ipc: IPC):
        self.is_editing = True
        self.current_ipc_id = ipc.id_ipc
        self.form_anio = ipc.anio
        self.form_valor = ipc.valor_ipc
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    @rx.event(background=True)
    async def save_ipc(self):
        """Guarda o actualiza IPC."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            current_user = await self.get_state(AuthState)
            usuario = current_user.user_nombre if current_user.is_authenticated else "sistema"

        try:
            servicio = ServicioIPC(db_manager)

            if self.is_editing:
                servicio.actualizar_ipc(self.current_ipc_id, self.form_valor, usuario)
            else:
                servicio.crear_ipc(self.form_anio, self.form_valor, usuario)

            # Recargar y cerrar
            lista = servicio.listar_todos()

            async with self:
                self.ipcs = lista
                self.show_modal = False
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

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

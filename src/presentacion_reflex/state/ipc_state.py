from typing import List

import reflex as rx

from src.aplicacion.servicios.servicio_ipc import ServicioIPC
from src.dominio.entidades.ipc import IPC
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

    def set_show_modal(self, value: bool):
        self.show_modal = value

    @rx.event(background=True)
    async def save_ipc(self):
        """Guarda o actualiza IPC."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            logger.info("IPCState.save_ipc: Attempting to retrieve AuthState")
            current_user = await self.get_state(AuthState)
            
            # Diagnóstico de estructura
            has_user = hasattr(current_user, "user")
            has_user_info = hasattr(current_user, "user_info")
            logger.info(f"AuthState Check - has_user: {has_user}, has_user_info: {has_user_info}")
            
            if has_user_info:
                u_info = current_user.user_info
                logger.info(f"User Info present: {u_info is not None}")
                usuario = u_info["nombre_usuario"] if u_info else "sistema"
            elif has_user:
                logger.warning("Legacy 'user' attribute detected in AuthState - This should not happen!")
                usuario = "sistema_legacy"
            else:
                logger.error("Neither 'user' nor 'user_info' found in AuthState")
                usuario = "sistema_unknown"

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

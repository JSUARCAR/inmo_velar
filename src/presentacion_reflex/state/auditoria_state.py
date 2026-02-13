from typing import List

import reflex as rx
from pydantic import BaseModel

from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.infraestructura.persistencia.database import db_manager


class AuditLogModel(BaseModel):
    """Modelo serializable para registros de auditoría."""

    id_auditoria: int
    fecha_cambio: str
    usuario: str
    tabla: str
    accion: str
    detalle: str
    color_scheme: str


class AuditoriaState(rx.State):
    """Estado para la gestión de Auditoría."""

    logs: List[AuditLogModel] = []
    is_loading: bool = False
    error_message: str = ""

    # Filtros
    filter_tabla: str = "Todas"
    search_query: str = ""

    @rx.event(background=True)
    async def load_logs(self):
        """Carga los registros de auditoría."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioConfiguracion(db_manager)

            # Obtener datos del backend
            if self.filter_tabla != "Todas":
                entidades = servicio.buscar_auditoria_por_tabla(self.filter_tabla, limit=100)
            else:
                entidades = servicio.listar_auditoria(limit=100)

            # Filtrado en memoria por búsqueda de texto (detalle/usuario)
            if self.search_query:
                q = self.search_query.lower()
                entidades = [
                    e
                    for e in entidades
                    if (e.usuario and q in e.usuario.lower())
                    or (e.campo and q in e.campo.lower())
                    or (e.motivo_cambio and q in e.motivo_cambio.lower())
                ]

            # Mapeo a modelo Reflex
            modelos = []
            for ent in entidades:
                # Construir detalle legible
                detalle_str = f"Reg: {ent.id_registro}"
                if ent.campo:
                    detalle_str += f" | {ent.campo}: {ent.valor_anterior or 'None'} -> {ent.valor_nuevo or 'None'}"
                elif ent.motivo_cambio:
                    detalle_str += f" | Motivo: {ent.motivo_cambio}"

                # Determinar color
                color = "blue"
                if ent.accion == "INSERT":
                    color = "green"
                elif ent.accion == "UPDATE":
                    color = "orange"
                elif ent.accion == "DELETE":
                    color = "red"

                modelos.append(
                    AuditLogModel(
                        id_auditoria=ent.id_auditoria,
                        fecha_cambio=ent.fecha_cambio or "",
                        usuario=ent.usuario or "Sistema",
                        tabla=ent.tabla or "Desconocida",
                        accion=ent.accion or "UNKNOWN",
                        detalle=detalle_str,
                        color_scheme=color,
                    )
                )

            async with self:
                self.logs = modelos
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    def set_filter_tabla(self, value: str):
        self.filter_tabla = value

    def set_search(self, value: str):
        self.search_query = value

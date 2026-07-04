import reflex as rx
from typing import List, Dict, Any
from datetime import datetime
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import (
    RepositorioAsesorPostgres,
)


class LiquidacionFiltrosState(rx.State):
    """Maneja únicamente los filtros y opciones de selección del módulo."""

    search_text: str = ""
    filter_estado: str = "Todos"
    filter_periodo: str = ""
    filter_asesor: str = ""

    estado_options: List[str] = ["Todos", "Pendiente", "Aprobada", "Pagada", "Anulada"]
    periodo_options: List[str] = []
    asesores_options: List[Dict[str, Any]] = []
    asesores_select_options: List[str] = []

    @rx.event(background=True)
    async def load_filter_options(self):
        try:
            repo_asesor = RepositorioAsesorPostgres(db_manager)
            asesores_entidades = repo_asesor.listar_activos()

            asesores = [
                {
                    "id": str(a.id_asesor),
                    "texto": a.nombre_completo,
                }
                for a in asesores_entidades
            ]

            from dateutil.relativedelta import relativedelta

            periodos = [
                (datetime.now() - relativedelta(months=i)).strftime("%Y-%m")
                for i in range(24)
            ]

            async with self:
                self.asesores_options = asesores
                self.asesores_select_options = [a["texto"] for a in asesores]
                self.periodo_options = periodos
        except Exception:
            pass

    def set_search(self, value: str):
        self.search_text = value

    def set_filter_estado(self, value: str):
        self.filter_estado = value

    def set_filter_periodo(self, value: str):
        self.filter_periodo = value

    def set_filter_asesor(self, value: str):
        self.filter_asesor = value

from typing import Optional

from src.dominio.entidades.incidente import Incidente
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioCostosIncidentes:
    def __init__(
        self,
        db_manager: DatabaseManager,
        repo_incidentes: Optional[RepositorioIncidentes] = None,
    ):
        self.db_manager = db_manager
        self.repo_incidentes = repo_incidentes

    def _get_repo(self) -> RepositorioIncidentes:
        if self.repo_incidentes is None:
            from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                RepositorioIncidentesPostgres,
            )

            return RepositorioIncidentesPostgres(self.db_manager)
        return self.repo_incidentes

    def calcular_costos_por_periodo(self, id_contrato_m: int, mes_anio: str) -> int:
        """
        Retorna la suma de costos de incidentes Aprobados/Finalizados en un mes dado,
        cuyo responsable de pago sea el Propietario.
        Útil para integración financiera.
        """
        repo = self._get_repo()
        incidentes = repo.listar()

        total = 0
        for inc in incidentes:
            if (
                inc.id_contrato_m == id_contrato_m
                and inc.responsable_pago == "Propietario"
            ):
                from datetime import datetime

                fecha_ref = inc.fecha_arreglo or inc.updated_at
                if fecha_ref:
                    if isinstance(fecha_ref, str):
                        fecha_ref = datetime.fromisoformat(fecha_ref)
                    if fecha_ref.strftime("%Y-%m") == mes_anio:
                        total += inc.costo_incidente
        return total

    def calcular_costos_por_propiedad(
        self, id_propiedad: int, estado: Optional[str] = None
    ) -> int:
        """
        Calcula el costo total de incidentes para una propiedad.
        Si estado es especificado, filtra por ese estado.
        """
        repo = self._get_repo()
        incidentes = repo.listar(id_propiedad=id_propiedad, estado=estado)

        return sum(inc.costo_incidente for inc in incidentes)

    def calcular_costos_por_proveedor(self, id_proveedor: int) -> int:
        """
        Calcula el costo total de incidentes asignados a un proveedor.
        """
        repo = self._get_repo()
        incidentes = repo.listar()

        total = 0
        for inc in incidentes:
            if inc.id_proveedor_asignado == id_proveedor:
                total += inc.costo_incidente
        return total

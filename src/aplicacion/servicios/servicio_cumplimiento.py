"""
Servicio: Cumplimiento
Calcula el estado de cumplimiento de obligaciones financieras de contratos.
"""

from typing import Optional

from src.dominio.value_objects.estado_cumplimiento import (
    EstadoCumplimiento,
    crear_estado_al_dia,
    crear_estado_pendiente,
    obtener_periodo_actual,
)
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_liquidacion_postgres import (
    RepositorioLiquidacionPostgres,
)
from src.infraestructura.persistencia.repositorio_recaudo import RepositorioRecaudo

DIAS_GRACIA_DEFAULT: int = 5


class ServicioCumplimiento:
    """
    Servicio para calcular el estado de cumplimiento de contratos.

    Para Mandato: consulta Liquidaciones (estado 'Pagada' = Al día)
    Para Arrendamiento: consulta Recaudos (estado 'Aplicado' = Al día)
    """

    def __init__(self, db_manager=None):
        self.db = db_manager or db_manager
        self.repo_liquidacion = RepositorioLiquidacionPostgres(self.db)
        self.repo_recaudo = RepositorioRecaudo(self.db)
        self.dias_gracia = DIAS_GRACIA_DEFAULT

    def obtener_estado_contrato(
        self,
        tipo_contrato: str,
        id_contrato: int,
        periodo: Optional[str] = None,
    ) -> EstadoCumplimiento:
        """
        Calcula el estado de cumplimiento de un contrato.

        Args:
            tipo_contrato: 'Mandato' o 'Arrendamiento'
            id_contrato: ID del contrato
            periodo: Período a evaluar (default: período actual)

        Returns:
            EstadoCumplimiento con el estado calculado
        """
        periodo = periodo or obtener_periodo_actual()

        if tipo_contrato == "Mandato":
            return self._calcular_estado_mandato(id_contrato, periodo)
        elif tipo_contrato == "Arrendamiento":
            return self._calcular_estado_arrendamiento(id_contrato, periodo)
        else:
            raise ValueError(f"Tipo de contrato inválido: {tipo_contrato}")

    def _calcular_estado_mandato(
        self, id_contrato_m: int, periodo: str
    ) -> EstadoCumplimiento:
        """
        Calcula el estado de cumplimiento para contrato de Mandato.
        Consulta la liquidación del período en LIQUIDACIONES.
        """
        try:
            liquidacion = self.repo_liquidacion.obtener_por_contrato_y_periodo(
                id_contrato_m, periodo
            )
        except Exception:
            liquidacion = None

        if liquidacion:
            if liquidacion.estado_liquidacion == "Pagada":
                return crear_estado_al_dia(
                    tipo_contrato="Mandato",
                    id_contrato=id_contrato_m,
                    periodo=periodo,
                    fecha_registro=liquidacion.fecha_pago,
                )
            elif liquidacion.estado_liquidacion in ("En Proceso", "Aprobada"):
                return crear_estado_pendiente(
                    tipo_contrato="Mandato",
                    id_contrato=id_contrato_m,
                    periodo=periodo,
                )

        return crear_estado_pendiente(
            tipo_contrato="Mandato",
            id_contrato=id_contrato_m,
            periodo=periodo,
        )

    def _calcular_estado_arrendamiento(
        self, id_contrato_a: int, periodo: str
    ) -> EstadoCumplimiento:
        """
        Calcula el estado de cumplimiento para contrato de Arrendamiento.
        Consulta los recaudos del período en RECAUDOS.
        """
        try:
            recaudos = self.repo_recaudo.listar_por_contrato(id_contrato_a)
        except Exception:
            recaudos = []

        periodo_buscar = periodo
        recaudo_en_periodo = None

        for recaudo in recaudos:
            if recaudo.estado_recaudo == "Aplicado" and periodo_buscar in str(
                recaudo.periodo
            ):
                recaudo_en_periodo = recaudo
                break

        if recaudo_en_periodo:
            return crear_estado_al_dia(
                tipo_contrato="Arrendamiento",
                id_contrato=id_contrato_a,
                periodo=periodo,
                fecha_registro=recaudo_en_periodo.fecha_pago,
            )

        return crear_estado_pendiente(
            tipo_contrato="Arrendamiento",
            id_contrato=id_contrato_a,
            periodo=periodo,
        )

    def obtener_estados_contratos(
        self,
        tipo_contrato: str,
        ids_contrato: list[int],
        periodo: Optional[str] = None,
    ) -> dict[int, EstadoCumplimiento]:
        """
        Calcula estados para múltiples contratos.
        Optimizado para evitar N+1 queries.

        Args:
            tipo_contrato: 'Mandato' o 'Arrendamiento'
            ids_contrato: Lista de IDs de contratos
            periodo: Período a evaluar

        Returns:
            Diccionario {id_contrato: EstadoCumplimiento}
        """
        periodo = periodo or obtener_periodo_actual()
        resultados = {}

        for id_contrato in ids_contrato:
            resultados[id_contrato] = self.obtener_estado_contrato(
                tipo_contrato, id_contrato, periodo
            )

        return resultados


def calcular_estado_cumplimiento_contrato(
    tipo_contrato: str,
    id_contrato: int,
    periodo: Optional[str] = None,
) -> EstadoCumplimiento:
    """
    Función de conveniencia para calcular estado de cumplimiento.
    Útil para usar en UI sin instanciar servicio.
    """
    servicio = ServicioCumplimiento(db_manager)
    return servicio.obtener_estado_contrato(tipo_contrato, id_contrato, periodo)

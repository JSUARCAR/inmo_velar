"""
Servicio para actualización automática del estado de pago de incidentes.
Se ejecuta cuando una liquidación cambia de estado (Pagada o Reversión).

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from typing import Dict

from src.dominio.interfaces.repositorio_plan_pago import RepositorioPlanPago
from src.dominio.interfaces.repositorio_cuota import RepositorioCuota
from src.dominio.interfaces.repositorio_incidente_liq import (
    RepositorioIncidenteLiquidacion,
)
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import db_manager

logger = logging.getLogger(__name__)


class ServicioEstadoPagoAutomatico:
    """
    Servicio para actualizar automáticamente el estado de pago de incidentes
    cuando el estado de una liquidación cambia.

    Responsibilities:
    - Recalcular estado_pago de incidentes cuando liquidación se marca como Pagada
    - Recalcular estado_pago de incidentes cuando liquidación se revierte
    - Mantener consistencia entre liquidaciones pagadas y estado de incidentes
    """

    def __init__(
        self,
        repositorio_plan: RepositorioPlanPago,
        repositorio_cuota: RepositorioCuota,
        repositorio_relacion: RepositorioIncidenteLiquidacion,
        repositorio_incidentes: RepositorioIncidentes,
    ):
        self.repositorio_plan = repositorio_plan
        self.repositorio_cuota = repositorio_cuota
        self.repositorio_relacion = repositorio_relacion
        self.repositorio_incidentes = repositorio_incidentes

    def actualizar_estado_pago_por_liquidacion(
        self,
        id_liquidacion: int,
        usuario: str,
    ) -> Dict[str, any]:
        """
        Actualiza el estado de pago de todos los incidentes asociados a una liquidación.
        Se llama cuando la liquidación cambia de estado (Pagada o Reversión).

        Args:
            id_liquidacion: ID de la liquidación que cambió de estado
            usuario: Usuario que realizó la operación

        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 1. Obtener todas las cuotas de esta liquidación
                cuotas = self.repositorio_cuota.obtener_por_liquidacion(id_liquidacion)

                if not cuotas:
                    return {
                        "success": True,
                        "data": {"incidentes_actualizados": 0},
                        "message": "No hay cuotas asociadas a esta liquidación",
                    }

                # 2. Para cada incidente asociado (vía plan de pago), recalcular su estado de pago
                incidentes_actualizados = 0
                planes_procesados = set()
                
                for cuota in cuotas:
                    if cuota.id_plan_pago in planes_procesados:
                        continue
                        
                    planes_procesados.add(cuota.id_plan_pago)
                    plan = self.repositorio_plan.obtener_por_id(cuota.id_plan_pago)
                    
                    if plan:
                        resultado = self.recalcular_estado_pago_incidente(
                            plan.id_incidente, usuario
                        )
                        if resultado.get("success"):
                            incidentes_actualizados += 1

                logger.info(
                    f"Estados de pago actualizados para liquidación {id_liquidacion}: "
                    f"{incidentes_actualizados} incidentes"
                )

            return {
                "success": True,
                "data": {"incidentes_actualizados": incidentes_actualizados},
                "message": f"{incidentes_actualizados} incidente(s) actualizado(s)",
            }

        except Exception as e:
            logger.error(f"Error al actualizar estados de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al actualizar estados: {str(e)}",
            }

    def recalcular_estado_pago_incidente(
        self,
        id_incidente: int,
        usuario: str,
    ) -> Dict[str, any]:
        """
        Recalcula el estado de pago de un incidente específico.

        Lógica:
        - Si tiene plan activo y todas sus cuotas asociadas a liquidaciones Pagadas → "Pagado"
        - Si tiene plan activo y algunas cuotas asociadas a liquidaciones Pagadas → "Parcialmente Pagado"
        - Si tiene plan activo pero ninguna cuota a liquidación Pagada → "Pendiente"
        - Si no tiene plan activo → "Pendiente"

        Args:
            id_incidente: ID del incidente
            usuario: Usuario que realizó la operación

        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 1. Obtener el plan activo del incidente
                plan = self.repositorio_plan.obtener_por_incidente(id_incidente)

            if not plan:
                # Sin plan activo, estado sigue pendiente
                return {
                    "success": True,
                    "data": {"estado_pago": "Pendiente"},
                }

            # 2. Obtener conteo de cuotas asociadas y pagadas optimizado (T080)
            total_con_liq, cuotas_pagadas = (
                self.repositorio_cuota.contar_estado_liquidaciones_por_plan(
                    plan.id_plan_pago
                )
            )

            if plan.num_cuotas == 0:
                # Fallback defensivo
                nuevo_estado = "Pendiente"
            else:
                # 5. Determinar estado de pago en base al total de cuotas del plan
                if cuotas_pagadas == plan.num_cuotas:
                    nuevo_estado = "Pagado"
                elif cuotas_pagadas > 0:
                    nuevo_estado = "Parcialmente Pagado"
                else:
                    nuevo_estado = "Pendiente"

            # 6. Actualizar estado del incidente
            incidente = self.repositorio_incidentes.obtener_por_id(id_incidente)
            if incidente:
                estado_anterior = incidente.estado_pago
                if estado_anterior != nuevo_estado:
                    import dataclasses
                    incidente_actualizado = dataclasses.replace(incidente, estado_pago=nuevo_estado)
                    self.repositorio_incidentes.actualizar(incidente_actualizado)

                    logger.info(
                        f"Incidente {id_incidente}: estado_pago cambiado "
                        f"de '{estado_anterior}' a '{nuevo_estado}' por {usuario}"
                    )

            return {
                "success": True,
                "data": {"estado_pago": nuevo_estado},
            }

        except Exception as e:
            logger.error(
                f"Error al recalculcar estado de pago del incidente {id_incidente}: {e}"
            )
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al recalcular: {str(e)}",
            }

    def revertir_estado_pago_por_liquidacion(
        self,
        id_liquidacion: int,
        usuario: str,
    ) -> Dict[str, any]:
        """
        Revierte el estado de pago de incidentes cuando una liquidación se revierte de Pagada.
        Actualiza los estados de pago de todos los incidentes asociados.

        Args:
            id_liquidacion: ID de la liquidación que se revirtió
            usuario: Usuario que realizó la reversión

        Returns:
            Dict con resultado de la operación
        """
        return self.actualizar_estado_pago_por_liquidacion(id_liquidacion, usuario)

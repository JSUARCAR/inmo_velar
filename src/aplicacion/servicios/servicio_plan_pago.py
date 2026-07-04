"""
Servicio para gestión de planes de pago de incidentes.
Implementa la lógica de negocio para definir, modificar y cancelar planes de pago.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from typing import Dict, Optional, Any

from src.dominio.entidades.plan_pago_incidente import PlanPagoIncidente
from src.dominio.interfaces.repositorio_plan_pago import RepositorioPlanPago
from src.dominio.interfaces.repositorio_cuota import RepositorioCuota
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.repositorio_bloqueos import RepositorioBloqueos
from src.infraestructura.persistencia.database import db_manager

logger = logging.getLogger(__name__)


class ServicioPlanPagoIncidente:
    """
    Servicio para gestionar planes de pago de incidentes.

    Responsibilities:
    - Crear planes de pago para incidentes aprobados
    - Modificar planes existentes (si no tienen liquidaciones asociadas)
    - Cancelar planes de pago
    - Consultar información de planes y cuotas
    """

    def __init__(
        self,
        repositorio_plan: RepositorioPlanPago,
        repositorio_cuota: RepositorioCuota,
        repositorio_incidentes: RepositorioIncidentes,
        repositorio_bloqueos: RepositorioBloqueos,
    ):
        self.repositorio_plan = repositorio_plan
        self.repositorio_cuota = repositorio_cuota
        self.repositorio_incidentes = repositorio_incidentes
        self.repositorio_bloqueos = repositorio_bloqueos

    def crear_plan(
        self,
        id_incidente: int,
        num_cuotas: int,
        valor_cuota: int,
        creado_por: str,
        sesion_id: str = "",
    ) -> Dict[str, Any]:
        """
        Crea un nuevo plan de pago para un incidente.

        Args:
            id_incidente: ID del incidente
            num_cuotas: Número de cuotas
            valor_cuota: Valor por cuota
            creado_por: Usuario que crea el plan
            sesion_id: ID de sesión para bloqueo

        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 1. Validar que el incidente existe y está calificado
                incidente = self.repositorio_incidentes.obtener_por_id(id_incidente)
                if not incidente:
                    return {
                        "success": False,
                        "error": "INCIDENTE_NO_ENCONTRADO",
                        "message": "El incidente no existe",
                    }

                if incidente.estado not in ["Aprobado", "En Reparacion", "Finalizado"]:
                    return {
                        "success": False,
                        "error": "INCIDENTE_NO_CALIFICADO",
                        "message": f"El incidente no está en un estado válido para crear plan de pago (estado actual: {incidente.estado})",
                    }

                # 2. Verificar que no exista un plan activo
                plan_existente = self.repositorio_plan.obtener_por_incidente(
                    id_incidente
                )
                if plan_existente and plan_existente.esta_activo():
                    return {
                        "success": False,
                        "error": "PLAN_YA_EXISTE",
                        "message": "Ya existe un plan de pago activo para este incidente",
                    }

                # 3. Validar parámetros
                if num_cuotas < 1:
                    return {
                        "success": False,
                        "error": "CUOTAS_INVALIDAS",
                        "message": "El número de cuotas debe ser mayor a 0",
                    }

            if valor_cuota <= 0:
                return {
                    "success": False,
                    "error": "VALOR_INVALIDO",
                    "message": "El valor de la cuota debe ser mayor a 0",
                }

            # 4. Adquirir bloqueo si se proporciona sesión
            if sesion_id:
                bloqueado = self.repositorio_bloqueos.adquirir_bloqueo(
                    "INCIDENTES", id_incidente, creado_por, sesion_id
                )
                if not bloqueado:
                    return {
                        "success": False,
                        "error": "BLOQUEADO",
                        "message": "El incidente está siendo editado por otro usuario",
                    }

            # 5. Crear el plan
            plan = PlanPagoIncidente.crear(
                id_incidente=id_incidente,
                num_cuotas=num_cuotas,
                valor_cuota=valor_cuota,
                creado_por=creado_por,
            )
            plan = self.repositorio_plan.crear(plan)

            # 6. Crear las cuotas
            cuotas = self.repositorio_cuota.crear_desde_plan(
                plan.id_plan_pago, num_cuotas, valor_cuota
            )

            # 7. Actualizar estado del incidente
            # Nota: El estado_pago se actualizará cuando se asocie a liquidaciones

            logger.info(
                f"Plan de pago creado: {plan.id_plan_pago} para incidente {id_incidente} "
                f"con {num_cuotas} cuotas de ${valor_cuota}"
            )

            return {
                "success": True,
                "data": {
                    "plan": plan.to_dict(),
                    "cuotas": [c.to_dict() for c in cuotas],
                },
                "message": "Plan de pago creado exitosamente",
            }

        except Exception as e:
            logger.error(f"Error al crear plan de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al crear plan de pago: {str(e)}",
            }

    def obtener_plan_por_incidente(self, id_incidente: int) -> Dict[str, Any]:
        """
        Obtiene el plan activo de pago para un incidente.

        Args:
            id_incidente: ID del incidente

        Returns:
            Dict con el plan y sus cuotas
        """
        try:
            plan = self.repositorio_plan.obtener_por_incidente(id_incidente)

            if not plan:
                return {
                    "success": False,
                    "error": "PLAN_NO_ENCONTRADO",
                    "message": "No se encontró un plan de pago activo para este incidente",
                }

            cuotas = self.repositorio_cuota.obtener_por_plan(plan.id_plan_pago)

            return {
                "success": True,
                "data": {
                    "plan": plan.to_dict(),
                    "cuotas": [c.to_dict() for c in cuotas],
                },
            }

        except Exception as e:
            logger.error(f"Error al obtener plan de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al obtener plan de pago: {str(e)}",
            }

    def modificar_plan(
        self,
        id_plan_pago: int,
        num_cuotas: Optional[int] = None,
        valor_cuota: Optional[int] = None,
        modificado_por: str = "",
        justificacion: str = "",
    ) -> Dict[str, Any]:
        """
        Modifica un plan de pago existente.

        Args:
            id_plan_pago: ID del plan a modificar
            num_cuotas: Nuevo número de cuotas (opcional)
            valor_cuota: Nuevo valor por cuota (opcional)
            modificado_por: Usuario que modifica
            justificacion: Justificación de la modificación

        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 0. Validar justificación
                if not justificacion or not justificacion.strip():
                    return {
                        "success": False,
                        "error": "JUSTIFICACION_REQUERIDA",
                        "message": "Se requiere una justificación para modificar el plan",
                    }

                # 1. Obtener el plan
            plan = self.repositorio_plan.obtener_por_id(id_plan_pago)

            if not plan:
                return {
                    "success": False,
                    "error": "PLAN_NO_ENCONTRADO",
                    "message": "El plan de pago no existe",
                }

            # 2. Verificar que el plan pueda modificarse
            if not plan.puede_modificarse():
                return {
                    "success": False,
                    "error": "PLAN_NO_MODIFICABLE",
                    "message": "El plan no puede modificarse (estado actual: {plan.estado})",
                }

            # 3. Verificar que no tenga cuotas asociadas a liquidaciones
            cuotas = self.repositorio_cuota.obtener_por_plan(id_plan_pago)
            cuotas_asociadas = [c for c in cuotas if c.id_liquidacion is not None]

            if cuotas_asociadas:
                return {
                    "success": False,
                    "error": "CUOTAS_ASOCIADAS",
                    "message": "No se puede modificar el plan porque tiene cuotas asociadas a liquidaciones",
                }

            # 4. Actualizar valores
            if num_cuotas is not None:
                if num_cuotas < 1:
                    return {
                        "success": False,
                        "error": "CUOTAS_INVALIDAS",
                        "message": "El número de cuotas debe ser mayor a 0",
                    }
                plan.num_cuotas = num_cuotas

            if valor_cuota is not None:
                if valor_cuota <= 0:
                    return {
                        "success": False,
                        "error": "VALOR_INVALIDO",
                        "message": "El valor de la cuota debe ser mayor a 0",
                    }
                plan.valor_cuota = valor_cuota

            # 5. Recalcular total
            plan.total_plan = plan.num_cuotas * plan.valor_cuota

            # 6. Guardar cambios
            plan = self.repositorio_plan.actualizar(plan)

            # 7. Recrear cuotas con nuevos valores
            # Eliminar cuotas existentes
            for cuota in cuotas:
                self.repositorio_cuota.eliminar(cuota.id_cuota)

            # Crear nuevas cuotas
            nuevas_cuotas = self.repositorio_cuota.crear_desde_plan(
                plan.id_plan_pago, plan.num_cuotas, plan.valor_cuota
            )

            logger.info(f"Plan de pago modificado: {plan.id_plan_pago}")

            return {
                "success": True,
                "data": {
                    "plan": plan.to_dict(),
                    "cuotas": [c.to_dict() for c in nuevas_cuotas],
                },
                "message": "Plan de pago modificado exitosamente",
            }

        except Exception as e:
            logger.error(f"Error al modificar plan de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al modificar plan de pago: {str(e)}",
            }

    def cancelar_plan(
        self,
        id_plan_pago: int,
        cancelado_por: str,
        justificacion: str = "",
    ) -> Dict[str, Any]:
        """
        Cancela un plan de pago.

        Args:
            id_plan_pago: ID del plan a cancelar
            cancelado_por: Usuario que cancela
            justificacion: Justificación de la cancelación

        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 0. Validar justificación
                if not justificacion or not justificacion.strip():
                    return {
                        "success": False,
                        "error": "JUSTIFICACION_REQUERIDA",
                        "message": "Se requiere una justificación para cancelar el plan",
                    }

                # 1. Obtener el plan
            plan = self.repositorio_plan.obtener_por_id(id_plan_pago)

            if not plan:
                return {
                    "success": False,
                    "error": "PLAN_NO_ENCONTRADO",
                    "message": "El plan de pago no existe",
                }

            # 2. Verificar que el plan pueda cancelarse
            if not plan.puede_modificarse():
                return {
                    "success": False,
                    "error": "PLAN_NO_CANCELABLE",
                    "message": "El plan no puede cancelarse (estado actual: {plan.estado})",
                }

            # 3. Verificar que no tenga cuotas asociadas a liquidaciones
            cuotas = self.repositorio_cuota.obtener_por_plan(id_plan_pago)
            cuotas_asociadas = [c for c in cuotas if c.id_liquidacion is not None]

            if cuotas_asociadas:
                return {
                    "success": False,
                    "error": "CUOTAS_ASOCIADAS",
                    "message": "No se puede cancelar el plan porque tiene cuotas asociadas a liquidaciones",
                }

            # 4. Cancelar el plan
            plan.cancelar()
            self.repositorio_plan.actualizar(plan)

            logger.info(
                f"Plan de pago cancelado: {plan.id_plan_pago} por {cancelado_por}"
            )

            return {
                "success": True,
                "data": {"plan": plan.to_dict()},
                "message": "Plan de pago cancelado exitosamente",
            }

        except Exception as e:
            logger.error(f"Error al cancelar plan de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al cancelar plan de pago: {str(e)}",
            }

    def calcular_estado_pago(self, id_incidente: int) -> Dict[str, Any]:
        """
        Calcula el estado de pago de un incidente basado en sus liquidaciones asociadas.

        Args:
            id_incidente: ID del incidente

        Returns:
            Dict con el estado calculado
        """
        try:
            # Obtener el plan del incidente
            plan = self.repositorio_plan.obtener_por_incidente(id_incidente)

            if not plan:
                return {
                    "success": True,
                    "data": {
                        "estado_pago": "Pendiente",
                        "num_liquidaciones": 0,
                        "num_pagadas": 0,
                    },
                }

            # Obtener cuotas del plan
            cuotas = self.repositorio_cuota.obtener_por_plan(plan.id_plan_pago)

            if not cuotas:
                return {
                    "success": True,
                    "data": {
                        "estado_pago": "Pendiente",
                        "num_liquidaciones": 0,
                        "num_pagadas": 0,
                    },
                }

            # Contar cuotas con liquidación asociada y pagadas
            cuotas_con_liq = [c for c in cuotas if c.id_liquidacion is not None]
            cuotas_pagadas = [c for c in cuotas_con_liq if c.esta_pagada()]

            num_liquidaciones = len(cuotas_con_liq)
            num_pagadas = len(cuotas_pagadas)

            # Calcular estado
            if num_liquidaciones == 0:
                estado_pago = "Pendiente"
            elif num_pagadas == num_liquidaciones:
                estado_pago = "Pagado"
            elif num_pagadas > 0:
                estado_pago = "Parcialmente Pagado"
            else:
                estado_pago = "Pendiente"

            return {
                "success": True,
                "data": {
                    "estado_pago": estado_pago,
                    "num_liquidaciones": num_liquidaciones,
                    "num_pagadas": num_pagadas,
                },
            }

        except Exception as e:
            logger.error(f"Error al calcular estado de pago: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al calcular estado de pago: {str(e)}",
            }

    def liberar_bloqueo(self, id_incidente: int, usuario: str) -> bool:
        """
        Libera el bloqueo de edición de un incidente.

        Args:
            id_incidente: ID del incidente
            usuario: Usuario que libera el bloqueo

        Returns:
            True si se liberó el bloqueo
        """
        return self.repositorio_bloqueos.liberar_bloqueo(
            "INCIDENTES", id_incidente, usuario
        )

    def verificar_bloqueo(self, id_incidente: int) -> Optional[Dict[str, str]]:
        """
        Verifica si un incidente está bloqueado.

        Args:
            id_incidente: ID del incidente

        Returns:
            Información del bloqueo o None
        """
        return self.repositorio_bloqueos.verificar_bloqueo("INCIDENTES", id_incidente)

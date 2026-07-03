"""
Repositorio PostgreSQL para PlanPagoIncidente.
Implementa la persistencia de planes de pago de incidentes.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.plan_pago_incidente import PlanPagoIncidente
from src.dominio.interfaces.repositorio_plan_pago import RepositorioPlanPago
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioPlanPagoPostgres(RepositorioPlanPago):
    """
    Repositorio PostgreSQL para la entidad PlanPagoIncidente.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Optional[PlanPagoIncidente]:
        """Convierte una fila SQL a entidad PlanPagoIncidente."""
        if row is None:
            return None

        row_dict = dict(row)

        def _date_to_str(val):
            if isinstance(val, datetime):
                return val.isoformat()
            elif hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val) if val else None

        return PlanPagoIncidente(
            id_plan_pago=row_dict.get("ID_PLAN_PAGO"),
            id_incidente=row_dict.get("ID_INCIDENTE", 0),
            num_cuotas=row_dict.get("NUM_CUOTAS", 0),
            valor_cuota=row_dict.get("VALOR_CUOTA", 0),
            total_plan=row_dict.get("TOTAL_PLAN", 0),
            estado=row_dict.get("ESTADO", "Activo"),
            creado_por=row_dict.get("CREADO_POR", ""),
            created_at=_date_to_str(row_dict.get("CREATED_AT")),
            updated_at=_date_to_str(row_dict.get("UPDATED_AT")),
        )

    def crear(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Crea un nuevo plan de pago."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            INSERT INTO PLAN_PAGO_INCIDENTE 
            (ID_INCIDENTE, NUM_CUOTAS, VALOR_CUOTA, TOTAL_PLAN, ESTADO, CREADO_POR)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING ID_PLAN_PAGO, CREATED_AT
            """
            params = (
                plan.id_incidente,
                plan.num_cuotas,
                plan.valor_cuota,
                plan.total_plan,
                plan.estado,
                plan.creado_por,
            )

            cursor.execute(query, params)
            result = cursor.fetchone()

            if result:
                plan.id_plan_pago = result.get("ID_PLAN_PAGO")
                plan.created_at = result.get("CREATED_AT")

            conn.commit()
            logger.info(f"Plan de pago creado: {plan.id_plan_pago} para incidente {plan.id_incidente}")
            return plan

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al crear plan de pago: {e}")
            raise

    def obtener_por_id(self, id_plan_pago: int) -> Optional[PlanPagoIncidente]:
        """Obtiene un plan de pago por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PLAN_PAGO_INCIDENTE WHERE ID_PLAN_PAGO = %s",
            (id_plan_pago,),
        )
        return self._row_to_entity(cursor.fetchone())

    def obtener_por_incidente(self, id_incidente: int) -> Optional[PlanPagoIncidente]:
        """Obtiene el plan activo de pago para un incidente."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PLAN_PAGO_INCIDENTE WHERE ID_INCIDENTE = %s AND ESTADO = 'Activo'",
            (id_incidente,),
        )
        return self._row_to_entity(cursor.fetchone())

    def actualizar(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Actualiza un plan de pago existente."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            UPDATE PLAN_PAGO_INCIDENTE 
            SET NUM_CUOTAS = %s, VALOR_CUOTA = %s, TOTAL_PLAN = %s, 
                ESTADO = %s, UPDATED_AT = %s
            WHERE ID_PLAN_PAGO = %s
            """
            params = (
                plan.num_cuotas,
                plan.valor_cuota,
                plan.total_plan,
                plan.estado,
                datetime.now().isoformat(),
                plan.id_plan_pago,
            )

            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Plan de pago actualizado: {plan.id_plan_pago}")
            return plan

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al actualizar plan de pago: {e}")
            raise

    def eliminar(self, id_plan_pago: int) -> bool:
        """Elimina un plan de pago (soft delete)."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            UPDATE PLAN_PAGO_INCIDENTE 
            SET ESTADO = 'Cancelado', UPDATED_AT = %s
            WHERE ID_PLAN_PAGO = %s
            """
            cursor.execute(query, (datetime.now().isoformat(), id_plan_pago))
            conn.commit()
            logger.info(f"Plan de pago eliminado: {id_plan_pago}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al eliminar plan de pago: {e}")
            return False

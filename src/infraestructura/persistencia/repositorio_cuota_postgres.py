"""
Repositorio PostgreSQL para CuotaIncidente.
Implementa la persistencia de cuotas de incidentes.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.cuota_incidente import CuotaIncidente
from src.dominio.interfaces.repositorio_cuota import RepositorioCuota
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioCuotaPostgres(RepositorioCuota):
    """
    Repositorio PostgreSQL para la entidad CuotaIncidente.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Optional[CuotaIncidente]:
        """Convierte una fila SQL a entidad CuotaIncidente."""
        if row is None:
            return None

        row_dict = dict(row)

        def _date_to_str(val):
            if isinstance(val, datetime):
                return val.isoformat()
            elif hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val) if val else None

        return CuotaIncidente(
            id_cuota=row_dict.get("ID_CUOTA"),
            id_plan_pago=row_dict.get("ID_PLAN_PAGO", 0),
            numero_cuota=row_dict.get("NUMERO_CUOTA", 0),
            valor_cuota=row_dict.get("VALOR_CUOTA", 0),
            id_liquidacion=row_dict.get("ID_LIQUIDACION"),
            estado_pago=row_dict.get("ESTADO_PAGO", "Pendiente"),
            created_at=_date_to_str(row_dict.get("CREATED_AT")),
        )

    def crear(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Crea una nueva cuota."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            INSERT INTO CUOTA_INCIDENTE 
            (ID_PLAN_PAGO, NUMERO_CUOTA, VALOR_CUOTA, ESTADO_PAGO)
            VALUES (%s, %s, %s, %s)
            RETURNING ID_CUOTA, CREATED_AT
            """
            params = (
                cuota.id_plan_pago,
                cuota.numero_cuota,
                cuota.valor_cuota,
                cuota.estado_pago,
            )

            cursor.execute(query, params)
            result = cursor.fetchone()

            if result:
                cuota.id_cuota = result.get("ID_CUOTA")
                cuota.created_at = result.get("CREATED_AT")

            conn.commit()
            logger.info(
                f"Cuota creada: {cuota.id_cuota} para plan {cuota.id_plan_pago}"
            )
            return cuota

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al crear cuota: {e}")
            raise

    def crear_desde_plan(
        self, id_plan_pago: int, num_cuotas: int, valor_cuota: int
    ) -> List[CuotaIncidente]:
        """Crea todas las cuotas para un plan."""
        cuotas_creadas = []

        for i in range(1, num_cuotas + 1):
            cuota = CuotaIncidente.crear(id_plan_pago, i, valor_cuota)
            cuota = self.crear(cuota)
            cuotas_creadas.append(cuota)

        logger.info(f"Creadas {len(cuotas_creadas)} cuotas para plan {id_plan_pago}")
        return cuotas_creadas

    def obtener_por_id(self, id_cuota: int) -> Optional[CuotaIncidente]:
        """Obtiene una cuota por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM CUOTA_INCIDENTE WHERE ID_CUOTA = %s",
            (id_cuota,),
        )
        return self._row_to_entity(cursor.fetchone())

    def obtener_por_plan(self, id_plan_pago: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas de un plan."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM CUOTA_INCIDENTE WHERE ID_PLAN_PAGO = %s ORDER BY NUMERO_CUOTA",
            (id_plan_pago,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas asociadas a una liquidación."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM CUOTA_INCIDENTE WHERE ID_LIQUIDACION = %s ORDER BY NUMERO_CUOTA",
            (id_liquidacion,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_cuotas_pendientes_por_propiedad(
        self, id_propiedad: int
    ) -> List[CuotaIncidente]:
        """Obtiene las cuotas pendientes que no están asociadas a ninguna liquidación para una propiedad."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = """
            SELECT c.*
            FROM CUOTA_INCIDENTE c
            JOIN PLAN_PAGO_INCIDENTE p ON c.ID_PLAN_PAGO = p.ID_PLAN_PAGO
            JOIN INCIDENTES i ON p.ID_INCIDENTE = i.ID_INCIDENTE
            WHERE i.ID_PROPIEDAD = %s 
              AND c.ESTADO_PAGO = 'Pendiente' 
              AND c.ID_LIQUIDACION IS NULL
            ORDER BY c.ID_CUOTA
        """
        cursor.execute(query, (id_propiedad,))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def contar_estado_liquidaciones_por_plan(
        self, id_plan_pago: int
    ) -> tuple[int, int]:
        """
        Calcula la cantidad de cuotas con liquidación y cuántas están pagadas
        para un plan de pago específico en una sola consulta optimizada.

        Returns:
            Tuple[int, int]: (total_cuotas_con_liq, total_cuotas_pagadas)
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = """
            SELECT 
                COUNT(c.ID_CUOTA) as total_con_liq,
                SUM(CASE WHEN l.ESTADO_LIQUIDACION = 'Pagada' THEN 1 ELSE 0 END) as total_pagadas
            FROM CUOTA_INCIDENTE c
            JOIN LIQUIDACIONES l ON c.ID_LIQUIDACION = l.ID_LIQUIDACION
            WHERE c.ID_PLAN_PAGO = %s
        """
        cursor.execute(query, (id_plan_pago,))
        row = cursor.fetchone()

        if not row:
            return 0, 0

        total_con_liq = row.get("total_con_liq", 0) or row.get("TOTAL_CON_LIQ", 0) or 0
        total_pagadas = row.get("total_pagadas", 0) or row.get("TOTAL_PAGADAS", 0) or 0

        return total_con_liq, total_pagadas

    def actualizar(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Actualiza una cuota existente."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            UPDATE CUOTA_INCIDENTE 
            SET ID_LIQUIDACION = %s, ESTADO_PAGO = %s
            WHERE ID_CUOTA = %s
            """
            params = (cuota.id_liquidacion, cuota.estado_pago, cuota.id_cuota)

            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Cuota actualizada: {cuota.id_cuota}")
            return cuota

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al actualizar cuota: {e}")
            raise

    def eliminar(self, id_cuota: int) -> bool:
        """Elimina una cuota."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            cursor.execute(
                "DELETE FROM CUOTA_INCIDENTE WHERE ID_CUOTA = %s", (id_cuota,)
            )
            conn.commit()
            logger.info(f"Cuota eliminada: {id_cuota}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al eliminar cuota: {e}")
            return False

"""
Repositorio PostgreSQL para IncidenteLiquidacion.
Implementa la persistencia de relaciones incidente-liquidación.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.incidente_liquidacion import IncidenteLiquidacion
from src.dominio.interfaces.repositorio_incidente_liq import (
    RepositorioIncidenteLiquidacion,
)
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioIncidenteLiquidacionPostgres(RepositorioIncidenteLiquidacion):
    """
    Repositorio PostgreSQL para la entidad IncidenteLiquidacion.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Optional[IncidenteLiquidacion]:
        """Convierte una fila SQL a entidad IncidenteLiquidacion."""
        if row is None:
            return None

        row_dict = dict(row)

        def _date_to_str(val):
            if isinstance(val, datetime):
                return val.isoformat()
            elif hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val) if val else None

        return IncidenteLiquidacion(
            id_relacion=row_dict.get("ID_RELACION"),
            id_incidente=row_dict.get("ID_INCIDENTE", 0),
            id_liquidacion=row_dict.get("ID_LIQUIDACION", 0),
            numero_cuota=row_dict.get("NUMERO_CUOTA", 0),
            valor_descuento=row_dict.get("VALOR_DESCUENTO", 0),
            asociado_por=row_dict.get("ASOCIADO_POR", ""),
            fecha_asociacion=_date_to_str(row_dict.get("FECHA_ASOCIACION")),
        )

    def crear(self, relacion: IncidenteLiquidacion) -> IncidenteLiquidacion:
        """Crea una nueva relación."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            query = """
            INSERT INTO INCIDENTE_LIQUIDACION 
            (ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA, VALOR_DESCUENTO, ASOCIADO_POR)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING ID_RELACION, FECHA_ASOCIACION
            """
            params = (
                relacion.id_incidente,
                relacion.id_liquidacion,
                relacion.numero_cuota,
                relacion.valor_descuento,
                relacion.asociado_por,
            )

            cursor.execute(query, params)
            result = cursor.fetchone()

            if result:
                relacion.id_relacion = result.get("ID_RELACION")
                relacion.fecha_asociacion = result.get("FECHA_ASOCIACION")

            conn.commit()
            logger.info(
                f"Relación creada: incidente {relacion.id_incidente} -> liquidación {relacion.id_liquidacion}"
            )
            return relacion

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al crear relación: {e}")
            raise

    def obtener_por_id(self, id_relacion: int) -> Optional[IncidenteLiquidacion]:
        """Obtiene una relación por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM INCIDENTE_LIQUIDACION WHERE ID_RELACION = %s",
            (id_relacion,),
        )
        return self._row_to_entity(cursor.fetchone())

    def obtener_por_incidente(self, id_incidente: int) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de un incidente."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM INCIDENTE_LIQUIDACION WHERE ID_INCIDENTE = %s ORDER BY FECHA_ASOCIACION",
            (id_incidente,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_por_liquidacion(
        self, id_liquidacion: int
    ) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de una liquidación."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM INCIDENTE_LIQUIDACION WHERE ID_LIQUIDACION = %s ORDER BY FECHA_ASOCIACION",
            (id_liquidacion,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def eliminar(self, id_relacion: int) -> bool:
        """Elimina una relación."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        try:
            cursor.execute(
                "DELETE FROM INCIDENTE_LIQUIDACION WHERE ID_RELACION = %s",
                (id_relacion,),
            )
            conn.commit()
            logger.info(f"Relación eliminada: {id_relacion}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error al eliminar relación: {e}")
            return False

    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """Calcula el total de descuentos para una liquidación."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            """
            SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) as TOTAL
            FROM INCIDENTE_LIQUIDACION 
            WHERE ID_LIQUIDACION = %s
            """,
            (id_liquidacion,),
        )
        result = cursor.fetchone()
        return result.get("TOTAL", 0) if result else 0

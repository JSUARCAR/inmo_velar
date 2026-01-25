import sqlite3
from typing import List, Optional

from src.dominio.entidades.bonificacion_asesor import BonificacionAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioBonificacionAsesorSQLite:
    """Repositorio SQLite para gestión de bonificaciones de asesores"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, bonificacion: BonificacionAsesor, usuario: str) -> BonificacionAsesor:
        """
        Crea una nueva bonificación.
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            INSERT INTO BONIFICACIONES_ASESORES (
                ID_LIQUIDACION_ASESOR, TIPO_BONIFICACION, DESCRIPCION_BONIFICACION,
                VALOR_BONIFICACION, CREATED_BY
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            RETURNING ID_BONIFICACION_ASESOR, FECHA_REGISTRO
        """

        params = (
            bonificacion.id_liquidacion_asesor,
            bonificacion.tipo_bonificacion,
            bonificacion.descripcion_bonificacion,
            bonificacion.valor_bonificacion,
            usuario,
        )

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                if hasattr(row, "keys") or isinstance(row, dict):
                    bonificacion.id_bonificacion_asesor = row.get(
                        "ID_BONIFICACION_ASESOR"
                    ) or row.get("id_bonificacion_asesor")
                    bonificacion.fecha_registro = row.get("FECHA_REGISTRO") or row.get(
                        "fecha_registro"
                    )
                else:
                    bonificacion.id_bonificacion_asesor = row[0]
                    bonificacion.fecha_registro = row[1]

            bonificacion.created_by = usuario
            return bonificacion

    def obtener_por_id(self, id_bonificacion: int) -> Optional[BonificacionAsesor]:
        """Obtiene una bonificación por ID."""
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM BONIFICACIONES_ASESORES WHERE ID_BONIFICACION_ASESOR = {ph}"

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_bonificacion,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def listar_por_liquidacion(self, id_liquidacion: int) -> List[BonificacionAsesor]:
        """Lista bonificaciones de una liquidación."""
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM BONIFICACIONES_ASESORES WHERE ID_LIQUIDACION_ASESOR = {ph} ORDER BY FECHA_REGISTRO DESC"

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def eliminar(self, id_bonificacion: int) -> bool:
        """Elimina una bonificación."""
        ph = self.db_manager.get_placeholder()
        query = f"DELETE FROM BONIFICACIONES_ASESORES WHERE ID_BONIFICACION_ASESOR = {ph}"

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_bonificacion,))
            return cursor.rowcount > 0

    def calcular_total_bonificaciones(self, id_liquidacion: int) -> int:
        """Calcula el valor total de bonificaciones para una liquidación."""
        ph = self.db_manager.get_placeholder()
        query = f"SELECT SUM(VALOR_BONIFICACION) as total FROM BONIFICACIONES_ASESORES WHERE ID_LIQUIDACION_ASESOR = {ph}"

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            if not row:
                return 0

            # Handle potential dict cursor (real dict or upper case)
            if hasattr(row, "get"):
                val = row.get("total") or row.get("TOTAL")
                return val if val else 0
            # Handle tuple cursor
            return row[0] if row[0] else 0

    def _row_to_entity(self, row: sqlite3.Row) -> BonificacionAsesor:
        return BonificacionAsesor(
            id_bonificacion_asesor=row["ID_BONIFICACION_ASESOR"],
            id_liquidacion_asesor=row["ID_LIQUIDACION_ASESOR"],
            tipo_bonificacion=row["TIPO_BONIFICACION"],
            descripcion_bonificacion=row["DESCRIPCION_BONIFICACION"],
            valor_bonificacion=row["VALOR_BONIFICACION"],
            fecha_registro=row["FECHA_REGISTRO"],
            created_by=row["CREATED_BY"],
        )

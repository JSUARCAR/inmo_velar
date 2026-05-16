"""
Repositorio PostgreSQL para entidad BonificacionAsesor.
Implementa operaciones CRUD bajo estándares Élite.
"""

from typing import List, Optional, Dict, Any

from src.dominio.entidades.bonificacion_asesor import BonificacionAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioBonificacionAsesor:
    """Repositorio para gestión de bonificaciones de asesores en PostgreSQL"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, bonificacion: BonificacionAsesor, usuario: str) -> BonificacionAsesor:
        """
        Crea una nueva bonificación con PostgreSQL Native.
        """
        query = """
            INSERT INTO BONIFICACIONES_ASESORES (
                ID_LIQUIDACION_ASESOR, TIPO_BONIFICACION, DESCRIPCION_BONIFICACION,
                VALOR_BONIFICACION, CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING ID_BONIFICACION_ASESOR, FECHA_REGISTRO
        """

        params = (
            bonificacion.id_liquidacion_asesor,
            bonificacion.tipo_bonificacion,
            bonificacion.descripcion_bonificacion,
            bonificacion.valor_bonificacion,
            usuario,
        )

        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                def gv(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower())
                
                if hasattr(row, "get") or isinstance(row, dict):
                    bonificacion.id_bonificacion_asesor = gv("ID_BONIFICACION_ASESOR")
                    bonificacion.fecha_registro = gv("FECHA_REGISTRO")
                else:
                    bonificacion.id_bonificacion_asesor = row[0]
                    bonificacion.fecha_registro = row[1]

            bonificacion.created_by = usuario
            return bonificacion

    def obtener_por_id(self, id_bonificacion: int) -> Optional[BonificacionAsesor]:
        """Obtiene una bonificación por ID."""
        query = "SELECT * FROM BONIFICACIONES_ASESORES WHERE ID_BONIFICACION_ASESOR = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_bonificacion,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def listar_por_liquidacion(self, id_liquidacion: int) -> List[BonificacionAsesor]:
        """Lista bonificaciones de una liquidación."""
        query = "SELECT * FROM BONIFICACIONES_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s ORDER BY FECHA_REGISTRO DESC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def eliminar(self, id_bonificacion: int) -> bool:
        """Elimina una bonificación."""
        query = "DELETE FROM BONIFICACIONES_ASESORES WHERE ID_BONIFICACION_ASESOR = %s"

        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_bonificacion,))
            return cursor.rowcount > 0

    def calcular_total_bonificaciones(self, id_liquidacion: int) -> int:
        """Calcula el valor total de bonificaciones para una liquidación."""
        query = "SELECT SUM(VALOR_BONIFICACION) as total FROM BONIFICACIONES_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            if not row:
                return 0

            val = row.get("total") or row.get("TOTAL")
            return int(val) if val else 0

    def _row_to_entity(self, row: Dict[str, Any]) -> BonificacionAsesor:
        """Helper para mapeo de fila a entidad."""
        def gv(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower())
        return BonificacionAsesor(
            id_bonificacion_asesor=gv("ID_BONIFICACION_ASESOR"),
            id_liquidacion_asesor=gv("ID_LIQUIDACION_ASESOR"),
            tipo_bonificacion=gv("TIPO_BONIFICACION"),
            descripcion_bonificacion=gv("DESCRIPCION_BONIFICACION"),
            valor_bonificacion=gv("VALOR_BONIFICACION"),
            fecha_registro=gv("FECHA_REGISTRO"),
            created_by=gv("CREATED_BY"),
        )

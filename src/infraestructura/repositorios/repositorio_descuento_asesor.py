"""
Repositorio PostgreSQL para entidad DescuentoAsesor.
Implementa operaciones CRUD bajo estándares Élite.
"""

from typing import List, Optional, Dict, Any

from src.dominio.entidades.descuento_asesor import DescuentoAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioDescuentoAsesor:
    """Repositorio para gestión de descuentos de asesores en PostgreSQL"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, descuento: DescuentoAsesor, usuario: str, conn=None) -> DescuentoAsesor:
        """
        Crea un nuevo descuento con PostgreSQL Native.
        """
        query = """
            INSERT INTO DESCUENTOS_ASESORES (
                ID_LIQUIDACION_ASESOR, TIPO_DESCUENTO, DESCRIPCION_DESCUENTO, 
                VALOR_DESCUENTO, CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s) 
            RETURNING ID_DESCUENTO_ASESOR
        """

        params = (
            descuento.id_liquidacion_asesor,
            descuento.tipo_descuento,
            descuento.descripcion_descuento,
            descuento.valor_descuento,
            usuario,
        )

        def execute_insert(conexion):
            cursor = self.db_manager.get_dict_cursor(conexion)
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                if hasattr(row, "get") or isinstance(row, dict):
                    descuento.id_descuento_asesor = row.get(
                        "ID_DESCUENTO_ASESOR"
                    ) or row.get("id_descuento_asesor")
                else:
                    descuento.id_descuento_asesor = row[0]

            descuento.created_by = usuario
            return descuento

        if conn:
            return execute_insert(conn)
        else:
            with self.db_manager.transaccion() as t_conn:
                return execute_insert(t_conn)


    def obtener_por_id(self, id_descuento: int) -> Optional[DescuentoAsesor]:
        """Obtiene un descuento por su ID."""
        query = "SELECT * FROM DESCUENTOS_ASESORES WHERE ID_DESCUENTO_ASESOR = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_descuento,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def listar_por_liquidacion(self, id_liquidacion: int) -> List[DescuentoAsesor]:
        """Lista todos los descuentos de una liquidación."""
        query = "SELECT * FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s ORDER BY FECHA_REGISTRO DESC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """Calcula el total de descuentos de una liquidación."""
        query = "SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) as total FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            if not row:
                return 0
            val = row.get("total") or row.get("TOTAL")
            return int(val) if val else 0

    def eliminar(self, id_descuento: int) -> bool:
        """Elimina un descuento."""
        query = "DELETE FROM DESCUENTOS_ASESORES WHERE ID_DESCUENTO_ASESOR = %s"

        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_descuento,))
            return cursor.rowcount > 0

    def _row_to_entity(self, row: Dict[str, Any]) -> DescuentoAsesor:
        """Helper para mapeo de fila a entidad."""

        def gv(k):
            return row.get(k) or row.get(k.upper()) or row.get(k.lower())

        return DescuentoAsesor(
            id_descuento_asesor=gv("ID_DESCUENTO_ASESOR"),
            id_liquidacion_asesor=gv("ID_LIQUIDACION_ASESOR"),
            tipo_descuento=gv("TIPO_DESCUENTO"),
            descripcion_descuento=gv("DESCRIPCION_DESCUENTO"),
            valor_descuento=gv("VALOR_DESCUENTO"),
            fecha_registro=gv("FECHA_REGISTRO"),
            created_at=gv("CREATED_AT"),
            created_by=gv("CREATED_BY"),
        )

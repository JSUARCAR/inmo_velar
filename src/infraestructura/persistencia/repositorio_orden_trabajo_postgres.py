from datetime import datetime
from typing import Optional

from src.dominio.entidades.orden_trabajo import OrdenTrabajo
from src.dominio.interfaces.repositorio_orden_trabajo import RepositorioOrdenTrabajo
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioOrdenTrabajoPostgres(RepositorioOrdenTrabajo):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def guardar(self, orden: OrdenTrabajo) -> int:
        query = """
            INSERT INTO ORDENES_TRABAJO (
                ID_INCIDENTE, ID_PROVEEDOR, FECHA_CREACION, FECHA_INICIO_ESTIMADA,
                FECHA_FIN_ESTIMADA, ESTADO, COSTO_MANO_OBRA, COSTO_MATERIALES,
                DESCRIPCION_TRABAJO, CREATED_AT, UPDATED_AT
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_ORDEN
            """
        params = (
            orden.id_incidente,
            orden.id_proveedor,
            orden.fecha_creacion.isoformat() if orden.fecha_creacion else None,
            orden.fecha_inicio_estimada.isoformat()
            if orden.fecha_inicio_estimada
            else None,
            orden.fecha_fin_estimada.isoformat() if orden.fecha_fin_estimada else None,
            orden.estado,
            orden.costo_mano_obra,
            orden.costo_materiales,
            orden.descripcion_trabajo,
            orden.created_at.isoformat(),
            orden.updated_at.isoformat(),
        )
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.commit()
            if row:
                if hasattr(row, "values"):
                    return list(row.values())[0]
                return row[0]
            raise ValueError("No se pudo obtener el ID de la orden insertada")

    def obtener_por_id(self, id_orden: int) -> Optional[OrdenTrabajo]:
        query = "SELECT * FROM ORDENES_TRABAJO WHERE ID_ORDEN = %s"
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_orden,))
            row = cursor.fetchone()
            return self._map_row_to_entity(row) if row else None

    def obtener_por_incidente(self, id_incidente: int) -> Optional[OrdenTrabajo]:
        query = "SELECT * FROM ORDENES_TRABAJO WHERE ID_INCIDENTE = %s"
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_incidente,))
            row = cursor.fetchone()
            return self._map_row_to_entity(row) if row else None

    def actualizar(self, orden: OrdenTrabajo) -> None:
        query = """
            UPDATE ORDENES_TRABAJO SET
                ESTADO = %s,
                FECHA_INICIO_ESTIMADA = %s,
                FECHA_FIN_ESTIMADA = %s,
                UPDATED_AT = %s
            WHERE ID_ORDEN = %s
            """
        params = (
            orden.estado,
            orden.fecha_inicio_estimada.isoformat()
            if orden.fecha_inicio_estimada
            else None,
            orden.fecha_fin_estimada.isoformat() if orden.fecha_fin_estimada else None,
            datetime.now().isoformat(),
            orden.id_orden,
        )
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def _map_row_to_entity(self, row: dict) -> Optional[OrdenTrabajo]:
        if not row:
            return None
        return OrdenTrabajo(
            id_orden=row.get("ID_ORDEN"),
            id_incidente=row.get("ID_INCIDENTE"),
            id_proveedor=row.get("ID_PROVEEDOR"),
            fecha_creacion=(
                datetime.fromisoformat(row["FECHA_CREACION"])
                if row.get("FECHA_CREACION")
                else None
            ),
            fecha_inicio_estimada=(
                datetime.fromisoformat(row["FECHA_INICIO_ESTIMADA"])
                if row.get("FECHA_INICIO_ESTIMADA")
                else None
            ),
            fecha_fin_estimada=(
                datetime.fromisoformat(row["FECHA_FIN_ESTIMADA"])
                if row.get("FECHA_FIN_ESTIMADA")
                else None
            ),
            estado=row.get("ESTADO"),
            costo_mano_obra=row.get("COSTO_MANO_OBRA"),
            costo_materiales=row.get("COSTO_MATERIALES"),
            descripcion_trabajo=row.get("DESCRIPCION_TRABAJO"),
            created_at=datetime.fromisoformat(row["CREATED_AT"])
            if row.get("CREATED_AT")
            else None,
            updated_at=datetime.fromisoformat(row["UPDATED_AT"])
            if row.get("UPDATED_AT")
            else None,
        )

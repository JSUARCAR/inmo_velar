from typing import List, Optional
from datetime import datetime
from src.dominio.entidades.orden_trabajo import OrdenTrabajo
from src.dominio.interfaces.repositorio_orden_trabajo import RepositorioOrdenTrabajo
from src.infraestructura.persistencia.database import DatabaseManager

class RepositorioOrdenTrabajoSQLite(RepositorioOrdenTrabajo):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def guardar(self, orden: OrdenTrabajo) -> int:
        query = """
            INSERT INTO ORDENES_TRABAJO (
                id_incidente, id_proveedor, fecha_creacion, fecha_inicio_estimada,
                fecha_fin_estimada, estado, costo_mano_obra, costo_materiales,
                descripcion_trabajo, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            orden.id_incidente,
            orden.id_proveedor,
            orden.fecha_creacion.isoformat() if orden.fecha_creacion else None,
            orden.fecha_inicio_estimada.isoformat() if orden.fecha_inicio_estimada else None,
            orden.fecha_fin_estimada.isoformat() if orden.fecha_fin_estimada else None,
            orden.estado,
            orden.costo_mano_obra,
            orden.costo_materiales,
            orden.descripcion_trabajo,
            orden.created_at.isoformat(),
            orden.updated_at.isoformat()
        )
        return self.db_manager.execute_write(query, params)

    def obtener_por_id(self, id_orden: int) -> Optional[OrdenTrabajo]:
        query = "SELECT * FROM ORDENES_TRABAJO WHERE id_orden = ?"
        row = self.db_manager.execute_query_one(query, (id_orden,))
        if row:
            return self._map_row_to_entity(row)
        return None

    def obtener_por_incidente(self, id_incidente: int) -> Optional[OrdenTrabajo]:
        query = "SELECT * FROM ORDENES_TRABAJO WHERE id_incidente = ?"
        row = self.db_manager.execute_query_one(query, (id_incidente,))
        if row:
            return self._map_row_to_entity(row)
        return None

    def actualizar(self, orden: OrdenTrabajo) -> None:
        query = """
            UPDATE ORDENES_TRABAJO SET
                estado = ?,
                fecha_inicio_estimada = ?,
                fecha_fin_estimada = ?,
                updated_at = ?
            WHERE id_orden = ?
        """
        params = (
            orden.estado,
            orden.fecha_inicio_estimada.isoformat() if orden.fecha_inicio_estimada else None,
            orden.fecha_fin_estimada.isoformat() if orden.fecha_fin_estimada else None,
            datetime.now().isoformat(),
            orden.id_orden
        )
        self.db_manager.execute_write(query, params)

    def _map_row_to_entity(self, row) -> OrdenTrabajo:
        return OrdenTrabajo(
            id_orden=row['id_orden'],
            id_incidente=row['id_incidente'],
            id_proveedor=row['id_proveedor'],
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion']) if row['fecha_creacion'] else None,
            fecha_inicio_estimada=datetime.fromisoformat(row['fecha_inicio_estimada']) if row['fecha_inicio_estimada'] else None,
            fecha_fin_estimada=datetime.fromisoformat(row['fecha_fin_estimada']) if row['fecha_fin_estimada'] else None,
            estado=row['estado'],
            costo_mano_obra=row['costo_mano_obra'],
            costo_materiales=row['costo_materiales'],
            descripcion_trabajo=row['descripcion_trabajo'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

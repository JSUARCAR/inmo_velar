from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.proveedor import Proveedor
from src.dominio.interfaces.repositorio_proveedores import RepositorioProveedores
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioProveedoresPostgres(RepositorioProveedores):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _mapear_proveedor(self, row: dict) -> Optional[Proveedor]:
        if not row:
            return None
        return Proveedor(
            id_proveedor=row.get("ID_PROVEEDOR"),
            id_persona=row.get("ID_PERSONA"),
            especialidad=row.get("ESPECIALIDAD"),
            calificacion=row.get("CALIFICACION"),
            observaciones=row.get("OBSERVACIONES"),
            estado_registro=row.get("ESTADO_REGISTRO"),
            created_at=row.get("CREATED_AT"),
            created_by=row.get("CREATED_BY"),
            nombre_completo=row.get("NOMBRE_COMPLETO"),
            contacto=row.get("TELEFONO_PRINCIPAL"),
            documento=row.get("NUMERO_DOCUMENTO"),
        )

    def obtener_por_id(self, id_proveedor: int) -> Optional[Proveedor]:
        query = """
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL, PER.NUMERO_DOCUMENTO
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ID_PROVEEDOR = %s
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_proveedor,))
            row = cursor.fetchone()
            return self._mapear_proveedor(row) if row else None

    def obtener_por_persona_id(self, id_persona: int) -> Optional[Proveedor]:
        query = """
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL, PER.NUMERO_DOCUMENTO
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ID_PERSONA = %s
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_persona,))
            row = cursor.fetchone()
            return self._mapear_proveedor(row) if row else None

    def listar(self, especialidad: Optional[str] = None) -> List[Proveedor]:
        query = """
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL, PER.NUMERO_DOCUMENTO
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ESTADO_REGISTRO = TRUE
        """
        params = []
        if especialidad:
            query += " AND P.ESPECIALIDAD = %s"
            params.append(especialidad)

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, tuple(params))
            return [self._mapear_proveedor(row) for row in cursor.fetchall()]

    def guardar(self, proveedor: Proveedor) -> int:
        query = """
        INSERT INTO PROVEEDORES (ID_PERSONA, ESPECIALIDAD, CALIFICACION, OBSERVACIONES, CREATED_BY)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING ID_PROVEEDOR
        """
        params = (
            proveedor.id_persona,
            proveedor.especialidad,
            proveedor.calificacion,
            proveedor.observaciones,
            proveedor.created_by,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def actualizar(self, proveedor: Proveedor) -> None:
        query = """
        UPDATE PROVEEDORES
        SET ESPECIALIDAD = %s, CALIFICACION = %s, OBSERVACIONES = %s, ESTADO_REGISTRO = %s
        WHERE ID_PROVEEDOR = %s
        """
        params = (
            proveedor.especialidad,
            proveedor.calificacion,
            proveedor.observaciones,
            proveedor.estado_registro,
            proveedor.id_proveedor,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

    def eliminar(self, id_proveedor: int) -> None:
        query = "UPDATE PROVEEDORES SET ESTADO_REGISTRO = FALSE WHERE ID_PROVEEDOR = %s"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_proveedor,))

    def eliminar_por_persona(self, id_persona: int) -> bool:
        query = "DELETE FROM PROVEEDORES WHERE ID_PERSONA = %s"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_persona,))
            return cursor.rowcount > 0

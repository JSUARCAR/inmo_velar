import sqlite3
from typing import List, Optional

from src.dominio.entidades.proveedor import Proveedor
from src.dominio.interfaces.repositorio_proveedores import RepositorioProveedores
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioProveedoresSQLite(RepositorioProveedores):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _mapear_proveedor(self, row: sqlite3.Row) -> Proveedor:
        if not row:
            return None
        return Proveedor(
            id_proveedor=row["ID_PROVEEDOR"],
            id_persona=row["ID_PERSONA"],
            especialidad=row["ESPECIALIDAD"],
            calificacion=row["CALIFICACION"],
            observaciones=row["OBSERVACIONES"],
            estado_registro=row["ESTADO_REGISTRO"],
            created_at=row["CREATED_AT"],
            created_by=row["CREATED_BY"],
            # Datos de persona (si hay join)
            nombre_completo=row["NOMBRE_COMPLETO"] if "NOMBRE_COMPLETO" in row.keys() else None,
            contacto=row["TELEFONO_PRINCIPAL"] if "TELEFONO_PRINCIPAL" in row.keys() else None,
        )

    def guardar(self, proveedor: Proveedor) -> int:
        placeholder = self.db.get_placeholder()
        query = f"""
        INSERT INTO PROVEEDORES (ID_PERSONA, ESPECIALIDAD, CALIFICACION, OBSERVACIONES, CREATED_BY)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
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
            conn.commit()
            return self.db.get_last_insert_id(cursor, "PROVEEDORES", "ID_PROVEEDOR")

    def obtener_por_id(self, id_proveedor: int) -> Optional[Proveedor]:
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ID_PROVEEDOR = {placeholder}
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_proveedor,))
        row = cursor.fetchone()
        return self._mapear_proveedor(row) if row else None

    def obtener_por_persona_id(self, id_persona: int) -> Optional[Proveedor]:
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ID_PERSONA = {placeholder}
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_persona,))
        row = cursor.fetchone()
        return self._mapear_proveedor(row) if row else None

    def listar(self, especialidad: Optional[str] = None) -> List[Proveedor]:
        query = """
        SELECT P.ID_PROVEEDOR, P.ID_PERSONA, P.ESPECIALIDAD, P.CALIFICACION, P.OBSERVACIONES, 
               P.ESTADO_REGISTRO, P.CREATED_AT, P.CREATED_BY,
               PER.NOMBRE_COMPLETO, PER.TELEFONO_PRINCIPAL
        FROM PROVEEDORES P
        JOIN PERSONAS PER ON P.ID_PERSONA = PER.ID_PERSONA
        WHERE P.ESTADO_REGISTRO = TRUE
        """
        params = []
        if especialidad:
            query += " AND P.ESPECIALIDAD = ?"
            params.append(especialidad)

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, tuple(params))
        return [self._mapear_proveedor(row) for row in cursor.fetchall()]

    def actualizar(self, proveedor: Proveedor) -> None:
        placeholder = self.db.get_placeholder()
        query = f"""
        UPDATE PROVEEDORES
        SET ESPECIALIDAD = {placeholder}, CALIFICACION = {placeholder}, OBSERVACIONES = {placeholder}, ESTADO_REGISTRO = {placeholder}
        WHERE ID_PROVEEDOR = {placeholder}
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
            conn.commit()

    def eliminar(self, id_proveedor: int) -> None:
        placeholder = self.db.get_placeholder()
        query = f"UPDATE PROVEEDORES SET ESTADO_REGISTRO = FALSE WHERE ID_PROVEEDOR = {placeholder}"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_proveedor,))
            conn.commit()

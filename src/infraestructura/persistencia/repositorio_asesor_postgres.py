"""
Repositorio Postgres para Asesor.
Implementa mapeo 1:1 estricto con tabla ASESORES en PostgreSQL.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.asesor import Asesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAsesorPostgres:
    """Repositorio PostgreSQL para la entidad Asesor."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Optional[Asesor]:
        """Convierte una fila SQL (dict de DictCursor) a entidad Asesor."""
        if row is None:
            return None

        def get_val(key):
            return row.get(key) or row.get(key.upper()) or row.get(key.lower())

        asesor = Asesor(
            id_asesor=get_val("ID_ASESOR"),
            id_persona=get_val("ID_PERSONA"),
            id_usuario=get_val("ID_USUARIO"),
            comision_porcentaje_arriendo=get_val("COMISION_PORCENTAJE_ARRIENDO"),
            comision_porcentaje_venta=get_val("COMISION_PORCENTAJE_VENTA"),
            fecha_ingreso=get_val("FECHA_INGRESO"),
            estado=get_val("ESTADO"),
            motivo_inactivacion=get_val("MOTIVO_INACTIVACION"),
            created_at=get_val("CREATED_AT"),
            created_by=get_val("CREATED_BY"),
            updated_at=get_val("UPDATED_AT"),
            updated_by=get_val("UPDATED_BY"),
        )
        
        # Campo extra de JOIN si está presente
        nombre = get_val("NOMBRE_COMPLETO")
        if nombre:
            asesor.nombre_completo = nombre
            
        return asesor

    def obtener_por_id(self, id_asesor: int) -> Optional[Asesor]:
        """Obtiene un asesor por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"SELECT * FROM ASESORES WHERE ID_ASESOR = {p}"
        cursor.execute(query, (id_asesor,))
        row = cursor.fetchone()
        cursor.close()
        return self._row_to_entity(row)

    def listar_activos(self) -> List[Asesor]:
        """Lista todos los asesores activos con sus datos personales."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = """
            SELECT a.*, p.NOMBRE_COMPLETO
            FROM ASESORES a
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            WHERE a.ESTADO = TRUE OR a.ESTADO = '1'
            ORDER BY p.NOMBRE_COMPLETO
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [self._row_to_entity(row) for row in rows]

    def crear(self, asesor: Asesor, usuario_sistema: str) -> Asesor:
        """Crea un nuevo asesor en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            INSERT INTO ASESORES (
                ID_PERSONA, ID_USUARIO, COMISION_PORCENTAJE_ARRIENDO,
                COMISION_PORCENTAJE_VENTA, FECHA_INGRESO, ESTADO,
                CREATED_AT, CREATED_BY
            ) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            RETURNING ID_ASESOR
        """
        
        cursor.execute(query, (
            asesor.id_persona,
            asesor.id_usuario,
            asesor.comision_porcentaje_arriendo,
            asesor.comision_porcentaje_venta,
            asesor.fecha_ingreso or datetime.now().isoformat(),
            asesor.estado if asesor.estado is not None else True,
            datetime.now().isoformat(),
            usuario_sistema
        ))
        
        result = cursor.fetchone()
        if result:
            asesor.id_asesor = result.get("ID_ASESOR") or result.get("id_asesor")
            
        conn.commit()
        cursor.close()
        return asesor

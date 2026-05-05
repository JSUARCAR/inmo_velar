from datetime import datetime
from typing import Optional

from src.dominio.interfaces.repositorio_auditoria import RepositorioAuditoria
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAuditoriaPostgres(RepositorioAuditoria):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def guardar_cambio(
        self,
        tabla: str,
        id_registro: int,
        tipo_operacion: str,
        valor_anterior: Optional[str],
        valor_nuevo: Optional[str],
        usuario: str,
        motivo_cambio: str,
    ) -> int:
        query = """
            INSERT INTO AUDITORIA_CAMBIOS 
            (TABLA_AFECTADA, ID_REGISTRO, OPERACION, FECHA_HORA, ID_USUARIO, DATOS_ANTERIORES, DATOS_NUEVOS)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_AUDITORIA
        """
        params = (
            tabla,
            id_registro,
            tipo_operacion,
            datetime.now().isoformat(),
            usuario,
            valor_anterior,
            valor_nuevo,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.commit()
            if row:
                if hasattr(row, "values"):
                    return list(row.values())[0]
                return row[0]
            raise ValueError("No se pudo obtener el ID de auditoría insertado")

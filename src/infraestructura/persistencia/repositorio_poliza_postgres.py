"""
Repositorio Postgres para la entidad PolizaSeguro.
Mapeo con la tabla POLIZAS_SEGUROS.
"""

from typing import List, Optional
from datetime import datetime

from src.dominio.entidades.poliza import PolizaSeguro
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPolizaPostgres:
    """Repositorio Postgres para PolizaSeguro."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: dict) -> Optional[PolizaSeguro]:
        """Convierte una fila SQL a entidad PolizaSeguro."""
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return PolizaSeguro(
            id_poliza=(row_dict.get("id_poliza") or row_dict.get("ID_POLIZA")),
            id_contrato=(row_dict.get("id_contrato") or row_dict.get("ID_CONTRATO")),
            id_seguro=(row_dict.get("id_seguro") or row_dict.get("ID_SEGURO")),
            fecha_inicio=(row_dict.get("fecha_inicio") or row_dict.get("FECHA_INICIO")),
            fecha_fin=(row_dict.get("fecha_fin") or row_dict.get("FECHA_FIN")),
            numero_poliza=(
                row_dict.get("numero_poliza") or row_dict.get("NUMERO_POLIZA")
            ),
            estado=(row_dict.get("estado") or row_dict.get("ESTADO")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def listar_todas(self) -> List[PolizaSeguro]:
        """Lista todas las pólizas registradas."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute("SELECT * FROM POLIZAS_SEGUROS ORDER BY FECHA_FIN DESC")
        return [self._row_to_entity(row) for row in cursor.fetchall() if row]

    def crear(self, poliza: PolizaSeguro, usuario: str) -> PolizaSeguro:
        """Crea un nuevo registro de Póliza."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            created_at = datetime.now().isoformat()

            cursor.execute(
                f"""
                INSERT INTO POLIZAS_SEGUROS (
                    ID_CONTRATO,
                    ID_SEGURO,
                    FECHA_INICIO,
                    FECHA_FIN,
                    NUMERO_POLIZA,
                    ESTADO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                RETURNING ID_POLIZA
                """,
                (
                    poliza.id_contrato,
                    poliza.id_seguro,
                    poliza.fecha_inicio,
                    poliza.fecha_fin,
                    poliza.numero_poliza,
                    poliza.estado,
                    created_at,
                    usuario,
                ),
            )

            poliza.id_poliza = cursor.fetchone()[0]
            conn.commit()

            return poliza

    def actualizar_estado(self, id_poliza: int, estado: str, usuario: str) -> bool:
        """
        Actualiza el estado de una póliza existente.
        """
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            updated_at = datetime.now().isoformat()

            cursor.execute(
                f"""
                UPDATE POLIZAS_SEGUROS SET
                    ESTADO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_POLIZA = {placeholder}
                """,
                (estado, updated_at, usuario, id_poliza),
            )

            conn.commit()
            return cursor.rowcount > 0

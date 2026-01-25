"""
Repositorio SQLite: RenovacionContrato
"""

import sqlite3
from typing import List

from src.dominio.entidades.renovacion_contrato import RenovacionContrato
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioRenovacionSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, renovacion: RenovacionContrato, usuario: str) -> RenovacionContrato:
        query = """
        INSERT INTO RENOVACIONES_CONTRATOS (
            ID_CONTRATO_M, ID_CONTRATO_A, TIPO_CONTRATO,
            FECHA_INICIO_ORIGINAL, FECHA_FIN_ORIGINAL,
            FECHA_INICIO_RENOVACION, FECHA_FIN_RENOVACION,
            CANON_ANTERIOR, CANON_NUEVO, PORCENTAJE_INCREMENTO,
            MOTIVO_RENOVACION, FECHA_RENOVACION,
            CREATED_BY, CREATED_AT
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, datetime(f'now', 'localtime'))
        """
        params = (
            renovacion.id_contrato_m,
            renovacion.id_contrato_a,
            renovacion.tipo_contrato,
            renovacion.fecha_inicio_original,
            renovacion.fecha_fin_original,
            renovacion.fecha_inicio_renovacion,
            renovacion.fecha_fin_renovacion,
            renovacion.canon_anterior,
            renovacion.canon_nuevo,
            renovacion.porcentaje_incremento,
            renovacion.motivo_renovacion,
            renovacion.fecha_renovacion,
            usuario,
        )

        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            renovacion.id_renovacion = cursor.lastrowid
            conn.commit()
            return renovacion

    def listar_por_contrato_arrendamiento(self, id_contrato_a: int) -> List[RenovacionContrato]:
        query = """
        SELECT * FROM RENOVACIONES_CONTRATOS 
        WHERE ID_CONTRATO_A = {placeholder}
        ORDER BY FECHA_RENOVACION DESC
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()
        cursor.execute(query, (id_contrato_a,))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _row_to_entity(self, row: sqlite3.Row) -> RenovacionContrato:
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None

        # Convertir a dict si es necesario
        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return RenovacionContrato(
            id_renovacion=(row_dict.get("id_renovacion") or row_dict.get("ID_RENOVACION")),
            id_contrato_m=(row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")),
            id_contrato_a=(row_dict.get("id_contrato_a") or row_dict.get("ID_CONTRATO_A")),
            tipo_contrato=(row_dict.get("tipo_contrato") or row_dict.get("TIPO_CONTRATO")),
            fecha_inicio_original=(
                row_dict.get("fecha_inicio_original") or row_dict.get("FECHA_INICIO_ORIGINAL")
            ),
            fecha_fin_original=(
                row_dict.get("fecha_fin_original") or row_dict.get("FECHA_FIN_ORIGINAL")
            ),
            fecha_inicio_renovacion=(
                row_dict.get("fecha_inicio_renovacion") or row_dict.get("FECHA_INICIO_RENOVACION")
            ),
            fecha_fin_renovacion=(
                row_dict.get("fecha_fin_renovacion") or row_dict.get("FECHA_FIN_RENOVACION")
            ),
            canon_anterior=(row_dict.get("canon_anterior") or row_dict.get("CANON_ANTERIOR")),
            canon_nuevo=(row_dict.get("canon_nuevo") or row_dict.get("CANON_NUEVO")),
            porcentaje_incremento=(
                row_dict.get("porcentaje_incremento") or row_dict.get("PORCENTAJE_INCREMENTO")
            ),
            motivo_renovacion=(
                row_dict.get("motivo_renovacion") or row_dict.get("MOTIVO_RENOVACION")
            ),
            fecha_renovacion=(row_dict.get("fecha_renovacion") or row_dict.get("FECHA_RENOVACION")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
        )

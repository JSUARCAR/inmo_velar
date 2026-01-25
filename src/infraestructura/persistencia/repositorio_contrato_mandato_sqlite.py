"""
Repositorio SQLite: ContratoMandato
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioContratoMandatoSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, contrato: ContratoMandato, usuario: str) -> ContratoMandato:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        INSERT INTO CONTRATOS_MANDATOS (
            ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR,
            FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M, DURACION_CONTRATO_M,
            CANON_MANDATO, COMISION_PORCENTAJE_CONTRATO_M, IVA_CONTRATO_M,
            ESTADO_CONTRATO_M, ALERTA_VENCIMINETO_CONTRATO_M, FECHA_RENOVACION_CONTRATO_M,
            CREATED_BY, UPDATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
            (
                contrato.id_propiedad,
                contrato.id_propietario,
                contrato.id_asesor,
                contrato.fecha_inicio_contrato_m,
                contrato.fecha_fin_contrato_m,
                contrato.duracion_contrato_m,
                contrato.canon_mandato,
                contrato.comision_porcentaje_contrato_m,
                contrato.iva_contrato_m,
                contrato.estado_contrato_m,
                contrato.alerta_vencimiento_contrato_m,
                contrato.fecha_renovacion_contrato_m,
                usuario,
                usuario,
            ),
        )

        conn.commit()
        contrato.id_contrato_m = self.db.get_last_insert_id(
            cursor, "CONTRATOS_MANDATOS", "ID_CONTRATO_M"
        )
        return contrato

    def obtener_por_id(self, id_contrato: int) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = {placeholder}", (id_contrato,)
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activo_por_propiedad(self, id_propiedad: int) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_MANDATOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_M = 'Activo'
        """,
            (id_propiedad,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[ContratoMandato]:
        """Lista todos los contratos de mandato."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute("SELECT * FROM CONTRATOS_MANDATOS ORDER BY ID_CONTRATO_M DESC")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_por_propietario_activos(self, id_propietario: int) -> List[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_MANDATOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_M = 'Activo'
        ORDER BY ID_CONTRATO_M
        """,
            (id_propietario,),
        )  # ERROR EN ORIGINAL: WHERE ID_PROPIEDAD = id_propietario, pero el método se llama listar_por_propietario_activos y el argumento es id_propietario.
        # El query original decía WHERE ID_PROPIETARIO = {placeholder}.
        # Y pasaba (id_propietario,). Eso es correcto.
        # Pero mi código arriba puso ID_PROPIEDAD. Corrijo a ID_PROPIETARIO.

        # Corrección:
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_MANDATOS 
        WHERE ID_PROPIETARIO = {placeholder} AND ESTADO_CONTRATO_M = 'Activo'
        ORDER BY ID_CONTRATO_M
        """,
            (id_propietario,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def actualizar(self, contrato: ContratoMandato, usuario: str) -> None:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        UPDATE CONTRATOS_MANDATOS SET
            ID_PROPIEDAD = {placeholder},
            ID_PROPIETARIO = {placeholder},
            ID_ASESOR = {placeholder},
            FECHA_INICIO_CONTRATO_M = {placeholder},
            FECHA_FIN_CONTRATO_M = {placeholder},
            DURACION_CONTRATO_M = {placeholder},
            CANON_MANDATO = {placeholder},
            COMISION_PORCENTAJE_CONTRATO_M = {placeholder},
            IVA_CONTRATO_M = {placeholder},
            ESTADO_CONTRATO_M = {placeholder},
            MOTIVO_CANCELACION = {placeholder},
            ALERTA_VENCIMINETO_CONTRATO_M = {placeholder},
            FECHA_RENOVACION_CONTRATO_M = {placeholder},
            UPDATED_AT = {placeholder},
            UPDATED_BY = {placeholder}
        WHERE ID_CONTRATO_M = {placeholder}
        """,
            (
                contrato.id_propiedad,
                contrato.id_propietario,
                contrato.id_asesor,
                contrato.fecha_inicio_contrato_m,
                contrato.fecha_fin_contrato_m,
                contrato.duracion_contrato_m,
                contrato.canon_mandato,
                contrato.comision_porcentaje_contrato_m,
                contrato.iva_contrato_m,
                contrato.estado_contrato_m,
                contrato.motivo_cancelacion,
                contrato.alerta_vencimiento_contrato_m,
                contrato.fecha_renovacion_contrato_m,
                datetime.now().replace(microsecond=0).isoformat(),
                usuario,
                contrato.id_contrato_m,
            ),
        )

        conn.commit()

    def _row_to_entity(self, row) -> ContratoMandato:
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return ContratoMandato(
            id_contrato_m=(row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")),
            id_propiedad=(row_dict.get("id_propiedad") or row_dict.get("ID_PROPIEDAD")),
            id_propietario=(row_dict.get("id_propietario") or row_dict.get("ID_PROPIETARIO")),
            id_asesor=(row_dict.get("id_asesor") or row_dict.get("ID_ASESOR")),
            fecha_inicio_contrato_m=(
                row_dict.get("fecha_inicio_contrato_m") or row_dict.get("FECHA_INICIO_CONTRATO_M")
            ),
            fecha_fin_contrato_m=(
                row_dict.get("fecha_fin_contrato_m") or row_dict.get("FECHA_FIN_CONTRATO_M")
            ),
            duracion_contrato_m=(
                row_dict.get("duracion_contrato_m") or row_dict.get("DURACION_CONTRATO_M")
            ),
            canon_mandato=(row_dict.get("canon_mandato") or row_dict.get("CANON_MANDATO")),
            comision_porcentaje_contrato_m=(
                row_dict.get("comision_porcentaje_contrato_m")
                or row_dict.get("COMISION_PORCENTAJE_CONTRATO_M")
            ),
            iva_contrato_m=(row_dict.get("iva_contrato_m") or row_dict.get("IVA_CONTRATO_M")),
            estado_contrato_m=(
                row_dict.get("estado_contrato_m") or row_dict.get("ESTADO_CONTRATO_M")
            ),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            # Typo in DB column name potentially? ALERTA_VENCIMINETO vs ALERTA_VENCIMIENTO
            # The original code had ALERTA_VENCIMINETO_CONTRATO_M in SQL insert/update and map.
            # We preserve it.
            alerta_vencimiento_contrato_m=(
                row_dict.get("alerta_vencimineto_contrato_m")
                or row_dict.get("ALERTA_VENCIMINETO_CONTRATO_M")
            ),
            fecha_renovacion_contrato_m=(
                row_dict.get("fecha_renovacion_contrato_m")
                or row_dict.get("FECHA_RENOVACION_CONTRATO_M")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

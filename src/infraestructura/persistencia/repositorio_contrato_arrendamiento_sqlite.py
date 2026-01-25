"""
Repositorio SQLite: ContratoArrendamiento
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioContratoArrendamientoSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, contrato: ContratoArrendamiento, usuario: str) -> ContratoArrendamiento:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        INSERT INTO CONTRATOS_ARRENDAMIENTOS (
            ID_PROPIEDAD, ID_ARRENDATARIO, ID_CODEUDOR,
            FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A, DURACION_CONTRATO_A,
            CANON_ARRENDAMIENTO, DEPOSITO,
            ESTADO_CONTRATO_A, ALERTA_VENCIMIENTO_CONTRATO_A, ALERTA_IPC,
            FECHA_RENOVACION_CONTRATO_A, FECHA_INCREMENTO_IPC,
            CREATED_BY, UPDATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
            (
                contrato.id_propiedad,
                contrato.id_arrendatario,
                contrato.id_codeudor,
                contrato.fecha_inicio_contrato_a,
                contrato.fecha_fin_contrato_a,
                contrato.duracion_contrato_a,
                contrato.canon_arrendamiento,
                contrato.deposito,
                contrato.estado_contrato_a,
                contrato.alerta_vencimiento_contrato_a,
                contrato.alerta_ipc,
                contrato.fecha_renovacion_contrato_a,
                contrato.fecha_incremento_ipc,
                usuario,
                usuario,
            ),
        )

        conn.commit()
        contrato.id_contrato_a = self.db.get_last_insert_id(
            cursor, "CONTRATOS_ARRENDAMIENTOS", "ID_CONTRATO_A"
        )

        return contrato

    def obtener_por_id(self, id_contrato: int) -> Optional[ContratoArrendamiento]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = {placeholder}",
            (id_contrato,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activo_por_propiedad(self, id_propiedad: int) -> Optional[ContratoArrendamiento]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_ARRENDAMIENTOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_A = 'Activo'
        """,
            (id_propiedad,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activos_por_asesor(self, id_asesor: int) -> List[ContratoArrendamiento]:
        """
        Obtiene los contratos de arrendamiento activos asociados a un asesor activo.
        Realiza JOIN con CONTRATOS_MANDATOS.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
            SELECT ca.* 
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
            WHERE cm.ID_ASESOR = {placeholder}
              AND ca.ESTADO_CONTRATO_A = 'Activo'
              AND cm.ESTADO_CONTRATO_M = 'Activo'
        """

        cursor.execute(query, (id_asesor,))
        rows = cursor.fetchall()

        return [self._row_to_entity(row) for row in rows]

    def obtener_detalle_contratos_asesor(self, id_asesor: int) -> List[dict]:
        """
        Obtiene detalles de contratos activos (incluyendo dirección) para UI.
        Retorna lista de diccionarios.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
            SELECT 
                ca.ID_CONTRATO_A,
                ca.CANON_ARRENDAMIENTO,
                ca.FECHA_INICIO_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            WHERE cm.ID_ASESOR = {placeholder}
              AND ca.ESTADO_CONTRATO_A = 'Activo'
              AND cm.ESTADO_CONTRATO_M = 'Activo'
        """

        cursor.execute(query, (id_asesor,))
        return [dict(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[ContratoArrendamiento]:
        """Lista todos los contratos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS ORDER BY ID_CONTRATO_A DESC")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def actualizar(self, contrato: ContratoArrendamiento, usuario: str) -> None:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        UPDATE CONTRATOS_ARRENDAMIENTOS SET
            FECHA_FIN_CONTRATO_A = {placeholder},
            CANON_ARRENDAMIENTO = {placeholder},
            ESTADO_CONTRATO_A = {placeholder},
            MOTIVO_CANCELACION = {placeholder},
            ALERTA_VENCIMIENTO_CONTRATO_A = {placeholder},
            ALERTA_IPC = {placeholder},
            FECHA_RENOVACION_CONTRATO_A = {placeholder},
            FECHA_INCREMENTO_IPC = {placeholder},
            UPDATED_AT = {placeholder},
            UPDATED_BY = {placeholder}
        WHERE ID_CONTRATO_A = {placeholder}
        """,
            (
                contrato.fecha_fin_contrato_a,
                contrato.canon_arrendamiento,
                contrato.estado_contrato_a,
                contrato.motivo_cancelacion,
                contrato.alerta_vencimiento_contrato_a,
                contrato.alerta_ipc,
                contrato.fecha_renovacion_contrato_a,
                contrato.fecha_incremento_ipc,
                datetime.now().isoformat(),  # updated_at fix (script used hardcoded datetime sqlite function?)
                usuario,
                contrato.id_contrato_a,
            ),
        )

        conn.commit()

    def _row_to_entity(self, row) -> ContratoArrendamiento:
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return ContratoArrendamiento(
            id_contrato_a=(row_dict.get("id_contrato_a") or row_dict.get("ID_CONTRATO_A")),
            id_propiedad=(row_dict.get("id_propiedad") or row_dict.get("ID_PROPIEDAD")),
            id_arrendatario=(row_dict.get("id_arrendatario") or row_dict.get("ID_ARRENDATARIO")),
            id_codeudor=(row_dict.get("id_codeudor") or row_dict.get("ID_CODEUDOR")),
            fecha_inicio_contrato_a=(
                row_dict.get("fecha_inicio_contrato_a") or row_dict.get("FECHA_INICIO_CONTRATO_A")
            ),
            fecha_fin_contrato_a=(
                row_dict.get("fecha_fin_contrato_a") or row_dict.get("FECHA_FIN_CONTRATO_A")
            ),
            duracion_contrato_a=(
                row_dict.get("duracion_contrato_a") or row_dict.get("DURACION_CONTRATO_A")
            ),
            canon_arrendamiento=(
                row_dict.get("canon_arrendamiento") or row_dict.get("CANON_ARRENDAMIENTO")
            ),
            deposito=(row_dict.get("deposito") or row_dict.get("DEPOSITO")),
            estado_contrato_a=(
                row_dict.get("estado_contrato_a") or row_dict.get("ESTADO_CONTRATO_A")
            ),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            alerta_vencimiento_contrato_a=(
                row_dict.get("alerta_vencimiento_contrato_a")
                or row_dict.get("ALERTA_VENCIMIENTO_CONTRATO_A")
            ),
            alerta_ipc=(row_dict.get("alerta_ipc") or row_dict.get("ALERTA_IPC")),
            fecha_renovacion_contrato_a=(
                row_dict.get("fecha_renovacion_contrato_a")
                or row_dict.get("FECHA_RENOVACION_CONTRATO_A")
            ),
            fecha_incremento_ipc=(
                row_dict.get("fecha_incremento_ipc") or row_dict.get("FECHA_INCREMENTO_IPC")
            ),
            # Fecha ultimo incremento no existe en entidad según el código anterior, pero el original lo tenía?
            # Si el original lo tenía en _row_to_entity es porque debería estar.
            # Verifique el código original: 'FECHA_ULTIMO_INCREMENTO_IPC'.
            # Pero ContratoArrendamiento entidad tiene ese campo?
            # Asumamos que sí.
            fecha_ultimo_incremento_ipc=(
                row_dict.get("fecha_ultimo_incremento_ipc")
                or row_dict.get("FECHA_ULTIMO_INCREMENTO_IPC")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

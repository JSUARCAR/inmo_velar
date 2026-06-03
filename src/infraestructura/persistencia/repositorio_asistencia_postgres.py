"""
Repositorio Postgres para AsistenciaAsambleas.
Implementa mapeo 1:1 con tabla ASAMBLEAS.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.asistencia_asambleas import AsistenciaAsambleas
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAsistenciaPostgres:
    """Repositorio para la entidad AsistenciaAsambleas."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Optional[AsistenciaAsambleas]:
        if row is None:
            return None

        # row ya viene como dict gracias a DictCursor
        def get_val(key):
            return row.get(key) or row.get(key.upper()) or row.get(key.lower())

        return AsistenciaAsambleas(
            id_asistencia=get_val("ID_ASISTENCIA"),
            id_propiedad=get_val("ID_PROPIEDAD"),
            fecha_asistencia=get_val("FECHA_ASISTENCIA"),
            hora_asistencia=get_val("HORA_ASISTENCIA"),
            tipo_reunion=get_val("TIPO_REUNION"),
            tipo_asistente=get_val("TIPO_ASISTENTE"),
            costo_asistente=get_val("COSTO_ASISTENTE"),
            id_asistente_persona=get_val("ID_ASISTENTE_PERSONA"),
            direccion_asistencia=get_val("DIRECCION_ASISTENCIA"),
            estado_asistencia=get_val("ESTADO_ASISTENCIA"),
            created_at=get_val("CREATED_AT"),
            updated_at=get_val("UPDATED_AT"),
        )

    def crear(
        self, asistencia: AsistenciaAsambleas, usuario_sistema: str
    ) -> AsistenciaAsambleas:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            INSERT INTO ASAMBLEAS (
                ID_PROPIEDAD, FECHA_ASISTENCIA, HORA_ASISTENCIA,
                TIPO_REUNION, TIPO_ASISTENTE, COSTO_ASISTENTE,
                ID_ASISTENTE_PERSONA, DIRECCION_ASISTENCIA, ESTADO_ASISTENCIA,
                CREATED_AT
            )
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            RETURNING ID_ASISTENCIA
        """

        cursor.execute(
            query,
            (
                asistencia.id_propiedad,
                asistencia.fecha_asistencia,
                asistencia.hora_asistencia,
                asistencia.tipo_reunion,
                asistencia.tipo_asistente,
                asistencia.costo_asistente,
                asistencia.id_asistente_persona,
                asistencia.direccion_asistencia,
                asistencia.estado_asistencia,
                datetime.now().isoformat(),
            ),
        )

        result = cursor.fetchone()
        if result:
            asistencia.id_asistencia = result.get("ID_ASISTENCIA") or result.get(
                "id_asistencia"
            )

        conn.commit()
        cursor.close()
        return asistencia

    def obtener_por_id(self, id_asistencia: int) -> Optional[AsistenciaAsambleas]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"SELECT * FROM ASAMBLEAS WHERE ID_ASISTENCIA = {p}"
        cursor.execute(query, (id_asistencia,))

        row = cursor.fetchone()
        cursor.close()

        return self._row_to_entity(row)

    def listar_por_propiedad(self, id_propiedad: int) -> List[AsistenciaAsambleas]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            SELECT * FROM ASAMBLEAS
            WHERE ID_PROPIEDAD = {p}
            ORDER BY FECHA_ASISTENCIA DESC, HORA_ASISTENCIA DESC
        """
        cursor.execute(query, (id_propiedad,))

        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_entity(row) for row in rows]

    def listar_todas(
        self,
        filtro_estado: Optional[str] = None,
        filtro_fecha_desde: Optional[str] = None,
        filtro_fecha_hasta: Optional[str] = None,
    ) -> List[AsistenciaAsambleas]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = "SELECT * FROM ASAMBLEAS WHERE 1=1"
        params = []

        if filtro_estado:
            query += f" AND ESTADO_ASISTENCIA = {p}"
            params.append(filtro_estado)

        if filtro_fecha_desde:
            query += f" AND FECHA_ASISTENCIA >= {p}"
            params.append(filtro_fecha_desde)

        if filtro_fecha_hasta:
            query += f" AND FECHA_ASISTENCIA <= {p}"
            params.append(filtro_fecha_hasta)

        query += " ORDER BY FECHA_ASISTENCIA DESC, HORA_ASISTENCIA DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_entity(row) for row in rows]

    def listar_por_rango_fechas(
        self,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> List[AsistenciaAsambleas]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            SELECT * FROM ASAMBLEAS
            WHERE FECHA_ASISTENCIA >= {p} AND FECHA_ASISTENCIA <= {p}
            ORDER BY FECHA_ASISTENCIA ASC, HORA_ASISTENCIA ASC
        """
        cursor.execute(query, (fecha_inicio, fecha_fin))
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_entity(row) for row in rows]

    def listar_por_mes(
        self,
        año: int,
        mes: int,
    ) -> List[AsistenciaAsambleas]:
        fecha_inicio = f"{año:04d}-{mes:02d}-01"
        if mes == 12:
            fecha_fin = f"{año + 1:04d}-01-01"
        else:
            fecha_fin = f"{año:04d}-{mes + 1:02d}-01"

        return self.listar_por_rango_fechas(fecha_inicio, fecha_fin)

    def actualizar_estado(
        self, id_asistencia: int, nuevo_estado: str, usuario_sistema: str
    ) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            UPDATE ASAMBLEAS
            SET ESTADO_ASISTENCIA = {p}, UPDATED_AT = {p}
            WHERE ID_ASISTENCIA = {p}
        """

        cursor.execute(query, (nuevo_estado, datetime.now().isoformat(), id_asistencia))
        conn.commit()
        cursor.close()
        return True

    def actualizar(self, asistencia: AsistenciaAsambleas, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            UPDATE ASAMBLEAS SET
                ID_PROPIEDAD = {p},
                FECHA_ASISTENCIA = {p},
                HORA_ASISTENCIA = {p},
                TIPO_REUNION = {p},
                TIPO_ASISTENTE = {p},
                COSTO_ASISTENTE = {p},
                ID_ASISTENTE_PERSONA = {p},
                DIRECCION_ASISTENCIA = {p},
                ESTADO_ASISTENCIA = {p},
                UPDATED_AT = {p}
            WHERE ID_ASISTENCIA = {p}
        """

        cursor.execute(
            query,
            (
                asistencia.id_propiedad,
                asistencia.fecha_asistencia,
                asistencia.hora_asistencia,
                asistencia.tipo_reunion,
                asistencia.tipo_asistente,
                asistencia.costo_asistente,
                asistencia.id_asistente_persona,
                asistencia.direccion_asistencia,
                asistencia.estado_asistencia,
                datetime.now().isoformat(),
                asistencia.id_asistencia,
            ),
        )
        conn.commit()
        cursor.close()
        return True

    def eliminar(self, id_asistencia: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"DELETE FROM ASAMBLEAS WHERE ID_ASISTENCIA = {p}"
        cursor.execute(query, (id_asistencia,))
        conn.commit()
        cursor.close()
        return True

    # --- Métodos Enriquecidos con JOIN (datos completos) ---

    _QUERY_JOIN_BASE = """
        SELECT
            a.ID_ASISTENCIA,
            a.ID_PROPIEDAD,
            a.FECHA_ASISTENCIA,
            a.HORA_ASISTENCIA,
            a.TIPO_REUNION,
            a.TIPO_ASISTENTE,
            a.COSTO_ASISTENTE,
            a.ID_ASISTENTE_PERSONA,
            a.DIRECCION_ASISTENCIA,
            a.ESTADO_ASISTENCIA,
            a.CREATED_AT,
            a.UPDATED_AT,
            COALESCE(p.DIRECCION_PROPIEDAD, 'Sin dirección') AS DIRECCION_PROPIEDAD_JOIN,
            COALESCE(persona_prop.NOMBRE_COMPLETO, 'Propietario desconocido') AS NOMBRE_PROPIETARIO_JOIN,
            COALESCE(persona_asesor.NOMBRE_COMPLETO, 'No asignado') AS NOMBRE_ASESOR_JOIN
        FROM ASAMBLEAS a
        LEFT JOIN PROPIEDADES p ON a.ID_PROPIEDAD = p.ID_PROPIEDAD
        LEFT JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
            AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
        LEFT JOIN PROPIETARIOS prop_jun ON cm.ID_PROPIETARIO = prop_jun.ID_PROPIETARIO
        LEFT JOIN PERSONAS persona_prop ON prop_jun.ID_PERSONA = persona_prop.ID_PERSONA
        LEFT JOIN PROPIETARIOS apo_jun ON cm.ID_ASESOR = apo_jun.ID_PROPIETARIO
        LEFT JOIN PERSONAS persona_asesor ON apo_jun.ID_PERSONA = persona_asesor.ID_PERSONA
    """

    def _row_to_enriched(self, row) -> Optional[dict]:
        """Convierte una fila enriquecida (JOIN) a dict con entidad + datos de propiedad."""
        if row is None:
            return None

        def get_val(key):
            return row.get(key) or row.get(key.upper()) or row.get(key.lower())

        entidad = AsistenciaAsambleas(
            id_asistencia=get_val("ID_ASISTENCIA"),
            id_propiedad=get_val("ID_PROPIEDAD"),
            fecha_asistencia=get_val("FECHA_ASISTENCIA"),
            hora_asistencia=get_val("HORA_ASISTENCIA"),
            tipo_reunion=get_val("TIPO_REUNION"),
            tipo_asistente=get_val("TIPO_ASISTENTE"),
            costo_asistente=get_val("COSTO_ASISTENTE"),
            id_asistente_persona=get_val("ID_ASISTENTE_PERSONA"),
            direccion_asistencia=get_val("DIRECCION_ASISTENCIA"),
            estado_asistencia=get_val("ESTADO_ASISTENCIA"),
            created_at=get_val("CREATED_AT"),
            updated_at=get_val("UPDATED_AT"),
        )

        return {
            "entidad": entidad,
            "direccion_propiedad": get_val("DIRECCION_PROPIEDAD_JOIN") or "Sin dirección",
            "nombre_propietario": get_val("NOMBRE_PROPIETARIO_JOIN") or "Propietario desconocido",
            "nombre_asesor": get_val("NOMBRE_ASESOR_JOIN") or "No asignado",
        }

    def listar_todas_enriquecidas(
        self,
        filtro_estado: Optional[str] = None,
    ) -> List[dict]:
        """Lista asambleas con datos de propiedad/propietario/asesor vía JOIN."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = self._QUERY_JOIN_BASE + " WHERE 1=1"
        params = []

        if filtro_estado:
            query += f" AND a.ESTADO_ASISTENCIA = {p}"
            params.append(filtro_estado)

        query += " ORDER BY a.FECHA_ASISTENCIA DESC, a.HORA_ASISTENCIA DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_enriched(row) for row in rows if row]

    def listar_por_mes_enriquecidas(
        self,
        año: int,
        mes: int,
    ) -> List[dict]:
        """Lista asambleas de un mes con datos enriquecidos vía JOIN."""
        fecha_inicio = f"{año:04d}-{mes:02d}-01"
        if mes == 12:
            fecha_fin = f"{año + 1:04d}-01-01"
        else:
            fecha_fin = f"{año:04d}-{mes + 1:02d}-01"

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = self._QUERY_JOIN_BASE + f"""
            WHERE a.FECHA_ASISTENCIA >= {p} AND a.FECHA_ASISTENCIA < {p}
            ORDER BY a.FECHA_ASISTENCIA ASC, a.HORA_ASISTENCIA ASC
        """

        cursor.execute(query, (fecha_inicio, fecha_fin))
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_enriched(row) for row in rows if row]

    # --- Métodos para Alertas ---

    def listar_asambleas_proximas(self, dias_antelacion: int) -> List[dict]:
        """
        Retorna asambleas programadas en los próximos N días (excluyendo hoy).
        Datos enriquecidos con propietario, dirección y asesor vía JOIN.

        Args:
            dias_antelacion: Número de días hacia adelante a consultar.

        Returns:
            Lista de dicts con entidad + datos de propiedad.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = self._QUERY_JOIN_BASE + f"""
            WHERE a.ESTADO_ASISTENCIA = 'Programada'
              AND a.FECHA_ASISTENCIA > CURRENT_DATE
              AND a.FECHA_ASISTENCIA <= CURRENT_DATE + {p}::integer
            ORDER BY a.FECHA_ASISTENCIA ASC, a.HORA_ASISTENCIA ASC
        """

        cursor.execute(query, (dias_antelacion,))
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_enriched(row) for row in rows if row]

    def listar_asambleas_hoy(self) -> List[dict]:
        """
        Retorna asambleas programadas para hoy con datos enriquecidos.

        Returns:
            Lista de dicts con entidad + datos de propiedad.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = self._QUERY_JOIN_BASE + """
            WHERE a.ESTADO_ASISTENCIA = 'Programada'
              AND a.FECHA_ASISTENCIA = CURRENT_DATE
            ORDER BY a.HORA_ASISTENCIA ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_enriched(row) for row in rows if row]

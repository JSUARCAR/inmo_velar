"""
Repositorio PostgreSQL para Persona.
Implementa mapeo 1:1 estricto con tabla PERSONAS.
"""

from datetime import datetime
from typing import List, Optional
import logging

from src.dominio.entidades.persona import Persona
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioPersonaPostgres:
    """
    Repositorio PostgreSQL para la entidad Persona.
    Garantiza mapeo 1:1 con tabla PERSONAS.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Persona:
        """Convierte una fila SQL a entidad Persona."""
        if row is None:
            return None

        # El wrapper de PostgreSQL ya retorna diccionarios con llaves en mayúsculas
        row_dict = dict(row)

        return Persona(
            id_persona=row_dict.get("ID_PERSONA"),
            tipo_documento=row_dict.get("TIPO_DOCUMENTO"),
            numero_documento=row_dict.get("NUMERO_DOCUMENTO"),
            nombre_completo=row_dict.get("NOMBRE_COMPLETO"),
            telefono_principal=row_dict.get("TELEFONO_PRINCIPAL"),
            correo_electronico=row_dict.get("CORREO_ELECTRONICO"),
            direccion_principal=row_dict.get("DIRECCION_PRINCIPAL"),
            estado_registro=row_dict.get("ESTADO_REGISTRO"),
            motivo_inactivacion=row_dict.get("MOTIVO_INACTIVACION"),
            created_at=row_dict.get("CREATED_AT"),
            created_by=row_dict.get("CREATED_BY"),
            updated_at=row_dict.get("UPDATED_AT"),
            updated_by=row_dict.get("UPDATED_BY"),
        )

    def obtener_por_id(self, id_persona: int) -> Optional[Persona]:
        """Obtiene una persona por su ID."""
        logger.debug(f"Ejecutando obtener_por_id: id_persona={id_persona}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        p = self.db.get_placeholder()
        cursor.execute(f"SELECT * FROM PERSONAS WHERE ID_PERSONA = {p}", (id_persona,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_documento(self, numero_documento: str) -> Optional[Persona]:
        """Obtiene una persona por su número de documento."""
        logger.debug(
            f"Ejecutando obtener_por_documento: numero_documento={numero_documento}"
        )
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        p = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM PERSONAS WHERE NUMERO_DOCUMENTO = {p}", (numero_documento,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def _construir_where_filtros(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        solo_inactivos: bool = False,
        sin_contrato: bool = False,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> tuple:
        """Construye la cláusula WHERE con filtros compartidos.
        
        Retorna: (where_clause, join_clause, params)
        """
        join_clause = ""
        if filtro_rol:
            roles_map = {
                "Propietario": "PROPIETARIOS",
                "Arrendatario": "ARRENDATARIOS",
                "Codeudor": "CODEUDORES",
                "Asesor": "ASESORES",
                "Proveedor": "PROVEEDORES",
            }
            tabla_rol = roles_map.get(filtro_rol)
            if tabla_rol:
                join_clause = f" INNER JOIN {tabla_rol} r ON p.ID_PERSONA = r.ID_PERSONA"

        conditions = []
        params = []

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = TRUE")
        elif solo_inactivos:
            conditions.append("p.ESTADO_REGISTRO = FALSE")

        if sin_contrato:
            conditions.append(
                "("
                "NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN PROPIETARIOS pr ON cm.ID_PROPIETARIO = pr.ID_PROPIETARIO WHERE pr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'ACTIVO') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN ASESORES asr ON cm.ID_ASESOR = asr.ID_ASESOR WHERE asr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'ACTIVO') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO WHERE arr.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'ACTIVO') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CODEUDORES cod ON ca.ID_CODEUDOR = cod.ID_CODEUDOR WHERE cod.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'ACTIVO') "
                "AND ("
                "   NOT EXISTS (SELECT 1 FROM PROVEEDORES prv WHERE prv.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM PROPIETARIOS po WHERE po.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ARRENDATARIOS ar_r WHERE ar_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM CODEUDORES co_r WHERE co_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ASESORES as_r WHERE as_r.ID_PERSONA = p.ID_PERSONA)"
                ")"
                ")"
            )

        p = self.db.get_placeholder()
        if busqueda:
            conditions.append(
                f"(unaccent(p.NOMBRE_COMPLETO) ILIKE unaccent({p}) OR p.NUMERO_DOCUMENTO ILIKE {p})"
            )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if fecha_inicio:
            conditions.append(f"p.CREATED_AT::DATE >= {p}")
            params.append(fecha_inicio)

        if fecha_fin:
            conditions.append(f"p.CREATED_AT::DATE <= {p}")
            params.append(fecha_fin)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, join_clause, params

    def obtener_todos(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        solo_inactivos: bool = False,
        sin_contrato: bool = False,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        sort_by: str = "id_persona",
        sort_order: str = "desc",
    ) -> List[Persona]:
        """Obtiene personas con filtros, paginación y ordenamiento dinámico en PostgreSQL."""
        logger.debug(
            f"Ejecutando obtener_todos (Postgres): filtro_rol={filtro_rol}, sin_contrato={sin_contrato}, sort_by={sort_by}"
        )
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # Mapeo de columnas (Whitelist)
        SORT_COLUMNS = {
            "id_persona": "p.ID_PERSONA",
            "nombre": "p.NOMBRE_COMPLETO",
            "documento": "p.NUMERO_DOCUMENTO",
            "email": "p.CORREO_ELECTRONICO",
            "estado": "p.ESTADO_REGISTRO",
            "creado": "p.CREATED_AT",
        }

        sort_col = SORT_COLUMNS.get(sort_by, "p.ID_PERSONA")
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        # OPTIMIZACIÓN: Usar método compartido para construir filtros
        where_clause, join_clause, params = self._construir_where_filtros(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            solo_inactivos=solo_inactivos,
            sin_contrato=sin_contrato,
            busqueda=busqueda,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        query = f"SELECT DISTINCT p.* FROM PERSONAS p{join_clause}{where_clause}"
        query += f" ORDER BY {sort_col} {order}"

        p = self.db.get_placeholder()
        if limit is not None:
            query += f" LIMIT {p} OFFSET {p}"
            params.extend([limit, offset])

        cursor.execute(query, params)
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def contar_todos(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        solo_inactivos: bool = False,
        sin_contrato: bool = False,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> int:
        """Cuenta total de personas con filtros en PostgreSQL."""
        logger.debug(
            f"Ejecutando contar_todos (Postgres): filtro_rol={filtro_rol}, sin_contrato={sin_contrato}"
        )
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # OPTIMIZACIÓN: Usar método compartido para construir filtros
        where_clause, join_clause, params = self._construir_where_filtros(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            solo_inactivos=solo_inactivos,
            sin_contrato=sin_contrato,
            busqueda=busqueda,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        query = f"SELECT COUNT(DISTINCT p.ID_PERSONA) as TOTAL FROM PERSONAS p{join_clause}{where_clause}"

        cursor.execute(query, params)
        row = cursor.fetchone()
        return row.get("TOTAL", 0) if row else 0

    def obtener_roles_por_personas(self, ids_personas: List[int]) -> dict:
        """Obtiene todos los roles para múltiples personas en una sola consulta.
        
        Retorna un diccionario: {id_persona: {rol: datos_rol, ...}}
        
        Ejemplo de retorno:
        {
            1: {"Propietario": {...}, "Arrendatario": {...}},
            2: {"Codeudor": {...}},
            3: {}
        }
        """
        if not ids_personas:
            return {}

        logger.debug(f"Ejecutando obtener_roles_por_personas: {len(ids_personas)} personas")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        p = self.db.get_placeholder()
        placeholders = ", ".join([f"{p}" for _ in ids_personas])

        query = f"""
            SELECT 'PROPIETARIO' as ROL, ID_PERSONA, 
                   ID_PROPIETARIO as ID_ENTIDAD, 
                   OBSERVACIONES_PROPIETARIO as OBSERVACIONES,
                   ESTADO_PROPIETARIO as ESTADO,
                   FECHA_INGRESO_PROPIETARIO as FECHA_INGRESO
            FROM PROPIETARIOS 
            WHERE ID_PERSONA IN ({placeholders})
            
            UNION ALL
            
            SELECT 'ARRENDATARIO' as ROL, ID_PERSONA,
                   ID_ARRENDATARIO as ID_ENTIDAD,
                   CODIGO_APROBACION_SEGURO as OBSERVACIONES,
                   NULL as ESTADO,
                   FECHA_INGRESO_ARRENDATARIO as FECHA_INGRESO
            FROM ARRENDATARIOS 
            WHERE ID_PERSONA IN ({placeholders})
            
            UNION ALL
            
            SELECT 'CODEUDOR' as ROL, ID_PERSONA,
                   ID_CODEUDOR as ID_ENTIDAD,
                   NULL as OBSERVACIONES,
                   NULL as ESTADO,
                   NULL as FECHA_INGRESO
            FROM CODEUDORES 
            WHERE ID_PERSONA IN ({placeholders})
            
            UNION ALL
            
            SELECT 'ASESOR' as ROL, ID_PERSONA,
                   ID_ASESOR as ID_ENTIDAD,
                   NULL as OBSERVACIONES,
                   NULL as ESTADO,
                   NULL as FECHA_INGRESO
            FROM ASESORES 
            WHERE ID_PERSONA IN ({placeholders})
            
            UNION ALL
            
            SELECT 'PROVEEDOR' as ROL, ID_PERSONA,
                   ID_PROVEEDOR as ID_ENTIDAD,
                   OBSERVACIONES as OBSERVACIONES,
                   ESTADO_REGISTRO as ESTADO,
                   CREATED_AT as FECHA_INGRESO
            FROM PROVEEDORES 
            WHERE ID_PERSONA IN ({placeholders})
        """

        # Los placeholders se repiten 5 veces (una por cada tabla)
        all_params = ids_personas * 5
        cursor.execute(query, all_params)

        # Agrupar resultados por persona
        resultado = {}
        for row in cursor.fetchall():
            id_persona = row["ID_PERSONA"]
            rol = row["ROL"]
            
            if id_persona not in resultado:
                resultado[id_persona] = {}
            
            resultado[id_persona][rol] = {
                "id_entidad": row["ID_ENTIDAD"],
                "observaciones": row["OBSERVACIONES"],
                "estado": row["ESTADO"],
                "fecha_ingreso": row["FECHA_INGRESO"],
            }

        return resultado

    def crear(self, persona: Persona, usuario_sistema: str) -> Persona:
        """Crea una nueva persona con RETURNING id (PostgreSQL)."""
        logger.debug(
            f"Ejecutando crear persona (Postgres): documento={persona.numero_documento}"
        )
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        p = self.db.get_placeholder()

        cursor.execute(
            f"""
            INSERT INTO PERSONAS (
                TIPO_DOCUMENTO,
                NUMERO_DOCUMENTO,
                NOMBRE_COMPLETO,
                TELEFONO_PRINCIPAL,
                CORREO_ELECTRONICO,
                DIRECCION_PRINCIPAL,
                ESTADO_REGISTRO,
                CREATED_AT,
                CREATED_BY
            ) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            RETURNING ID_PERSONA
            """,
            (
                persona.tipo_documento,
                persona.numero_documento,
                persona.nombre_completo,
                persona.telefono_principal,
                persona.correo_electronico,
                persona.direccion_principal,
                (
                    bool(persona.estado_registro)
                    if persona.estado_registro is not None
                    else True
                ),
                persona.created_at or datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        id_persona = cursor.fetchone()
        if id_persona:
            if isinstance(id_persona, dict):
                persona.id_persona = id_persona["ID_PERSONA"]
            else:
                persona.id_persona = id_persona[0]

        conn.commit()
        return persona

    def actualizar(self, persona: Persona, usuario_sistema: str) -> bool:
        """Actualiza una persona existente en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        p = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE PERSONAS SET
                TIPO_DOCUMENTO = {p},
                NUMERO_DOCUMENTO = {p},
                NOMBRE_COMPLETO = {p},
                TELEFONO_PRINCIPAL = {p},
                CORREO_ELECTRONICO = {p},
                DIRECCION_PRINCIPAL = {p},
                ESTADO_REGISTRO = {p},
                UPDATED_AT = {p},
                UPDATED_BY = {p}
            WHERE ID_PERSONA = {p}
            """,
            (
                persona.tipo_documento,
                persona.numero_documento,
                persona.nombre_completo,
                persona.telefono_principal,
                persona.correo_electronico,
                persona.direccion_principal,
                (
                    bool(persona.estado_registro)
                    if persona.estado_registro is not None
                    else True
                ),
                datetime.now().isoformat(),
                usuario_sistema,
                persona.id_persona,
            ),
        )

        conn.commit()
        return cursor.rowcount > 0

    def inactivar(self, id_persona: int, motivo: str, usuario_sistema: str) -> bool:
        """Inactiva una persona (soft delete) en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        p = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE PERSONAS SET
                ESTADO_REGISTRO = FALSE,
                MOTIVO_INACTIVACION = {p},
                UPDATED_AT = {p},
                UPDATED_BY = {p}
            WHERE ID_PERSONA = {p}
            """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_persona),
        )

        conn.commit()
        return cursor.rowcount > 0

    def obtener_por_email(self, email: str) -> Optional[Persona]:
        """Busca una persona por email."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM PERSONAS WHERE CORREO_ELECTRONICO = {p}", (email,)
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def buscar_por_nombre(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Persona]:
        """Búsqueda fuzzy por nombre en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        query = f"""
            SELECT * FROM PERSONAS 
            WHERE unaccent(NOMBRE_COMPLETO) ILIKE unaccent({p})
            AND ESTADO_REGISTRO = TRUE
            LIMIT {p}
        """
        cursor.execute(query, (f"%{termino_busqueda}%", limite))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_conteos_por_rol(self) -> dict[str, dict[str, int]]:
        """Obtiene el número total de personas activas e inactivas que tienen cada rol."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # Consulta unificada para obtener activos e inactivos por rol
        # Un registro se considera activo si tanto la PERSONA como el ROL están activos.
        # Caso especial: PROVEEDORES no tiene ESTADO_PROVEEDOR en algunos esquemas, usamos ESTADO_REGISTRO de persona.
        query = """
        SELECT 
            -- Propietarios
            COUNT(CASE WHEN pr.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO IS TRUE AND pr.ESTADO_PROPIETARIO::INTEGER = 1 THEN 1 END) as prop_activos,
            COUNT(CASE WHEN pr.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO IS FALSE OR pr.ESTADO_PROPIETARIO::INTEGER = 0) THEN 1 END) as prop_inactivos,
            -- Arrendatarios
            COUNT(CASE WHEN ar.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO IS TRUE AND ar.ESTADO_ARRENDATARIO::INTEGER = 1 THEN 1 END) as arr_activos,
            COUNT(CASE WHEN ar.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO IS FALSE OR ar.ESTADO_ARRENDATARIO::INTEGER = 0) THEN 1 END) as arr_inactivos,
            -- Codeudores
            COUNT(CASE WHEN co.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO IS TRUE AND co.ESTADO_REGISTRO::INTEGER = 1 THEN 1 END) as cod_activos,
            COUNT(CASE WHEN co.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO IS FALSE OR co.ESTADO_REGISTRO::INTEGER = 0) THEN 1 END) as cod_inactivos,
            -- Asesores
            COUNT(CASE WHEN ase.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO IS TRUE AND ase.ESTADO::INTEGER = 1 THEN 1 END) as ase_activos,
            COUNT(CASE WHEN ase.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO IS FALSE OR ase.ESTADO::INTEGER = 0) THEN 1 END) as ase_inactivos,
            -- Proveedores
            COUNT(CASE WHEN prov.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO IS TRUE AND prov.ESTADO_REGISTRO::INTEGER = 1 THEN 1 END) as prov_activos,
            COUNT(CASE WHEN prov.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO IS FALSE OR prov.ESTADO_REGISTRO::INTEGER = 0) THEN 1 END) as prov_inactivos
        FROM PERSONAS p
        LEFT JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA
        LEFT JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA
        LEFT JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA
        LEFT JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA
        LEFT JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA
        """

        cursor.execute(query)
        row = cursor.fetchone()

        conteos = {
            "Propietario": {"activos": 0, "inactivos": 0},
            "Arrendatario": {"activos": 0, "inactivos": 0},
            "Codeudor": {"activos": 0, "inactivos": 0},
            "Asesor": {"activos": 0, "inactivos": 0},
            "Proveedor": {"activos": 0, "inactivos": 0},
        }

        if row:
            conteos["Propietario"]["activos"] = row.get("PROP_ACTIVOS", 0)
            conteos["Propietario"]["inactivos"] = row.get("PROP_INACTIVOS", 0)

            conteos["Arrendatario"]["activos"] = row.get("ARR_ACTIVOS", 0)
            conteos["Arrendatario"]["inactivos"] = row.get("ARR_INACTIVOS", 0)

            conteos["Codeudor"]["activos"] = row.get("COD_ACTIVOS", 0)
            conteos["Codeudor"]["inactivos"] = row.get("COD_INACTIVOS", 0)

            conteos["Asesor"]["activos"] = row.get("ASE_ACTIVOS", 0)
            conteos["Asesor"]["inactivos"] = row.get("ASE_INACTIVOS", 0)

            conteos["Proveedor"]["activos"] = row.get("PROV_ACTIVOS", 0)
            conteos["Proveedor"]["inactivos"] = row.get("PROV_INACTIVOS", 0)

        return conteos

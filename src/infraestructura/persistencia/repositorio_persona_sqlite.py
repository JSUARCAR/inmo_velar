"""
Repositorio SQLite para Persona.
Implementa mapeo 1:1 estricto con tabla PERSONAS.
"""

from datetime import datetime
from typing import List, Optional
import logging

from src.dominio.entidades.persona import Persona
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)

class RepositorioPersonaSQLite:
    """
    Repositorio SQLite para la entidad Persona.
    Garantiza mapeo 1:1 con tabla PERSONAS.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Persona:
        """Convierte una fila SQL a entidad Persona."""
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None

        # Convertir a dict si es necesario
        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return Persona(
            id_persona=(row_dict.get("id_persona") or row_dict.get("ID_PERSONA")),
            tipo_documento=(row_dict.get("tipo_documento") or row_dict.get("TIPO_DOCUMENTO")),
            numero_documento=(row_dict.get("numero_documento") or row_dict.get("NUMERO_DOCUMENTO")),
            nombre_completo=(row_dict.get("nombre_completo") or row_dict.get("NOMBRE_COMPLETO")),
            telefono_principal=(
                row_dict.get("telefono_principal") or row_dict.get("TELEFONO_PRINCIPAL")
            ),
            correo_electronico=(
                row_dict.get("correo_electronico") or row_dict.get("CORREO_ELECTRONICO")
            ),
            direccion_principal=(
                row_dict.get("direccion_principal") or row_dict.get("DIRECCION_PRINCIPAL")
            ),
            estado_registro=(row_dict.get("estado_registro") or row_dict.get("ESTADO_REGISTRO")),
            motivo_inactivacion=(
                row_dict.get("motivo_inactivacion") or row_dict.get("MOTIVO_INACTIVACION")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def obtener_por_id(self, id_persona: int) -> Optional[Persona]:
        """Obtiene una persona por su ID."""
        logger.debug(f"Ejecutando obtener_por_id: id_persona={id_persona}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(f"SELECT * FROM PERSONAS WHERE ID_PERSONA = {placeholder}", (id_persona,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_documento(self, numero_documento: str) -> Optional[Persona]:
        """Obtiene una persona por su número de documento."""
        logger.debug(f"Ejecutando obtener_por_documento: numero_documento={numero_documento}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PERSONAS WHERE NUMERO_DOCUMENTO = {placeholder}", (numero_documento,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

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
        """Obtiene personas con filtros, paginación y ordenamiento dinámico."""
        logger.debug(f"Ejecutando obtener_todos: filtro_rol={filtro_rol}, sin_contrato={sin_contrato}, sort_by={sort_by}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Mapeo de columnas (Whitelist)
        SORT_COLUMNS = {
            "id_persona": "p.ID_PERSONA",
            "nombre": "p.NOMBRE_COMPLETO",
            "documento": "p.NUMERO_DOCUMENTO",
            "email": "p.CORREO_ELECTRONICO",
            "estado": "p.ESTADO_REGISTRO",
            "creado": "p.CREATED_AT"
        }
        
        sort_col = SORT_COLUMNS.get(sort_by, "p.ID_PERSONA")
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        query = "SELECT DISTINCT p.* FROM PERSONAS p"
        join_clause = ""
        if filtro_rol:
            if filtro_rol == "Propietario":
                join_clause = " INNER JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA"
            elif filtro_rol == "Arrendatario":
                join_clause = " INNER JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA"
            elif filtro_rol == "Codeudor":
                join_clause = " INNER JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA"
            elif filtro_rol == "Asesor":
                join_clause = " INNER JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA"
            elif filtro_rol == "Proveedor":
                join_clause = " INNER JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA"
        
        query += join_clause
        conditions = []
        params = []

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = TRUE")
        elif solo_inactivos:
            conditions.append("p.ESTADO_REGISTRO = FALSE")

        if sin_contrato:
            conditions.append(
                "("
                "NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN PROPIETARIOS pr ON cm.ID_PROPIETARIO = pr.ID_PROPIETARIO WHERE pr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN ASESORES asr ON cm.ID_ASESOR = asr.ID_ASESOR WHERE asr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN ARRENDATARIOS ar ON ca.ID_ARRENDATARIO = ar.ID_ARRENDATARIO WHERE ar.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CODEUDORES co ON ca.ID_CODEUDOR = co.ID_CODEUDOR WHERE co.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'Activo') "
                "AND ("
                "   NOT EXISTS (SELECT 1 FROM PROVEEDORES prv WHERE prv.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM PROPIETARIOS po WHERE po.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ARRENDATARIOS ar_r WHERE ar_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM CODEUDORES co_r WHERE co_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ASESORES as_r WHERE as_r.ID_PERSONA = p.ID_PERSONA)"
                ")"
                ")"
            )

        if busqueda:
            if self.db.use_postgresql:
                conditions.append(
                    f"(TRANSLATE(p.NOMBRE_COMPLETO, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') ILIKE TRANSLATE({placeholder}, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') OR TRANSLATE(p.NUMERO_DOCUMENTO, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') ILIKE TRANSLATE({placeholder}, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU'))"
                )
            else:
                conditions.append(
                    f"(p.NOMBRE_COMPLETO LIKE {placeholder} OR p.NUMERO_DOCUMENTO LIKE {placeholder})"
                )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if fecha_inicio:
            conditions.append(f"DATE(p.CREATED_AT) >= {placeholder}")
            params.append(fecha_inicio)

        if fecha_fin:
            conditions.append(f"DATE(p.CREATED_AT) <= {placeholder}")
            params.append(fecha_fin)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY {sort_col} {order}"

        if limit is not None:
            query += f" LIMIT {placeholder} OFFSET {placeholder}"
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
        """Cuenta total de personas con filtros."""
        logger.debug(f"Ejecutando contar_todos: filtro_rol={filtro_rol}, solo_activos={solo_activos}, sin_contrato={sin_contrato}, busqueda={busqueda}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Usar alias TOTAL en mayúsculas para consistencia
        query = "SELECT COUNT(DISTINCT p.ID_PERSONA) as TOTAL FROM PERSONAS p"
        join_clause = ""
        if filtro_rol:
            if filtro_rol == "Propietario":
                join_clause = " INNER JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA"
            elif filtro_rol == "Arrendatario":
                join_clause = " INNER JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA"
            elif filtro_rol == "Codeudor":
                join_clause = " INNER JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA"
            elif filtro_rol == "Asesor":
                join_clause = " INNER JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA"
            elif filtro_rol == "Proveedor":
                join_clause = " INNER JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA"
        
        query += join_clause
        conditions = []
        params = []

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = TRUE")
        elif solo_inactivos:
            conditions.append("p.ESTADO_REGISTRO = FALSE")

        if sin_contrato:
            conditions.append(
                "("
                "NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN PROPIETARIOS pr ON cm.ID_PROPIETARIO = pr.ID_PROPIETARIO WHERE pr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm JOIN ASESORES asr ON cm.ID_ASESOR = asr.ID_ASESOR WHERE asr.ID_PERSONA = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN ARRENDATARIOS ar ON ca.ID_ARRENDATARIO = ar.ID_ARRENDATARIO WHERE ar.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'Activo') "
                "AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CODEUDORES co ON ca.ID_CODEUDOR = co.ID_CODEUDOR WHERE co.ID_PERSONA = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'Activo') "
                "AND ("
                "   NOT EXISTS (SELECT 1 FROM PROVEEDORES prv WHERE prv.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM PROPIETARIOS po WHERE po.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ARRENDATARIOS ar_r WHERE ar_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM CODEUDORES co_r WHERE co_r.ID_PERSONA = p.ID_PERSONA) "
                "   OR EXISTS (SELECT 1 FROM ASESORES as_r WHERE as_r.ID_PERSONA = p.ID_PERSONA)"
                ")"
                ")"
            )

        if busqueda:
            if self.db.use_postgresql:
                conditions.append(
                    f"(TRANSLATE(p.NOMBRE_COMPLETO, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') ILIKE TRANSLATE({placeholder}, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') OR TRANSLATE(p.NUMERO_DOCUMENTO, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU') ILIKE TRANSLATE({placeholder}, 'áéíóúÁÉÍÓÚ', 'aeiouAEIOU'))"
                )
            else:
                conditions.append(
                    f"(p.NOMBRE_COMPLETO LIKE {placeholder} OR p.NUMERO_DOCUMENTO LIKE {placeholder})"
                )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if fecha_inicio:
            conditions.append(f"DATE(p.CREATED_AT) >= {placeholder}")
            params.append(fecha_inicio)

        if fecha_fin:
            conditions.append(f"DATE(p.CREATED_AT) <= {placeholder}")
            params.append(fecha_fin)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            # Soporte robusto para sqlite3.Row (acceso key/index) y dict (Postgres wrapper/Uppercase)
            try:
                # Intento 1: Alias explícito (Uppercase común en Postgres wrapper)
                return row["TOTAL"]
            except (KeyError, TypeError):
                try:
                    # Intento 2: Lowercase (SQLite dict factory a veces)
                    return row["total"]
                except (KeyError, TypeError):
                    # Intento 3: Index access (sqlite3.Row o Tuple)
                    try:
                        return row[0]
                    except (IndexError, TypeError):
                        pass
                    # Intento 4: Primer valor de dict (si las keys son raras)
        return 0

    def obtener_conteos_por_rol(self) -> dict[str, dict[str, int]]:
        """Obtiene el número total de personas activas e inactivas que tienen cada rol."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # Consulta unificada para SQLite corregida para evitar inflación
        query = """
        SELECT 
            -- Propietarios
            SUM(CASE WHEN pr.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO = 1 AND pr.ESTADO_PROPIETARIO = 1 THEN 1 ELSE 0 END) as prop_activos,
            SUM(CASE WHEN pr.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO = 0 OR pr.ESTADO_PROPIETARIO = 0) THEN 1 ELSE 0 END) as prop_inactivos,
            -- Arrendatarios
            SUM(CASE WHEN ar.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO = 1 AND ar.ESTADO_ARRENDATARIO = 1 THEN 1 ELSE 0 END) as arr_activos,
            SUM(CASE WHEN ar.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO = 0 OR ar.ESTADO_ARRENDATARIO = 0) THEN 1 ELSE 0 END) as arr_inactivos,
            -- Codeudores
            SUM(CASE WHEN co.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO = 1 AND co.ESTADO_REGISTRO = 1 THEN 1 ELSE 0 END) as cod_activos,
            SUM(CASE WHEN co.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO = 0 OR co.ESTADO_REGISTRO = 0) THEN 1 ELSE 0 END) as cod_inactivos,
            -- Asesores
            SUM(CASE WHEN ase.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO = 1 AND ase.ESTADO = 1 THEN 1 ELSE 0 END) as ase_activos,
            SUM(CASE WHEN ase.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO = 0 OR ase.ESTADO = 0) THEN 1 ELSE 0 END) as ase_inactivos,
            -- Proveedores
            SUM(CASE WHEN prov.ID_PERSONA IS NOT NULL AND p.ESTADO_REGISTRO = 1 AND prov.ESTADO_REGISTRO = 1 THEN 1 ELSE 0 END) as prov_activos,
            SUM(CASE WHEN prov.ID_PERSONA IS NOT NULL AND (p.ESTADO_REGISTRO = 0 OR prov.ESTADO_REGISTRO = 0) THEN 1 ELSE 0 END) as prov_inactivos
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
            "Proveedor": {"activos": 0, "inactivos": 0}
        }

        if row:
            r_dict = dict(row)
            # Normalizar nombres de columnas a lowercase para SQLite dict factory
            r_dict = {k.lower(): v for k, v in r_dict.items()}
            
            conteos["Propietario"]["activos"] = r_dict.get("prop_activos") or 0
            conteos["Propietario"]["inactivos"] = r_dict.get("prop_inactivos") or 0
            
            conteos["Arrendatario"]["activos"] = r_dict.get("arr_activos") or 0
            conteos["Arrendatario"]["inactivos"] = r_dict.get("arr_inactivos") or 0
            
            conteos["Codeudor"]["activos"] = r_dict.get("cod_activos") or 0
            conteos["Codeudor"]["inactivos"] = r_dict.get("cod_inactivos") or 0
            
            conteos["Asesor"]["activos"] = r_dict.get("ase_activos") or 0
            conteos["Asesor"]["inactivos"] = r_dict.get("ase_inactivos") or 0
            
            conteos["Proveedor"]["activos"] = r_dict.get("prov_activos") or 0
            conteos["Proveedor"]["inactivos"] = r_dict.get("prov_inactivos") or 0
                
        return conteos
        return conteos

    def crear(self, persona: Persona, usuario_sistema: str) -> Persona:
        """Crea una nueva persona en la BD."""
        logger.debug(f"Ejecutando crear persona: documento={persona.numero_documento}, usuario_sistema={usuario_sistema}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

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
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """,
            (
                persona.tipo_documento,
                persona.numero_documento,
                persona.nombre_completo,
                persona.telefono_principal,
                persona.correo_electronico,
                persona.direccion_principal,
                (
                    bool(persona.estado_registro) if persona.estado_registro is not None else True
                ),  # PostgreSQL boolean
                persona.created_at or datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        conn.commit()
        persona.id_persona = self.db.get_last_insert_id(cursor, "PERSONAS", "ID_PERSONA")

        return persona

    def actualizar(self, persona: Persona, usuario_sistema: str) -> bool:
        """Actualiza una persona existente."""
        logger.debug(f"Ejecutando actualizar persona: id_persona={persona.id_persona}, usuario_sistema={usuario_sistema}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE PERSONAS SET
                TIPO_DOCUMENTO = {placeholder},
                NUMERO_DOCUMENTO = {placeholder},
                NOMBRE_COMPLETO = {placeholder},
                TELEFONO_PRINCIPAL = {placeholder},
                CORREO_ELECTRONICO = {placeholder},
                DIRECCION_PRINCIPAL = {placeholder},
                ESTADO_REGISTRO = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_PERSONA = {placeholder}
            """,
            (
                persona.tipo_documento,
                persona.numero_documento,
                persona.nombre_completo,
                persona.telefono_principal,
                persona.correo_electronico,
                persona.direccion_principal,
                bool(persona.estado_registro) if persona.estado_registro is not None else True,
                datetime.now().isoformat(),
                usuario_sistema,
                persona.id_persona,
            ),
        )

        conn.commit()
        return cursor.rowcount > 0

    def inactivar(self, id_persona: int, motivo: str, usuario_sistema: str) -> bool:
        """Inactiva una persona (soft delete)."""
        logger.debug(f"Ejecutando inactivar persona: id_persona={id_persona}, motivo={motivo}, usuario_sistema={usuario_sistema}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE PERSONAS SET
                ESTADO_REGISTRO = FALSE,
                MOTIVO_INACTIVACION = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_PERSONA = {placeholder}
            """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_persona),
        )

        conn.commit()
        return cursor.rowcount > 0

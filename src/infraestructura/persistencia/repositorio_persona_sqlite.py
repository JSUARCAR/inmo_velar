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
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Persona]:
        """Obtiene personas con filtros y paginación."""
        logger.debug(f"Ejecutando obtener_todos: filtro_rol={filtro_rol}, solo_activos={solo_activos}, busqueda={busqueda}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, limit={limit}, offset={offset}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

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

        query += " ORDER BY p.NOMBRE_COMPLETO"

        if limit is not None:
            query += f" LIMIT {placeholder} OFFSET {placeholder}"
            params.extend([limit, offset])

        cursor.execute(query, params)
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def contar_todos(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> int:
        """Cuenta total de personas con filtros."""
        logger.debug(f"Ejecutando contar_todos: filtro_rol={filtro_rol}, solo_activos={solo_activos}, busqueda={busqueda}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
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

    def obtener_conteos_por_rol(self, solo_activos: bool = True) -> dict[str, int]:
        """Obtiene el número total de personas que tienen cada rol (Propietario, Arrendatario, etc.)"""
        logger.debug(f"Ejecutando obtener_conteos_por_rol: solo_activos={solo_activos}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        condition = "WHERE p.ESTADO_REGISTRO = TRUE" if solo_activos else ""

        query = f"""
        SELECT 
            (SELECT COUNT(pr.ID_PERSONA) FROM PROPIETARIOS pr INNER JOIN PERSONAS p ON p.ID_PERSONA = pr.ID_PERSONA {condition}) as total_propietarios,
            (SELECT COUNT(ar.ID_PERSONA) FROM ARRENDATARIOS ar INNER JOIN PERSONAS p ON p.ID_PERSONA = ar.ID_PERSONA {condition}) as total_arrendatarios,
            (SELECT COUNT(co.ID_PERSONA) FROM CODEUDORES co INNER JOIN PERSONAS p ON p.ID_PERSONA = co.ID_PERSONA {condition}) as total_codeudores,
            (SELECT COUNT(ase.ID_PERSONA) FROM ASESORES ase INNER JOIN PERSONAS p ON p.ID_PERSONA = ase.ID_PERSONA {condition}) as total_asesores,
            (SELECT COUNT(prov.ID_PERSONA) FROM PROVEEDORES prov INNER JOIN PERSONAS p ON p.ID_PERSONA = prov.ID_PERSONA {condition}) as total_proveedores
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        conteos = {
            "Propietario": 0,
            "Arrendatario": 0,
            "Codeudor": 0,
            "Asesor": 0,
            "Proveedor": 0
        }

        if row:
            if isinstance(row, dict) or hasattr(row, "keys"):
                # dict-like (psycopg2 RealDictRow v. sqlite3.Row)
                r_dict = dict(row)
                conteos["Propietario"] = r_dict.get("total_propietarios") or r_dict.get("TOTAL_PROPIETARIOS") or 0
                conteos["Arrendatario"] = r_dict.get("total_arrendatarios") or r_dict.get("TOTAL_ARRENDATARIOS") or 0
                conteos["Codeudor"] = r_dict.get("total_codeudores") or r_dict.get("TOTAL_CODEUDORES") or 0
                conteos["Asesor"] = r_dict.get("total_asesores") or r_dict.get("TOTAL_ASESORES") or 0
                conteos["Proveedor"] = r_dict.get("total_proveedores") or r_dict.get("TOTAL_PROVEEDORES") or 0
            else:
                # tuple fallback
                conteos["Propietario"] = row[0] or 0
                conteos["Arrendatario"] = row[1] or 0
                conteos["Codeudor"] = row[2] or 0
                conteos["Asesor"] = row[3] or 0
                conteos["Proveedor"] = row[4] or 0
                
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

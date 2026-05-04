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

        cursor.execute("SELECT * FROM PERSONAS WHERE ID_PERSONA = %s", (id_persona,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_documento(self, numero_documento: str) -> Optional[Persona]:
        """Obtiene una persona por su número de documento."""
        logger.debug(f"Ejecutando obtener_por_documento: numero_documento={numero_documento}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PERSONAS WHERE NUMERO_DOCUMENTO = %s", (numero_documento,)
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
        """Obtiene personas con filtros y paginación en PostgreSQL."""
        logger.debug(f"Ejecutando obtener_todos (Postgres): filtro_rol={filtro_rol}, solo_activos={solo_activos}")
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT DISTINCT p.* FROM PERSONAS p"
        join_clause = ""
        if filtro_rol:
            roles_map = {
                "Propietario": "PROPIETARIOS",
                "Arrendatario": "ARRENDATARIOS",
                "Codeudor": "CODEUDORES",
                "Asesor": "ASESORES",
                "Proveedor": "PROVEEDORES"
            }
            tabla_rol = roles_map.get(filtro_rol)
            if tabla_rol:
                join_clause = f" INNER JOIN {tabla_rol} r ON p.ID_PERSONA = r.ID_PERSONA"
        
        query += join_clause
        conditions = []
        params = []

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = TRUE")

        if busqueda:
            # Uso de unaccent para PostgreSQL nativo como se sugirió
            conditions.append(
                "(unaccent(p.NOMBRE_COMPLETO) ILIKE unaccent(%s) OR p.NUMERO_DOCUMENTO ILIKE %s)"
            )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if fecha_inicio:
            conditions.append("p.CREATED_AT::DATE >= %s")
            params.append(fecha_inicio)

        if fecha_fin:
            conditions.append("p.CREATED_AT::DATE <= %s")
            params.append(fecha_fin)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.NOMBRE_COMPLETO"

        if limit is not None:
            query += " LIMIT %s OFFSET %s"
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
        """Cuenta total de personas con filtros en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT COUNT(DISTINCT p.ID_PERSONA) as TOTAL FROM PERSONAS p"
        join_clause = ""
        if filtro_rol:
            roles_map = {
                "Propietario": "PROPIETARIOS",
                "Arrendatario": "ARRENDATARIOS",
                "Codeudor": "CODEUDORES",
                "Asesor": "ASESORES",
                "Proveedor": "PROVEEDORES"
            }
            tabla_rol = roles_map.get(filtro_rol)
            if tabla_rol:
                join_clause = f" INNER JOIN {tabla_rol} r ON p.ID_PERSONA = r.ID_PERSONA"
        
        query += join_clause
        conditions = []
        params = []

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = TRUE")

        if busqueda:
            conditions.append(
                "(unaccent(p.NOMBRE_COMPLETO) ILIKE unaccent(%s) OR p.NUMERO_DOCUMENTO ILIKE %s)"
            )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if fecha_inicio:
            conditions.append("p.CREATED_AT::DATE >= %s")
            params.append(fecha_inicio)

        if fecha_fin:
            conditions.append("p.CREATED_AT::DATE <= %s")
            params.append(fecha_fin)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        return row.get("TOTAL", 0) if row else 0

    def crear(self, persona: Persona, usuario_sistema: str) -> Persona:
        """Crea una nueva persona con RETURNING id (PostgreSQL)."""
        logger.debug(f"Ejecutando crear persona (Postgres): documento={persona.numero_documento}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_PERSONA
            """,
            (
                persona.tipo_documento,
                persona.numero_documento,
                persona.nombre_completo,
                persona.telefono_principal,
                persona.correo_electronico,
                persona.direccion_principal,
                bool(persona.estado_registro) if persona.estado_registro is not None else True,
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

        cursor.execute(
            """
            UPDATE PERSONAS SET
                TIPO_DOCUMENTO = %s,
                NUMERO_DOCUMENTO = %s,
                NOMBRE_COMPLETO = %s,
                TELEFONO_PRINCIPAL = %s,
                CORREO_ELECTRONICO = %s,
                DIRECCION_PRINCIPAL = %s,
                ESTADO_REGISTRO = %s,
                UPDATED_AT = %s,
                UPDATED_BY = %s
            WHERE ID_PERSONA = %s
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
        """Inactiva una persona (soft delete) en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE PERSONAS SET
                ESTADO_REGISTRO = FALSE,
                MOTIVO_INACTIVACION = %s,
                UPDATED_AT = %s,
                UPDATED_BY = %s
            WHERE ID_PERSONA = %s
            """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_persona),
        )

        conn.commit()
        return cursor.rowcount > 0

    def obtener_por_email(self, email: str) -> Optional[Persona]:
        """Busca una persona por email."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute("SELECT * FROM PERSONAS WHERE CORREO_ELECTRONICO = %s", (email,))
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def buscar_por_nombre(self, termino_busqueda: str, limite: int = 20) -> List[Persona]:
        """Búsqueda fuzzy por nombre en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        query = """
            SELECT * FROM PERSONAS 
            WHERE unaccent(NOMBRE_COMPLETO) ILIKE unaccent(%s)
            AND ESTADO_REGISTRO = TRUE
            LIMIT %s
        """
        cursor.execute(query, (f"%{termino_busqueda}%", limite))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_conteos_por_rol(self, solo_activos: bool = True) -> dict[str, int]:
        """Obtiene el número total de personas que tienen cada rol."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

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
            # En PostgreSQL con DictCursor, accedemos por alias (UpperCase por el wrapper si aplica)
            # El wrapper DatabaseManager.UpperCaseConnectionWrapper asegura llaves en Mayúsculas
            conteos["Propietario"] = row.get("TOTAL_PROPIETARIOS", 0)
            conteos["Arrendatario"] = row.get("TOTAL_ARRENDATARIOS", 0)
            conteos["Codeudor"] = row.get("TOTAL_CODEUDORES", 0)
            conteos["Asesor"] = row.get("TOTAL_ASESORES", 0)
            conteos["Proveedor"] = row.get("TOTAL_PROVEEDORES", 0)
                
        return conteos

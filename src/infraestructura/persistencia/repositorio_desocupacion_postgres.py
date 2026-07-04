"""
Repositorio de Persistencia: Desocupaciones
Maneja operaciones CRUD para desocupaciones y tareas asociadas en PostgreSQL.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.desocupacion import Desocupacion, TareaDesocupacion
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioDesocupacionPostgres:
    """Repositorio para gestionar desocupaciones en PostgreSQL."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, desocupacion: Desocupacion, tareas: List[str]) -> Desocupacion:
        """
        Crea una nueva desocupación con sus tareas asociadas.

        Args:
            desocupacion: Entidad desocupación
            tareas: Lista de descripciones de tareas a inicializar

        Returns:
            Desocupacion con ID asignado
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()

            # Insertar desocupación
            query_insert = f"""
                INSERT INTO DESOCUPACIONES (
                    ID_CONTRATO, FECHA_SOLICITUD, FECHA_PROGRAMADA, ESTADO,
                    OBSERVACIONES, CREATED_AT, CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                RETURNING ID_DESOCUPACION
            """
            cursor.execute(
                query_insert,
                (
                    desocupacion.id_contrato,
                    desocupacion.fecha_solicitud,
                    desocupacion.fecha_programada,
                    desocupacion.estado,
                    desocupacion.observaciones,
                    desocupacion.created_at,
                    desocupacion.created_by,
                ),
            )

            row = cursor.fetchone()
            id_desocupacion = row["id_desocupacion"]
            desocupacion.id_desocupacion = id_desocupacion

            # Crear tareas asociadas
            for i, descripcion in enumerate(tareas, 1):
                query_task = f"""
                    INSERT INTO TAREAS_DESOCUPACION (
                        ID_DESOCUPACION, DESCRIPCION, ORDEN, COMPLETADA
                    ) VALUES ({placeholder}, {placeholder}, {placeholder}, 0)
                """
                cursor.execute(query_task, (id_desocupacion, descripcion, i))

            conn.commit()
            return desocupacion

    def listar_todas(self, estado: Optional[str] = None) -> List[Desocupacion]:
        """
        Lista todas las desocupaciones con información enriquecida.

        Args:
            estado: Filtro opcional por estado

        Returns:
            Lista de Desocupacion con info de propiedad e inquilino
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()

            query = """
                SELECT 
                    d.ID_DESOCUPACION, d.ID_CONTRATO, 
                    d.FECHA_SOLICITUD, d.FECHA_PROGRAMADA, d.FECHA_REAL,
                    d.ESTADO, d.OBSERVACIONES,
                    d.CREATED_AT, d.CREATED_BY, d.UPDATED_AT, d.UPDATED_BY,
                    prop.DIRECCION_PROPIEDAD,
                    per.NOMBRE_COMPLETO as INQUILINO
                FROM DESOCUPACIONES d
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON d.ID_CONTRATO = ca.ID_CONTRATO_A
                JOIN PROPIEDADES prop ON ca.ID_PROPIEDAD = prop.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            """

            if estado:
                cursor.execute(
                    f"{query} WHERE d.ESTADO = {placeholder} ORDER BY d.FECHA_PROGRAMADA ASC",
                    (estado,),
                )
            else:
                cursor.execute(f"{query} ORDER BY d.FECHA_PROGRAMADA ASC")

            desocupaciones = []
            for row in cursor.fetchall():
                # Calcular progreso
                progreso = self._calcular_progreso(row["id_desocupacion"])

                d = Desocupacion(
                    id_desocupacion=row["id_desocupacion"],
                    id_contrato=row["id_contrato"],
                    fecha_solicitud=row["fecha_solicitud"],
                    fecha_programada=row["fecha_programada"],
                    fecha_real=row["fecha_real"],
                    estado=row["estado"],
                    observaciones=row["observaciones"],
                    created_at=row["created_at"],
                    created_by=row["created_by"],
                    updated_at=row["updated_at"],
                    updated_by=row["updated_by"],
                    direccion_propiedad=row["direccion_propiedad"],
                    nombre_inquilino=row["inquilino"],
                    progreso_porcentaje=progreso,
                )
                desocupaciones.append(d)

            return desocupaciones

    def listar_todas_paginado(
        self, page: int = 1, page_size: int = 25, estado: Optional[str] = None
    ) -> tuple[List[Desocupacion], int]:
        """
        Lista desocupaciones con paginación.

        Args:
            page: Número de página (1-indexed)
            page_size: Cantidad de registros por página
            estado: Filtro opcional por estado

        Returns:
            Tuple of (desocupaciones_list, total_count)
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()

            # Query base
            base_query = """
                SELECT 
                    d.ID_DESOCUPACION, d.ID_CONTRATO, 
                    d.FECHA_SOLICITUD, d.FECHA_PROGRAMADA, d.FECHA_REAL,
                    d.ESTADO, d.OBSERVACIONES,
                    d.CREATED_AT, d.CREATED_BY, d.UPDATED_AT, d.UPDATED_BY,
                    prop.DIRECCION_PROPIEDAD,
                    per.NOMBRE_COMPLETO as INQUILINO
                FROM DESOCUPACIONES d
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON d.ID_CONTRATO = ca.ID_CONTRATO_A
                JOIN PROPIEDADES prop ON ca.ID_PROPIEDAD = prop.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            """

            count_query = """
                SELECT COUNT(*) as TOTAL
                FROM DESOCUPACIONES d
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON d.ID_CONTRATO = ca.ID_CONTRATO_A
            """

            # WHERE clause
            where_clause = ""
            params = []
            if estado:
                where_clause = f" WHERE d.ESTADO = {placeholder}"
                params.append(estado)

            # Get total count
            cursor.execute(f"{count_query}{where_clause}", params)
            row_count = cursor.fetchone()
            total = row_count["total"] if row_count else 0

            # Get paginated data
            offset = (page - 1) * page_size
            query = f"{base_query}{where_clause} ORDER BY d.FECHA_PROGRAMADA ASC LIMIT {placeholder} OFFSET {placeholder}"
            cursor.execute(query, params + [page_size, offset])

            desocupaciones = []
            for row in cursor.fetchall():
                # Calcular progreso
                progreso = self._calcular_progreso(row["id_desocupacion"])

                d = Desocupacion(
                    id_desocupacion=row["id_desocupacion"],
                    id_contrato=row["id_contrato"],
                    fecha_solicitud=row["fecha_solicitud"],
                    fecha_programada=row["fecha_programada"],
                    fecha_real=row["fecha_real"],
                    estado=row["estado"],
                    observaciones=row["observaciones"],
                    created_at=row["created_at"],
                    created_by=row["created_by"],
                    updated_at=row["updated_at"],
                    updated_by=row["updated_by"],
                    direccion_propiedad=row["direccion_propiedad"],
                    nombre_inquilino=row["inquilino"],
                    progreso_porcentaje=progreso,
                )
                desocupaciones.append(d)

            return desocupaciones, total

    def obtener_por_id(self, id_desocupacion: int) -> Optional[Desocupacion]:
        """Obtiene una desocupación por su ID."""
        desocupaciones = self.listar_todas()
        for d in desocupaciones:
            if d.id_desocupacion == id_desocupacion:
                return d
        return None

    def obtener_tareas(self, id_desocupacion: int) -> List[TareaDesocupacion]:
        """Obtiene todas las tareas de una desocupación."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            query = f"""
                SELECT ID_TAREA, ID_DESOCUPACION, DESCRIPCION, ORDEN,
                       COMPLETADA, FECHA_COMPLETADA, RESPONSABLE, OBSERVACIONES
                FROM TAREAS_DESOCUPACION
                WHERE ID_DESOCUPACION = {placeholder}
                ORDER BY ORDEN ASC
            """
            cursor.execute(query, (id_desocupacion,))

            tareas = []
            for row in cursor.fetchall():
                t = TareaDesocupacion(
                    id_tarea=row["id_tarea"],
                    id_desocupacion=row["id_desocupacion"],
                    descripcion=row["descripcion"],
                    orden=row["orden"],
                    completada=bool(row["completada"]),
                    fecha_completada=row["fecha_completada"],
                    responsable=row["responsable"],
                    observaciones=row["observaciones"],
                )
                tareas.append(t)

            return tareas

    def completar_tarea(
        self, id_tarea: int, usuario: str, observaciones: Optional[str] = None
    ):
        """Marca una tarea como completada."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            query = f"""
                UPDATE TAREAS_DESOCUPACION
                SET COMPLETADA = 1,
                    FECHA_COMPLETADA = {placeholder},
                    RESPONSABLE = {placeholder},
                    OBSERVACIONES = {placeholder}
                WHERE ID_TAREA = {placeholder}
            """
            cursor.execute(
                query, (datetime.now().isoformat(), usuario, observaciones, id_tarea)
            )
            conn.commit()

    def actualizar_estado(
        self,
        id_desocupacion: int,
        nuevo_estado: str,
        usuario: str,
        fecha_real: Optional[str] = None,
    ):
        """Actualiza el estado de una desocupación."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            query = f"""
                UPDATE DESOCUPACIONES
                SET ESTADO = {placeholder},
                    FECHA_REAL = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_DESOCUPACION = {placeholder}
            """
            cursor.execute(
                query,
                (
                    nuevo_estado,
                    fecha_real,
                    datetime.now().isoformat(),
                    usuario,
                    id_desocupacion,
                ),
            )
            conn.commit()

    def _calcular_progreso(self, id_desocupacion: int) -> int:
        """Calcula el porcentaje de tareas completadas."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            query = f"""
                SELECT 
                    COUNT(*) as TOTAL,
                    SUM(CASE WHEN COMPLETADA = 1 THEN 1 ELSE 0 END) as COMPLETADAS
                FROM TAREAS_DESOCUPACION
                WHERE ID_DESOCUPACION = {placeholder}
            """
            cursor.execute(query, (id_desocupacion,))

            row = cursor.fetchone()
            total = row["total"]
            completadas = row["completadas"]

            if total == 0:
                return 0

            if completadas is None:
                completadas = 0

            return int((completadas / total) * 100)

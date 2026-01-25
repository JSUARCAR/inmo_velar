"""
Repositorio de Persistencia: Desocupaciones
Maneja operaciones CRUD para desocupaciones y tareas asociadas en SQLite.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.desocupacion import Desocupacion, TareaDesocupacion
from src.infraestructura.persistencia.database import DatabaseManager

# Tareas predefinidas del checklist
TAREAS_PREDEFINIDAS = [
    "Inspección de la propiedad",
    "Verificación de servicios públicos cancelados",
    "Revisión de inventario de muebles/electrodomésticos",
    "Evaluación de daños y reparaciones necesarias",
    "Cálculo de descuentos/devoluciones del depósito",
    "Entrega de llaves",
    "Firma de acta de entrega",
    "Liquidación final de cuentas",
]


class RepositorioDesocupacionSQLite:
    """Repositorio para gestionar desocupaciones en SQLite."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._ensure_tables()

    def _ensure_tables(self):
        if self.db_manager.use_postgresql:
            return
        """Crea las tablas si no existen."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            self.db_manager.get_placeholder()

            # Tabla DESOCUPACIONES
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS DESOCUPACIONES (
                    ID_DESOCUPACION INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_CONTRATO INTEGER NOT NULL,
                    FECHA_SOLICITUD TEXT NOT NULL,
                    FECHA_PROGRAMADA TEXT NOT NULL,
                    FECHA_REAL TEXT,
                    ESTADO TEXT DEFAULT 'En Proceso' CHECK(ESTADO IN ('En Proceso', 'Completada', 'Cancelada')),
                    OBSERVACIONES TEXT,
                    CREATED_AT TEXT NOT NULL,
                    CREATED_BY TEXT,
                    UPDATED_AT TEXT,
                    UPDATED_BY TEXT,
                    FOREIGN KEY(ID_CONTRATO) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A)
                )
            """
            )

            # Tabla TAREAS_DESOCUPACION
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS TAREAS_DESOCUPACION (
                    ID_TAREA INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_DESOCUPACION INTEGER NOT NULL,
                    DESCRIPCION TEXT NOT NULL,
                    ORDEN INTEGER NOT NULL,
                    COMPLETADA INTEGER DEFAULT 0,
                    FECHA_COMPLETADA TEXT,
                    RESPONSABLE TEXT,
                    OBSERVACIONES TEXT,
                    FOREIGN KEY(ID_DESOCUPACION) REFERENCES DESOCUPACIONES(ID_DESOCUPACION)
                )
            """
            )

            conn.commit()

    def crear(self, desocupacion: Desocupacion) -> Desocupacion:
        """
        Crea una nueva desocupación con sus tareas predefinidas.

        Returns:
            Desocupacion con ID asignado
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db_manager.get_placeholder()

            # Insertar desocupación
            query_insert = f"""
                INSERT INTO DESOCUPACIONES (
                    ID_CONTRATO, FECHA_SOLICITUD, FECHA_PROGRAMADA, ESTADO,
                    OBSERVACIONES, CREATED_AT, CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
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

            id_desocupacion = self.db_manager.get_last_insert_id(
                cursor, "DESOCUPACIONES", "ID_DESOCUPACION"
            )
            desocupacion.id_desocupacion = id_desocupacion

            # Crear tareas predefinidas
            for i, descripcion in enumerate(TAREAS_PREDEFINIDAS, 1):
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
            cursor = conn.cursor()
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
                progreso = self._calcular_progreso(row["ID_DESOCUPACION"])

                d = Desocupacion(
                    id_desocupacion=row["ID_DESOCUPACION"],
                    id_contrato=row["ID_CONTRATO"],
                    fecha_solicitud=row["FECHA_SOLICITUD"],
                    fecha_programada=row["FECHA_PROGRAMADA"],
                    fecha_real=row["FECHA_REAL"],
                    estado=row["ESTADO"],
                    observaciones=row["OBSERVACIONES"],
                    created_at=row["CREATED_AT"],
                    created_by=row["CREATED_BY"],
                    updated_at=row["UPDATED_AT"],
                    updated_by=row["UPDATED_BY"],
                    direccion_propiedad=row["DIRECCION_PROPIEDAD"],
                    nombre_inquilino=row["INQUILINO"],
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
            cursor = conn.cursor()
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
            total = row_count["TOTAL"] if row_count else 0

            # Get paginated data
            offset = (page - 1) * page_size
            query = f"{base_query}{where_clause} ORDER BY d.FECHA_PROGRAMADA ASC LIMIT {placeholder} OFFSET {placeholder}"
            cursor.execute(query, params + [page_size, offset])

            desocupaciones = []
            for row in cursor.fetchall():
                # Calcular progreso
                progreso = self._calcular_progreso(row["ID_DESOCUPACION"])

                d = Desocupacion(
                    id_desocupacion=row["ID_DESOCUPACION"],
                    id_contrato=row["ID_CONTRATO"],
                    fecha_solicitud=row["FECHA_SOLICITUD"],
                    fecha_programada=row["FECHA_PROGRAMADA"],
                    fecha_real=row["FECHA_REAL"],
                    estado=row["ESTADO"],
                    observaciones=row["OBSERVACIONES"],
                    created_at=row["CREATED_AT"],
                    created_by=row["CREATED_BY"],
                    updated_at=row["UPDATED_AT"],
                    updated_by=row["UPDATED_BY"],
                    direccion_propiedad=row["DIRECCION_PROPIEDAD"],
                    nombre_inquilino=row["INQUILINO"],
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
            cursor = conn.cursor()
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
                    id_tarea=row["ID_TAREA"],
                    id_desocupacion=row["ID_DESOCUPACION"],
                    descripcion=row["DESCRIPCION"],
                    orden=row["ORDEN"],
                    completada=bool(row["COMPLETADA"]),
                    fecha_completada=row["FECHA_COMPLETADA"],
                    responsable=row["RESPONSABLE"],
                    observaciones=row["OBSERVACIONES"],
                )
                tareas.append(t)

            return tareas

    def completar_tarea(self, id_tarea: int, usuario: str, observaciones: Optional[str] = None):
        """Marca una tarea como completada."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db_manager.get_placeholder()
            query = f"""
                UPDATE TAREAS_DESOCUPACION
                SET COMPLETADA = 1,
                    FECHA_COMPLETADA = {placeholder},
                    RESPONSABLE = {placeholder},
                    OBSERVACIONES = {placeholder}
                WHERE ID_TAREA = {placeholder}
            """
            cursor.execute(query, (datetime.now().isoformat(), usuario, observaciones, id_tarea))
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
            cursor = conn.cursor()
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
                (nuevo_estado, fecha_real, datetime.now().isoformat(), usuario, id_desocupacion),
            )
            conn.commit()

    def _calcular_progreso(self, id_desocupacion: int) -> int:
        """Calcula el porcentaje de tareas completadas."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
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
            total = row["TOTAL"]
            completadas = row["COMPLETADAS"]

            if total == 0:
                return 0

            if completadas is None:
                completadas = 0

            return int((completadas / total) * 100)

import sqlite3
from typing import List, Optional

from src.dominio.entidades.cotizacion import Cotizacion
from src.dominio.entidades.historial_incidente import HistorialIncidente
from src.dominio.entidades.incidente import Incidente
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioIncidentesSQLite(RepositorioIncidentes):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _mapear_incidente(self, row: sqlite3.Row) -> Incidente:
        if not row:
            return None
        return Incidente(
            id_incidente=row["ID_INCIDENTE"],
            id_propiedad=row["ID_PROPIEDAD"],
            id_contrato_m=row["ID_CONTRATO_M"],
            descripcion_incidente=row["DESCRIPCION_INCIDENTE"],
            costo_incidente=row["COSTO_INCIDENTE"],
            fecha_incidente=row["FECHA_INCIDENTE"],
            prioridad=row["PRIORIDAD"],
            origen_reporte=row["ORIGEN_REPORTE"],
            responsable_pago=row["RESPONSABLE_PAGO"],
            id_proveedor_asignado=row["ID_PROVEEDOR_ASIGNADO"],
            id_cotizacion_aprobada=row["ID_COTIZACION_APROBADA"],
            quien_arregla=row["QUIEN_ARREGLA"],
            aprobado_por=row["APROBADO_POR"],
            fecha_arreglo=row["FECHA_ARREGLO"],
            estado=row["ESTADO"],
            dias_sin_resolver=row["DIAS_SIN_RESOLVER"],
            motivo_cancelacion=row["MOTIVO_CANCELACION"],
            created_at=row["CREATED_AT"],
            created_by=row["CREATED_BY"],
            updated_at=row["UPDATED_AT"],
            updated_by=row["UPDATED_BY"],
        )

    def _mapear_cotizacion(self, row: sqlite3.Row) -> Cotizacion:
        if not row:
            return None
        return Cotizacion(
            id_cotizacion=row["ID_COTIZACION"],
            id_incidente=row["ID_INCIDENTE"],
            id_proveedor=row["ID_PROVEEDOR"],
            valor_materiales=row["VALOR_MATERIALES"],
            valor_mano_obra=row["VALOR_MANO_OBRA"],
            valor_total=row["VALOR_TOTAL"],
            descripcion_trabajo=row["DESCRIPCION_TRABAJO"],
            dias_estimados=row["DIAS_ESTIMADOS"],
            fecha_cotizacion=row["FECHA_COTIZACION"],
            estado_cotizacion=row["ESTADO_COTIZACION"],
            created_at=row["CREATED_AT"],
            created_by=row["CREATED_BY"],
        )

    def guardar(self, incidente: Incidente) -> int:
        placeholder = self.db.get_placeholder()
        query = f"""
        INSERT INTO INCIDENTES (
            ID_PROPIEDAD, ID_CONTRATO_M, DESCRIPCION_INCIDENTE, COSTO_INCIDENTE,
            FECHA_INCIDENTE, PRIORIDAD, ORIGEN_REPORTE, RESPONSABLE_PAGO,
            ID_PROVEEDOR_ASIGNADO, ID_COTIZACION_APROBADA, QUIEN_ARREGLA, APROBADO_POR,
            FECHA_ARREGLO, ESTADO, CREATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        params = (
            incidente.id_propiedad,
            incidente.id_contrato_m,
            incidente.descripcion_incidente,
            incidente.costo_incidente,
            incidente.fecha_incidente,
            incidente.prioridad,
            incidente.origen_reporte,
            incidente.responsable_pago,
            incidente.id_proveedor_asignado,
            incidente.id_cotizacion_aprobada,
            incidente.quien_arregla,
            incidente.aprobado_por,
            incidente.fecha_arreglo,
            incidente.estado,
            incidente.created_by,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return self.db.get_last_insert_id(cursor, "INCIDENTES", "ID_INCIDENTE")

    def actualizar(self, incidente: Incidente) -> None:
        placeholder = self.db.get_placeholder()
        query = f"""
        UPDATE INCIDENTES
        SET DESCRIPCION_INCIDENTE={placeholder}, COSTO_INCIDENTE={placeholder}, FECHA_INCIDENTE={placeholder}, PRIORIDAD={placeholder},
            ORIGEN_REPORTE={placeholder}, RESPONSABLE_PAGO={placeholder}, ID_PROVEEDOR_ASIGNADO={placeholder},
            ID_COTIZACION_APROBADA={placeholder}, QUIEN_ARREGLA={placeholder}, APROBADO_POR={placeholder},
            FECHA_ARREGLO={placeholder}, ESTADO={placeholder}, MOTIVO_CANCELACION={placeholder}, UPDATED_AT={placeholder}, UPDATED_BY={placeholder}
        WHERE ID_INCIDENTE={placeholder}
        """
        params = (
            incidente.descripcion_incidente,
            incidente.costo_incidente,
            incidente.fecha_incidente,
            incidente.prioridad,
            incidente.origen_reporte,
            incidente.responsable_pago,
            incidente.id_proveedor_asignado,
            incidente.id_cotizacion_aprobada,
            incidente.quien_arregla,
            incidente.aprobado_por,
            incidente.fecha_arreglo,
            incidente.estado,
            incidente.motivo_cancelacion,
            incidente.updated_at,
            incidente.updated_by,
            incidente.id_incidente,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def obtener_por_id(self, id_incidente: int) -> Optional[Incidente]:
        placeholder = self.db.get_placeholder()
        query = f"SELECT * FROM INCIDENTES WHERE ID_INCIDENTE = {placeholder}"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        row = cursor.fetchone()
        return self._mapear_incidente(row) if row else None

    def listar(
        self, id_propiedad: Optional[int] = None, estado: Optional[str] = None
    ) -> List[Incidente]:
        placeholder = self.db.get_placeholder()
        query = "SELECT * FROM INCIDENTES WHERE 1=1"
        params = []
        if id_propiedad:
            query += f" AND ID_PROPIEDAD = {placeholder}"
            params.append(id_propiedad)
        if estado:
            query += f" AND ESTADO = {placeholder}"
            params.append(estado)
        query += " ORDER BY FECHA_INCIDENTE DESC"

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, tuple(params))
        return [self._mapear_incidente(row) for row in cursor.fetchall()]

    def eliminar(self, id_incidente: int) -> None:
        placeholder = self.db.get_placeholder()
        query = f"UPDATE INCIDENTES SET ESTADO = 'Cancelado' WHERE ID_INCIDENTE = {placeholder}"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_incidente,))
            conn.commit()

    # Cotizaciones
    def guardar_cotizacion(self, cotizacion: Cotizacion) -> int:
        pass  # print("\n" + "="*80) [OpSec Removed]
        pass  # print("DEBUG REPOSITORIO: guardar_cotizacion INICIADO") [OpSec Removed]
        # ... (skipping generic types print for brevity, keeping SQL fix)

        placeholder = self.db.get_placeholder()
        query = f"""
        INSERT INTO COTIZACIONES (
            ID_INCIDENTE, ID_PROVEEDOR, VALOR_MATERIALES, VALOR_MANO_OBRA, VALOR_TOTAL,
            DESCRIPCION_TRABAJO, DIAS_ESTIMADOS, FECHA_COTIZACION, ESTADO_COTIZACION, CREATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        params = (
            cotizacion.id_incidente,
            cotizacion.id_proveedor,
            cotizacion.valor_materiales,
            cotizacion.valor_mano_obra,
            cotizacion.valor_total,
            cotizacion.descripcion_trabajo,
            cotizacion.dias_estimados,
            cotizacion.fecha_cotizacion,
            cotizacion.estado_cotizacion,
            cotizacion.created_by,
        )

        try:
            with self.db.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except Exception:
            import traceback

            traceback.print_exc()
            raise

    def obtener_cotizaciones(self, id_incidente: int) -> List[Cotizacion]:
        placeholder = self.db.get_placeholder()
        query = f"SELECT * FROM COTIZACIONES WHERE ID_INCIDENTE = {placeholder}"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        return [self._mapear_cotizacion(row) for row in cursor.fetchall()]

    def actualizar_cotizacion(self, cotizacion: Cotizacion) -> None:
        placeholder = self.db.get_placeholder()
        query = f"""
        UPDATE COTIZACIONES
        SET ESTADO_COTIZACION = {placeholder}
        WHERE ID_COTIZACION = {placeholder}
        """
        params = (cotizacion.estado_cotizacion, cotizacion.id_cotizacion)
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    # ==================== HISTORIAL DE INCIDENTES ====================

    def crear_tabla_historial(self) -> None:
        """Crea la tabla de historial si no existe."""
        query = """
        CREATE TABLE IF NOT EXISTS HISTORIAL_INCIDENTES (
            ID_HISTORIAL SERIAL PRIMARY KEY,
            ID_INCIDENTE INTEGER NOT NULL,
            ESTADO_ANTERIOR TEXT,
            ESTADO_NUEVO TEXT NOT NULL,
            FECHA_CAMBIO TEXT DEFAULT CURRENT_TIMESTAMP,
            USUARIO TEXT NOT NULL,
            COMENTARIO TEXT,
            TIPO_ACCION TEXT DEFAULT 'CAMBIO_ESTADO',
            DATOS_ADICIONALES TEXT,
            CREATED_AT TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE)
        )
        """
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def _mapear_historial(self, row: sqlite3.Row) -> HistorialIncidente:
        """Mapea una fila de BD a entidad HistorialIncidente."""
        if not row:
            return None
        return HistorialIncidente(
            id_historial=row["ID_HISTORIAL"],
            id_incidente=row["ID_INCIDENTE"],
            estado_anterior=row["ESTADO_ANTERIOR"],
            estado_nuevo=row["ESTADO_NUEVO"],
            fecha_cambio=row["FECHA_CAMBIO"],
            usuario=row["USUARIO"],
            comentario=row["COMENTARIO"],
            tipo_accion=row["TIPO_ACCION"],
            datos_adicionales=row["DATOS_ADICIONALES"],
            created_at=row["CREATED_AT"],
        )

    def guardar_historial(self, historial: HistorialIncidente) -> int:
        """Guarda un registro de historial de incidente."""
        # Se asume que la tabla existe (migración ejecutada)

        placeholder = self.db.get_placeholder()
        query = f"""
        INSERT INTO HISTORIAL_INCIDENTES (
            ID_INCIDENTE, ESTADO_ANTERIOR, ESTADO_NUEVO, USUARIO,
            COMENTARIO, TIPO_ACCION, DATOS_ADICIONALES
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        params = (
            historial.id_incidente,
            historial.estado_anterior,
            historial.estado_nuevo,
            historial.usuario,
            historial.comentario,
            historial.tipo_accion,
            historial.datos_adicionales,
        )
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def obtener_historial(self, id_incidente: int) -> List[HistorialIncidente]:
        """Obtiene el historial completo de un incidente ordenado por fecha."""

        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT * FROM HISTORIAL_INCIDENTES 
        WHERE ID_INCIDENTE = {placeholder} 
        ORDER BY FECHA_CAMBIO DESC
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        return [self._mapear_historial(row) for row in cursor.fetchall()]

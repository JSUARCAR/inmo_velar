import json
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.cotizacion import Cotizacion
from src.dominio.entidades.historial_incidente import HistorialIncidente
from src.dominio.entidades.incidente import Incidente
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioIncidentesPostgres(RepositorioIncidentes):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _mapear_incidente(self, row: dict) -> Optional[Incidente]:
        if not row:
            return None
            
        # Transform datetime objects back to datetime if necessary 
        # (psycopg2 returns datetime natively, but just to be sure)
        return Incidente(
            id_incidente=row.get("ID_INCIDENTE"),
            id_propiedad=row.get("ID_PROPIEDAD", 0),
            id_contrato_m=row.get("ID_CONTRATO_M"),
            descripcion_incidente=row.get("DESCRIPCION_INCIDENTE", ""),
            costo_incidente=row.get("COSTO_INCIDENTE", 0),
            fecha_incidente=row.get("FECHA_INCIDENTE", datetime.now()),
            prioridad=row.get("PRIORIDAD", "Media"),
            origen_reporte=row.get("ORIGEN_REPORTE", "Inquilino"),
            responsable_pago=row.get("RESPONSABLE_PAGO"),
            id_proveedor_asignado=row.get("ID_PROVEEDOR_ASIGNADO"),
            id_cotizacion_aprobada=row.get("ID_COTIZACION_APROBADA"),
            quien_arregla=row.get("QUIEN_ARREGLA"),
            aprobado_por=row.get("APROBADO_POR"),
            fecha_arreglo=row.get("FECHA_ARREGLO"),
            estado=row.get("ESTADO", "Reportado"),
            dias_sin_resolver=row.get("DIAS_SIN_RESOLVER", 0),
            motivo_cancelacion=row.get("MOTIVO_CANCELACION"),
            created_at=row.get("CREATED_AT", datetime.now()),
            created_by=row.get("CREATED_BY"),
            updated_at=row.get("UPDATED_AT", datetime.now()),
            updated_by=row.get("UPDATED_BY"),
        )

    def _mapear_cotizacion(self, row: dict) -> Optional[Cotizacion]:
        if not row:
            return None
        return Cotizacion(
            id_cotizacion=row.get("ID_COTIZACION"),
            id_incidente=row.get("ID_INCIDENTE", 0),
            id_proveedor=row.get("ID_PROVEEDOR", 0),
            valor_materiales=row.get("VALOR_MATERIALES", 0),
            valor_mano_obra=row.get("VALOR_MANO_OBRA", 0),
            valor_total=row.get("VALOR_TOTAL", 0),
            descripcion_trabajo=row.get("DESCRIPCION_TRABAJO"),
            dias_estimados=row.get("DIAS_ESTIMADOS", 1),
            fecha_cotizacion=row.get("FECHA_COTIZACION", datetime.now()),
            estado_cotizacion=row.get("ESTADO_COTIZACION", "Pendiente"),
            created_at=row.get("CREATED_AT", datetime.now()),
            created_by=row.get("CREATED_BY"),
        )

    def guardar(self, incidente: Incidente) -> int:
        query = """
        INSERT INTO INCIDENTES (
            ID_PROPIEDAD, ID_CONTRATO_M, DESCRIPCION_INCIDENTE, COSTO_INCIDENTE,
            FECHA_INCIDENTE, PRIORIDAD, ORIGEN_REPORTE, RESPONSABLE_PAGO,
            ID_PROVEEDOR_ASIGNADO, ID_COTIZACION_APROBADA, QUIEN_ARREGLA, APROBADO_POR,
            FECHA_ARREGLO, ESTADO, CREATED_BY
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ID_INCIDENTE;
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
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def actualizar(self, incidente: Incidente) -> None:
        query = """
        UPDATE INCIDENTES
        SET DESCRIPCION_INCIDENTE=%s, COSTO_INCIDENTE=%s, FECHA_INCIDENTE=%s, PRIORIDAD=%s,
            ORIGEN_REPORTE=%s, RESPONSABLE_PAGO=%s, ID_PROVEEDOR_ASIGNADO=%s,
            ID_COTIZACION_APROBADA=%s, QUIEN_ARREGLA=%s, APROBADO_POR=%s,
            FECHA_ARREGLO=%s, ESTADO=%s, MOTIVO_CANCELACION=%s, UPDATED_AT=%s, UPDATED_BY=%s
        WHERE ID_INCIDENTE=%s
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
        query = "SELECT * FROM INCIDENTES WHERE ID_INCIDENTE = %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        row = cursor.fetchone()
        return self._mapear_incidente(row) if row else None

    def listar(
        self, id_propiedad: Optional[int] = None, estado: Optional[str] = None
    ) -> List[Incidente]:
        query = "SELECT * FROM INCIDENTES WHERE 1=1"
        params = []
        if id_propiedad:
            query += " AND ID_PROPIEDAD = %s"
            params.append(id_propiedad)
        if estado:
            query += " AND ESTADO = %s"
            params.append(estado)
        query += " ORDER BY FECHA_INCIDENTE DESC"

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, tuple(params))
        return [self._mapear_incidente(row) for row in cursor.fetchall()]

    def eliminar(self, id_incidente: int) -> None:
        query = "UPDATE INCIDENTES SET ESTADO = 'Cancelado' WHERE ID_INCIDENTE = %s"
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_incidente,))
            conn.commit()

    # Cotizaciones
    def guardar_cotizacion(self, cotizacion: Cotizacion) -> int:
        query = """
        INSERT INTO COTIZACIONES (
            ID_INCIDENTE, ID_PROVEEDOR, VALOR_MATERIALES, VALOR_MANO_OBRA, VALOR_TOTAL,
            DESCRIPCION_TRABAJO, DIAS_ESTIMADOS, FECHA_COTIZACION, ESTADO_COTIZACION, CREATED_BY
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ID_COTIZACION;
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

        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def obtener_cotizaciones(self, id_incidente: int) -> List[Cotizacion]:
        query = "SELECT * FROM COTIZACIONES WHERE ID_INCIDENTE = %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        return [self._mapear_cotizacion(row) for row in cursor.fetchall()]

    def actualizar_cotizacion(self, cotizacion: Cotizacion) -> None:
        query = """
        UPDATE COTIZACIONES
        SET ESTADO_COTIZACION = %s
        WHERE ID_COTIZACION = %s
        """
        params = (cotizacion.estado_cotizacion, cotizacion.id_cotizacion)
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    # ==================== HISTORIAL DE INCIDENTES ====================

    def _mapear_historial(self, row: dict) -> HistorialIncidente:
        if not row:
            return None
        return HistorialIncidente(
            id_historial=row.get("ID_HISTORIAL"),
            id_incidente=row.get("ID_INCIDENTE", 0),
            estado_anterior=row.get("ESTADO_ANTERIOR"),
            estado_nuevo=row.get("ESTADO_NUEVO", ""),
            fecha_cambio=row.get("FECHA_CAMBIO", datetime.now()),
            usuario=row.get("USUARIO", ""),
            comentario=row.get("COMENTARIO"),
            tipo_accion=row.get("TIPO_ACCION", "CAMBIO_ESTADO"),
            datos_adicionales=row.get("DATOS_ADICIONALES"),
            created_at=row.get("CREATED_AT", datetime.now()),
        )

    def guardar_historial(self, historial: HistorialIncidente) -> int:
        query = """
        INSERT INTO HISTORIAL_INCIDENTES (
            ID_INCIDENTE, ESTADO_ANTERIOR, ESTADO_NUEVO, USUARIO,
            COMENTARIO, TIPO_ACCION, DATOS_ADICIONALES
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING ID_HISTORIAL;
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
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def obtener_historial(self, id_incidente: int) -> List[HistorialIncidente]:
        query = """
        SELECT * FROM HISTORIAL_INCIDENTES 
        WHERE ID_INCIDENTE = %s 
        ORDER BY FECHA_CAMBIO DESC
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        return [self._mapear_historial(row) for row in cursor.fetchall()]

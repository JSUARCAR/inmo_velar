import json
from datetime import datetime
from typing import Any, Dict, List, Optional

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

        cotizaciones_list = []
        if row.get("COTIZACIONES_JSON"):
            try:
                cotizaciones_list = row["COTIZACIONES_JSON"]
            except Exception:
                pass

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
            nombre_proveedor=row.get("NOMBRE_PROVEEDOR"),
            cotizaciones_resumen=cotizaciones_list,
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
            row = cursor.fetchone()
            return list(row.values())[0] if row else None

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

    def obtener_por_id(self, id_incidente: int) -> Optional[Incidente]:
        query = "SELECT * FROM INCIDENTES WHERE ID_INCIDENTE = %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (id_incidente,))
        row = cursor.fetchone()
        return self._mapear_incidente(row) if row else None

    def listar_con_filtros(
        self,
        busqueda: Optional[str] = None,
        id_propiedad: Optional[int] = None,
        prioridad: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_proveedor: Optional[int] = None,
        dias_min: Optional[int] = None,
        estado: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by: str = "FECHA_INCIDENTE",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        query = """
        SELECT I.*, PER_PROV.NOMBRE_COMPLETO AS NOMBRE_PROVEEDOR,
            COALESCE(
                (SELECT JSON_AGG(
                    JSON_BUILD_OBJECT(
                        'id_cotizacion', C.ID_COTIZACION,
                        'id_proveedor', C.ID_PROVEEDOR,
                        'valor_total', C.VALOR_TOTAL,
                        'estado', C.ESTADO_COTIZACION
                    ) ORDER BY C.FECHA_COTIZACION DESC
                ) FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
                ), '[]'::json
            ) AS COTIZACIONES_JSON
        FROM INCIDENTES I
        LEFT JOIN PROVEEDORES PR ON I.ID_PROVEEDOR_ASIGNADO = PR.ID_PROVEEDOR
        LEFT JOIN PERSONAS PER_PROV ON PR.ID_PERSONA = PER_PROV.ID_PERSONA
        WHERE 1=1"""
        params = []

        if busqueda:
            query += " AND (DESCRIPCION_INCIDENTE ILIKE %s OR CAST(ID_INCIDENTE AS TEXT) = %s)"
            params.extend([f"%{busqueda}%", busqueda])

        if id_propiedad:
            query += " AND ID_PROPIEDAD = %s"
            params.append(id_propiedad)

        if prioridad:
            query += " AND PRIORIDAD = %s"
            params.append(prioridad)

        if estado:
            query += " AND ESTADO = %s"
            params.append(estado)

        if id_proveedor:
            query += " AND ID_PROVEEDOR_ASIGNADO = %s"
            params.append(id_proveedor)

        if dias_min is not None:
            query += " AND DIAS_SIN_RESOLVER >= %s"
            params.append(dias_min)

        if fecha_desde:
            query += " AND FECHA_INCIDENTE >= %s"
            params.append(fecha_desde)

        if fecha_hasta:
            query += " AND FECHA_INCIDENTE <= %s"
            params.append(fecha_hasta)

        # Count query independiente — evita romper con el SELECT complejo
        count_query = """
        SELECT COUNT(*) AS total
        FROM INCIDENTES I
        LEFT JOIN PROVEEDORES PR ON I.ID_PROVEEDOR_ASIGNADO = PR.ID_PROVEEDOR
        WHERE 1=1"""

        # Re-aplicar los mismos filtros al count_query
        count_params = []
        if busqueda:
            count_query += " AND (I.DESCRIPCION_INCIDENTE ILIKE %s OR CAST(I.ID_INCIDENTE AS TEXT) = %s)"
            count_params.extend([f"%{busqueda}%", busqueda])
        if id_propiedad:
            count_query += " AND I.ID_PROPIEDAD = %s"
            count_params.append(id_propiedad)
        if prioridad:
            count_query += " AND I.PRIORIDAD = %s"
            count_params.append(prioridad)
        if estado:
            count_query += " AND I.ESTADO = %s"
            count_params.append(estado)
        if id_proveedor:
            count_query += " AND I.ID_PROVEEDOR_ASIGNADO = %s"
            count_params.append(id_proveedor)
        if dias_min is not None:
            count_query += " AND I.DIAS_SIN_RESOLVER >= %s"
            count_params.append(dias_min)
        if fecha_desde:
            count_query += " AND I.FECHA_INCIDENTE >= %s"
            count_params.append(fecha_desde)
        if fecha_hasta:
            count_query += " AND I.FECHA_INCIDENTE <= %s"
            count_params.append(fecha_hasta)

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(count_query, tuple(count_params))
        total_row = cursor.fetchone()

        # Soportar clave en minúscula o mayúscula según comportamiento del entorno
        total = 0
        if total_row:
            total = int(total_row.get("total") or total_row.get("TOTAL") or 0)

        # Whitelist de columnas permitidas para ORDER BY
        SORT_COLUMNS = {
            "ID_INCIDENTE": "I.ID_INCIDENTE",
            "FECHA_INCIDENTE": "I.FECHA_INCIDENTE",
            "PRIORIDAD": "I.PRIORIDAD",
            "ESTADO": "I.ESTADO",
            "COSTO_INCIDENTE": "I.COSTO_INCIDENTE",
            "DIRECCION": "PROP.DIRECCION_PROPIEDAD",
            "NOMBRE_PROVEEDOR": "PER_PROV.NOMBRE_COMPLETO",
        }
        sort_column = SORT_COLUMNS.get(sort_by, "I.FECHA_INCIDENTE")
        sort_order_valid = (
            sort_order.lower() if sort_order.lower() in ("asc", "desc") else "desc"
        )

        query += f" ORDER BY {sort_column} {sort_order_valid}"

        if page is not None and page_size is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

        cursor.execute(query, tuple(params))
        incidentes = [self._mapear_incidente(row) for row in cursor.fetchall()]

        return {"items": incidentes, "total": total}

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
            row = cursor.fetchone()
            return list(row.values())[0] if row else None

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
            row = cursor.fetchone()
            return list(row.values())[0] if row else None

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

"""
Repositorio SQLite para Alertas.
===============================
Implementa la persistencia de alertas en SQLite mapeando a la tabla ALERTAS.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-05-10
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.alerta import Alerta
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioAlertaSQLite:
    """
    Repositorio SQLite para la entidad Alerta.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Alerta:
        """Convierte una fila SQL a entidad Alerta."""
        if row is None:
            return None

        # Convertir a dict si es necesario
        row_dict = dict(row) if hasattr(row, "keys") else row

        return Alerta(
            id_alertas=row_dict.get("ID_ALERTAS"),
            tipo_alerta=row_dict.get("TIPO_ALERTA"),
            descripcion_alerta=row_dict.get("DESCRIPCION_ALERTA"),
            prioridad=row_dict.get("PRIORIDAD", "Media"),
            fecha_generacion_alerta=row_dict.get("FECHA_GENERACION_ALERTA"),
            fecha_vencimiento_alerta=row_dict.get("FECHA_VENCIMIENTO_ALERTA"),
            estado_alerta=row_dict.get("ESTADO_ALERTA", "Pendiente"),
            id_entidad_relacionada=row_dict.get("ID_ENTIDAD_RELACIONADA"),
            tipo_entidad=row_dict.get("TIPO_ENTIDAD"),
            usuario_asignado=row_dict.get("USUARIO_ASIGNADO"),
            accion_tomada=row_dict.get("ACCION_TOMADA"),
            fecha_accion=row_dict.get("FECHA_ACCION"),
            plantilla_mensaje=row_dict.get("PLANTILLA_MENSAJE"),
            destinatario_nombre=row_dict.get("DESTINATARIO_NOMBRE"),
            destinatario_telefono=row_dict.get("DESTINATARIO_TELEFONO"),
            destinatario_email=row_dict.get("DESTINATARIO_EMAIL"),
            fecha_resolucion=row_dict.get("FECHA_RESOLUCION"),
            resuelto_automaticamente=bool(row_dict.get("RESUELTO_AUTOMATICAMENTE", 0)),
            created_at=row_dict.get("CREATED_AT"),
            created_by=row_dict.get("CREATED_BY"),
        )

    def obtener_por_id(self, id_alerta: int) -> Optional[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        p = self.db.get_placeholder()
        cursor.execute(f"SELECT * FROM ALERTAS WHERE ID_ALERTAS = {p}", (id_alerta,))
        return self._row_to_entity(cursor.fetchone())

    def obtener_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = "SELECT * FROM ALERTAS"
        conditions = []
        params = []
        
        if estado:
            conditions.append(f"ESTADO_ALERTA = {p}")
            params.append(estado)
        if prioridad:
            conditions.append(f"PRIORIDAD = {p}")
            params.append(prioridad)
        if tipo:
            conditions.append(f"TIPO_ALERTA = {p}")
            params.append(tipo)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += f" ORDER BY FECHA_GENERACION_ALERTA DESC LIMIT {p} OFFSET {p}"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def contar_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> int:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = "SELECT COUNT(*) as total FROM ALERTAS"
        conditions = []
        params = []
        
        if estado:
            conditions.append(f"ESTADO_ALERTA = {p}")
            params.append(estado)
        if prioridad:
            conditions.append(f"PRIORIDAD = {p}")
            params.append(prioridad)
        if tipo:
            conditions.append(f"TIPO_ALERTA = {p}")
            params.append(tipo)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            if isinstance(row, dict): return row.get("total", 0) or row.get("TOTAL", 0)
            return row[0]
        return 0

    def obtener_por_entidad_y_tipo(
        self, 
        id_entidad: Optional[int], 
        tipo_entidad: str, 
        tipo_alerta: str,
        solo_pendientes: bool = True
    ) -> Optional[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = f"SELECT * FROM ALERTAS WHERE TIPO_ENTIDAD = {p} AND TIPO_ALERTA = {p}"
        params = [tipo_entidad, tipo_alerta]

        if id_entidad is None:
            query += " AND ID_ENTIDAD_RELACIONADA IS NULL"
        else:
            query += f" AND ID_ENTIDAD_RELACIONADA = {p}"
            params.append(id_entidad)
        
        if solo_pendientes:
            query += " AND ESTADO_ALERTA IN ('Pendiente', 'En Proceso')"
        else:
            query += " ORDER BY FECHA_GENERACION_ALERTA DESC"
            
        cursor.execute(query, params)
        return self._row_to_entity(cursor.fetchone())

    def guardar(self, alerta: Alerta, usuario_sistema: str) -> Alerta:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        sql = f"""
            INSERT INTO ALERTAS (
                TIPO_ALERTA, DESCRIPCION_ALERTA, PRIORIDAD, 
                FECHA_GENERACION_ALERTA, FECHA_VENCIMIENTO_ALERTA, ESTADO_ALERTA,
                ID_ENTIDAD_RELACIONADA, TIPO_ENTIDAD, DESTINATARIO_NOMBRE,
                DESTINATARIO_TELEFONO, DESTINATARIO_EMAIL, CREATED_BY
            ) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """
        params = (
            alerta.tipo_alerta,
            alerta.descripcion_alerta,
            alerta.prioridad,
            alerta.fecha_generacion_alerta or datetime.now().isoformat(),
            alerta.fecha_vencimiento_alerta,
            alerta.estado_alerta,
            alerta.id_entidad_relacionada,
            alerta.tipo_entidad,
            alerta.destinatario_nombre,
            alerta.destinatario_telefono,
            alerta.destinatario_email,
            usuario_sistema
        )
        
        cursor.execute(sql, params)
        if hasattr(cursor, 'lastrowid'):
            alerta.id_alertas = cursor.lastrowid
        conn.commit()
        return alerta

    def actualizar(self, alerta: Alerta, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        sql = f"""
            UPDATE ALERTAS SET
                ESTADO_ALERTA = {p}, ACCION_TOMADA = {p}, FECHA_ACCION = {p},
                USUARIO_ASIGNADO = {p}, FECHA_RESOLUCION = {p}, 
                RESUELTO_AUTOMATICAMENTE = {p}
            WHERE ID_ALERTAS = {p}
        """
        params = (
            alerta.estado_alerta,
            alerta.accion_tomada,
            alerta.fecha_accion,
            alerta.usuario_asignado,
            alerta.fecha_resolucion,
            1 if alerta.resuelto_automaticamente else 0,
            alerta.id_alertas
        )
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0

    def marcar_resuelta(
        self, 
        id_alerta: int, 
        usuario_sistema: str, 
        accion: str,
        automatica: bool = False
    ) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        ahora = datetime.now().isoformat()
        sql = f"""
            UPDATE ALERTAS SET
                ESTADO_ALERTA = 'Resuelta',
                ACCION_TOMADA = {p},
                FECHA_ACCION = {p},
                FECHA_RESOLUCION = {p},
                RESUELTO_AUTOMATICAMENTE = {p}
            WHERE ID_ALERTAS = {p}
        """
        params = (accion, ahora, ahora, 1 if automatica else 0, id_alerta)
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0

    def eliminar(self, id_alerta: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        cursor.execute(f"DELETE FROM ALERTAS WHERE ID_ALERTAS = {p}", (id_alerta,))
        conn.commit()
        return cursor.rowcount > 0

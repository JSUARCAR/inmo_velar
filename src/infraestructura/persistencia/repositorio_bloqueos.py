"""
Repositorio para Bloqueos de Edición (Pessimistic Locking).
Implementa bloqueo pesimista para prevenir ediciones concurrentes.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioBloqueos:
    """
    Repositorio para gestionar bloqueos de edición (pessimistic locking).
    
    Este repositorio implementa bloqueo pesimista a nivel de aplicación
    para prevenir ediciones concurrentes en la definición de planes de pago.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._lock_timeout_minutes = 5  # Tiempo de expiración del bloqueo

    def _ensure_table_exists(self):
        """Asegura que la tabla BLOQUEOS_EDICION exista."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BLOQUEOS_EDICION (
                ID_BLOQUEO INTEGER PRIMARY KEY AUTOINCREMENT,
                TABLA TEXT NOT NULL,
                ID_REGISTRO INTEGER NOT NULL,
                USUARIO TEXT NOT NULL,
                SESION_ID TEXT NOT NULL,
                FECHA_BLOQUEO TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FECHA_EXPIRACION TEXT NOT NULL,
                UNIQUE(TABLA, ID_REGISTRO)
            )
        """)
        conn.commit()

    def adquirir_bloqueo(self, tabla: str, id_registro: int, usuario: str, 
                         sesion_id: str) -> bool:
        """
        Intenta adquirir un bloqueo de edición.
        
        Args:
            tabla: Nombre de la tabla (ej: 'INCIDENTES')
            id_registro: ID del registro a bloquear
            usuario: Usuario que solicita el bloqueo
            sesion_id: ID de la sesión del usuario
            
        Returns:
            True si se adquirió el bloqueo, False si ya está bloqueado
        """
        self._ensure_table_exists()
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        try:
            # Primero, limpiar bloqueos expirados
            self._limpiar_bloqueos_expirados(tabla)
            
            # Verificar si ya existe un bloqueo activo
            cursor.execute("""
                SELECT ID_BLOQUEO, USUARIO, FECHA_EXPIRACION 
                FROM BLOQUEOS_EDICION 
                WHERE TABLA = %s AND ID_REGISTRO = %s
            """, (tabla, id_registro))
            
            existing_lock = cursor.fetchone()
            
            if existing_lock:
                # Verificar si el bloqueo ha expirado
                fecha_expiracion = existing_lock.get("FECHA_EXPIRACION")
                if fecha_expiracion:
                    exp_dt = datetime.fromisoformat(fecha_expiracion)
                    if datetime.now() > exp_dt:
                        # Bloqueo expirado, eliminarlo
                        cursor.execute("""
                            DELETE FROM BLOQUEOS_EDICION 
                            WHERE TABLA = %s AND ID_REGISTRO = %s
                        """, (tabla, id_registro))
                        conn.commit()
                    else:
                        # Bloqueo activo
                        usuario_bloqueador = existing_lock.get("USUARIO")
                        if usuario_bloqueador != usuario:
                            logger.warning(
                                f"Registro {id_registro} en {tabla} bloqueado por {usuario_bloqueador}"
                            )
                            return False
            
            # Calcular fecha de expiración
            fecha_expiracion = datetime.now() + timedelta(minutes=self._lock_timeout_minutes)
            
            # Intentar insertar o actualizar el bloqueo
            cursor.execute("""
                INSERT INTO BLOQUEOS_EDICION 
                (TABLA, ID_REGISTRO, USUARIO, SESION_ID, FECHA_EXPIRACION)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(TABLA, ID_REGISTRO) 
                DO UPDATE SET 
                    USUARIO = EXCLUDED.USUARIO,
                    SESION_ID = EXCLUDED.SESION_ID,
                    FECHA_BLOQUEO = datetime('now', 'localtime'),
                    FECHA_EXPIRACION = EXCLUDED.FECHA_EXPIRACION
            """, (tabla, id_registro, usuario, sesion_id, fecha_expiracion.isoformat()))
            
            conn.commit()
            logger.info(f"Bloqueo adquirido: {tabla}:{id_registro} por {usuario}")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error al adquirir bloqueo: {e}")
            return False

    def liberar_bloqueo(self, tabla: str, id_registro: int, usuario: str) -> bool:
        """
        Libera un bloqueo de edición.
        
        Args:
            tabla: Nombre de la tabla
            id_registro: ID del registro a desbloquear
            usuario: Usuario que libera el bloqueo
            
        Returns:
            True si se liberó el bloqueo
        """
        self._ensure_table_exists()
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        try:
            cursor.execute("""
                DELETE FROM BLOQUEOS_EDICION 
                WHERE TABLA = %s AND ID_REGISTRO = %s AND USUARIO = %s
            """, (tabla, id_registro, usuario))
            
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Bloqueo liberado: {tabla}:{id_registro} por {usuario}")
            return deleted
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error al liberar bloqueo: {e}")
            return False

    def verificar_bloqueo(self, tabla: str, id_registro: int) -> Optional[dict]:
        """
        Verifica si un registro está bloqueado.
        
        Args:
            tabla: Nombre de la tabla
            id_registro: ID del registro
            
        Returns:
            Información del bloqueo o None si no está bloqueado
        """
        self._ensure_table_exists()
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        # Limpiar bloqueos expirados primero
        self._limpiar_bloqueos_expirados(tabla)
        
        cursor.execute("""
            SELECT USUARIO, SESION_ID, FECHA_BLOQUEO, FECHA_EXPIRACION
            FROM BLOQUEOS_EDICION 
            WHERE TABLA = %s AND ID_REGISTRO = %s
        """, (tabla, id_registro))
        
        lock = cursor.fetchone()
        if lock:
            return dict(lock)
        return None

    def _limpiar_bloqueos_expirados(self, tabla: str):
        """Elimina bloqueos expirados para una tabla específica."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        try:
            cursor.execute("""
                DELETE FROM BLOQUEOS_EDICION 
                WHERE TABLA = %s AND FECHA_EXPIRACION < datetime('now', 'localtime')
            """, (tabla,))
            conn.commit()
        except Exception as e:
            logger.error(f"Error al limpiar bloqueos expirados: {e}")

    def liberar_bloqueos_expirados(self):
        """Elimina todos los bloqueos expirados de todas las tablas."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        
        try:
            cursor.execute("""
                DELETE FROM BLOQUEOS_EDICION 
                WHERE FECHA_EXPIRACION < datetime('now', 'localtime')
            """)
            deleted = cursor.rowcount
            conn.commit()
            if deleted > 0:
                logger.info(f"Se liberaron {deleted} bloqueos expirados")
        except Exception as e:
            logger.error(f"Error al liberar bloqueos expirados: {e}")

"""
Script para ejecutar la migración de la columna ELIMINADA.
Ejecutar una sola vez para agregar la columna a la tabla LIQUIDACIONES.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager


def ejecutar_migracion():
    """Ejecuta la migración para agregar la columna ELIMINADA."""
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        if db_manager.use_postgresql:
            cursor.execute(
                """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'LIQUIDACIONES' AND COLUMN_NAME = 'ELIMINADA'
            """
            )
        else:
            # SQLite
            cursor.execute("PRAGMA table_info(LIQUIDACIONES)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'ELIMINADA' in columns:
                print("La columna ELIMINADA ya existe en la tabla LIQUIDACIONES.")
                return

        result = cursor.fetchone()
        if result:
            print("La columna ELIMINADA ya existe en la tabla LIQUIDACIONES.")
            return

        # Agregar la columna
        print("Agregando columna ELIMINADA a la tabla LIQUIDACIONES...")
        cursor.execute("ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE")
        conn.commit()

        # Crear índice
        print("Creando índice idx_liquidaciones_eliminada...")
        cursor.execute("CREATE INDEX idx_liquidaciones_eliminada ON LIQUIDACIONES(ELIMINADA)")
        conn.commit()

        print("Migración ejecutada exitosamente.")

    except Exception as e:
        print(f"Error al ejecutar migración: {e}")
        conn.rollback()
        raise


if __name__ == "__main__":
    ejecutar_migracion()

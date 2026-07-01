"""
Script para registrar el permiso ELIMINAR para el módulo Liquidaciones.
Ejecutar una sola vez después de la migración de base de datos.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager


def registrar_permiso_eliminar():
    """Registra el permiso ELIMINAR para el módulo Liquidaciones."""
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()

    try:
        # Verificar si ya existe el permiso
        cursor.execute(
            """
            SELECT COUNT(*) as TOTAL
            FROM PERMISOS
            WHERE MODULO = 'Liquidaciones' AND ACCION = 'ELIMINAR'
        """
        )
        result = cursor.fetchone()
        total = result["TOTAL"] if result else 0

        if total > 0:
            print("El permiso ELIMINAR para Liquidaciones ya existe.")
            return

        # Insertar el permiso
        cursor.execute(
            """
            INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
            VALUES ('Liquidaciones', '/liquidaciones', 'ELIMINAR', 'Eliminar liquidaciones', 'Gestión')
        """
        )
        conn.commit()

        print("Permiso ELIMINAR para Liquidaciones registrado exitosamente.")

    except Exception as e:
        print(f"Error al registrar permiso: {e}")
        conn.rollback()
        raise


if __name__ == "__main__":
    registrar_permiso_eliminar()

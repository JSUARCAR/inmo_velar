"""
Script de migración: Agregar columna SEGURO_MONTO a LIQUIDACIONES.
Idempotente - seguro para ejecutar múltiples veces.
"""
import os
import sys

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infraestructura.persistencia.database import db_manager


def migrar() -> None:
    """Agrega la columna SEGURO_MONTO si no existe."""
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()

    columnas_a_agregar = [
        ("SEGURO_MONTO", "INTEGER DEFAULT 0"),
    ]

    for nombre_col, tipo_col in columnas_a_agregar:
        try:
            cursor.execute(
                f"ALTER TABLE LIQUIDACIONES ADD COLUMN {nombre_col} {tipo_col}"
            )
            conn.commit()
            print(f"✅ Columna '{nombre_col}' agregada exitosamente.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"ℹ️  Columna '{nombre_col}' ya existe. Sin cambios.")
            else:
                print(f"❌ Error al agregar '{nombre_col}': {e}")
                conn.rollback()

    cursor.close()
    conn.close()
    print("\n🏁 Migración completada.")


if __name__ == "__main__":
    migrar()

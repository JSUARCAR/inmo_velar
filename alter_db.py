import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from migraciones.database_config import get_database_connection


def apply_migration():
    """Agrega columnas PAGO_PREDIAL y OTROS_EGRESOS a LIQUIDACIONES si no existen."""
    print("Obteniendo conexion a produccion...")
    conn = get_database_connection()
    cursor = conn.cursor()

    columnas = [
        ("PAGO_PREDIAL", "INTEGER DEFAULT 0"),
        ("OTROS_EGRESOS", "INTEGER DEFAULT 0"),
    ]

    for nombre_col, tipo_col in columnas:
        try:
            print(f"Ejecutando ALTER TABLE LIQUIDACIONES ADD COLUMN {nombre_col}...")
            cursor.execute(
                f"ALTER TABLE LIQUIDACIONES ADD COLUMN {nombre_col} {tipo_col};"
            )
            conn.commit()
            print(f"  -> Columna {nombre_col} agregada exitosamente.")
        except Exception as e:
            conn.rollback()
            print(f"  -> {nombre_col} ya existe o error: {e}")

    cursor.close()
    conn.close()
    print("Migracion finalizada.")


if __name__ == "__main__":
    apply_migration()

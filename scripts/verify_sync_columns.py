
import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar desde migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

def verify_columns():
    if DB_MODE != 'postgresql':
        print("Este script requiere PostgreSQL (DB_MODE=postgresql)")
        return

    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("Verificando columnas de CONTRATOS_MANDATOS...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'contratos_mandatos'
            AND column_name IN ('fecha_inicio_contrato_m', 'fecha_fin_contrato_m', 'id_contrato_m');
        """)
        cols_m = [row[0].upper() for row in cursor.fetchall()]
        print(f"Columnas encontradas en CONTRATOS_MANDATOS: {cols_m}")

        print("\nVerificando columnas de CONTRATOS_ARRENDAMIENTOS...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'contratos_arrendamientos'
            AND column_name IN ('fecha_inicio_contrato_a', 'fecha_fin_contrato_a', 'id_contrato_a');
        """)
        cols_a = [row[0].upper() for row in cursor.fetchall()]
        print(f"Columnas encontradas en CONTRATOS_ARRENDAMIENTOS: {cols_a}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_columns()

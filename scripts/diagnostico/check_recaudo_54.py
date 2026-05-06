
import os
import sys

# Agregar el directorio raíz al path para importar migraciones.database_config
sys.path.append(os.getcwd())

from migraciones.database_config import get_database_connection, DB_MODE

def check_recaudo_54():
    print(f"Conectando a la base de datos (Modo: {DB_MODE})...")
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Consultar recaudo 54
        print("Consultando recaudo con ID 54 (id_recaudo)...")
        cursor.execute("SELECT * FROM recaudos WHERE id_recaudo = 54")
        row = cursor.fetchone()
        
        if row:
            colnames = [desc[0] for desc in cursor.description]
            recaudo = dict(zip(colnames, row))
            print("\nRecaudo 54 encontrado:")
            for k, v in recaudo.items():
                print(f"  {k}: {v}")
        else:
            print("\n[ERROR] No se encontró el recaudo con ID 54.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error al consultar el recaudo: {e}")

if __name__ == "__main__":
    check_recaudo_54()

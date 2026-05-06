
import sqlite3
from src.infraestructura.configuracion.settings import obtener_configuracion

config = obtener_configuracion()
db_path = config.database_path

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def inspect_table(name):
    try:
        print(f"\nInspeccionando: {name}")
        cursor.execute(f"PRAGMA table_info({name})")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"- {col[1]}")
            return [col[1] for col in columns]
        else:
            print("No devolvió columnas con PRAGMA. Probando SELECT * LIMIT 1")
            cursor.execute(f"SELECT * FROM {name} LIMIT 1")
            cols = [d[0] for d in cursor.description]
            for c in cols:
                print(f"- {c}")
            return cols
            
    except Exception as e:
        print(f"Error inspeccionando {name}: {e}")
        return []

try:
    # Verificar la que fallaba antes para confirmar
    # inspect_table("VW_ALERTA_MORA_DIARIA") 
    
    # Verificar la otra vista usada
    cols_vencimiento = inspect_table("VW_ALERTA_VENCIMIENTO_CONTRATOS")
    
    # Verificar si tiene la columna usada en el query
    if "DIAS_PARA_VENCER" in cols_vencimiento:
        print("\n✅ VW_ALERTA_VENCIMIENTO_CONTRATOS tiene DIAS_PARA_VENCER")
    else:
         print("\n❌ ALERTA: VW_ALERTA_VENCIMIENTO_CONTRATOS NO tiene DIAS_PARA_VENCER")

except Exception as e:
    print(f"Error global: {e}")

finally:
    conn.close()

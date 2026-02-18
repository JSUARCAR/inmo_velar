import os
import sys
import pandas as pd

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_pandas():
    print("=== Pandas Inspection ===")
    try:
        with db_manager.obtener_conexion() as conn:
            # Check available tables
            print("\n[TABLES]")
            df_tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", conn)
            print(df_tables)
            
            # Check CONTRATOS_ARRENDAMIENTOS
            print("\n[CONTRATOS_ARRENDAMIENTOS]")
            try:
                df_ca = pd.read_sql("SELECT * FROM CONTRATOS_ARRENDAMIENTOS LIMIT 5", conn)
                print(df_ca)
                print(df_ca.columns)
            except Exception as e:
                print(f"Error reading CA: {e}")

            # Check VW
            print("\n[VIEW]")
            try:
                df_view = pd.read_sql("SELECT * FROM VW_ALERTA_VENCIMIENTO_CONTRATOS LIMIT 5", conn)
                print(df_view)
            except Exception as e:
                print(f"Error reading VIEW: {e}")

    except Exception as e:
        print(f"[FATAL] {e}")

if __name__ == "__main__":
    check_pandas()

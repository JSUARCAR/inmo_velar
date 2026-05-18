import sys
import os
sys.path.append(os.getcwd())
from migraciones.database_config import get_database_connection

def verify():
    conn = get_database_connection()
    cur = conn.cursor()
    
    print("Verificando LIQUIDACIONES_CONTRATOS:")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'liquidaciones_contratos' 
          AND column_name IN ('comision_porcentaje_contrato', 'comision_monto_contrato');
    """)
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
        
    print("\nVerificando LIQUIDACIONES_ASESORES:")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'liquidaciones_asesores' 
          AND column_name = 'modo_comision';
    """)
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify()

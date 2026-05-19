
import os
import sys
from datetime import datetime

# Configurar PYTHONPATH
sys.path.append(os.getcwd())

from migraciones.database_config import get_database_connection
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

def corregir_tabla(conn, tabla: str, prefijo: str):
    cursor = conn.cursor()
    print(f"\n>>> CORRIGIENDO {tabla}...")
    
    id_col = f"ID_CONTRATO_{prefijo}"
    inicio_col = f"FECHA_INICIO_CONTRATO_{prefijo}"
    fin_col = f"FECHA_FIN_CONTRATO_{prefijo}"
    duracion_col = f"DURACION_CONTRATO_{prefijo}"
    
    query = f"SELECT {id_col}, {inicio_col}, {fin_col}, {duracion_col} FROM {tabla}"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    corregidos = 0
    errores = 0
    
    for row in rows:
        cid, f_inicio, f_fin, duracion_reg = row
        
        if not f_inicio or not f_fin:
            continue
            
        try:
            s_inicio = str(f_inicio)[:10]
            s_fin = str(f_fin)[:10]
            d_inicio = datetime.strptime(s_inicio, "%Y-%m-%d").date()
            d_fin = datetime.strptime(s_fin, "%Y-%m-%d").date()
            
            if d_fin < d_inicio:
                print(f"ID {cid}: SALTADO (Fechas invertidas: {s_inicio} a {s_fin})")
                errores += 1
                continue
                
            duracion_calc = CalculadoraContratos.calcular_duracion_meses(d_inicio, d_fin)
            
            if duracion_calc != duracion_reg:
                # Actualizar base de datos
                update_query = f"UPDATE {tabla} SET {duracion_col} = %s WHERE {id_col} = %s"
                cursor.execute(update_query, (duracion_calc, cid))
                corregidos += 1
                print(f"ID {cid}: ACTUALIZADO {duracion_reg} -> {duracion_calc} ({s_inicio} a {s_fin})")
                
        except Exception as e:
            print(f"ID {cid}: ERROR procesando: {e}")
            errores += 1
            
    conn.commit()
    cursor.close()
    print(f"FIN {tabla}: {corregidos} corregidos, {errores} pendientes de revisión manual.")

def main():
    try:
        conn = get_database_connection()
        corregir_tabla(conn, "CONTRATOS_MANDATOS", "M")
        corregir_tabla(conn, "CONTRATOS_ARRENDAMIENTOS", "A")
        print("\nSANEAMIENTO COMPLETADO EXITOSAMENTE.")
    except Exception as e:
        print(f"ERROR FATAL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()

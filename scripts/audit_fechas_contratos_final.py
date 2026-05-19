
import os
import sys
from datetime import datetime

# Configurar PYTHONPATH para importar desde src
sys.path.append(os.getcwd())

from migraciones.database_config import get_database_connection, DB_MODE
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

def auditar_tabla(cursor, tabla: str, prefijo: str):
    print(f"\n{'='*20} AUDITANDO {tabla} {'='*20}")
    id_col = f"ID_CONTRATO_{prefijo}"
    inicio_col = f"FECHA_INICIO_CONTRATO_{prefijo}"
    fin_col = f"FECHA_FIN_CONTRATO_{prefijo}"
    duracion_col = f"DURACION_CONTRATO_{prefijo}"
    
    query = f"SELECT {id_col}, {inicio_col}, {fin_col}, {duracion_col} FROM {tabla}"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    total = len(rows)
    inconsistencias = 0
    negativos = 0
    discrepancias = 0
    nulos = 0
    
    for row in rows:
        cid, f_inicio, f_fin, duracion_reg = row
        
        if not f_inicio or not f_fin:
            nulos += 1
            print(f"ID {cid}: Fechas nulas ({f_inicio} a {f_fin})")
            continue
            
        try:
            # Asegurar formato string y limpiar si es datetime de psycopg2
            s_inicio = str(f_inicio)[:10]
            s_fin = str(f_fin)[:10]
            
            # 1. Validar orden
            d_inicio = datetime.strptime(s_inicio, "%Y-%m-%d").date()
            d_fin = datetime.strptime(s_fin, "%Y-%m-%d").date()
            
            if d_fin < d_inicio:
                negativos += 1
                print(f"ID {cid}: CRÍTICO - Fecha Fin ({s_fin}) < Fecha Inicio ({s_inicio})")
                continue
                
            # 2. Validar duración calculada vs registrada
            duracion_calc = CalculadoraContratos.calcular_duracion_meses(d_inicio, d_fin)
            
            if duracion_calc != duracion_reg:
                discrepancias += 1
                print(f"ID {cid}: DISCREPANCIA - Calc: {duracion_calc} vs Reg: {duracion_reg} ({s_inicio} al {s_fin})")
                
        except Exception as e:
            print(f"ID {cid}: Error procesando: {e}")
            inconsistencias += 1

    print(f"\nRESUMEN {tabla}:")
    print(f"  - Total registros: {total}")
    print(f"  - Fechas nulas/error: {nulos + inconsistencias}")
    print(f"  - Fechas invertidas (Fin < Inicio): {negativos}")
    print(f"  - Discrepancias de duración: {discrepancias}")
    print(f"  - OK: {total - (nulos + inconsistencias + negativos + discrepancias)}")

def main():
    if DB_MODE != 'postgresql':
        print(f"Aviso: DB_MODE es {DB_MODE}, se recomienda 'postgresql' para esta auditoría.")
        
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        auditar_tabla(cursor, "CONTRATOS_MANDATOS", "M")
        auditar_tabla(cursor, "CONTRATOS_ARRENDAMIENTOS", "A")
        
    except Exception as e:
        print(f"Error fatal: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()

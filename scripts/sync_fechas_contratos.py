
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar desde migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

# IDs de Contratos de Mandato
GRUPO_1_INICIO_ONLY = [22, 28, 36, 37, 39, 45, 56, 65, 72, 73, 76, 84, 87]
GRUPO_2_INICIO_Y_FIN = [20, 38, 43, 44, 50, 51, 53, 55, 57, 66, 67, 74, 82, 83]

def run_sync():
    if DB_MODE != 'postgresql':
        print("ERROR: Este script requiere PostgreSQL (DB_MODE=postgresql)")
        return

    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # 1. DIAGNÓSTICO PREVIO
        print("--- DIAGNÓSTICO Y RESPALDO LÓGICO ---")
        
        all_ids = GRUPO_1_INICIO_ONLY + GRUPO_2_INICIO_Y_FIN
        
        query_diagnostic = """
            SELECT 
                cm.ID_CONTRATO_M, 
                cm.FECHA_INICIO_CONTRATO_M, 
                cm.FECHA_FIN_CONTRATO_M,
                ca.ID_CONTRATO_A,
                ca.FECHA_INICIO_CONTRATO_A,
                ca.FECHA_FIN_CONTRATO_A
            FROM CONTRATOS_MANDATOS cm
            LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON cm.ID_PROPIEDAD = ca.ID_PROPIEDAD
            WHERE cm.ID_CONTRATO_M = ANY(%s)
        """
        
        cursor.execute(query_diagnostic, (all_ids,))
        rows = cursor.fetchall()
        
        diag_data = {}
        for row in rows:
            id_m = row[0]
            if id_m not in diag_data:
                diag_data[id_m] = []
            diag_data[id_m].append({
                'inicio_m': str(row[1]),
                'fin_m': str(row[2]),
                'id_a': row[3],
                'inicio_a': str(row[4]),
                'fin_a': str(row[5])
            })

        # Validaciones de integridad
        print(f"Total contratos de mandato a procesar: {len(all_ids)}")
        print(f"Contratos encontrados en BD: {len(diag_data)}")
        
        issues = []
        for id_m in all_ids:
            if id_m not in diag_data:
                issues.append(f"Mandato {id_m}: No encontrado en la base de datos.")
                continue
            
            matches = diag_data[id_m]
            if not matches[0]['id_a']:
                issues.append(f"Mandato {id_m}: No tiene contrato de arrendamiento asociado (Propiedad sin arriendo).")
            elif len(matches) > 1:
                # Si hay múltiples arriendos para la misma propiedad, tomamos el más reciente o el activo
                # Por ahora, advertimos
                print(f"AVISO: Mandato {id_m} tiene {len(matches)} arriendos asociados. Se usará el primero encontrado ({matches[0]['id_a']}).")
            
            # Validar que fechas origen no sean NULL
            if id_m in GRUPO_1_INICIO_ONLY:
                if matches[0]['inicio_a'] == 'None':
                    issues.append(f"Mandato {id_m}: FECHA_INICIO_A es NULL.")
            else:
                if matches[0]['inicio_a'] == 'None' or matches[0]['fin_a'] == 'None':
                    issues.append(f"Mandato {id_m}: FECHA_INICIO_A o FECHA_FIN_A es NULL.")

        if issues:
            print("\n!!! SE ENCONTRARON PROBLEMAS DE INTEGRIDAD !!!")
            for issue in issues:
                print(f" - {issue}")
            print("\nLa operación se detendrá para proteger la integridad de los datos.")
            return

        print("\nIntegridad validada. Procediendo con la actualización...")

        # 2. EJECUCIÓN TRANSACCIONAL
        # Grupo 1: Solo Inicio
        updated_count = 0
        
        print("\nActualizando Grupo 1 (Solo Inicio)...")
        for id_m in GRUPO_1_INICIO_ONLY:
            target_date = diag_data[id_m][0]['inicio_a']
            cursor.execute("""
                UPDATE CONTRATOS_MANDATOS 
                SET FECHA_INICIO_CONTRATO_M = %s 
                WHERE ID_CONTRATO_M = %s
            """, (target_date, id_m))
            updated_count += cursor.rowcount

        # Grupo 2: Inicio y Fin
        print("Actualizando Grupo 2 (Inicio y Fin)...")
        for id_m in GRUPO_2_INICIO_Y_FIN:
            target_inicio = diag_data[id_m][0]['inicio_a']
            target_fin = diag_data[id_m][0]['fin_a']
            cursor.execute("""
                UPDATE CONTRATOS_MANDATOS 
                SET FECHA_INICIO_CONTRATO_M = %s, FECHA_FIN_CONTRATO_M = %s
                WHERE ID_CONTRATO_M = %s
            """, (target_inicio, target_fin, id_m))
            updated_count += cursor.rowcount

        # 3. VERIFICACIÓN POSTERIOR
        print("\n--- RESUMEN DE CAMBIOS ---")
        cursor.execute(query_diagnostic, (all_ids,))
        final_rows = cursor.fetchall()
        
        print(f"{'ID_M':<6} | {'INICIO_M (ANT)':<15} -> {'INICIO_M (NUEVO)':<15} | {'FIN_M (ANT)':<15} -> {'FIN_M (NUEVO)':<15}")
        print("-" * 85)
        
        for row in final_rows:
            id_m = row[0]
            nuevo_inicio = str(row[1])
            nuevo_fin = str(row[2])
            ant_inicio = diag_data[id_m][0]['inicio_m']
            ant_fin = diag_data[id_m][0]['fin_m']
            
            print(f"{id_m:<6} | {ant_inicio:<15} -> {nuevo_inicio:<15} | {ant_fin:<15} -> {nuevo_fin:<15}")

        print(f"\nTotal de registros actualizados: {updated_count}")
        
        # Confirmar transacción
        conn.commit()
        print("\n[ÉXITO] Sincronización completada y confirmada en la base de datos.")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Se produjo un error durante la ejecución. Se ha realizado ROLLBACK.")
        print(f"Detalle: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_sync()

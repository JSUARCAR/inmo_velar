
import os
import sys
from pathlib import Path

# Configurar path para importar modulos del proyecto
project_root = Path(r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX")
sys.path.append(str(project_root))

from src.infraestructura.persistencia.database import db_manager

def diagnostico_liquidaciones():
    print("--- DIAGNÓSTICO DE LIQUIDACIONES ---")
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # 1. Ver las últimas 5 liquidaciones
        print("\nÚltimas 5 liquidaciones:")
        cursor.execute("""
            SELECT ID_LIQUIDACION, PERIODO, ID_CONTRATO_M, CANON_BRUTO, 
                   COMISION_MONTO, IVA_COMISION, IMPUESTO_4X1000, 
                   GASTOS_ADMINISTRACION, SEGURO_MONTO, NETO_A_PAGAR
            FROM LIQUIDACIONES 
            ORDER BY ID_LIQUIDACION DESC 
            LIMIT 5
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row['ID_LIQUIDACION']} | Per: {row['PERIODO']} | Seguro: {row['SEGURO_MONTO']} | Neto: {row['NETO_A_PAGAR']}")
            # Verificar cálculo manual
            total_egresos = (row['COMISION_MONTO'] or 0) + (row['IVA_COMISION'] or 0) + \
                            (row['IMPUESTO_4X1000'] or 0) + (row['GASTOS_ADMINISTRACION'] or 0) + \
                            (row['SEGURO_MONTO'] or 0)
            neto_calculado = (row['CANON_BRUTO'] or 0) - total_egresos
            if abs(neto_calculado - (row['NETO_A_PAGAR'] or 0)) > 1:
                print(f"  [ERROR] Discrepancia! Calculado: {neto_calculado}, DB: {row['NETO_A_PAGAR']}")
            else:
                print(f"  [OK] Neto coincide con egresos (incluyendo seguro)")

        # 2. Verificar si hay pólizas activas para esos contratos
        if rows:
            print("\nVerificando pólizas para estos contratos:")
            for row in rows:
                id_contrato = row['ID_CONTRATO_M']
                query = """
                    SELECT pol.ID_POLIZA, seg.NOMBRE_SEGURO, seg.PORCENTAJE_SEGURO
                    FROM POLIZAS pol
                    JOIN SEGUROS seg ON pol.ID_SEGURO = seg.ID_SEGURO
                    WHERE pol.ID_CONTRATO = %s AND pol.ESTADO = 'Activa'
                """
                cursor.execute(query, (id_contrato,))
                p = cursor.fetchone()
                if p:
                    print(f"  Contrato {id_contrato}: Póliza {p['ID_POLIZA']} ({p['NOMBRE_SEGURO']}) - {p['PORCENTAJE_SEGURO']}%")
                else:
                    print(f"  Contrato {id_contrato}: Sin póliza activa")

if __name__ == "__main__":
    diagnostico_liquidaciones()

"""
Script para diagnosticar y corregir la secuencia de tareas_desocupacion
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.infraestructura.persistencia.database import db_manager

def diagnose_sequence():
    """Diagnóstico del problema de secuencia"""
    print("=" * 60)
    print("DIAGNÓSTICO DE SECUENCIA - TAREAS_DESOCUPACION")
    print("=" * 60)
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # 1. Verificar el valor máximo actual en la tabla
        print("\n1. Valor máximo de ID_TAREA en la tabla:")
        cursor.execute("SELECT MAX(ID_TAREA) as MAX_ID FROM TAREAS_DESOCUPACION")
        row = cursor.fetchone()
        max_id = row['MAX_ID'] if row and row['MAX_ID'] else 0
        print(f"   MAX(ID_TAREA) = {max_id}")
        
        # 2. Verificar el valor actual de la secuencia
        print("\n2. Valor actual de la secuencia:")
        try:
            cursor.execute("SELECT last_value, is_called FROM tareas_desocupacion_id_tarea_seq")
            seq_row = cursor.fetchone()
            last_value = seq_row['LAST_VALUE'] if seq_row else 'No encontrado'
            is_called = seq_row['IS_CALLED'] if seq_row else 'No encontrado'
            print(f"   last_value = {last_value}")
            print(f"   is_called = {is_called}")
        except Exception as e:
            print(f"   Error al consultar secuencia: {e}")
            
        # 3. Listar todos los registros actuales
        print("\n3. Registros actuales en TAREAS_DESOCUPACION:")
        cursor.execute("SELECT ID_TAREA, ID_DESOCUPACION, DESCRIPCION FROM TAREAS_DESOCUPACION ORDER BY ID_TAREA")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   ID_TAREA={row['ID_TAREA']}, ID_DESOCUPACION={row['ID_DESOCUPACION']}, DESC={row['DESCRIPCION'][:30]}...")
        print(f"   Total: {len(rows)} registros")
        
        # 4. Verificar desocupaciones
        print("\n4. Desocupaciones existentes:")
        cursor.execute("SELECT ID_DESOCUPACION, ID_CONTRATO, ESTADO FROM DESOCUPACIONES ORDER BY ID_DESOCUPACION")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   ID={row['ID_DESOCUPACION']}, CONTRATO={row['ID_CONTRATO']}, ESTADO={row['ESTADO']}")
        print(f"   Total: {len(rows)} desocupaciones")

def fix_sequence():
    """Corrige la secuencia para que su próximo valor sea mayor al MAX(ID_TAREA)"""
    print("\n" + "=" * 60)
    print("CORRIGIENDO SECUENCIA")
    print("=" * 60)
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # Obtener el máximo
        cursor.execute("SELECT COALESCE(MAX(ID_TAREA), 0) + 1 as NEXT_VAL FROM TAREAS_DESOCUPACION")
        row = cursor.fetchone()
        next_val = row['NEXT_VAL']
        
        print(f"   Próximo valor a usar: {next_val}")
        
        # Corregir la secuencia usando un cursor ejecutable (no dict)
        cursor.execute(f"SELECT setval('tareas_desocupacion_id_tarea_seq', {next_val}, false)")
        conn.commit()
        
        print("   ✅ Secuencia corregida exitosamente")
        
        # Verificar
        cursor.execute("SELECT last_value, is_called FROM tareas_desocupacion_id_tarea_seq")
        seq_row = cursor.fetchone()
        print(f"   Nuevo valor de secuencia: {seq_row['LAST_VALUE']}")

if __name__ == "__main__":
    diagnose_sequence()
    
    print("\n¿Desea corregir la secuencia? (s/n): ", end="")
    # Para ejecución automática desde el agente
    fix_sequence()

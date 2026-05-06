"""
Script para eliminar tareas duplicadas en TAREAS_DESOCUPACION
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.infraestructura.persistencia.database import db_manager

def diagnose_duplicates():
    """Diagnostica las tareas duplicadas"""
    print("=" * 60)
    print("DIAGNÓSTICO DE TAREAS DUPLICADAS")
    print("=" * 60)
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # Encontrar duplicados por desocupación + descripción
        print("\n1. Buscando tareas duplicadas por (ID_DESOCUPACION, DESCRIPCION)...")
        cursor.execute("""
            SELECT ID_DESOCUPACION, DESCRIPCION, COUNT(*) as CNT
            FROM TAREAS_DESOCUPACION
            GROUP BY ID_DESOCUPACION, DESCRIPCION
            HAVING COUNT(*) > 1
            ORDER BY ID_DESOCUPACION, DESCRIPCION
        """)
        
        duplicados = cursor.fetchall()
        print(f"   Encontrados {len(duplicados)} grupos de duplicados")
        
        for dup in duplicados:
            print(f"   - Desocupación {dup['ID_DESOCUPACION']}: '{dup['DESCRIPCION'][:40]}...' -> {dup['CNT']} copias")
        
        # Contar total de tareas por desocupación
        print("\n2. Conteo de tareas por desocupación:")
        cursor.execute("""
            SELECT ID_DESOCUPACION, COUNT(*) as TOTAL
            FROM TAREAS_DESOCUPACION
            GROUP BY ID_DESOCUPACION
            ORDER BY ID_DESOCUPACION
        """)
        
        for row in cursor.fetchall():
            status = "⚠️" if row['TOTAL'] > 8 else "✓"
            print(f"   {status} Desocupación {row['ID_DESOCUPACION']}: {row['TOTAL']} tareas")
        
        return len(duplicados) > 0

def remove_duplicates():
    """Elimina tareas duplicadas manteniendo la de menor ID_TAREA (la original)"""
    print("\n" + "=" * 60)
    print("ELIMINANDO TAREAS DUPLICADAS")
    print("=" * 60)
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # Para cada grupo de duplicados, mantener el ID más bajo
        # y eliminar los demás
        cursor.execute("""
            SELECT ID_DESOCUPACION, DESCRIPCION, MIN(ID_TAREA) as KEEP_ID
            FROM TAREAS_DESOCUPACION
            GROUP BY ID_DESOCUPACION, DESCRIPCION
            HAVING COUNT(*) > 1
        """)
        
        duplicates_info = cursor.fetchall()
        total_deleted = 0
        
        for dup in duplicates_info:
            id_desocupacion = dup['ID_DESOCUPACION']
            descripcion = dup['DESCRIPCION']
            keep_id = dup['KEEP_ID']
            
            # Eliminar todas las copias excepto la de menor ID
            placeholder = db_manager.get_placeholder()
            cursor.execute(f"""
                DELETE FROM TAREAS_DESOCUPACION
                WHERE ID_DESOCUPACION = {placeholder}
                  AND DESCRIPCION = {placeholder}
                  AND ID_TAREA != {placeholder}
            """, (id_desocupacion, descripcion, keep_id))
            
            deleted = cursor.rowcount
            total_deleted += deleted
            print(f"   Eliminadas {deleted} copias de '{descripcion[:30]}...' (Desocupación {id_desocupacion})")
        
        conn.commit()
        print(f"\n   ✅ Total eliminadas: {total_deleted} tareas duplicadas")
        
        # Verificar resultado
        print("\n3. Verificación post-limpieza:")
        cursor.execute("""
            SELECT ID_DESOCUPACION, COUNT(*) as TOTAL
            FROM TAREAS_DESOCUPACION
            GROUP BY ID_DESOCUPACION
            ORDER BY ID_DESOCUPACION
        """)
        
        for row in cursor.fetchall():
            status = "✓" if row['TOTAL'] == 8 else "⚠️"
            print(f"   {status} Desocupación {row['ID_DESOCUPACION']}: {row['TOTAL']} tareas")

if __name__ == "__main__":
    has_duplicates = diagnose_duplicates()
    
    if has_duplicates:
        print("\n¿Proceder a eliminar duplicados?")
        remove_duplicates()
    else:
        print("\n✅ No hay tareas duplicadas")

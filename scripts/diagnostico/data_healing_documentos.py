import sys
import os

# Add parent dir to path to allow importing src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.infraestructura.persistencia.database import db_manager

def verificar_integridad_documental():
    print("Iniciando Diagnóstico de Integridad Documental...")
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()

    try:
        # Verificar documentos de INCIDENTE
        placeholder = db_manager.get_placeholder()
        
        # En SQLite usamos ?, en Postgres %s
        cursor.execute("SELECT id, entidad_id, nombre_archivo FROM DOCUMENTOS WHERE entidad_tipo = 'INCIDENTE'")
        docs_incidente = cursor.fetchall()
        
        huerfanos_incidente = []
        for doc in docs_incidente:
            doc_id, entidad_id, nombre = doc
            try:
                # Check if incident exists
                cursor.execute(f"SELECT id FROM INCIDENTES WHERE id = {placeholder}", (int(entidad_id),))
                if not cursor.fetchone():
                    huerfanos_incidente.append((doc_id, nombre, entidad_id))
            except Exception:
                huerfanos_incidente.append((doc_id, nombre, entidad_id))
        
        print(f"Documentos de INCIDENTE analizados: {len(docs_incidente)}")
        print(f"Documentos de INCIDENTE HUÉRFANOS (Sin registro en bd): {len(huerfanos_incidente)}")
        if huerfanos_incidente:
            print("\nPosibles documentos afectados por el State Leakage (guardados como Incidente en lugar de Contrato/Propiedad):")
            for h in huerfanos_incidente:
                print(f"- Doc ID: {h[0]} | Archivo: {h[1]} | Entidad ID (Falso Incidente): {h[2]}")

        print("\nSolución arquitectónica implementada en código: Se forzó el Fail-Fast en DocumentosStateMixin.")
    finally:
        # La conexion no se cierra explícitamente porque db_manager maneja thread_local
        pass

if __name__ == "__main__":
    verificar_integridad_documental()

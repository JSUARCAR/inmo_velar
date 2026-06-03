import sys
import os

# Asegurar que importamos desde el src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.infraestructura.persistencia.database import DatabaseManager

def migrar_estados():
    print("Conectando a la base de datos...")
    db_manager = DatabaseManager()
    
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # Migrar CONTRATOS_MANDATOS
        cursor.execute("UPDATE CONTRATOS_MANDATOS SET ESTADO_CONTRATO_M = UPPER(ESTADO_CONTRATO_M)")
        mandatos_afectados = cursor.rowcount
        print(f"Mandatos actualizados: {mandatos_afectados}")
        
        # Migrar CONTRATOS_ARRENDAMIENTOS
        cursor.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = UPPER(ESTADO_CONTRATO_A)")
        arrendamientos_afectados = cursor.rowcount
        print(f"Arrendamientos actualizados: {arrendamientos_afectados}")
        
        conn.commit()
    
    print("Migración completada.")

if __name__ == "__main__":
    migrar_estados()

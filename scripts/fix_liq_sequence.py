from src.infraestructura.persistencia.database import db_manager

def fix_sequences():
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # 1. Check Max ID
            cursor.execute("SELECT MAX(id_liquidacion_asesor) FROM LIQUIDACIONES_ASESORES")
            max_id = cursor.fetchone()[0]
            print(f"Current Max ID in Table: {max_id}")
            
            if max_id is None:
                max_id = 0
            
            # 2. Reset Sequence
            # Note: Sequence name is typically table_column_seq
            seq_name = "liquidaciones_asesores_id_liquidacion_asesor_seq"
            
            print(f"Resetting sequence {seq_name} to {max_id + 1}...")
            cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_id + 1}")
            
            conn.commit()
            print("Sequence synchronized successfully.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_sequences()

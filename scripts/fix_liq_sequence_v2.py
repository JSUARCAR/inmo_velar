import traceback
from src.infraestructura.persistencia.database import db_manager

def fix_sequences_v2():
    print("Starting sequence fix v2...")
    try:
        with db_manager.obtener_conexion() as conn:
            print(f"Connected to DB.")
            cursor = conn.cursor()
            
            # Check DB Type
            # cursor.execute("SELECT version();")
            # ver = cursor.fetchone()
            # print(f"DB Version: {ver}")

            # 1. Check Max ID
            cursor.execute("SELECT MAX(id_liquidacion_asesor) as max_val FROM LIQUIDACIONES_ASESORES")
            row = cursor.fetchone()
            print(f"Row fetched: {row}")
            # Handle RealDictRow or similar, keys might be case sensitive depending on driver config
            # But usually lowercase in psycopg2 unless quoted.
            # Row fetched: {'MAX': 5} in partial output suggests uppercase or driver specific.
            # Let's try safe get
            key = list(row.keys())[0]
            max_id = row[key]
            if max_id is None: max_id = 0
            print(f"Current Max ID in Table: {max_id}")
            
            # 2. Find Sequence Name
            # Try to query pg_class for the sequence
            cursor.execute("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S' AND c.relname LIKE '%liquidacion%'")
            seqs = cursor.fetchall()
            print(f"Found sequences: {seqs}")
            
            target_seq = "liquidaciones_asesores_id_liquidacion_asesor_seq"
            
            # Check if target matches any found
            found_seq = None
            for s in seqs:
                # s is a dict, get first value
                name = list(s.values())[0]
                if name == target_seq:
                    found_seq = name
                    break
            
            if not found_seq and seqs:
                # Try to find one containing 'asesor'
                for s in seqs:
                    name = list(s.values())[0]
                    if "asesor" in name:
                        found_seq = name
                        break
                
                if not found_seq:
                     found_seq = list(seqs[0].values())[0] 
                     print(f"Using first found sequence: {found_seq}")
                else:
                    print(f"Found fuzzy match: {found_seq}")
            else:
                print(f"Found exact match: {found_seq}")
            
            if found_seq:
                # 3. Reset Sequence
                new_val = max_id + 1
                print(f"Resetting sequence {found_seq} to {new_val}...")
                cursor.execute(f"ALTER SEQUENCE {found_seq} RESTART WITH {new_val}")
                
                conn.commit()
                print("Sequence synchronized successfully.")
            else:
                print("No suitable sequence found.")
            
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    fix_sequences_v2()

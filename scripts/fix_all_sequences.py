import traceback
from src.infraestructura.persistencia.database import db_manager

def fix_all_sequences():
    print("Starting Comprehensive Sequence Fix...")
    tables_to_fix = [
        # (Table Name, PK Column, Sequence Keyword Hint)
        ("LIQUIDACIONES_ASESORES", "id_liquidacion_asesor", "liquidaciones_asesores_id"),
        ("LIQUIDACIONES_CONTRATOS", "id_liquidacion_contrato", "liquidaciones_contratos_id"),
        ("DESCUENTOS_ASESORES", "id_descuento_asesor", "descuentos_asesores_id"),
        ("PAGOS_ASESORES", "id_pago_asesor", "pagos_asesor_id")
    ]

    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Get all sequences first
            cursor.execute("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S'")
            all_seqs_rows = cursor.fetchall()
            # Convert to list of strings
            all_seqs = [list(r.values())[0] for r in all_seqs_rows]
            print(f"Total sequences in DB: {len(all_seqs)}")
            
            for table, pk, hint in tables_to_fix:
                print(f"\n--- Fixing {table} ---")
                
                # 1. Get Max ID
                try:
                    cursor.execute(f"SELECT MAX({pk}) as max_val FROM {table}")
                    row = cursor.fetchone()
                    if row:
                        key = list(row.keys())[0]
                        max_id = row[key]
                    else:
                        max_id = 0
                        
                    if max_id is None: max_id = 0
                    print(f"Max ID: {max_id}")
                except Exception as e:
                    print(f"Error fetching max id for {table}: {e}")
                    continue

                # 2. Find Sequence
                target_seq = None
                for s in all_seqs:
                    if hint in s:
                        target_seq = s
                        break
                
                if not target_seq:
                    print(f"WARNING: No sequence found for hint '{hint}'")
                    continue
                
                print(f"Target Sequence: {target_seq}")
                
                # 3. Restart
                new_val = max_id + 1
                try:
                    print(f"Restarting with {new_val}")
                    cursor.execute(f"ALTER SEQUENCE {target_seq} RESTART WITH {new_val}")
                    print("Success.")
                except Exception as e:
                    print(f"Error restarting sequence: {e}")
            
            conn.commit()
            print("\nAll Done.")

    except Exception as e:
        print("Global Error:")
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_sequences()

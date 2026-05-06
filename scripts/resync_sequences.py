"""Script to resynchronize PostgreSQL sequences for RECAUDOS and RECAUDO_CONCEPTOS tables."""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def resync_sequences():
    """Resynchronize sequences to max(id) + 1."""
    print("=" * 60)
    print("Resynchronizing PostgreSQL sequences...")
    print("=" * 60)
    
    # Connect directly with psycopg2 (not using wrapper)
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'db_inmo_velar'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    
    try:
        # Resync RECAUDOS sequence
        print("\n1. Checking RECAUDOS table...")
        cursor.execute("SELECT MAX(id_recaudo) FROM recaudos")
        result = cursor.fetchone()
        max_recaudo = result[0] if result and result[0] else 0
        print(f"   Max ID_RECAUDO: {max_recaudo}")
        
        if max_recaudo:
            cursor.execute(f"SELECT setval('recaudos_id_recaudo_seq', {max_recaudo}, true)")
            result = cursor.fetchone()
            print(f"   Sequence set to: {result[0]}")
        else:
            print("   No records found, resetting to 1...")
            cursor.execute("SELECT setval('recaudos_id_recaudo_seq', 1, false)")
        
        # Resync RECAUDO_CONCEPTOS sequence
        print("\n2. Checking RECAUDO_CONCEPTOS table...")
        cursor.execute("SELECT MAX(id_recaudo_concepto) FROM recaudo_conceptos")
        result = cursor.fetchone()
        max_concepto = result[0] if result and result[0] else 0
        print(f"   Max ID_RECAUDO_CONCEPTO: {max_concepto}")
        
        if max_concepto:
            cursor.execute(f"SELECT setval('recaudo_conceptos_id_recaudo_concepto_seq', {max_concepto}, true)")
            result = cursor.fetchone()
            print(f"   Sequence set to: {result[0]}")
        else:
            print("   No records found, resetting to 1...")
            cursor.execute("SELECT setval('recaudo_conceptos_id_recaudo_concepto_seq', 1, false)")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("Sequences resynchronized successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    resync_sequences()

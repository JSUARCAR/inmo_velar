
import sqlite3
import os
import sys

# Config
DB_PATH = 'DB_Inmo_Velar.db'
OUTPUT_FILE = 'debug_recaudos_output.txt'

def inspect_recaudos():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"--- Inspecting RECAUDO_ARRENDAMIENTO ---\n")
        
        if not os.path.exists(DB_PATH):
            f.write(f"Error: Database not found at {DB_PATH}\n")
            return

        try:
            conn = sqlite3.connect(DB_PATH, timeout=10) # 10s timeout
            cursor = conn.cursor()
            
            # 1. Check distinct statuses
            cursor.execute("SELECT DISTINCT ESTADO_RECAUDO FROM RECAUDO_ARRENDAMIENTO")
            statuses = cursor.fetchall()
            f.write(f"Distinct ESTADO_RECAUDO values: {statuses}\n")
            
            # 2. Check all rows with dates and statuses
            cursor.execute("SELECT ID_RECAUDO, FECHA_RECAUDO, VALOR_RECAUDO, ESTADO_RECAUDO FROM RECAUDO_ARRENDAMIENTO")
            rows = cursor.fetchall()
            f.write(f"\nAll Rows ({len(rows)}):\n")
            f.write(f"{'ID':<5} {'FECHA':<12} {'VALOR':<15} {'ESTADO':<15}\n")
            f.write("-" * 50 + "\n")
            for row in rows:
                f.write(f"{row[0]:<5} {row[1]:<12} {row[2]:<15} {row[3]:<15}\n")
                
        except Exception as e:
            f.write(f"Error: {e}\n")
        finally:
            if conn:
                conn.close()
    
    # Print content to stdout as well
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    inspect_recaudos()

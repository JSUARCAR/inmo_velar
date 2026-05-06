
import sqlite3
import os

# Config
DB_PATH = 'DB_Inmo_Velar.db'
OUTPUT_FILE = 'debug_recaudos_correct_table.txt'

def inspect_recaudos_correct():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"--- Inspecting RECAUDOS (Correct Table) ---\n")
        
        if not os.path.exists(DB_PATH):
            f.write(f"Error: Database not found at {DB_PATH}\n")
            return

        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cursor = conn.cursor()
            
            # Check schema
            cursor.execute("PRAGMA table_info(RECAUDOS)")
            columns = cursor.fetchall()
            f.write("Columns:\n")
            for col in columns:
                f.write(f"  {col[1]} ({col[2]})\n")

            # Check rows
            cursor.execute("SELECT ID_RECAUDO, FECHA_PAGO, VALOR_TOTAL, ESTADO_RECAUDO FROM RECAUDOS")
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
    
    # Print content
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    inspect_recaudos_correct()

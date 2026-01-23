import psycopg2
import os
import time

# Config from .env
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

try:
    print(f"Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # 1. Get a test property ID
    cursor.execute("SELECT ID_PROPIEDAD, OBSERVACIONES_PROPIEDAD FROM PROPIEDADES LIMIT 1")
    row = cursor.fetchone()
    if not row:
        print("[SKIP] No properties found to test.")
        exit(0)
        
    id_prop = row[0]
    old_obs = row[1] or ""
    new_obs = f"Test Audit {int(time.time())}"
    
    print(f"Testing Update on Property ID {id_prop}...")
    
    # 2. Update Property
    cursor.execute("""
        UPDATE PROPIEDADES 
        SET OBSERVACIONES_PROPIEDAD = %s,
            UPDATED_BY = 'TEST_SCRIPT_USER'
        WHERE ID_PROPIEDAD = %s
    """, (new_obs, id_prop))
    conn.commit()
    
    # 3. Check Audit Log
    print("Checking Audit Log...")
    # Wait a moment for trigger (synchronous but good practice)
    time.sleep(1)
    
    cursor.execute("""
        SELECT * FROM AUDITORIA_CAMBIOS 
        WHERE TABLA = 'propiedades' 
        AND ID_REGISTRO = %s
        ORDER BY ID_AUDITORIA DESC
        LIMIT 1
    """, (id_prop,))
    
    audit_row = cursor.fetchone()
    
    if audit_row:
        # Columns: id, table, record_id, operation, field, old, new, user, date...
        # Assuming typical order or use dict cursor but tuple is fine for quick check
        print("[SUCCESS] Audit Record Found!")
        print(f"  - User: {audit_row[7]}") # Index 7 is usually USER based on schema
        print(f"  - Field: {audit_row[3]} -> {audit_row[5]}") # Field -> New Val
        
        if audit_row[7] == 'TEST_SCRIPT_USER' and audit_row[5] == new_obs:
            print("[PASS] Audit data matches expected values.")
        else:
            print("[WARNING] Audit data mismatch.")
            print(f"Expected User: TEST_SCRIPT_USER, Got: {audit_row[7]}")
            print(f"Expected New Val: {new_obs}, Got: {audit_row[5]}")
            
    else:
        print("[FAIL] No audit record found for this update.")

    # Restore (Optional, or leave as test artifact)
    # cursor.execute("UPDATE PROPIEDADES SET OBSERVACIONES_PROPIEDAD = %s WHERE ID_PROPIEDAD = %s", (old_obs, id_prop))
    # conn.commit()

    conn.close()

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")

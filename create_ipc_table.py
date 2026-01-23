import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="inmo_user",
    password="7323"
)

cursor = conn.cursor()

# Create IPC increment history table
print("Creating IPC_INCREMENT_HISTORY table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS IPC_INCREMENT_HISTORY (
        ID_INCREMENTO_IPC SERIAL PRIMARY KEY,
        ID_CONTRATO_A INTEGER NOT NULL,
        FECHA_APLICACION DATE NOT NULL,
        PORCENTAJE_IPC DECIMAL(5,2) NOT NULL,
        CANON_ANTERIOR BIGINT NOT NULL,
        CANON_NUEVO BIGINT NOT NULL,
        OBSERVACIONES TEXT,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CREATED_BY TEXT,
        FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A)
    )
""")

# Create indexes
print("Creating indexes...")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ipc_history_contrato 
    ON IPC_INCREMENT_HISTORY(ID_CONTRATO_A)
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ipc_history_fecha 
    ON IPC_INCREMENT_HISTORY(FECHA_APLICACION)
""")

conn.commit()

# Verify table created
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'ipc_increment_history'
""")
result = cursor.fetchone()

if result:
    print(f"✅ Table '{result[0]}' created successfully!")
    
    # Show table structure
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ipc_increment_history'
        ORDER BY ordinal_position
    """)
    print("\nTable structure:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
else:
    print("❌ Table creation failed")

cursor.close()
conn.close()

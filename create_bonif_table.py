import psycopg2

# Conexión directa a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="inmo_user",
    password="7323"
)

try:
    cursor = conn.cursor()
    
    # Crear tabla BONIFICACIONES_ASESORES
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS BONIFICACIONES_ASESORES (
        ID_BONIFICACION_ASESOR SERIAL PRIMARY KEY,
        ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
        TIPO_BONIFICACION VARCHAR(50) NOT NULL,
        DESCRIPCION_BONIFICACION TEXT,
        VALOR_BONIFICACION INTEGER NOT NULL,
        FECHA_REGISTRO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CREATED_BY VARCHAR(50),
        CONSTRAINT fk_liquidacion_bono
            FOREIGN KEY(ID_LIQUIDACION_ASESOR) 
            REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR)
            ON DELETE CASCADE
    );
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("✓ Tabla BONIFICACIONES_ASESORES creada exitosamente")
    
    # Verificar que se creó
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'bonificaciones_asesores'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"✓ Verificado: Tabla {result[0]} existe en la base de datos")
    else:
        print("✗ Error: No se pudo verificar la tabla")
        
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()

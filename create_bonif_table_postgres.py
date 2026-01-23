import psycopg2

# Conexión como superusuario postgres
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=""
)

try:
    cursor = conn.cursor()
    
    # Crear tabla BONIFICACIONES_ASESORES
    print("Creando tabla BONIFICACIONES_ASESORES...")
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
    
    # Otorgar permisos a inmo_user
    print("Otorgando permisos a inmo_user...")
    cursor.execute("GRANT ALL PRIVILEGES ON TABLE BONIFICACIONES_ASESORES TO inmo_user;")
    cursor.execute("GRANT USAGE, SELECT ON SEQUENCE bonificaciones_asesores_id_bonificacion_asesor_seq TO inmo_user;")
    conn.commit()
    print("✓ Permisos otorgados a inmo_user")
    
    # Verificar que se creó
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'bonificaciones_asesores'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"✓ Verificado: Tabla '{result[0]}' existe en la base de datos")
    else:
        print("✗ Error: No se pudo verificar la tabla")
        
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()

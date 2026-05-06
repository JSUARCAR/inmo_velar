import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("Verificando/Creando tabla BONIFICACIONES_ASESORES...")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=os.getenv("DB_PASSWORD", "")
)

try:
    cursor = conn.cursor()
    
    # Verificar si existe
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE LOWER(table_name) = 'bonificaciones_asesores'
    """)
    
    exists = cursor.fetchone()
    
    if exists:
        print("✓ Tabla BONIFICACIONES_ASESORES ya existe")
    else:
        print("⚠️  Tabla no existe, creando...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BONIFICACIONES_ASESORES (
                id_bonificacion_asesor SERIAL PRIMARY KEY,
                id_liquidacion_asesor INTEGER NOT NULL,
                tipo_bonificacion TEXT NOT NULL,
                descripcion_bonificacion TEXT,
                valor_bonificacion BIGINT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY (id_liquidacion_asesor) REFERENCES LIQUIDACIONES_ASESORES(id_liquidacion_asesor)
            )
        """)
        
        # Grant permissions
        cursor.execute("GRANT ALL ON BONIFICACIONES_ASESORES TO inmo_user")
        cursor.execute("GRANT USAGE, SELECT ON SEQUENCE bonificaciones_asesores_id_bonificacion_asesor_seq TO inmo_user")
        
        conn.commit()
        print("✅ Tabla BONIFICACIONES_ASESORES creada exitosamente")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()

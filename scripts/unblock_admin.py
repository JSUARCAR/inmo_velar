"""
Script para desbloquear el usuario admin
"""
import psycopg2

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Primero, ver las columnas de la tabla USUARIOS
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position
    """)
    
    print("📋 Columnas de la tabla USUARIOS:")
    columns = cur.fetchall()
    for col in columns:
        print(f"   - {col[0]}: {col[1]}")
    
    print("\n🔍 Verificando usuario admin...")
    cur.execute("SELECT * FROM USUARIOS WHERE NOMBRE_USUARIO = 'admin' LIMIT 1")
    admin_user = cur.fetchone()
    
    if admin_user:
        print(f"✅ Usuario 'admin' encontrado")
        print(f"   Datos: {admin_user}")
    else:
        print("❌ No se encontró el usuario 'admin'")
    
    # Cerrar conexiones
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

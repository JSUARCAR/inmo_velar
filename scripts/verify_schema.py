import psycopg2
from psycopg2 import sql

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password="7323"
)

cur = conn.cursor()

print("="*80)
print("VERIFICACIÓN DE ESQUEMA DE BASE DE DATOS")
print("="*80)

# 1. List all tables
print("\n1. TABLAS EN LA BASE DE DATOS:")
cur.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY tablename
""")
tables = cur.fetchall()
for table in tables:
    print(f"   - {table[0]}")

# 2. Check RECAUDOS table structure
print("\n2. ESQUEMA DE TABLA 'RECAUDOS':")
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'recaudos'
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
if columns:
    for col in columns:
        print(f"   - {col[0]:30s} {col[1]:20s} NULL={col[2]} DEFAULT={col[3]}")
else:
    print("   ⚠️ Tabla 'recaudos' no encontrada (case-sensitive)")

# 3. Check for RECAUDOS_CONCEPTOS table (different names)
print("\n3. BUSCANDO TABLA DE CONCEPTOS:")
cur.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND (tablename LIKE '%recaudo%concepto%' OR tablename LIKE '%concepto%recaudo%')
""")
concepto_tables = cur.fetchall()
if concepto_tables:
    for table in concepto_tables:
        print(f"   ✅ Encontrada: {table[0]}")
else:
    print("   ❌ No se encontró tabla de conceptos")

# 4. Sample data from RECAUDOS
print("\n4. MUESTRA DE DATOS DE 'RECAUDOS' (primeros 2 registros):")
try:
    cur.execute("SELECT * FROM RECAUDOS LIMIT 2")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    print(f"   Columnas: {', '.join(colnames)}")
    for row in rows:
        print(f"   {row}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*80)
print("FIN VERIFICACIÓN")
print("="*80)

cur.close()
conn.close()

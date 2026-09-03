"""
Diagnóstico: ver bloqueos en tabla IPC y terminar conexiones bloqueantes.
Luego ejecutar la migración.
"""
import sys
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no configurada")

parsed = urlparse(DATABASE_URL)
print(f"Conectando a {parsed.hostname}:{parsed.port}...")

conn = psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    database=(parsed.path or "/railway").lstrip("/"),
    user=parsed.username,
    password=parsed.password,
    connect_timeout=15,
)
conn.autocommit = True
cur = conn.cursor()

print("\n[DIAGNÓSTICO] Conexiones activas en la tabla ipc:")
cur.execute("""
    SELECT pid, state, query_start, query
    FROM pg_stat_activity
    WHERE state <> 'idle'
    AND (query ILIKE '%ipc%' OR datname = 'railway')
    ORDER BY query_start;
""")
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"   PID={row[0]} state={row[1]} query={row[3][:80]}")
else:
    print("   Ninguna actividad en ipc encontrada.")

print("\n[ACCIÓN] Terminando conexiones idle/bloqueantes (excepto la actual)...")
cur.execute("""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE pid <> pg_backend_pid()
    AND datname = 'railway'
    AND state = 'idle in transaction';
""")
terminated = cur.fetchall()
print(f"   Conexiones terminadas: {len(terminated)}")

# Ahora ejecutar la migración
print("\n[MIGRACIÓN] Verificando tipo actual...")
cur.execute("""
    SELECT data_type
    FROM information_schema.columns
    WHERE table_name = 'ipc' AND column_name = 'valor_ipc';
""")
row = cur.fetchone()
current_type = row[0] if row else "UNKNOWN"
print(f"   Tipo actual: {current_type}")

if current_type in ("numeric", "real", "double precision"):
    print("   ✅ Ya es tipo decimal. No se necesita migración.")
    sys.exit(0)

print("\n[STEP 1] Usando USING para cambiar tipo en UN SOLO ALTER (sin columna temporal)...")
cur.execute("""
    ALTER TABLE ipc 
    ALTER COLUMN valor_ipc TYPE NUMERIC(8,4) USING valor_ipc::NUMERIC(8,4);
""")
print("   ✅ OK")

print("\n[VERIFY FINAL]")
cur.execute("""
    SELECT column_name, data_type, numeric_precision, numeric_scale
    FROM information_schema.columns
    WHERE table_name = 'ipc' AND column_name = 'valor_ipc';
""")
result = cur.fetchone()
print(f"   {result}")

cur.close()
conn.close()
print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")

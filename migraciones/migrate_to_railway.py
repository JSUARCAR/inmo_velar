"""
Migracion SQLite Local -> Railway PostgreSQL.
"""
import sqlite3
import sys
import os
import psycopg2

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SQLITE_PATH = "migraciones/DB_Inmo_Velar.db"
RAILWAY = {
    "host": "hopper.proxy.rlwy.net",
    "port": 12937,
    "dbname": "railway",
    "user": "postgres",
    "password": "tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU",
}

TYPE_MAP = {
    "INTEGER": "INTEGER",
    "TEXT": "TEXT",
    "REAL": "DOUBLE PRECISION",
    "BLOB": "BYTEA",
    "NUMERIC": "NUMERIC",
    "BOOLEAN": "BOOLEAN",
    "DATETIME": "TIMESTAMP",
    "DATE": "DATE",
    "TIMESTAMP": "TIMESTAMP",
    "DECIMAL": "NUMERIC",
}

# Explicit overrides for columns that SQLite treats as INTEGER but really are BOOLEAN
COLUMN_TYPE_OVERRIDES = {
    "estado_usuario": "BOOLEAN",
    "es_propietario": "BOOLEAN",
    "es_inquilino": "BOOLEAN", 
    "activo": "BOOLEAN",
    "es_vigente": "BOOLEAN",
    "disponibilidad_propiedad": "BOOLEAN",
}

def map_type(t, col_name=None):
    if col_name and col_name.lower() in COLUMN_TYPE_OVERRIDES:
        return COLUMN_TYPE_OVERRIDES[col_name.lower()]
        
    if not t:
        return "TEXT"
    base = t.upper().split("(")[0].strip()
    if base.startswith("VARCHAR"):
        return t
    return TYPE_MAP.get(base, "TEXT")


def main():
    print("=" * 60)
    print("  MIGRACION: SQLite -> Railway PostgreSQL")
    print("=" * 60)

    sq = sqlite3.connect(SQLITE_PATH)
    sc = sq.cursor()
    pg = psycopg2.connect(**RAILWAY)
    pg.autocommit = True
    pc = pg.cursor()

    sc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in sc.fetchall()]
    print(f"\nTablas encontradas: {len(tables)}\n")

    # PASO 0: Drop existing
    print("PASO 0: Limpiando tablas existentes...")
    pc.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    for r in pc.fetchall():
        if r[0] != 'alembic_version':
            pc.execute(f'DROP TABLE IF EXISTS "{r[0]}" CASCADE')
            print(f"  DROPPED {r[0]}")

    # PASO 1: Create tables
    print("\nPASO 1: Creando tablas...")
    created = []
    for table in tables:
        sc.execute(f'PRAGMA table_info("{table}")')
        cols = sc.fetchall()
        pg_table = table.lower()

        col_defs = []
        for cid, name, ctype, notnull, default, pk in cols:
            pgtype = map_type(ctype, name)
            lcname = name.lower()

            if pk == 1 and pgtype == "INTEGER":
                col_defs.append(f'"{lcname}" SERIAL PRIMARY KEY')
            else:
                parts = [f'"{lcname}" {pgtype}']
                if notnull and not pk:
                    parts.append("NOT NULL")
                if default is not None:
                    d = str(default)
                    d_lower = d.lower()
                    
                    # Handle SQLite Timestamps
                    if "datetime('now'" in d_lower or "timestamp('now'" in d_lower:
                        parts.append("DEFAULT CURRENT_TIMESTAMP")
                    elif "date('now'" in d_lower:
                        parts.append("DEFAULT CURRENT_DATE")
                    elif pgtype == "BOOLEAN":
                        if d in ("1", "true", "True"):
                            parts.append("DEFAULT TRUE")
                        elif d in ("0", "false", "False"):
                            parts.append("DEFAULT FALSE")
                        else:
                             parts.append(f"DEFAULT {d}")
                    elif "autoincrement" not in d_lower and "nextval" not in d_lower:
                        parts.append(f"DEFAULT {d}")
                col_defs.append(" ".join(parts))

        ddl = f'CREATE TABLE IF NOT EXISTS "{pg_table}" (\n  {",".join(col_defs)}\n);'

        try:
            pc.execute(ddl)
            created.append(table)
            print(f"  OK {table} -> {pg_table}")
        except Exception as e:
            print(f"  FAIL {table}: {e}")
            print(f"       DDL: {ddl[:300]}")

    # Manual check for configuracion_sistema
    if "configuracion_sistema" not in [t.lower() for t in tables]:
        print("\nCreating missing table 'configuracion_sistema'...")
        try:
            pc.execute("""
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    id SERIAL PRIMARY KEY,
                    nombre_empresa TEXT DEFAULT 'Inmobiliaria Velar',
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    nit TEXT,
                    logo_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Insert default row
            pc.execute("INSERT INTO configuracion_sistema (id, nombre_empresa) VALUES (1, 'Inmobiliaria Velar') ON CONFLICT DO NOTHING")
            print("  OK configuracion_sistema (Created manually)")
            created.append("configuracion_sistema") # Treat as created for counting
        except Exception as e:
            print(f"  FAIL configuracion_sistema: {e}")

    print(f"\nCreated {len(created)} tables (including manual)")

    # PASO 2: Copy data
    print("\nPASO 2: Copiando datos...")
    pg.autocommit = False
    total = 0

    for table in created:
        if table == "configuracion_sistema" and table not in tables:
            continue # Skip data copy if manually created

        pg_table = table.lower()
        sc.execute(f'PRAGMA table_info("{table}")')
        cols = sc.fetchall()
        col_names = [c[1] for c in cols]
        
        # Determine boolean indices
        bool_indices = []
        for idx, col_def in enumerate(cols):
            # col_def: (cid, name, type, notnull, dflt_value, pk)
            ctype = col_def[2]
            name = col_def[1]
            pgtype = map_type(ctype, name)
            if pgtype == "BOOLEAN":
                bool_indices.append(idx)

        sc.execute(f'SELECT * FROM "{table}"')
        rows = sc.fetchall()
        if not rows:
            print(f"  EMPTY {table}")
            continue

        col_list = ", ".join(f'"{c.lower()}"' for c in col_names)
        phs = ", ".join(["%s"] * len(col_names))
        sql = f'INSERT INTO "{pg_table}" ({col_list}) VALUES ({phs})'

        ok = 0
        err = 0
        for row in rows:
            try:
                # Convert row tuple to list to modify
                row_data = list(row)
                # Convert booleans
                for idx in bool_indices:
                    val = row_data[idx]
                    if val == 1:
                        row_data[idx] = True
                    elif val == 0:
                        row_data[idx] = False
                    # else leave as None or whatever
                
                pc.execute(sql, row_data)
                pg.commit()
                ok += 1
            except Exception as e:
                pg.rollback()
                err += 1
                if err <= 2:
                    print(f"  DATA_ERR {pg_table}: {str(e)[:150]}")

        total += ok
        e_str = f" ({err} errors)" if err else ""
        print(f"  DATA {table}: {ok} rows{e_str}")

    # PASO 3: Reset sequences
    print("\nPASO 3: Reseteando secuencias...")
    pg.autocommit = True
    for table in created:
        pg_table = table.lower()
        
        # For manual table, assume id
        if table == "configuracion_sistema" and table not in tables:
             try:
                pc.execute(f"SELECT setval('configuracion_sistema_id_seq', COALESCE((SELECT MAX(id) FROM configuracion_sistema), 1))")
                print(f"  SEQ configuracion_sistema.id")
             except: pass
             continue

        sc.execute(f'PRAGMA table_info("{table}")')
        for c in sc.fetchall():
            if c[5] == 1:
                col = c[1].lower()
                seq = f"{pg_table}_{col}_seq"
                try:
                    pc.execute(f"SELECT setval('{seq}', COALESCE((SELECT MAX(\"{col}\") FROM \"{pg_table}\"), 1))")
                    print(f"  SEQ {pg_table}.{col}")
                except:
                    pass

    # VERIFICACION
    print(f"\n{'=' * 60}")
    print("  VERIFICACION FINAL")
    print(f"{'=' * 60}")
    pc.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename != 'alembic_version' ORDER BY tablename")
    for r in pc.fetchall():
        pc.execute(f'SELECT COUNT(*) FROM "{r[0]}"')
        cnt = pc.fetchone()[0]
        print(f"  {r[0]}: {cnt} rows")
    print(f"\nCOMPLETED: {len(created)} tables, {total} rows")

    sq.close()
    pg.close()


if __name__ == "__main__":
    main()

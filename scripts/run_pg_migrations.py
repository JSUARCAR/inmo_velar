import psycopg2

DATABASE_URL = "postgresql://postgres:tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU@hopper.proxy.rlwy.net:12937/railway"

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

migrations = [
    # Migration 001: Add estado_pago to INCIDENTES
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='incidentes' AND column_name='estado_pago') THEN
            ALTER TABLE incidentes ADD COLUMN estado_pago TEXT DEFAULT 'Pendiente';
        END IF;
    END $$;
    """,
    # Migration 002: Add valor_incidentes to LIQUIDACIONES
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='liquidaciones' AND column_name='valor_incidentes') THEN
            ALTER TABLE liquidaciones ADD COLUMN valor_incidentes INTEGER DEFAULT 0;
        END IF;
    END $$;
    """,
    # Migration 003: Create PLAN_PAGO_INCIDENTE
    """
    CREATE TABLE IF NOT EXISTS PLAN_PAGO_INCIDENTE (
        ID_PLAN_PAGO SERIAL PRIMARY KEY,
        ID_INCIDENTE INTEGER NOT NULL,
        NUM_CUOTAS INTEGER NOT NULL CHECK(NUM_CUOTAS > 0),
        VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
        TOTAL_PLAN INTEGER NOT NULL CHECK(TOTAL_PLAN > 0),
        ESTADO TEXT NOT NULL DEFAULT 'Activo' CHECK(ESTADO IN ('Activo', 'Cancelado', 'Completado')),
        CREADO_POR TEXT NOT NULL,
        CREATED_AT TEXT NOT NULL DEFAULT (NOW() AT TIME ZONE 'America/Bogota')::TEXT,
        UPDATED_AT TEXT,
        FOREIGN KEY (ID_INCIDENTE) REFERENCES incidentes(ID_INCIDENTE) ON DELETE CASCADE
    );
    """,
    # Migration 004: Create CUOTA_INCIDENTE
    """
    CREATE TABLE IF NOT EXISTS CUOTA_INCIDENTE (
        ID_CUOTA SERIAL PRIMARY KEY,
        ID_PLAN_PAGO INTEGER NOT NULL,
        NUMERO_CUOTA INTEGER NOT NULL CHECK(NUMERO_CUOTA > 0),
        VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
        ID_LIQUIDACION INTEGER,
        ESTADO_PAGO TEXT NOT NULL DEFAULT 'Pendiente' CHECK(ESTADO_PAGO IN ('Pendiente', 'Asociada', 'Pagada')),
        CREATED_AT TEXT NOT NULL DEFAULT (NOW() AT TIME ZONE 'America/Bogota')::TEXT,
        FOREIGN KEY (ID_PLAN_PAGO) REFERENCES PLAN_PAGO_INCIDENTE(ID_PLAN_PAGO) ON DELETE CASCADE,
        FOREIGN KEY (ID_LIQUIDACION) REFERENCES liquidaciones(ID_LIQUIDACION),
        UNIQUE(ID_PLAN_PAGO, NUMERO_CUOTA)
    );
    """,
    # Migration 005: Create INCIDENTE_LIQUIDACION
    """
    CREATE TABLE IF NOT EXISTS INCIDENTE_LIQUIDACION (
        ID_RELACION SERIAL PRIMARY KEY,
        ID_INCIDENTE INTEGER NOT NULL,
        ID_LIQUIDACION INTEGER NOT NULL,
        NUMERO_CUOTA INTEGER NOT NULL,
        VALOR_DESCUENTO INTEGER NOT NULL CHECK(VALOR_DESCUENTO > 0),
        ASOCIADO_POR TEXT NOT NULL,
        FECHA_ASOCIACION TEXT NOT NULL DEFAULT (NOW() AT TIME ZONE 'America/Bogota')::TEXT,
        FOREIGN KEY (ID_INCIDENTE) REFERENCES incidentes(ID_INCIDENTE),
        FOREIGN KEY (ID_LIQUIDACION) REFERENCES liquidaciones(ID_LIQUIDACION),
        UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)
    );
    """,
    # Migration 006: Create BLOQUEOS_EDICION
    """
    CREATE TABLE IF NOT EXISTS BLOQUEOS_EDICION (
        ID_BLOQUEO SERIAL PRIMARY KEY,
        TABLA TEXT NOT NULL,
        ID_REGISTRO INTEGER NOT NULL,
        USUARIO TEXT NOT NULL,
        SESION_ID TEXT NOT NULL,
        FECHA_BLOQUEO TEXT NOT NULL DEFAULT (NOW() AT TIME ZONE 'America/Bogota')::TEXT,
        FECHA_EXPIRACION TEXT NOT NULL,
        UNIQUE(TABLA, ID_REGISTRO)
    );
    """,
    # Indexes
    """
    CREATE INDEX IF NOT EXISTS idx_incidentes_estado_pago ON incidentes(estado_pago);
    CREATE INDEX IF NOT EXISTS idx_incidentes_estado_pago_estado ON incidentes(estado_pago, ESTADO);
    CREATE INDEX IF NOT EXISTS idx_liquidaciones_valor_incidentes ON liquidaciones(valor_incidentes);
    CREATE INDEX IF NOT EXISTS idx_plan_pago_incidente_id_incidente ON PLAN_PAGO_INCIDENTE(ID_INCIDENTE);
    CREATE INDEX IF NOT EXISTS idx_plan_pago_incidente_estado ON PLAN_PAGO_INCIDENTE(ESTADO);
    CREATE INDEX IF NOT EXISTS idx_cuota_plan_pago ON CUOTA_INCIDENTE(ID_PLAN_PAGO);
    CREATE INDEX IF NOT EXISTS idx_cuota_liquidacion ON CUOTA_INCIDENTE(ID_LIQUIDACION);
    CREATE INDEX IF NOT EXISTS idx_cuota_estado ON CUOTA_INCIDENTE(ESTADO_PAGO);
    CREATE INDEX IF NOT EXISTS idx_incidente_liq_incidente ON INCIDENTE_LIQUIDACION(ID_INCIDENTE);
    CREATE INDEX IF NOT EXISTS idx_incidente_liq_liquidacion ON INCIDENTE_LIQUIDACION(ID_LIQUIDACION);
    """,
    # Triggers for INCIDENTE_LIQUIDACION - auto-update valor_incidentes
    """
    CREATE OR REPLACE FUNCTION fn_actualizar_valor_incidentes_insert()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE liquidaciones 
        SET valor_incidentes = (
            SELECT COALESCE(SUM(VALOR_DESCUENTO), 0)
            FROM INCIDENTE_LIQUIDACION
            WHERE ID_LIQUIDACION = NEW.ID_LIQUIDACION
        )
        WHERE ID_LIQUIDACION = NEW.ID_LIQUIDACION;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION fn_actualizar_valor_incidentes_delete()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE liquidaciones 
        SET valor_incidentes = (
            SELECT COALESCE(SUM(VALOR_DESCUENTO), 0)
            FROM INCIDENTE_LIQUIDACION
            WHERE ID_LIQUIDACION = OLD.ID_LIQUIDACION
        )
        WHERE ID_LIQUIDACION = OLD.ID_LIQUIDACION;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_incidente_liq_actualizar_valor_insert ON INCIDENTE_LIQUIDACION;
    CREATE TRIGGER trg_incidente_liq_actualizar_valor_insert
    AFTER INSERT ON INCIDENTE_LIQUIDACION
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_valor_incidentes_insert();

    DROP TRIGGER IF EXISTS trg_incidente_liq_actualizar_valor_delete ON INCIDENTE_LIQUIDACION;
    CREATE TRIGGER trg_incidente_liq_actualizar_valor_delete
    AFTER DELETE ON INCIDENTE_LIQUIDACION
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_valor_incidentes_delete();
    """,
]

for i, sql in enumerate(migrations):
    try:
        cursor.execute(sql)
        print(f"Migration {i+1}: OK")
    except Exception as e:
        print(f"Migration {i+1}: {e}")
        conn.rollback()

# Verify
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('plan_pago_incidente','cuota_incidente','incidente_liquidacion','bloqueos_edicion')
    ORDER BY table_name
""")
tables = [r[0] for r in cursor.fetchall()]
print(f"\nNew tables: {tables}")

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='incidentes' AND column_name='estado_pago'")
col = cursor.fetchone()
print(f"estado_pago column: {'EXISTS' if col else 'MISSING'}")

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='liquidaciones' AND column_name='valor_incidentes'")
col = cursor.fetchone()
print(f"valor_incidentes column: {'EXISTS' if col else 'MISSING'}")

cursor.execute("SELECT ID_INCIDENTE, ESTADO, estado_pago FROM INCIDENTES LIMIT 3")
for r in cursor.fetchall():
    print(f"  {r}")

cursor.close()
conn.close()

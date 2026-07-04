#!/usr/bin/env python3
"""
Script de Migraciones PostgreSQL para Inmobiliaria Velar
Uso: python scripts/run_pg_migrations.py
Requiere: Variable de entorno DATABASE_URL configurada
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def get_database_url():
    """Obtiene DATABASE_URL del entorno o lanza error."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL no está configurada en el entorno")
        sys.exit(1)
    return db_url


def run_migrations():
    """Ejecuta todas las migraciones pendientes de forma idempotente."""
    import psycopg2
    
    db_url = get_database_url()
    logger.info(f"Conectando a la base de datos...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Conexión exitosa. Iniciando migraciones...")
        
        # Lista de migraciones (idempotentes - CREATE IF NOT EXISTS)
        migrations = [
            # Migration 001: Add estado_pago to INCIDENTES
            ("Add estado_pago column", """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='incidentes' AND column_name='estado_pago'
                    ) THEN
                        ALTER TABLE incidentes ADD COLUMN estado_pago TEXT DEFAULT 'Pendiente';
                        RAISE NOTICE 'Columna estado_pago agregada';
                    ELSE
                        RAISE NOTICE 'Columna estado_pago ya existe';
                    END IF;
                END $$;
            """),
            
            # Migration 002: Add valor_incidentes to LIQUIDACIONES
            ("Add valor_incidentes column", """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='liquidaciones' AND column_name='valor_incidentes'
                    ) THEN
                        ALTER TABLE liquidaciones ADD COLUMN valor_incidentes INTEGER DEFAULT 0;
                        RAISE NOTICE 'Columna valor_incidentes agregada';
                    ELSE
                        RAISE NOTICE 'Columna valor_incidentes ya existe';
                    END IF;
                END $$;
            """),
            
            # Migration 003: Create PLAN_PAGO_INCIDENTE
            ("Create PLAN_PAGO_INCIDENTE table", """
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
            """),
            
            # Migration 004: Create CUOTA_INCIDENTE
            ("Create CUOTA_INCIDENTE table", """
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
            """),
            
            # Migration 005: Create INCIDENTE_LIQUIDACION
            ("Create INCIDENTE_LIQUIDACION table", """
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
            """),
            
            # Migration 006: Create BLOQUEOS_EDICION
            ("Create BLOQUEOS_EDICION table", """
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
            """),
            
            # Indexes
            ("Create indexes", """
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
            """),
            
            # Triggers for INCIDENTE_LIQUIDACION - auto-update valor_incidentes
            ("Create triggers for auto-update valor_incidentes", """
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
            """),
        ]
        
        # Ejecutar migraciones
        successful = 0
        failed = 0
        
        for name, sql in migrations:
            try:
                cursor.execute(sql)
                logger.info(f"✓ {name}")
                successful += 1
            except Exception as e:
                logger.error(f"✗ {name}: {e}")
                failed += 1
        
        # Verificar estado final
        logger.info("\n--- Verificación de Estado ---")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('plan_pago_incidente','cuota_incidente','incidente_liquidacion','bloqueos_edicion')
            ORDER BY table_name
        """)
        tables = [r[0] for r in cursor.fetchall()]
        logger.info(f"Tablas nuevas: {tables}")
        
        # Verificar columnas
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='incidentes' AND column_name='estado_pago'")
        col = cursor.fetchone()
        logger.info(f"Columna estado_pago: {'EXISTS' if col else 'MISSING'}")
        
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='liquidaciones' AND column_name='valor_incidentes'")
        col = cursor.fetchone()
        logger.info(f"Columna valor_incidentes: {'EXISTS' if col else 'MISSING'}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n--- Resumen ---")
        logger.info(f"Migraciones exitosas: {successful}")
        logger.info(f"Migraciones fallidas: {failed}")
        
        return failed == 0
        
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

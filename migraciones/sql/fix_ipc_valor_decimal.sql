-- ============================================================
-- Migración: fix_ipc_valor_decimal.sql
-- Descripción: Cambia la columna VALOR_IPC de INTEGER a REAL
--              para soportar porcentajes con decimales (ej. 5.1%)
-- Fecha: 2026-02-24
-- ============================================================

-- ── PostgreSQL (Railway) ──────────────────────────────────
-- Eliminar el CHECK constraint antiguo y cambiar el tipo de columna.
-- En PostgreSQL no se puede alterar tipo directamente si hay constraints dependientes,
-- por lo que se crea una columna temporal, se migra el dato, y se renombra.

-- Paso 1: Agregar columna temporal con tipo correcto
ALTER TABLE IPC ADD COLUMN VALOR_IPC_NEW NUMERIC(8,4);

-- Paso 2: Copiar datos existentes (la conversión de INTEGER a NUMERIC es segura)
UPDATE IPC SET VALOR_IPC_NEW = VALOR_IPC::NUMERIC;

-- Paso 3: Eliminar columna antigua (con su CHECK constraint)
ALTER TABLE IPC DROP COLUMN VALOR_IPC;

-- Paso 4: Renombrar columna nueva
ALTER TABLE IPC RENAME COLUMN VALOR_IPC_NEW TO VALOR_IPC;

-- Paso 5: Agregar NOT NULL y CHECK constraint equivalente
ALTER TABLE IPC ALTER COLUMN VALOR_IPC SET NOT NULL;
ALTER TABLE IPC ADD CONSTRAINT chk_ipc_valor 
    CHECK (VALOR_IPC >= 0 AND VALOR_IPC <= 10000);

-- ── Verificación ──────────────────────────────────────────
SELECT column_name, data_type, numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_name = 'ipc' AND column_name = 'valor_ipc';

-- Migración: Agregar columna VALOR_INCIDENTES a tabla LIQUIDACIONES
-- Feature: 003-integracion-incidentes-liquidaciones
-- Date: 2026-07-03

-- Verificar si la columna ya existe antes de agregarla
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'liquidaciones' 
        AND column_name = 'valor_incidentes'
    ) THEN
        ALTER TABLE LIQUIDACIONES ADD COLUMN VALOR_INCIDENTES INTEGER DEFAULT 0;
        
        -- Crear índice para búsquedas frecuentes
        CREATE INDEX idx_liquidaciones_valor_incidentes ON LIQUIDACIONES(VALOR_INCIDENTES) WHERE VALOR_INCIDENTES > 0;
        
        RAISE NOTICE 'Columna VALOR_INCIDENTES agregada exitosamente';
    ELSE
        RAISE NOTICE 'La columna VALOR_INCIDENTES ya existe';
    END IF;
END $$;

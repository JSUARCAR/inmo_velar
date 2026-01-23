-- ==================================================================================
-- MIGRACIÓN: Agregar soporte para múltiples contratos por liquidación
-- Fecha: 2025-12-26
-- Descripción: Permite que una liquidación de asesor incluya múltiples contratos
--              de arrendamiento activos, reflejando cómo se liquida en la práctica.
-- ==================================================================================

-- PASO 1: Crear tabla intermedia para relacionar liquidaciones con contratos
-- ==================================================================================

CREATE TABLE IF NOT EXISTS LIQUIDACIONES_CONTRATOS (
    ID_LIQUIDACION_CONTRATO INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Referencias
    ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
    ID_CONTRATO_A INTEGER NOT NULL,
    
    -- Canon incluido en esta liquidación para este contrato
    CANON_INCLUIDO INTEGER NOT NULL DEFAULT 0,
    
    -- Auditoría
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now')),
    CREATED_BY TEXT,
    
    -- Constraints
    CHECK(CANON_INCLUIDO >= 0),
    UNIQUE(ID_LIQUIDACION_ASESOR, ID_CONTRATO_A),
    
    -- Foreign Keys
    FOREIGN KEY (ID_LIQUIDACION_ASESOR) REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR) ON DELETE CASCADE,
    FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_liq_contratos_liquidacion ON LIQUIDACIONES_CONTRATOS(ID_LIQUIDACION_ASESOR);
CREATE INDEX IF NOT EXISTS idx_liq_contratos_contrato ON LIQUIDACIONES_CONTRATOS(ID_CONTRATO_A);


-- PASO 2: Migrar datos existentes (si hay liquidaciones previas)
-- ==================================================================================
-- Si existen liquidaciones con ID_CONTRATO_A, crearemos registros en la tabla intermedia

INSERT INTO LIQUIDACIONES_CONTRATOS (
    ID_LIQUIDACION_ASESOR,
    ID_CONTRATO_A,
    CANON_INCLUIDO,
    CREATED_AT,
    CREATED_BY
)
SELECT 
    ID_LIQUIDACION_ASESOR,
    ID_CONTRATO_A,
    CANON_ARRENDAMIENTO_LIQUIDADO,
    CREATED_AT,
    CREATED_BY
FROM LIQUIDACIONES_ASESORES
WHERE ID_CONTRATO_A IS NOT NULL;


-- ==================================================================================
-- PASO 3: Modificar tabla LIQUIDACIONES_ASESORES
-- ==================================================================================
-- SQLite no soporta DROP CONSTRAINT, así que recreamos la tabla
-- IMPORTANTE: Hacemos esto ANTES de insertar en LIQUIDACIONES_CONTRATOS para evitar FK errors

-- 3.1 Crear tabla temporal con la nueva estructura
CREATE TABLE IF NOT EXISTS LIQUIDACIONES_ASESORES_NEW (
    ID_LIQUIDACION_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Referencias
    ID_CONTRATO_A INTEGER,  -- Ahora es nullable (legacy field)
    ID_ASESOR INTEGER NOT NULL,
    
    -- Período y Cálculo
    PERIODO_LIQUIDACION TEXT NOT NULL,
    CANON_ARRENDAMIENTO_LIQUIDADO INTEGER NOT NULL DEFAULT 0,
    PORCENTAJE_COMISION INTEGER NOT NULL DEFAULT 0,
    COMISION_BRUTA INTEGER NOT NULL DEFAULT 0,
    TOTAL_DESCUENTOS INTEGER NOT NULL DEFAULT 0,
    VALOR_NETO_ASESOR INTEGER NOT NULL DEFAULT 0,
    
    -- Estado y Flujo
    ESTADO_LIQUIDACION TEXT NOT NULL DEFAULT 'Pendiente',
    FECHA_CREACION TEXT,
    FECHA_APROBACION TEXT,
    USUARIO_CREADOR TEXT,
    USUARIO_APROBADOR TEXT,
    
    -- Observaciones
    OBSERVACIONES_LIQUIDACION TEXT,
    MOTIVO_ANULACION TEXT,
    
    -- Auditoría
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now')),
    CREATED_BY TEXT,
    UPDATED_AT TEXT,
    UPDATED_BY TEXT,
    
    -- Constraints MODIFICADOS:
    -- CAMBIO CRÍTICO: Ahora es UNIQUE por (ID_ASESOR, PERIODO) en lugar de (ID_CONTRATO_A, PERIODO)
    -- Esto permite que un asesor tenga solo UNA liquidación por período
    UNIQUE(ID_ASESOR, PERIODO_LIQUIDACION),
    CHECK(ESTADO_LIQUIDACION IN ('Pendiente', 'Aprobada', 'Pagada', 'Anulada')),
    CHECK(PORCENTAJE_COMISION >= 0 AND PORCENTAJE_COMISION <= 10000),
    CHECK(COMISION_BRUTA >= 0),
    CHECK(TOTAL_DESCUENTOS >= 0),
    
    -- Foreign Keys
    FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A),
    FOREIGN KEY (ID_ASESOR) REFERENCES ASESORES(ID_ASESOR)
);

-- 3.2 Copiar datos de la tabla antigua a la nueva (si existe y tiene datos)
INSERT INTO LIQUIDACIONES_ASESORES_NEW 
SELECT 
    ID_LIQUIDACION_ASESOR,
    ID_CONTRATO_A,
    ID_ASESOR,
    PERIODO_LIQUIDACION,
    CANON_ARRENDAMIENTO_LIQUIDADO,
    PORCENTAJE_COMISION,
    COMISION_BRUTA,
    TOTAL_DESCUENTOS,
    VALOR_NETO_ASESOR,
    ESTADO_LIQUIDACION,
    FECHA_CREACION,
    FECHA_APROBACION,
    USUARIO_CREADOR,
    USUARIO_APROBADOR,
    OBSERVACIONES_LIQUIDACION,
    MOTIVO_ANULACION,
    CREATED_AT,
    CREATED_BY,
    UPDATED_AT,
    UPDATED_BY
FROM LIQUIDACIONES_ASESORES
WHERE EXISTS (SELECT 1 FROM LIQUIDACIONES_ASESORES LIMIT 1);

-- 3.3 Deshabilitar foreign keys temporalmente para poder eliminar tabla
PRAGMA foreign_keys = OFF;

-- 3.4 Eliminar tabla antigua y renombrar
DROP TABLE IF EXISTS LIQUIDACIONES_ASESORES;
ALTER TABLE LIQUIDACIONES_ASESORES_NEW RENAME TO LIQUIDACIONES_ASESORES;

-- 3.5 Reactivar foreign keys
PRAGMA foreign_keys = ON;

-- 3.6 Recrear índices
CREATE INDEX IF NOT EXISTS idx_liquidaciones_asesor ON LIQUIDACIONES_ASESORES(ID_ASESOR);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_contrato ON LIQUIDACIONES_ASESORES(ID_CONTRATO_A);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_periodo ON LIQUIDACIONES_ASESORES(PERIODO_LIQUIDACION);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_estado ON LIQUIDACIONES_ASESORES(ESTADO_LIQUIDACION);


-- ==================================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- ==================================================================================

-- Verificar que la tabla intermedia se creó correctamente
SELECT 'Verificando LIQUIDACIONES_CONTRATOS...' AS verificacion;
SELECT COUNT(*) as total_registros FROM LIQUIDACIONES_CONTRATOS;

-- Verificar que el constraint UNIQUE funciona correctamente
SELECT 'Verificando constraint UNIQUE en LIQUIDACIONES_ASESORES...' AS verificacion;
SELECT ID_ASESOR, PERIODO_LIQUIDACION, COUNT(*) as duplicados
FROM LIQUIDACIONES_ASESORES
GROUP BY ID_ASESOR, PERIODO_LIQUIDACION
HAVING COUNT(*) > 1;
-- Debería retornar 0 filas

-- ==================================================================================
-- MIGRACIÓN COMPLETADA
-- ==================================================================================
-- La estructura ahora soporta:
-- 1. Múltiples contratos por liquidación (tabla LIQUIDACIONES_CONTRATOS)
-- 2. Una sola liquidación por asesor por período (constraint UNIQUE modificado)
-- 3. Trazabilidad completa de qué contratos se incluyeron en cada liquidación
-- ==================================================================================

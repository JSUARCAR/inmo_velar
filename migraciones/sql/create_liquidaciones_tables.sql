-- Script para crear las tablas del Módulo de Liquidaciones de Asesores
-- Ejecutar una vez para inicializar las tablas

-- ==================================================================================
-- TABLA: LIQUIDACIONES_ASESORES
-- Almacena las liquidaciones de comisiones para asesores
-- ==================================================================================

CREATE TABLE IF NOT EXISTS LIQUIDACIONES_ASESORES (
    ID_LIQUIDACION_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Referencias
    ID_CONTRATO_A INTEGER NOT NULL,
    ID_ASESOR INTEGER NOT NULL,
    
    -- Período y Cálculo
    PERIODO_LIQUIDACION TEXT NOT NULL,
    CANON_ARRENDAMIENTO_LIQUIDADO INTEGER NOT NULL DEFAULT 0,
    PORCENTAJE_COMISION INTEGER NOT NULL DEFAULT 0,  -- 0-10000 representa 0.00% - 100.00%
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
    
    -- Constraints
    UNIQUE(ID_CONTRATO_A, PERIODO_LIQUIDACION),
    CHECK(ESTADO_LIQUIDACION IN ('Pendiente', 'Aprobada', 'Pagada', 'Anulada')),
    CHECK(PORCENTAJE_COMISION >= 0 AND PORCENTAJE_COMISION <= 10000),
    CHECK(COMISION_BRUTA >= 0),
    CHECK(TOTAL_DESCUENTOS >= 0),
    
    -- Foreign Keys (sin REFERENCES para evitar foreign key mismatch si las tablas no existen)
    -- La integridad referencial se maneja en la capa de aplicación
    FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A),
    FOREIGN KEY (ID_ASESOR) REFERENCES ASESORES(ID_ASESOR)
);

-- ==================================================================================
-- TABLA: DESCUENTOS_ASESORES
-- Almacena los descuentos aplicados a las liquidaciones de asesores
-- ==================================================================================

CREATE TABLE IF NOT EXISTS DESCUENTOS_ASESORES (
    ID_DESCUENTO_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Referencias
    ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
    
    -- Información del Descuento
    TIPO_DESCUENTO TEXT NOT NULL,  -- Préstamo, Anticipo, Sanción, Ajuste, Otros
    DESCRIPCION_DESCUENTO TEXT NOT NULL,
    VALOR_DESCUENTO INTEGER NOT NULL DEFAULT 0,
    
    -- Auditoría
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now')),
    CREATED_BY TEXT,
    UPDATED_AT TEXT,
    UPDATED_BY TEXT,
    
    -- Constraints
    CHECK(TIPO_DESCUENTO IN ('Préstamo', 'Anticipo', 'Sanción', 'Ajuste', 'Otros')),
    CHECK(VALOR_DESCUENTO >= 0),
    
    -- Foreign Keys
    FOREIGN KEY (ID_LIQUIDACION_ASESOR) REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR) ON DELETE CASCADE
);

-- ==================================================================================
-- TABLA: PAGOS_ASESORES
-- Almacena los pagos realizados a asesores
-- ==================================================================================

CREATE TABLE IF NOT EXISTS PAGOS_ASESORES (
    ID_PAGO_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Referencias
    ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
    
    -- Información del Pago
    FECHA_PROGRAMADA TEXT NOT NULL,
    FECHA_PAGO_REAL TEXT,
    METODO_PAGO TEXT,  -- Transferencia, Cheque, Efectivo, Consignación
    REFERENCIA_PAGO TEXT,
    VALOR_PAGO INTEGER NOT NULL DEFAULT 0,
    ESTADO_PAGO TEXT NOT NULL DEFAULT 'Programado',  -- Programado, Pagado, Rechazado
    
    -- Observaciones
    OBSERVACIONES_PAGO TEXT,
    
    -- Auditoría
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now')),
    CREATED_BY TEXT,
    UPDATED_AT TEXT,
    UPDATED_BY TEXT,
    
    -- Constraints
    CHECK(ESTADO_PAGO IN ('Programado', 'Pagado', 'Rechazado')),
    CHECK(VALOR_PAGO >= 0),
    
    -- Foreign Keys
    FOREIGN KEY (ID_LIQUIDACION_ASESOR) REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR) ON DELETE CASCADE
);

-- ==================================================================================
-- ÍNDICES para mejorar rendimiento
-- ==================================================================================

CREATE INDEX IF NOT EXISTS idx_liquidaciones_asesor ON LIQUIDACIONES_ASESORES(ID_ASESOR);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_contrato ON LIQUIDACIONES_ASESORES(ID_CONTRATO_A);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_periodo ON LIQUIDACIONES_ASESORES(PERIODO_LIQUIDACION);
CREATE INDEX IF NOT EXISTS idx_liquidaciones_estado ON LIQUIDACIONES_ASESORES(ESTADO_LIQUIDACION);
CREATE INDEX IF NOT EXISTS idx_descuentos_liquidacion ON DESCUENTOS_ASESORES(ID_LIQUIDACION_ASESOR);
CREATE INDEX IF NOT EXISTS idx_pagos_liquidacion ON PAGOS_ASESORES(ID_LIQUIDACION_ASESOR);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON PAGOS_ASESORES(ESTADO_PAGO);

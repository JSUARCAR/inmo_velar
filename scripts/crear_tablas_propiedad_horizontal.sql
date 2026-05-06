-- ============================================================================
-- Migration: Crear tablas Propiedad Horizontal
-- Fecha: 2026-04-09
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Tabla: ASAMBLEAS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ASAMBLEAS (
    id_asistencia SERIAL PRIMARY KEY,
    id_propiedad INTEGER NOT NULL REFERENCES PROPIEDADES(ID_PROPIEDAD),
    fecha_asistencia DATE NOT NULL,
    hora_asistencia TIME NOT NULL,
    tipo_reunion VARCHAR(30) NOT NULL CHECK (tipo_reunion IN ('Ordinaria', 'Extraordinaria', 'SegundaConvocatoria')),
    tipo_asistente VARCHAR(20) NOT NULL CHECK (tipo_asistente IN ('Propietario', 'Inmobiliaria')),
    costo_asistente DECIMAL(12,2) NOT NULL DEFAULT 0,
    id_asistente_persona INTEGER REFERENCES PERSONAS(ID_PERSONA),
    direccion_asistencia VARCHAR(255) NOT NULL,
    estado_asistencia VARCHAR(20) DEFAULT 'Programada' CHECK (estado_asistencia IN ('Programada', 'Realizada', 'Cancelada')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT uq_asistencia_propiedad_fecha UNIQUE (id_propiedad, fecha_asistencia)
);

CREATE INDEX IF NOT EXISTS idx_asambleas_id_propiedad ON ASAMBLEAS(id_propiedad);
CREATE INDEX IF NOT EXISTS idx_asambleas_fecha ON ASAMBLEAS(fecha_asistencia);
CREATE INDEX IF NOT EXISTS idx_asambleas_estado ON ASAMBLEAS(estado_asistencia);

-- ----------------------------------------------------------------------------
-- Tabla: PAGOS_ADMINISTRACION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS PAGOS_ADMINISTRACION (
    id_pago_admin SERIAL PRIMARY KEY,
    id_propiedad INTEGER NOT NULL REFERENCES PROPIEDADES(ID_PROPIEDAD),
    nombre_propietario VARCHAR(255) NOT NULL,
    direccion_propiedad VARCHAR(255) NOT NULL,
    valor_administracion DECIMAL(12,2) NOT NULL,
    fecha_pago INTEGER NOT NULL DEFAULT 1,
    link_pago VARCHAR(500),
    periodo_pago VARCHAR(7) NOT NULL,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado_pago IN ('Pendiente', 'Pagado', 'Vencido')),
    fecha_generacion TIMESTAMP DEFAULT NOW(),
    fecha_pago_real TIMESTAMP,
    CONSTRAINT uq_pago_admin_propiedad_periodo UNIQUE (id_propiedad, periodo_pago)
);

CREATE INDEX IF NOT EXISTS idx_pagos_admin_id_propiedad ON PAGOS_ADMINISTRACION(id_propiedad);
CREATE INDEX IF NOT EXISTS idx_pagos_admin_periodo ON PAGOS_ADMINISTRACION(periodo_pago);
CREATE INDEX IF NOT EXISTS idx_pagos_admin_estado ON PAGOS_ADMINISTRACION(estado_pago);

-- ============================================================================
-- Fin Migration
-- ============================================================================
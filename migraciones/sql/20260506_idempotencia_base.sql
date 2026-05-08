-- ============================================================================
-- SCRIPT: Implementación de Infraestructura para Idempotencia
-- Fecha: 2026-05-06
-- ============================================================================

-- Tabla central de idempotencia (Nativa PostgreSQL)
-- Almacena el resultado de operaciones para evitar ejecuciones duplicadas.
CREATE TABLE IF NOT EXISTS IDEMPOTENCY_KEYS (
    ID_KEY SERIAL PRIMARY KEY,
    KEY VARCHAR(64) UNIQUE NOT NULL,          -- SHA256 del payload/contexto
    OPERACION VARCHAR(100) NOT NULL,          -- Nombre del servicio/metodo
    PARAMETROS JSONB,                         -- Argumentos de la llamada
    RESULTADO JSONB,                          -- Respuesta exitosa cacheada
    USUARIO_ID INTEGER NOT NULL,              -- Usuario que originó la petición
    FECHA_CREACION TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FECHA_EXPIRA TIMESTAMP WITH TIME ZONE NOT NULL, -- TTL para limpieza
    ESTADO VARCHAR(20) DEFAULT 'completed',   -- completed|failed|processing
    INTENTOS INTEGER DEFAULT 0,               -- Tracking de reintentos
    CONSTRAINT fk_idempotency_usuario FOREIGN KEY (USUARIO_ID) 
        REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE
);

-- Índices críticos para rendimiento y mantenimiento
CREATE INDEX IF NOT EXISTS idx_idempotency_key ON IDEMPOTENCY_KEYS(KEY);
CREATE INDEX IF NOT EXISTS idx_idempotency_expira ON IDEMPOTENCY_KEYS(FECHA_EXPIRA);
CREATE INDEX IF NOT EXISTS idx_idempotency_usuario ON IDEMPOTENCY_KEYS(USUARIO_ID);

-- Tabla para tracking de eventos (Event Sourcing ligero)
-- Proporciona una auditoría inmutable de cambios de estado.
CREATE TABLE IF NOT EXISTS EVENTOS_IDEMPOTENCIA (
    ID_EVENTO SERIAL PRIMARY KEY,
    ENTIDAD_TIPO VARCHAR(50) NOT NULL,        -- Ej: "Recaudo", "Liquidacion"
    ENTIDAD_ID INTEGER NOT NULL,              -- ID de la entidad afectada
    TIPO_EVENTO VARCHAR(50) NOT NULL,         -- Ej: "CREATED", "UPDATED"
    IDEMPOTENCY_KEY VARCHAR(64) NOT NULL,     -- Enlace a la petición original
    PAYLOAD JSONB NOT NULL,                   -- Estado completo del evento
    METADATA JSONB,                           -- IP, User-Agent, etc.
    FECHA_EVENTO TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    USUARIO_ID INTEGER NOT NULL,              -- Actor del evento
    CONSTRAINT fk_evento_usuario FOREIGN KEY (USUARIO_ID) 
        REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE,
    CONSTRAINT fk_evento_idempotency FOREIGN KEY (IDEMPOTENCY_KEY)
        REFERENCES IDEMPOTENCY_KEYS(KEY) ON DELETE CASCADE,
    UNIQUE(ENTIDAD_TIPO, ENTIDAD_ID, TIPO_EVENTO)
);

-- Índices para EVENTOS_IDEMPOTENCIA
CREATE INDEX IF NOT EXISTS idx_eventos_entidad ON EVENTOS_IDEMPOTENCIA(ENTIDAD_TIPO, ENTIDAD_ID);
CREATE INDEX IF NOT EXISTS idx_eventos_key ON EVENTOS_IDEMPOTENCIA(IDEMPOTENCY_KEY);

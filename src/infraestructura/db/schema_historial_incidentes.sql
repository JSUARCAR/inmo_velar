-- HISTORIAL_INCIDENTES
-- Tabla para registrar el historial de cambios de estado de los incidentes
-- Permite auditoría completa y trazabilidad de operaciones

CREATE TABLE IF NOT EXISTS HISTORIAL_INCIDENTES (
    ID_HISTORIAL INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_INCIDENTE INTEGER NOT NULL,
    ESTADO_ANTERIOR TEXT,
    ESTADO_NUEVO TEXT NOT NULL,
    FECHA_CAMBIO TEXT DEFAULT (datetime('now', 'localtime')),
    USUARIO TEXT NOT NULL,
    COMENTARIO TEXT,
    TIPO_ACCION TEXT DEFAULT 'CAMBIO_ESTADO' CHECK(TIPO_ACCION IN (
        'CREACION',
        'CAMBIO_ESTADO', 
        'COTIZACION_AGREGADA',
        'COTIZACION_APROBADA',
        'COTIZACION_RECHAZADA',
        'ASIGNACION_PROVEEDOR',
        'MODIFICACION_COSTO',
        'CANCELACION'
    )),
    DATOS_ADICIONALES TEXT, -- JSON para datos extra como id_cotizacion, costo anterior, etc.
    CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE)
);

-- Índice para consultas rápidas por incidente
CREATE INDEX IF NOT EXISTS idx_historial_incidente ON HISTORIAL_INCIDENTES(ID_INCIDENTE);

-- Índice para consultas por fecha
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON HISTORIAL_INCIDENTES(FECHA_CAMBIO);

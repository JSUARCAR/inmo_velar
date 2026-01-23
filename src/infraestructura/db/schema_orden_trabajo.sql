CREATE TABLE IF NOT EXISTS ORDENES_TRABAJO (
    id_orden SERIAL PRIMARY KEY,
    id_incidente INTEGER NOT NULL,
    id_proveedor INTEGER NOT NULL,
    fecha_creacion TEXT NOT NULL,
    fecha_inicio_estimada TEXT,
    fecha_fin_estimada TEXT,
    estado TEXT DEFAULT 'Pendiente', 
    costo_mano_obra INTEGER DEFAULT 0,
    costo_materiales INTEGER DEFAULT 0,
    descripcion_trabajo TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_incidente) REFERENCES INCIDENTES(id_incidente),
    FOREIGN KEY (id_proveedor) REFERENCES PROVEEDORES(id_proveedor)
);

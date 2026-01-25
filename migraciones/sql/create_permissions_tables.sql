-- ============================================================================
-- SCRIPT FINAL: Creación de Tablas de Permisos
-- ============================================================================
-- INSTRUCCIONES: 
-- 1. Abrir pgAdmin 4
-- 2. Conectarse a la base de datos 'db_inmo_velar'
-- 3. Click derecho en la base de datos → Query Tool
-- 4. Copiar y pegar TODO este script
-- 5. Presionar F5 o click en el botón "Execute"
-- ============================================================================

-- Crear tabla PERMISOS
CREATE TABLE IF NOT EXISTS PERMISOS (
    ID_PERMISO SERIAL PRIMARY KEY,
    MODULO VARCHAR(100) NOT NULL,
    RUTA VARCHAR(200) NOT NULL,
    ACCION VARCHAR(20) NOT NULL,
    DESCRIPCION TEXT,
    CATEGORIA VARCHAR(50),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uk_permisos_modulo_accion UNIQUE(MODULO, ACCION)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_permisos_modulo ON PERMISOS(MODULO);
CREATE INDEX IF NOT EXISTS idx_permisos_ruta ON PERMISOS(RUTA);
CREATE INDEX IF NOT EXISTS idx_permisos_categoria ON PERMISOS(CATEGORIA);

-- Crear tabla ROL_PERMISOS
CREATE TABLE IF NOT EXISTS ROL_PERMISOS (
    ID_ROL_PERMISO SERIAL PRIMARY KEY,
    ROL VARCHAR(50) NOT NULL,
    ID_PERMISO INTEGER NOT NULL,
    ACTIVO BOOLEAN DEFAULT TRUE,
    CREATED_BY VARCHAR(100),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    UPDATED_BY VARCHAR(100),
    UPDATED_AT TIMESTAMP,
    CONSTRAINT fk_rol_permisos_permiso FOREIGN KEY (ID_PERMISO) 
        REFERENCES PERMISOS(ID_PERMISO) ON DELETE CASCADE,
    CONSTRAINT uk_rol_permisos_rol_permiso UNIQUE(ROL, ID_PERMISO)
);

-- Índices para ROL_PERMISOS
CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol ON ROL_PERMISOS(ROL);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_activo ON ROL_PERMISOS(ROL, ACTIVO);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_permiso ON ROL_PERMISOS(ID_PERMISO);

-- Otorgar permisos al usuario de la aplicación
DO $$
BEGIN
    -- Verificar si el usuario existe antes de otorgar permisos
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'inmo_user') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON PERMISOS TO inmo_user;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ROL_PERMISOS TO inmo_user;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO inmo_user;
        RAISE NOTICE 'Permisos otorgados a inmo_user correctamente';
    ELSE
        RAISE NOTICE 'Usuario inmo_user no existe, saltando permisos';
    END IF;
END $$;

-- Verificar que las tablas se crearon correctamente
DO $$
DECLARE
    tabla_permisos_existe BOOLEAN;
    tabla_rol_permisos_existe BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'permisos'
    ) INTO tabla_permisos_existe;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'rol_permisos'
    ) INTO tabla_rol_permisos_existe;
    
    IF tabla_permisos_existe AND tabla_rol_permisos_existe THEN
        RAISE NOTICE '✅ ¡ÉXITO! Tablas PERMISOS y ROL_PERMISOS creadas correctamente';
    ELSE
        RAISE WARNING '❌ ERROR: Alguna tabla no se creó correctamente';
    END IF;
END $$;

-- ============================================================================
-- FIN DEL SCRIPT
--  Esperado al ejecutar: "✅ ¡ÉXITO! Tablas PERMISOS y ROL_PERMISOS creadas correctamente"
-- ============================================================================

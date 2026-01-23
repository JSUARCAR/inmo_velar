-- Agregar columnas para almacenar logo de la empresa
ALTER TABLE configuracion_sistema 
ADD COLUMN IF NOT EXISTS logo_base64 TEXT,
ADD COLUMN IF NOT EXISTS logo_filename TEXT;

-- Comentarios para documentación
COMMENT ON COLUMN configuracion_sistema.logo_base64 IS 'Logo de la empresa codificado en Base64';
COMMENT ON COLUMN configuracion_sistema.logo_filename IS 'Nombre original del archivo del logo';

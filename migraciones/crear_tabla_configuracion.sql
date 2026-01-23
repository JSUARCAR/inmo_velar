-- Crear tabla de configuración del sistema si no existe
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id SERIAL PRIMARY KEY,
    nombre_empresa TEXT,
    nit TEXT,
    email TEXT,
    telefono TEXT,
    direccion TEXT,
    ubicacion TEXT,
    website TEXT,
    redes_sociales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar registro por defecto si no existe (ID = 1)
INSERT INTO configuracion_sistema (
    id, 
    nombre_empresa, 
    nit, 
    email, 
    telefono, 
    direccion, 
    ubicacion, 
    website, 
    redes_sociales
) 
SELECT 
    1, 
    'Inmobiliaria Velar', 
    '900.000.000-1', 
    'contacto@inmobiliariavelar.com', 
    '300 123 4567', 
    'Calle 123 # 45-67', 
    'Bogotá, Colombia', 
    'www.inmobiliariavelar.com', 
    '{}'
WHERE NOT EXISTS (SELECT 1 FROM configuracion_sistema WHERE id = 1);

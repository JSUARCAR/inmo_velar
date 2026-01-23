ALTER TABLE configuracion_sistema
ADD COLUMN IF NOT EXISTS representante_legal TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS cedula_representante TEXT DEFAULT '';

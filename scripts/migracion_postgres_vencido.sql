-- =============================================================================
-- Script de Migración PostgreSQL: Agregar estado VENCIDO a tabla RECAUDOS
-- =============================================================================
-- Este script debe ejecutarse en la base de datos PostgreSQL de producción
-- (Railway: hopper.proxy.rlwy.net:12937/railway)
--
-- Efecto: Agrega el estado 'Vencido' al CHECK constraint de ESTADO_RECAUDO
--         permitiendo que los recaudos generados masivamente se marquen como
--         vencidos cuando la fecha de pago calculada es anterior a la fecha actual.
--
-- Ejecución: psql -U postgres -d railway -f migracion_postgres_vencido.sql
-- =============================================================================

-- Verificar estado actual de la tabla
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'recaudos' AND column_name = 'estado_recaudo';

-- Verificar constraint actual
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint 
WHERE conname LIKE '%estado%recaudo%';

-- Eliminar constraint antiguo y crear nuevo
ALTER TABLE recaudos 
DROP CONSTRAINT IF EXISTS estado_recaudo_check;

ALTER TABLE recaudos 
ADD CONSTRAINT estado_recaudo_check 
CHECK (estado_recaudo IN ('Pendiente', 'Aplicado', 'Reversado', 'Vencido'));

-- Verificar nuevo constraint
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint 
WHERE conname = 'estado_recaudo_check';

-- Verificar que la tabla permite el nuevo estado (test)
-- INSERT INTO recaudos (id_contrato_a, fecha_pago, valor_total, metodo_pago, estado_recaudo, created_by)
-- VALUES (1, '2026-04-01', 1500000, 'Efectivo', 'Vencido', 'test');

-- Verificar estados disponibles
SELECT DISTINCT estado_recaudo FROM recaudos;

-- Resultado esperado: Pendiente, Aplicado, Reversado, Vencido
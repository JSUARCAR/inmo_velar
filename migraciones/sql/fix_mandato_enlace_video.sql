-- Migración para auditar y marcar contratos de mandato afectados por el bug de pérdida de datos
-- Bug: El campo ENLACE_VIDEO se perdía al hacer UPDATE en el repositorio de Mandato.
-- Fecha: 2026-07-21

-- Opción 1: Identificar contratos sospechosos (tienen ENLACE_VIDEO NULL pero fueron actualizados recientemente)
-- Esto permite a los administradores revisarlos manualmente.
SELECT ID_CONTRATO_M, ID_PROPIEDAD, ESTADO_CONTRATO_M, UPDATED_AT
FROM CONTRATOS_MANDATOS
WHERE ENLACE_VIDEO IS NULL
  AND UPDATED_AT IS NOT NULL
ORDER BY UPDATED_AT DESC;

-- Nota: Como los datos se sobrescribieron con NULL (o no se incluyeron en el SET y luego se perdió referencia al guardarse y leerse), 
-- la recuperación real del enlace de video requerirá que los administradores busquen los videos en su plataforma
-- de almacenamiento e ingresen los links manualmente usando la interfaz de la aplicación,
-- la cual ahora persistirá el dato correctamente gracias al fix en el repositorio.

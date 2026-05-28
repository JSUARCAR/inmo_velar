-- 006_unificar_vistas_dashboard.sql
-- Eliminamos las vistas materializadas a nivel de base de datos ya que ahora se manejarán
-- mediante consultas inline (CTEs) en el repositorio para soportar bifurcación PG/SQLite sin DDL divergente.

DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS;
DROP VIEW IF EXISTS VW_ALERTA_MORA_DIARIA;

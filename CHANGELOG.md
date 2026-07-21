# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-07-21

### Fixed
- Fixed bug in `repositorio_contrato_mandato_postgres.py` where `ENLACE_VIDEO` was lost upon `UPDATE`.
- Fixed missing case-insensitive fallback logic for `consignatario`, `documento_consignatario`, and `enlace_video` in Mandato's `_row_to_entity()`.
- Fixed missing case-insensitive fallback logic for `enlace_video` in Arrendamiento's `_row_to_entity()`.

### Added
- Added migration script `migraciones/sql/fix_mandato_enlace_video.sql` to identify `ContratoMandato` records that might have lost their `ENLACE_VIDEO` data due to the persistence bug, allowing administrators to manually restore the links.
- Added comprehensive integration tests in `tests/integration/test_servicios_aplicacion/test_persistencia_contratos.py` to ensure `Create/Read/Update` lifecycle of `Mandato` and `Arrendamiento` persists all required fields correctly to PostgreSQL.

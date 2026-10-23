# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-10-22

### Seguridad (spec 080)
- Lock de dependencias con hashes: `requirements.in` / `requirements-dev.in` (editables) y `requirements.txt` / `requirements-dev.txt` (generados con `uv pip compile --generate-hashes --python-version 3.11`).
- `pip-audit --require-hashes` sin vulnerabilidades conocidas en ambos locks (starlette 1.9.0, pillow 13.0.0, python-multipart 0.0.32).
- Reflex fijo en `0.8.28`; `sqlalchemy<2.1` fijado (SQLAlchemy 2.1 ya no instala `greenlet`).
- Se excluyen de producción `gunicorn` y `pyautogui`; las herramientas de desarrollo pasan a `requirements-dev.in`.

### Cambiado
- `Dockerfile` y `build-validate.yml` instalan con `--require-hashes`.

### Añadido
- Workflow `pip-audit.yml` (push/PR a `main` y diario `0 12 * * *`) y `.github/dependabot.yml` (pip, docker, github-actions; ignora minor/major de `reflex`).
- `DEPENDENCIAS.md`, ADR `docs/decisions/080-lock-dependencias-hashes-prod-dev.md` y `scripts/diagnostico/prueba_humo_dependencias.py`.

## [Unreleased] - 2026-07-21

### Fixed
- Fixed bug in `repositorio_contrato_mandato_postgres.py` where `ENLACE_VIDEO` was lost upon `UPDATE`.
- Fixed missing case-insensitive fallback logic for `consignatario`, `documento_consignatario`, and `enlace_video` in Mandato's `_row_to_entity()`.
- Fixed missing case-insensitive fallback logic for `enlace_video` in Arrendamiento's `_row_to_entity()`.

### Added
- Added migration script `migraciones/sql/fix_mandato_enlace_video.sql` to identify `ContratoMandato` records that might have lost their `ENLACE_VIDEO` data due to the persistence bug, allowing administrators to manually restore the links.
- Added comprehensive integration tests in `tests/integration/test_servicios_aplicacion/test_persistencia_contratos.py` to ensure `Create/Read/Update` lifecycle of `Mandato` and `Arrendamiento` persists all required fields correctly to PostgreSQL.

# Implementation Plan: Remediación de Credenciales Hardcodeadas y Datos Sensibles Expuestos

**Branch**: `074-remediacion-secretos-hardcodeados` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/074-remediacion-secretos-hardcodeados/spec.md`

## Summary

Remediar por completo la exposición detectada en la auditoría (`AUDIT_SECRETS_CREDENCIALES_HARDCODEADAS.md`): (1) rotación coordinada de las tres credenciales comprometidas (cuenta administradora, base de datos de producción y cuenta de prueba); (2) eliminación de todo fallback inseguro y par usuario/contraseña de archivos versionados (código, pruebas, scripts y documentación); (3) purga del historial con `git-filter-repo`; (4) retiro de 19 artefactos con PII y endurecimiento de `.gitignore`; (5) escaneo Gitleaks fail-closed con reglas generalizadas versionadas y denylista exacta inyectada desde configuración protegida (nunca versionada); (6) inventario enmascarado versionado como evidencia verificable.

Enfoque técnico: endurecer la capa de configuración siguiendo el patrón existente de `Settings` (pydantic-settings con validador que aborta el arranque) y `rxconfig.py`; sustituir el `gitleaks.toml` local (no versionado y con literales) por un `.gitleaks.toml` versionado de reglas generalizadas; inyectar la denylista exacta mediante `GITLEAKS_CONFIG`/`GITLEAKS_CONFIG_TOML` compuesto en `$RUNNER_TEMP`; exigir el job `security-scan` como check requerido de rama.

## Technical Context

**Language/Version**: Python 3.11 (`runtime.txt`); PowerShell 7 para automatización local (win32); Node.js solo para `test_login_visible.mjs`

**Primary Dependencies**: Reflex ≥ 0.6, pydantic ≥ 2.5 / pydantic-settings ≥ 2.1, psycopg2-binary, python-dotenv; CI: GitHub Actions + `gitleaks/gitleaks-action@v2`; purga: `git-filter-repo`; pruebas: pytest/pytest-cov + Playwright

**Storage**: PostgreSQL en Railway (vía `DATABASE_URL`); artefactos SQLite heredados solo como objeto de purga; sin nuevos almacenes

**Testing**: pytest (unitario/integración) y Playwright (e2e); verificación adicional por `git grep`, `git log` y `gitleaks git`

**Target Platform**: CI `ubuntu-latest`; producción Railway (Dockerfile); desarrollo local Windows + PowerShell 7

**Project Type**: Aplicación web full-stack (Reflex) con cambios de configuración, CI y limpieza de repositorio

**Performance Goals**: N/A (iniciativa de seguridad); escaneo de CI completo en < 5 minutos con `fetch-depth: 0`

**Constraints**: prohibido todo valor literal comprometido en archivos versionados; bloqueo fail-closed sin excepciones; 100% español; reescritura de historial destructiva con ventana coordinada y respaldo espejo; el check de rama debe impedir fusiones

**Scale/Scope**: 2037 archivos trackeados; 32 con fallback de contraseña de BD; 10 con credencial de administrador; ~12 con credencial de prueba; 45 scripts de diagnóstico trackeados; 19 artefactos PII; 2 workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate (Constitución) | Estado | Evidencia |
|---|---|---|
| §4 Zero Leak (protección de credenciales, higiene de raíz) | ✅ PASA | La iniciativa es la remediación completa; el diseño evita reversionar literales |
| §1 Idioma 100% español | ✅ PASA | Artefactos, mensajes y evidencia en español |
| §2 Arquitectura limpia (capas, sin SQLite nuevo) | ✅ PASA | Cambios en configuración/CI/scripts; sin tocar dominio ni introducir SQLite |
| §5 Calidad y pruebas | ✅ PASA | Validadores y contratos cubiertos con pytest; gates pre-commit existentes |
| §6 Ramas y commits convencionales | ✅ PASA | Rama de feature + commits `fix(security)` / `chore(security)` |
| §14 SDD / Source-driven | ✅ PASA | `research.md` con decisiones y fuentes oficiales citadas |
| §15 ADR de decisiones relevantes | ✅ PASA | Se registra ADR de estrategia de escaneo con denylista protegida |

**Re-check post-diseño (Phase 1)**: ✅ Sin cambios; los contratos y el modelo de datos no introducen violaciones.

Sin violaciones → tabla de Complejidad vacía.

## Project Structure

### Documentation (this feature)

```text
specs/074-remediacion-secretos-hardcodeados/
├── plan.md              # Este archivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── escaneo-seguridad.md
│   ├── configuracion-credenciales.md
│   └── inventario-hallazgos.md
├── checklists/
│   ├── requirements.md
│   └── security.md
└── tasks.md             # Fase 2 (/speckit.tasks - NO creado aquí)
```

### Source Code (repository root)

```text
.github/workflows/security-scan.yml            # Gate: config inyectada + check requerido
.github/workflows/build-validate.yml           # Existente (sin cambios)
.gitleaks.toml                                 # NUEVO: reglas generalizadas versionadas (sin literales)
.gitignore                                     # Patrones explícitos para PII y artefactos
assets/exports/                                # RETIRAR del tracking (CSV con PII)
assets/pdfs/                                   # RETIRAR del tracking (contratos/estados/liquidaciones)
config/shared_db_config.py                     # Eliminar fallback de password
rxconfig.py                                    # Endurecer: sin password embebida; fail-fast
src/infraestructura/configuracion/settings.py  # Validadores fail-fast de credenciales
migraciones/**                                 # Eliminar literales y documentación expuesta
scripts/**                                     # Eliminar fallbacks en scripts operativos
scripts/diagnostico/**                         # Retirar/parametrizar (45 trackeados)
tests/**                                       # Credenciales solo por entorno
playwright_test.py · test_login_visible.mjs    # Parametrizar o retirar
docs/security/INVENTARIO_REMEDIACION_074.md    # NUEVO: inventario enmascarado + evidencia
docs/decisions/ADR-074-estrategia-escaneo.md   # NUEVO: ADR de la estrategia de escaneo
```

**Structure Decision**: Proyecto único (aplicación Reflex) con cambios transversales de repositorio; no se crean módulos de dominio. La lógica nueva de validación permanece en `src/infraestructura/configuracion/`; la evidencia en `docs/security/`; la configuración del gate en `.github/`. El repositorio opera hoy sobre `main`; antes de ejecutar tareas se recomienda crear la rama de feature (Constitución §6) para aislar la reescritura de historial.

## Complexity Tracking

> **Sin violaciones constitucionales que justificar.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

# Implementation Plan: 066-security-hardening-remediation

**Branch**: `security/066-security-hardening-remediation` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/066-security-hardening-remediation/spec.md`

## Summary

Remediación integral de seguridad de 20 hallazgos (4 críticos), incluyendo rotación inmediata y ocultamiento de credenciales expuestas (Railway PostgreSQL), protección contra IDOR en 4 endpoints de la API de documentos de Reflex/FastAPI, purga de secretos del historial Git y fortalecimiento de la infraestructura en Caddy. Se implementará un enfoque fail-fast para la configuración, rate limiting vía caddy-ratelimit y expiración estricta de sesiones.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Reflex, FastAPI, Pydantic v2, pydantic-settings, Bcrypt

**Storage**: PostgreSQL (Railway)

**Testing**: Pytest

**Target Platform**: Linux server (Docker en Railway)

**Project Type**: Web application (Reflex backend + frontend, sub-apps FastAPI)

**Performance Goals**: N/A (enfocado en seguridad, rate limiting no bloqueante en Python)

**Constraints**: Railway enviroment, no external cache (Redis) available (rate limiting en proxy Caddy)

**Scale/Scope**: Crítico - afecta protección de datos (Ley 1581/2012), remediación obligatoria.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Zero Leak (Secrets)**: PASSED - El plan prioriza mover credenciales a variables de entorno, implementar `pydantic-settings` con fail-fast y purgar explícitamente el historial Git.
- **Fail-Fast (PostgreSQL)**: PASSED - Se validarán la conexión de base de datos y la clave `SECRET_KEY` en el arranque, deteniendo la aplicación si no cumplen las políticas.
- **Clean Architecture (Elite)**: PASSED - Las validaciones de IDOR se integran en el servicio de aplicación (`ServicioDocumentalElite`) y los endpoints actúan solo como controladores, usando `Depends()` de FastAPI correctamente.
- **Shift Left / CI**: PASSED - Se especifica integración de `pip-audit`, `bandit` o `semgrep`, y uso de pre-commits para evitar futuros leaks.

## Project Structure

### Documentation (this feature)

```text
specs/066-security-hardening-remediation/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           
│   └── api-documentos-auth.md # Phase 1 output
└── tasks.md             # Phase 2 output (pending /speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── aplicacion/
│   └── servicios/
│       ├── servicio_autenticacion.py
│       └── servicio_documental.py
├── dominio/
│   └── entidades/
│       └── sesion_usuario.py
├── infraestructura/
│   └── configuracion/
│       └── settings.py
└── presentacion_reflex/
    ├── api/
    │   ├── documentos_api.py
    │   └── document_download_api.py
    └── styles.py

/
├── Dockerfile
├── entrypoint.sh
└── rxconfig.py
```

**Structure Decision**: La estructura sigue la Clean Architecture existente. Se modificarán archivos clave en las capas de Infraestructura (settings), Dominio (sesiones), Aplicación (servicios) y Presentación (endpoints FastAPI). Además, infraestructura de despliegue (`Dockerfile`, `entrypoint.sh`).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations.*

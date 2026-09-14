# Fase 0 — Investigación: Remediación de Credenciales Hardcodeadas (074)

**Fecha**: 2026-09-14
**Fuentes**: documentación oficial de Gitleaks y git-filter-repo, GitHub Docs (eliminación de datos sensibles) y estado real del repositorio (commit `94c7b16`).

Todas las incógnitas del contexto técnico quedan resueltas aquí; no queda ningún `NEEDS CLARIFICATION`.

## D1 — Detección de secretos: reglas versionadas + denylista exacta protegida

- **Decisión**: versionar `.gitleaks.toml` (nombre con punto, detectado por defecto por Gitleaks) con `[extend] useDefault = true` y reglas generalizadas: (a) fallback `os.getenv("DB_PASSWORD", "<literal>")`, (b) DSN con usuario:password embebidos, (c) asignación literal a variables `PASSWORD/CONTRASEÑA`, (d) `fill()` con credenciales en Playwright. La denylista con los literales exactos comprometidos **no se versiona**: se inyecta en CI desde configuración protegida (`GITLEAKS_CONFIG` o `GITLEAKS_CONFIG_TOML`), componiendo la configuración final en `$RUNNER_TEMP` (fuera del árbol de trabajo del repositorio).
- **Rationale**: Gitleaks resuelve la configuración en orden `--config` → `GITLEAKS_CONFIG` → `GITLEAKS_CONFIG_TOML` → `(ruta objetivo)/.gitleaks.toml` → default. Hoy el repo no versiona ninguna configuración (el `gitleaks.toml` local no está trackeado y contiene los literales), por lo que la CI escanea con reglas por defecto y no detecta literales cortos de baja entropía. Separar reglas generalizadas (revisables en PR) de la lista exacta (secreto) cumple FR-013 sin violar FR-003.
- **Alternatives considered**:
  - Versionar los literales en la configuración → viola FR-003 (descartado).
  - `.gitleaksignore` → opera por huella (fingerprint), no por patrón de valor (descartado).
  - Solo reglas generalizadas → no cumple la detección de los valores exactos exigida por FR-013/SC-005 (descartado).
  - TruffleHog o detect-secrets → menor integración con el workflow existente y mayor mantenimiento (descartado).
- **Sources**: https://github.com/gitleaks/gitleaks (README: precedencia de configuración, `gitleaks git --config`); https://github.com/gitleaks/gitleaks-action

## D2 — Purga del historial con git-filter-repo

- **Decisión**: purgar en una réplica espejo local con `git filter-repo --replace-text` (literales → `***REMOVED***`) y `--invert-paths` (rutas con PII); respaldar el espejo antes de la operación; force-push coordinado; guía de re-clonado.
- **Rationale**: es la herramienta recomendada por GitHub para eliminar datos sensibles del historial; reescribe todos los commits de forma determinista y permite verificación posterior. El archivo de reemplazos contiene los literales y **jamás debe versionarse** (se crea en un directorio temporal y se elimina al terminar).
- **Alternatives considered**:
  - BFG Repo-Cleaner → menos mantenido y requiere JVM (descartado).
  - Reiniciar el repositorio con un commit limpio → pierde trazabilidad y viola FR-009/FR-016 (descartado).
  - Purga vía soporte de GitHub → lenta y pensada para casos muy específicos (descartado).
- **Sources**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository ; https://github.com/newren/git-filter-repo

## D3 — Fail-fast de credenciales en Python

- **Decisión**: centralizar la validación en `Settings` (pydantic-settings) con validadores que aborten con mensaje explícito indicando la variable faltante (patrón ya usado por `secret_key`); en scripts y `rxconfig.py`, exigir `os.environ[...]`/`Settings` sin valores por defecto y fallar con error legible. Prohibido `os.getenv("X", "<literal>")` para credenciales.
- **Rationale**: reutiliza un patrón probado (`src/infraestructura/configuracion/settings.py:66-74`), evita divergencias entre decenas de scripts y cumple FR-002/FR-004 sin filtrar el valor.
- **Alternatives considered**:
  - Defaults vacíos silenciosos → errores de conexión confusos (descartado).
  - `assert` → se desactiva con `python -O` (descartado).
  - Registrar el valor esperado en el error → filtra (descartado).
- **Sources**: patrón interno existente (`Settings.validate_secret_key`).

## D4 — Retiro de PII y datos de prueba

- **Decisión**: `git rm --cached` de `assets/exports/*.csv` y `assets/pdfs/*.pdf`; patrones explícitos en `.gitignore` para ambas rutas y artefactos de base de datos; traslado de copias operativas a almacenamiento controlado fuera del repositorio; pruebas con datos sintéticos o anonimizados.
- **Rationale**: las rutas no están cubiertas explícitamente hoy (aunque `*.pdf` ignora PDFs nuevos, los ya trackeados permanecen); cumple FR-008/FR-010/FR-011/FR-012.
- **Alternatives considered**:
  - Anonimizar in situ → el dato real ya está comprometido y el historial lo conserva (descartado).
  - Almacenamiento LFS privado → el repositorio es de acceso público (descartado).
- **Sources**: `.gitignore` actual (líneas 1-120); auditoría §4.

## D5 — Verificación reproducible y evidencia (FR-016 / SC-001/002/008)

- **Decisión**: documentar en `docs/security/INVENTARIO_REMEDIACION_074.md` el inventario enmascarado con identificador único por hallazgo (`H-01`…`H-03`) y por ubicación (`U-###`), estados y evidencia (fecha, responsable, resultado). Verificación con `git grep` sobre `HEAD`, `gitleaks git` sobre el historial completo y búsquedas puntuales en `git log --all -p`.
- **Rationale**: sin valores reales el documento es seguro de versionar; permite medir "cero ocurrencias" de forma objetiva y da trazabilidad a operaciones (clarificación Q2 del 2026-09-14).
- **Alternatives considered**: evidencia solo externa al repo → no reproducible desde el código (descartado).

## D6 — Coordinación de la reescritura y bloqueo de rama

- **Decisión**: inventariar ramas/PRs abiertas, notificar a colaboradores, respaldar espejo, ejecutar purga, force-push y re-clonado en ≤ 5 días hábiles; exigir el job `security-scan` como check requerido en la protección de `main` (fail-closed, FR-014/FR-019/SC-010).
- **Rationale**: cumple FR-009 y SC-007; GitHub permite marcar jobs como checks requeridos, con lo que ninguna fusión ocurre sin escaneo exitoso.
- **Alternatives considered**:
  - No reescribir el historial → los valores siguen recuperables desde 2026-05-25 (descartado).
  - Escaneo solo informativo → contrario a la decisión fail-closed de la clarificación Q1 (descartado).

## D7 — ADR de la estrategia de escaneo

- **Decisión**: registrar `docs/decisions/ADR-074-estrategia-escaneo-secretos.md` documentando el contexto, la decisión (D1), las alternativas descartadas y las consecuencias (rotación de la denylista, mantenimiento de reglas).
- **Rationale**: Constitución §15 exige ADRs para decisiones arquitectónicas relevantes.
- **Alternatives considered**: documentar solo en `research.md` → sin registro permanente junto al código (descartado).

## Resumen de incógnitas resueltas

| Incógnita | Resolución |
|---|---|
| ¿Cómo detectar literales cortos con Gitleaks sin versionarlos? | D1: config generalizada versionada + denylista inyectada desde secreto |
| ¿Cómo purgar el historial de forma verificable? | D2: `git-filter-repo` en espejo + verificación post-purga |
| ¿Cómo unificar el fail-fast de credenciales? | D3: validadores en `Settings` + prohibición de defaults literales |
| ¿Dónde va la evidencia y cómo se verifica? | D5: inventario enmascarado versionado + búsquedas/escaneo reproducibles |
| ¿Cómo garantizar el bloqueo efectivo de fusiones? | D6: check requerido en la protección de rama |

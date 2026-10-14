# AGENTS.md — Guía de Agentes IA · Inmobiliaria Velar

> **Actualizado:** 2026-10-14 · **Rama activa:** `main` (`JSUARCAR/inmo_velar`)
> **Gobernanza:** `.specify/memory/constitution.md` **v2.0.0** prevalece sobre este archivo, `README.md`, `CLAUDE.md` y `GEMINI.md`.

## 1. Qué es este repositorio

Sistema Core de Gestión Inmobiliaria Velar: plataforma transaccional (contratos, liquidaciones financieras, PDF, RBAC, auditoría) con **Clean Architecture + DDD**, **Reflex 0.8.28 + PostgreSQL 13+**, desplegada en **Railway** (Docker + Caddy con ratelimit, `entrypoint.sh`).

- Código: `src/` (≈418 ficheros). Tests: `tests/` (≈107 ficheros `test_*`). Specs activas: `specs/072–079`.
- Estado a 2026-10-14: `079-fix-liquidacion-oct2026` **en curso** (working tree con cambios sin commitear en `servicio_financiero.py`, states y tests de renovación). Hitos recientes: auth 077/078 (spinner + 404 router), 074 secretos+gitleaks, 072 renovación con 47 tests verdes.
- Stack real: Python prod `3.11-slim` / dev `3.12`, Reflex instalado `0.8.28.post1`, `psycopg2-binary`, Pydantic 2.5+. Puertos: backend `8001`, frontend `3000` (`rxconfig.py`).

## 2. Reglas no negociables (resumen Constitución v2.0.0)

1. **100% español** en código, UI, comentarios y docs (solo términos de librería en inglés).
2. **Capas unidireccionales:** Dominio → Aplicación → Infraestructura → Presentación. Dominio con ZERO deps externas, VOs `frozen=True`.
3. **PostgreSQL nativo:** placeholders `%s`, `INSERT ... RETURNING id`, booleanos/fechas ISO 8601 validados. Prohibidos `?`, `lastrowid` y sufijo `_sqlite.py` (`repositorio_[entidad].py`).
4. **Zero Leak:** jamás commitear `.env`, `railway.json` con secretos ni `*.key/*.pem`. Sanitizar con `config/sanitize_credentials.py`. `gitleaks.toml` activo.
5. **Testing:** Dominio 100%, lógica nueva >90%. Pre-commit: `check_syntax.py`, `mypy`, `ruff`, `black` + render Reflex.
6. **Reflex único framework** (Flet obsoleto). Mutaciones de State atómicas; sin vars heredadas colisionadas (`is_loading`, etc. en Reflex ≥0.9); sin `_` inicial en background events.
7. **Diseño Claude/Anthropic** + escala `Z_*` de `styles.py` (prohibidos `z-index: 9999` y estética IA genérica). Overlays Radix con `pointer-events: auto`.
8. **Contract-First + validación en fronteras**; un solo formato de error estructurado.
9. **Stop-the-Line:** ante test/build roto, detener features hasta corregir raíz + test de regresión. **Zero Guessing:** si falta info, preguntar (`CONFUSION:` / `MISSING REQUIREMENT:`), no adivinar.
10. **Docs dinámicas:** todo cambio estructural MUST actualizar `README.md` + `CLAUDE.md` + este `AGENTS.md`; decisiones relevantes → ADR en `docs/decisions/`.

## 3. Estructura (rutas reales)

```
src/
├── dominio/              # entidades, value_objects, interfaces, servicios, excepciones
├── aplicacion/           # servicios de orquestación + esquemas.py (DTOs Pydantic)
├── infraestructura/      # persistencia (repositorio_*.py), pdf_elite, cache, logging
├── presentacion_reflex/  # pages/, components/, state/, api/, utils/, config/, styles.py
├── core/                 # helpers, decoradores (RBAC)
└── scripts/              # utilidades (diagnostico/)
migraciones/sql/ | tests/ | specs/ | docs/decisions/ | scripts/diagnostico/
inmobiliaria_velar/inmobiliaria_velar.py  # entry point Reflex (app_name="inmobiliaria_velar")
```

## 4. Comandos operativos

```bash
# Entorno
python -m venv venv; venv\Scripts\activate  # Windows (o source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env  # completar DATABASE_URL=postgresql://... , SECRET_KEY, API_URL

# Desarrollo (HMR) — validación final exigida: reflex run --env dev
reflex run
reflex run --env dev

# Calidad (orden Shift-Left: lint → tipado → tests → build)
python scripts/check_syntax.py
ruff check . ; black --check . ; mypy src
pytest -v
pytest --cov=src --cov-report=term-missing
```

## 5. Reglas de Build

1. ANTES de modificar `inmobiliaria_velar.py`:
   - Verificar que todos los símbolos nuevos existen en sus módulos fuente
   - Ejecutar: `python -c "from src.presentacion_reflex.styles import BASE_STYLE"`
2. ANTES de hacer push:
   - `git status` debe mostrar working tree limpio
   - Ejecutar: `DATABASE_URL=sqlite:///test.db reflex export --frontend-only --no-zip`
3. Commits Semver + Conventional Commits (`feat/fix/refactor/perf/test/chore`) con scope (`feat(dominio): ...`). Ramas `feature/` y `bugfix/` (base histórica `develop`; integración actual sobre `main`).

## 6. Modelo de ejecución con skills

Los skills se cargan **on-demand** vía el tool `skill` (no están en contexto permanente). Si la intención coincide con un skill — aunque sea 1% — invocarlo y seguirlo al pie de la letra.

| Intención | Skill(s) |
| :--- | :--- |
| Feature / funcionalidad nueva | `spec-driven-development` → `incremental-implementation` → `test-driven-development` (+ `speckit-specify/plan/tasks/implement` en `.agents/skills` para trazabilidad SpecKit) |
| Planificar / descomponer | `planning-and-task-breakdown` |
| Bug / fallo / comportamiento inesperado | `debugging-and-error-recovery` (+ `browser-testing-with-devtools` si es UI/Runtime) |
| Revisar código antes de merge | `code-review-and-quality` (5 ejes de la Constitución) |
| Refactorizar / simplificar | `code-simplification` (solo lo tocado por la tarea; Chesterton's Fence) |
| API / interfaces | `api-and-interface-design` (Contract-First) |
| UI / estilos | `frontend-ui-engineering` (sistema Claude, sin estética IA) |
| Seguridad / secretos / RBAC | `security-and-hardening` |
| Perf / N+1 / bundle | `performance-optimization` (medir, no adivinar; metas p95) |
| Docs de decisiones | `documentation-and-adrs` |
| Deploy / release | `shipping-and-launch` + `ci-cd-and-automation` (gates verdes, rollback claro) |
| Deprecar / migrar legacy | `deprecation-and-migration` |
| Duda de framework (Reflex/Python) | `source-driven-development` (citar docs oficiales) |

Ciclo de vida: `DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP`. Anti-racionalización: "es muy pequeño para un skill", "primero exploro y luego veo" y "ya me sé el skill" son incorrectos — invocar el skill primero.

## 7. Higiene del repo

- Raíz limpia: `debug_*.py`, `repro_*.py`, `.txt` sueltos o logs huérfanos van a `scripts/diagnostico/` o se eliminan.
- Cambios atómicos (~100 líneas); lo masivo se divide en subtareas/commits.
- No construir sobre base inestable; consola del navegador limpia; capturas Antes/Después en cambios visuales.

# DEPENDENCIAS — Referencia única

> Spec **080** · ADR: [`docs/decisions/080-lock-dependencias-hashes-prod-dev.md`](docs/decisions/080-lock-dependencias-hashes-prod-dev.md)
> Python de referencia: **3.11** (igual que producción, `python:3.11-slim`).

## 1. Archivos

| Archivo | Tipo | ¿Se edita a mano? | Uso |
| :--- | :--- | :--- | :--- |
| `requirements.in` | Dependencias directas de **producción** | **Sí** | Fuente de verdad de prod |
| `requirements.txt` | Lock con hashes (generado) | **No** | `Dockerfile`, CI, instalación |
| `requirements-dev.in` | Dependencias de desarrollo/CI (`-c requirements.txt`) | **Sí** | Fuente de verdad de dev |
| `requirements-dev.txt` | Lock con hashes de dev (generado) | **No** | CI y desarrollo local |

Los `.txt` se generan con `uv`; nunca se editan a mano. Cambiar el lock invalida por sí solo el caché de Docker (ya no se usa el comentario "Rebuild Trigger").

## 2. Regla: Reflex fijo en 0.8.28

`reflex==0.8.28` está **fijo** en `requirements.in`. No subir a 0.9+/0.10: hay choques documentados (vars heredadas como `is_loading`, entre otros). La migración se hace en una spec aparte. Dependabot ignora subidas minor/major de `reflex` (`.github/dependabot.yml`).

Otros pines deliberados (cada uno con su motivo en `requirements.in`):

| Paquete | Restricción | Motivo |
| :--- | :--- | :--- |
| `sqlalchemy` (transitiva) | `>=2.0.14,<2.1` | SQLAlchemy 2.1 ya no instala `greenlet` por defecto y rompe el soporte asyncio; producción venía usando 2.0.x. |
| `kaleido` | `>=0.2.1` | `plotly.io.to_image` (`pdf_elite/utils/chart_converter.py`) lo necesita en runtime. Con kaleido 1.x se requiere Chrome/Chromium instalado en la imagen. |

## 3. Comandos

Preparar herramientas (una vez):

```bash
python -m venv .venv-audit && source .venv-audit/bin/activate   # Windows: .venv-audit\Scripts\activate
pip install uv pip-audit
```

### Actualizar todo

```bash
uv pip compile requirements.in     -o requirements.txt     --generate-hashes --python-version 3.11 --upgrade
uv pip compile requirements-dev.in -o requirements-dev.txt --generate-hashes --python-version 3.11 --upgrade
```

### Actualizar un solo paquete (por CVE)

```bash
uv pip compile requirements.in -o requirements.txt --generate-hashes --python-version 3.11 --upgrade-package <paquete>
uv pip compile requirements-dev.in -o requirements-dev.txt --generate-hashes --python-version 3.11 --upgrade-package <paquete>
```

Si no hay versión corregida compatible con `reflex==0.8.28`, **no se ignora**: se documenta en este archivo (ID del aviso, paquete, versión, mitigación).

### Validar antes de desplegar

```bash
pip-audit -r requirements.txt     --require-hashes --progress-spinner off
pip-audit -r requirements-dev.txt --require-hashes --progress-spinner off

python -m venv .venv-prod && source .venv-prod/bin/activate   # Windows: .venv-prod\Scripts\activate
pip install --require-hashes -r requirements.txt -r requirements-dev.txt
pip check
pytest -q
ruff check . && black --check . && mypy src
python scripts/diagnostico/prueba_humo_dependencias.py
DATABASE_URL=sqlite:///test.db reflex export --frontend-only --no-zip
reflex run --env dev
```

Usar siempre valores dummy (`SECRET_KEY` aleatoria, `DATABASE_URL=sqlite:///tmp_test.db`); nunca credenciales reales. Borrar `*.db` temporales al terminar.

## 4. Instalación

```bash
pip install --require-hashes -r requirements.txt                          # producción
pip install --require-hashes -r requirements.txt -r requirements-dev.txt  # desarrollo
```

## 5. Automatización

| Pieza | Archivo | Función |
| :--- | :--- | :--- |
| Auditoría | `.github/workflows/pip-audit.yml` | `pip-audit -r requirements.txt --require-hashes` en push/PR a `main` y a diario (`0 12 * * *`). |
| Build | `.github/workflows/build-validate.yml` | Instala con hashes y verifica `reflex export`. |
| Dependabot | `.github/dependabot.yml` | pip, docker y github-actions, semanal, agrupando patch/minor; ignora minor/major de `reflex`. |

## 6. Avisos sin corrección compatible

Ninguno al 2026-10-22 (`pip-audit` limpio sobre ambos locks).

## 7. Fuera de alcance (specs aparte)

- Migrar Reflex a 0.9+/0.10.
- Auditar el frontend npm de `.web/`.
- Cambiar la imagen base `python:3.11-slim` o la versión de Caddy.

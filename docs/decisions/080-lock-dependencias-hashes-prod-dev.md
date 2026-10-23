# ADR 080 — Lock de dependencias con hashes y separación prod/dev

- **Estado:** Aceptado
- **Fecha:** 2026-10-22
- **Spec:** 080 (`chore/080-actualizacion-dependencias-seguridad`)
- **Gobernanza:** Constitución v2.0.0 (Stack congelado: `Reflex 0.8.28+`, Python 3.11 en prod; Zero Leak; Shift Left)

## Contexto

`requirements.txt` declaraba todo con `>=` (incluido `reflex>=0.6.0`), sin lock y mezclando producción con herramientas de desarrollo (`pytest`, `mypy`, `ruff`, `black`) y paquetes que producción no usa (`pyautogui`, `gunicorn`).

Consecuencias medidas el 2026-10-22:

- Un `pip install` nuevo resolvía a **reflex 0.10.0**, ya incompatible con el código (choques documentados desde 0.9+). El build de Docker dependía del día en que se ejecutara.
- `pip-audit -r requirements.txt` daba "sin vulnerabilidades" porque resolvía a lo más reciente, pero el entorno real (reflex 0.8.28.post1) tenía **286 avisos en 25 paquetes** (aiohttp, starlette 0.50.0, pillow 12.0.0, python-multipart 0.0.21, cryptography, pypdf, etc.). La auditoría sobre un archivo sin lock no representa lo que se despliega.
- Sin hashes, no había verificación de integridad de la cadena de suministro.

## Decisión

1. **Separar** dependencias directas en `requirements.in` (prod) y `requirements-dev.in` (dev, con `-c requirements.txt` para no divergir de prod).
2. **Generar** los `.txt` con `uv pip compile --generate-hashes --python-version 3.11` y nunca editarlos a mano.
3. **Instalar** siempre con `pip install --require-hashes`.
4. **Fijar** `reflex==0.8.28`; la migración a 0.9+/0.10 es una spec aparte.
5. **Auditar** con `pip-audit --require-hashes` en CI (push/PR a `main` y diario) y actualizar con Dependabot semanal (ignorando minor/major de `reflex`).
6. Excluir de producción `gunicorn` (el `entrypoint.sh` arranca con `reflex run`) y `pyautogui` (solo `cliente_whatsapp_desktop.py`, con import protegido por `try/except`).
7. Mantener `kaleido` en producción: `pdf_elite/utils/chart_converter.py` usa `plotly.io.to_image`.
8. Fijar `sqlalchemy<2.1` (transitiva): SQLAlchemy 2.1 ya no instala `greenlet` por defecto y rompe el soporte asyncio. Producción venía con 2.0.x.

## Alternativas descartadas

| Alternativa | Motivo del descarte |
| :--- | :--- |
| `pip-tools` (`pip-compile`) | `uv` es más rápido, soporta `--python-version` y es compatible con los mismos archivos `.in`. |
| Poetry / PDM | Cambio de herramienta y de flujo de Docker innecesario; el repo usa `requirements*.txt`. |
| Mantener `>=` y confiar en la auditoría diaria | No es reproducible ni verificable por hash. |
| Un solo lock con dev incluido | Imagen de producción con herramientas de desarrollo (mayor superficie de ataque). |
| Subir Reflex a 0.9+/0.10 en este cambio | Choques documentados; riesgo alto para un cambio de seguridad. |

## Consecuencias

- Builds reproducibles; cualquier cambio de dependencias es un diff revisable del lock, que además invalida el caché de Docker (se elimina el comentario "Rebuild Trigger").
- Saltos mayores de versión (Plotly 5→7, ReportLab 4→5, Pillow 11/12→13, entre otros) validados con `scripts/diagnostico/prueba_humo_dependencias.py`.
- `pip-audit` limpio sobre `requirements.txt` y `requirements-dev.txt` al 2026-10-22.
- Costo: hay que regenerar el lock para cada actualización (ver `DEPENDENCIAS.md`).
- Los locks se generan para la plataforma del equipo que ejecuta `uv` (Windows en esta spec). Se verificó con `--python-platform x86_64-unknown-linux-gnu` que el lock de Linux contiene los mismos paquetes salvo `colorama` y `psutil`, que solo aparecen en Windows y son inocuos en Linux. `uv` registra los hashes de todas las distribuciones de cada versión, por lo que el build de Docker (Linux) verifica integridad. Si una actualización futura añadiera una dependencia exclusiva de Linux, regenerar el lock desde Linux/WSL o con `--universal`.

## Riesgos abiertos

- `kaleido>=1` requiere Chrome/Chromium en la imagen para `pio.to_image`; `python:3.11-slim` no lo incluye. El método solo lo usa una prueba (`tests/pdf_elite/test_templates.py`); candidato a retirar en una spec aparte.
- `playwright` y `pytest-playwright` se usan en `tests/e2e/` y no estaban declarados en ningún archivo de dependencias.

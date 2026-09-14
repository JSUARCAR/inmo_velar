# Quickstart — Validación de la remediación (074)

Guía de escenarios ejecutables que demuestran el cumplimiento de la spec de extremo a extremo. No contiene código de implementación; los detalles de construcción están en `tasks.md`.

## Prerrequisitos

- Repositorio clonado con acceso de escritura y `fetch-depth` completo (`git fetch --unshallow` si aplica).
- Python 3.11 con el entorno del proyecto instalado (`pip install -r requirements.txt`).
- `gitleaks` CLI disponible localmente (para verificaciones locales).
- `git-filter-repo` disponible (solo para la fase de purga; no se ejecuta en validación diaria).
- Acceso a la configuración protegida de CI (secreto `GITLEAKS_KNOWN_LEAKS_REGEX`) para probar el gate.
- PowerShell 7 en Windows o bash en CI/Linux.

## Escenario 1 — Cero literales en el árbol de trabajo (SC-001)

```bash
# Con la lista protegida cargada en el entorno (sin imprimir literales):
#   REGEX_PROTEGIDA="<patrón de alternancia de la lista protegida>"
git grep -n -I -E "$REGEX_PROTEGIDA" -- .
git grep -n -E 'getenv\(\s*["'"'"']DB_PASSWORD["'"'"']\s*,\s*["'"'"'][^"'"'"']+' -- '*.py'
```

**Resultado esperado**: cero coincidencias en el primer comando; cero fallbacks literales en el segundo. Registrar como `E-###` (tipo `búsqueda_árbol`, resultado "0 coincidencias").

## Escenario 2 — Modo de fallo seguro de la configuración (FR-004 / US-02)

1. En una terminal sin `.env` ni variables de credenciales, ejecutar un componente consumidor (p. ej., un script de `migraciones/` o la app).
2. Observar el resultado.

**Resultado esperado**: aborta de inmediato con `[ERROR DE CONFIGURACIÓN] Falta la variable <NOMBRE>...`, salida distinta de cero, y ninguna conexión intentada con valores supuestos.

## Escenario 3 — Detección local de la denylista (SC-005, prueba controlada)

1. Crear una rama temporal y un archivo de prueba con un **señuelo** (patrón de la lista protegida, valor ficticio con el mismo formato; nunca un valor real).
2. Ejecutar localmente el escaneo con la configuración compuesta (base versionada + denylista protegida).

**Resultado esperado**: el escáner detecta el señuelo y termina con salida distinta de cero; el escaneo del repositorio limpio no reporta hallazgos. Eliminar la rama temporal al terminar.

## Escenario 4 — El gate bloquea la fusión (FR-014 / SC-010)

1. Abrir un PR de prueba (o push a rama protegida) que introduzca un señuelo.
2. Revisar el estado del check `security-scan` y la posibilidad de fusionar.

**Resultado esperado**: check en `failure` y fusión impedida por la protección de rama. Repetir con un cambio limpio: check en `success`. Registrar como `E-###` (tipo `bloqueo_prueba`).

## Escenario 5 — Historial purgado (SC-002)

1. Tras la purga, clonar el repositorio en un directorio nuevo.
2. Buscar los valores en todo el historial con el escaneo de Gitleaks (`gitleaks git` sobre el clon, configuración protegida) y con búsquedas en `git log --all -p`.

**Resultado esperado**: cero coincidencias en todos los commits, ramas y etiquetas; el clon no contiene ningún archivo con PII. Registrar como `E-###` (tipo `búsqueda_historial`, resultado "0 coincidencias").

## Escenario 6 — PII fuera del repositorio (SC-006)

```bash
git ls-files assets/exports assets/pdfs        # debe devolver vacío
```

1. Crear un archivo de prueba en `assets/exports/` y verificar que el control de versiones no lo rastrea.

**Resultado esperado**: sin archivos trackeados en rutas sensibles; archivos nuevos ignorados; historial sin versiones con datos reales.

## Escenario 7 — Evidencia completa (SC-008 / FR-016)

1. Abrir `docs/security/INVENTARIO_REMEDIACION_074.md`.
2. Verificar que cada hallazgo tiene estado final, cada ubicación su limpieza/purga y cada criterio SC su evidencia (`E-###`).

**Resultado esperado**: documento completo, fechado, con responsable, sin ningún valor real, y con resultado "en cero" para las búsquedas y el escaneo.

## Criterio de salida global

La remediación se considera validada cuando los 7 escenarios arrojan el resultado esperado y la evidencia está registrada en el inventario. Cualquier desviación detiene el cierre (Constitución §13, Stop-the-line).

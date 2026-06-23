# Task 3: Refactorizar Llamadas a `.execute` en Configuraciones y Parámetros - Reporte de Ejecución

## Implementación
- Se modificaron las llamadas a `conn.execute()` y `conn.executemany()` en los archivos de integración para utilizar cursores explícitos (`cursor = conn.cursor()`).
- Se cambiaron los placeholders de SQLite (`?`) por la convención de PostgreSQL (`%s`), alineado con las reglas en `GEMINI.md`.
- Se corrigió la sintaxis de inserción: se migró de `INSERT OR REPLACE INTO` a `INSERT INTO` simple, apoyándose en las operaciones previas de `DELETE FROM` de la limpieza de datos (`setup` / `cleanup`).
- Se corrigieron los datos booleanos enviados directamente en los tests de `1` o `0` a `True` o `False` para alinearse con los tipos estrictos de PostgreSQL.
- Se ajustó el año del test de IPC (2998 a 2997) para evitar colisiones con un test que podía quedar a medio fallar por problemas anteriores.

## Pruebas y Resultados
- Se ejecutó: `pytest tests/integration/test_repositorio_parametro.py tests/integration/test_servicio_configuracion.py -v`.
- **Resultados:** De los 20 tests descubiertos, 18 pasaron (PASS) y 2 fallaron (FAIL).
- Ningún test arrojó el error original especificado (`AttributeError: 'psycopg2.extensions.connection' object has no attribute 'execute'`), lo que significa que la migración a nivel de `tests/` fue exitosa.
- Se ejecutó `ruff format` y `ruff check --fix` exitosamente, validando la integridad del código modificado.

## Archivos Modificados
- `tests/integration/test_repositorio_parametro.py`
- `tests/integration/test_servicio_configuracion.py`

## Hallazgos de Revisión (Self-review)
Los cambios en los scripts de prueba son correctos y aseguran compatibilidad con la nueva conexión de PostgreSQL en `TestDatabaseManager`. 

## Problemas y Preocupaciones (Issues/Concerns)
Las 2 fallas restantes se deben a errores originados en la lógica de negocio (carpeta `src/`):
1. `TestRepositorioParametroPostgres.test_crear_parametro`: Falla con `AttributeError: 'RepositorioParametroPostgres' object has no attribute 'crear'`. El método en el repositorio puede llamarse de otra forma o no haber sido implementado.
2. `TestServicioConfiguracionUsuarios.test_crear_usuario`: Falla con `psycopg2.errors.DatatypeMismatch` en `estado_usuario`. El repositorio (`repositorio_usuario.py` línea 117) está intentando insertar un `1` de tipo entero en una columna booleana. 

Al estar el scope actual restringido estrictamente a los tests, no se modificó la carpeta `src/`. Esto deberá resolverse en otra subtarea de refactorización.

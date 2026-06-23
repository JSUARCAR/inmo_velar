### Task 3: Refactorizar Llamadas a `.execute` en Configuraciones y Parámetros

**Files:**
- Modify: `tests/integration/test_repositorio_parametro.py`
- Modify: `tests/integration/test_servicio_configuracion.py`

**Interfaces:**
- Consumes: Fixtures que devuelven la conexión `conn` en `conftest.py` y `TestDatabaseManager`.

- [ ] **Step 1: Escribir la corrección en `test_repositorio_parametro.py`**

Buscar todas las ocurrencias de `conn.executemany(` y `conn.execute(` y reemplazarlas para que usen un cursor intermedio.
Ejemplo de código defectuoso:
```python
with db_manager.obtener_conexion() as conn:
    conn.executemany("""
        INSERT OR REPLACE INTO PARAMETROS_SISTEMA ...
```

Debe cambiarse a:
```python
with db_manager.obtener_conexion() as conn:
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO PARAMETROS_SISTEMA ...
```

**ATENCIÓN**: Asegúrate de cambiar `conn.execute(...)` a `cursor.execute(...)` donde aplique, actualizando las variables que reciben los cursores o iteradores según corresponda, o solo creando un `cursor = conn.cursor()` y usando `cursor` para los queries.

- [ ] **Step 2: Escribir la corrección en `test_servicio_configuracion.py`**

Realizar el mismo cambio, asegurando que `conn.execute(` pase a ser `cursor = conn.cursor()` seguido de `cursor.execute(`.

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/integration/test_repositorio_parametro.py tests/integration/test_servicio_configuracion.py -v`
Expected: PASS (ningún `AttributeError: 'psycopg2.extensions.connection' object has no attribute 'execute'`).

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_repositorio_parametro.py tests/integration/test_servicio_configuracion.py
git commit -m "fix(tests): usar cursor explicito para execute y executemany en setup de datos"
```

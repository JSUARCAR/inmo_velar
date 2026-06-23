### Task 2: Reparar Inicialización de Base de Datos en Tests Financieros

**Files:**
- Modify: `tests/integration/test_servicios_aplicacion/test_financiero_integration.py`
- Modify: `tests/integration/test_servicios_aplicacion/test_financiero_integration_v2.py`

**Interfaces:**
- Consumes: `TestDatabaseManager` (desde `tests/integration/test_database_manager.py`)

- [ ] **Step 1: Escribir la corrección en `test_financiero_integration.py`**

Reemplazar la importación de `DatabaseManager`:
```python
# Eliminar o comentar:
# from src.infraestructura.persistencia.database import DatabaseManager

# Agregar:
from tests.integration.test_database_manager import TestDatabaseManager
```

En la función `setUpClass(cls)`:
```python
# Cambiar:
# cls.db_manager = DatabaseManager(DB_PATH)

# A:
cls.db_manager = TestDatabaseManager(DB_PATH)
```

- [ ] **Step 2: Escribir la misma corrección en `test_financiero_integration_v2.py`**

Realizar exactamente los mismos cambios en importación y en `setUpClass(cls)`.

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/integration/test_servicios_aplicacion/test_financiero_integration.py -v`
Expected: Las pruebas ya no fallan con `TypeError: DatabaseManager.__new__()`.

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_servicios_aplicacion/test_financiero_integration.py tests/integration/test_servicios_aplicacion/test_financiero_integration_v2.py
git commit -m "fix(tests): reemplazar DatabaseManager por TestDatabaseManager en integracion financiera"
```

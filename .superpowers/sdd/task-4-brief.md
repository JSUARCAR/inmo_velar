### Task 4: Condicionar Tests E2E que Requieren Servidor Activo

**Files:**
- Create: `tests/utils_network.py`
- Modify: `tests/pdf_elite/test_integration.py`
- Modify: `tests/test_playwright_filtro_asesores.py`
- Modify: `tests/test_playwright_liquidacion_asesores.py`
- Modify: `tests/test_dashboard_row4.py`

**Interfaces:**
- Produces: Tests E2E ignorados gentilmente (SKIP) si el puerto 8000 no está en escucha.

- [ ] **Step 1: Crear función de utilidad para detectar servidor local**

Crear un nuevo archivo `tests/utils_network.py`:
```python
import socket

def is_server_running(host="localhost", port=8000) -> bool:
    """Verifica si el servidor Reflex está corriendo en el puerto indicado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

SERVER_RUNNING = is_server_running()
```

- [ ] **Step 2: Aplicar decorador de Skip a los archivos E2E**

En la cabecera de `tests/pdf_elite/test_integration.py`, `tests/test_playwright_filtro_asesores.py`, `tests/test_playwright_liquidacion_asesores.py`, y `tests/test_dashboard_row4.py`:

```python
import pytest
from tests.utils_network import SERVER_RUNNING

pytestmark = pytest.mark.skipif(
    not SERVER_RUNNING, 
    reason="El servidor local en localhost:8000 no esta activo. E2E/Playwright tests ignorados."
)
```

- [ ] **Step 3: Run test to verify SKIP**

Run: `pytest tests/pdf_elite/test_integration.py -v`
Expected: SKIPPED con el mensaje especificado.

- [ ] **Step 4: Ejecutar suite completa y hacer Commit**

```bash
pytest
git add tests/utils_network.py tests/pdf_elite/test_integration.py tests/test_playwright_*.py tests/test_dashboard_row4.py
git commit -m "test(suite): omitir pruebas E2E y playwright si el servidor local esta inactivo"
```

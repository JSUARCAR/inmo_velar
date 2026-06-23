### Task 1: Instalar y Configurar `pytest-asyncio`

**Files:**
- Create/Modify: `pytest.ini`

**Interfaces:**
- Consumes: N/A
- Produces: Entorno capaz de correr tests asíncronos nativamente.

- [ ] **Step 1: Instalar paquete via pip**

```bash
pip install pytest-asyncio
```

- [ ] **Step 2: Configurar pytest.ini**

Crear o modificar el archivo `pytest.ini` en la raíz del proyecto para definir el modo asíncrono automático.

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

- [ ] **Step 3: Run test to verify `async` issue is resolved**

Run: `pytest tests/test_dashboard_state_integration.py -v`
Expected: PASS (al menos no fallará por "async def functions are not natively supported").

- [ ] **Step 4: Commit**

```bash
git add pytest.ini
git commit -m "test(suite): agregar pytest-asyncio y configurar pytest.ini para soporte asincrono"
```

# Task 3: Corregir booleanos enteros en PostgreSQL

## Ubicación en el Plan
Task 3 del Plan Maestro de Estabilización. Independiente de Tasks 1 y 2.
Base commit del plan: ec14ba4

## Objetivo
Varios repositorios de producción pasan valores enteros `1`/`0` a columnas declaradas como `BOOLEAN` en PostgreSQL. PostgreSQL rechaza esto con:

```
psycopg2.errors.DatatypeMismatch: column "estado_usuario" is of type boolean but expression is of type integer
```

Error específico:
```
FAILED tests/integration/test_servicio_configuracion.py::TestServicioConfiguracionUsuarios::test_crear_usuario
```

## Global Constraints
- Rama activa: `feat/desarrollo-experto-elite`
- Directorio de trabajo: `C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX`
- Venv: `venv\Scripts\activate`
- PostgreSQL: usar `True`/`False` Python en columnas BOOLEAN (nunca `1`/`0`)
- Commits en español con Conventional Commits
- Ruff + Black limpios antes de cada commit

## Archivos a Investigar y Posiblemente Modificar
- `src/infraestructura/persistencia/repositorio_usuario_postgres.py`
- Cualquier otro repositorio con columnas BOOLEAN en sus INSERT

## Pasos

### Step 1: Confirmar el error exacto
```powershell
venv\Scripts\activate
pytest tests/integration/test_servicio_configuracion.py::TestServicioConfiguracionUsuarios::test_crear_usuario --tb=long -q
```

### Step 2: Buscar todos los repos con enteros en columnas boolean
```powershell
Select-String ", 1," src\infraestructura\persistencia\ -Recurse | Select-String "estado|activo|disponible|habilitado"
Select-String ", 0," src\infraestructura\persistencia\ -Recurse | Select-String "estado|activo|disponible|habilitado"
```

### Step 3: Inspeccionar el repositorio afectado
```powershell
Get-Content "src\infraestructura\persistencia\repositorio_usuario_postgres.py" | Select-String "estado_usuario|INSERT|execute" | Select-Object -First 30
```

### Step 4: Corregir todos los INSERT/UPDATE con 1/0 en columnas BOOLEAN

En todos los repositorios afectados, cambiar el patrón:
```python
# ANTES (incorrecto para PostgreSQL BOOLEAN)
cursor.execute(sql, (..., 1, ...))  # columna boolean
cursor.execute(sql, (..., 0, ...))  # columna boolean

# DESPUÉS (correcto)
cursor.execute(sql, (..., True, ...))  # columna boolean
cursor.execute(sql, (..., False, ...))  # columna boolean
```

NOTA: En SQLite (tests), `True`/`False` también funcionan correctamente.

### Step 5: Verificar
```powershell
venv\Scripts\activate
pytest tests/integration/test_servicio_configuracion.py -q
```
Resultado esperado: todos los tests de configuración pasan.

### Step 6: Verificar que no se rompió nada más
```powershell
venv\Scripts\activate
pytest tests/integration/ -q --tb=line
```

### Step 7: Commit
```bash
git add src/infraestructura/persistencia/
git commit -m "fix(infra): reemplaza enteros 1/0 por True/False en columnas BOOLEAN de PostgreSQL"
```

## Criterio de Aceptación
- `pytest tests/integration/test_servicio_configuracion.py` → todos passed
- Sin regresión en tests de integración que ya pasaban
- Ruff y Black limpios

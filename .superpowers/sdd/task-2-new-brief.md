# Task 2: Actualizar esquema SQLite en TestDatabaseManager

## Ubicación en el Plan
Task 2 del Plan Maestro de Estabilización. Independiente de Task 1.
Base commit del plan: ec14ba4

## Objetivo
La clase `TestDatabaseManager` en `tests/integration/test_database_manager.py` usa un esquema SQLite desactualizado: le faltan columnas que el repositorio de producción `repositorio_propiedad_postgres.py` ya usa (ej. `CODIGO_ENERGIA`, `MATRICULA_INMOBILIARIA`, `ESTRATO_PROPIEDAD`, etc.).

Error actual:
```
sqlite3.OperationalError: table PROPIEDADES has no column named CODIGO_ENERGIA
```

Esto causa ~8 fallos en:
- `tests/integration/test_repositorios/test_repositorio_propiedad.py` (8 tests)

## Global Constraints
- Rama activa: `feat/desarrollo-experto-elite`
- Directorio de trabajo: `C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX`
- Venv: `venv\Scripts\activate`
- Placeholders SQLite: `?` (nunca `%s`)
- Commits en español con Conventional Commits
- Ruff + Black limpios antes de cada commit

## Archivos a Modificar
- `tests/integration/test_database_manager.py` — actualizar el `CREATE TABLE PROPIEDADES`

## Pasos

### Step 1: Inspeccionar columnas usadas en repositorio_propiedad_postgres.py
```powershell
Select-String "INSERT INTO PROPIEDADES|CODIGO_ENERGIA|MATRICULA_INMOBILIARIA|ESTRATO|AREA_|CODIGO_GAS|HABITACIONES|GARAJES|PISO_" "src\infraestructura\persistencia\repositorio_propiedad_postgres.py" | Select-Object -First 40
```

### Step 2: Confirmar el error actual
```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorios/test_repositorio_propiedad.py::TestRepositorioPropiedad::test_crear_propiedad_completa --tb=long -q
```

### Step 3: Actualizar el CREATE TABLE PROPIEDADES en test_database_manager.py
Localizar el bloque `CREATE TABLE IF NOT EXISTS PROPIEDADES` y reemplazarlo con:

```sql
CREATE TABLE IF NOT EXISTS PROPIEDADES (
    ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
    DIRECCION_PROPIEDAD TEXT NOT NULL,
    ID_MUNICIPIO INTEGER,
    ID_ASESOR INTEGER,
    DISPONIBILIDAD_PROPIEDAD BOOLEAN DEFAULT 1,
    ESTADO_REGISTRO BOOLEAN DEFAULT 1,
    TIPO_PROPIEDAD TEXT DEFAULT 'CASA',
    CANON_ARRENDAMIENTO_ESTIMADO REAL DEFAULT 0,
    DESCRIPCION_PROPIEDAD TEXT,
    AREA_PROPIEDAD REAL,
    ESTRATO_PROPIEDAD INTEGER,
    MATRICULA_INMOBILIARIA TEXT,
    CODIGO_ENERGIA TEXT,
    CODIGO_GAS TEXT,
    HABITACIONES_PROPIEDAD INTEGER,
    BANOS_PROPIEDAD INTEGER,
    GARAJES_PROPIEDAD INTEGER,
    PISO_PROPIEDAD INTEGER,
    FECHA_REGISTRO TEXT,
    USUARIO_REGISTRO TEXT,
    FECHA_MODIFICACION TEXT,
    USUARIO_MODIFICACION TEXT
);
```

IMPORTANTE: Revisa primero el archivo actual para asegurarte de no romper otros tests que sí pasaban. Añade solo las columnas faltantes, no elimines las existentes.

### Step 4: Si hay otras tablas con columnas faltantes, identificarlas y actualizarlas
```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorios/ --tb=line -q
```

### Step 5: Verificar
```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorios/test_repositorio_propiedad.py -q
```
Resultado esperado: 8 passed.

### Step 6: Asegurarse de que los tests que ya pasaban siguen pasando
```powershell
venv\Scripts\activate
pytest tests/integration/ -q --tb=line
```

### Step 7: Commit
```bash
git add tests/integration/test_database_manager.py
git commit -m "test(infra): actualiza esquema SQLite en TestDatabaseManager con columnas faltantes de PROPIEDADES"
```

## Criterio de Aceptación
- `pytest tests/integration/test_repositorios/test_repositorio_propiedad.py` → 8 passed
- Sin regresión en otros tests de integración que ya pasaban
- Ruff y Black limpios

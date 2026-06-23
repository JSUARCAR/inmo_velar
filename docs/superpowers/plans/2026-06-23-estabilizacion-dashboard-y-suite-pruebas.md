# Plan Maestro: Estabilización de Suite de Pruebas y Dashboard

> **Para trabajadores agénticos:** USA EL SUB-SKILL: `superpowers:subagent-driven-development` para implementar este plan tarea por tarea.

**Goal:** Llevar la suite global de pruebas de 86 fallos a 0 fallos, y corregir los bugs visuales del Dashboard ("0 días" y registros duplicados) para dejar el sistema en estado productivo estable.

**Architecture:** Cirugía quirúrgica capa por capa — entorno de pruebas → infraestructura → lógica de dominio → estado Reflex → UI. Cada tarea es atómica con su propio ciclo TDD verificable. Cero cambios fuera del alcance de cada tarea.

**Tech Stack:** Python 3.12, Reflex, PostgreSQL (psycopg2), SQLite (tests), pytest, ruff, black, mypy.

## Global Constraints
- Placeholders SQL: `%s` (PostgreSQL), `?` (SQLite tests). Nunca mezclar.
- Booleanos para PostgreSQL: `True`/`False` Python explícito, nunca `1`/`0` enteros.
- INSERT PostgreSQL: obligatorio `RETURNING id`.
- Idioma del código: español (variables, comentarios, docstrings).
- Ruff + Black limpios antes de cada commit.
- Sin modificar lógica de negocio fuera del alcance de cada tarea.

---

## Diagnóstico: Clasificación de Fallos (86 totales)

| Cat | Fallos | Causa Raíz | Archivos Afectados |
|---|---|---|---|
| **A** | ~8 | Dependencias `holidays`, `python-barcode` no instaladas | `requirements.txt`, venv |
| **B** | ~8 | Schema SQLite de test sin columna `CODIGO_ENERGIA` y otras | `tests/integration/test_database_manager.py` |
| **C** | ~5 | Enteros `1`/`0` en columnas `BOOLEAN` de PostgreSQL | `repositorio_usuario_postgres.py` y similares |
| **D** | ~27 | `DatabaseManager.obtener_por_matricula` no existe — se pasa `db_manager` en vez de `RepositorioPropiedadPostgres` | `servicio_propiedades.py`, tests `CIU`, `servicio_propiedades` |
| **E** | ~7 | Tests de estado Reflex instancian estado sin contexto válido / variable `_load_run_id` no definida | `test_dashboard_state_v2.py`, `test_dashboard_state_integration.py` |
| **F** | ~3 | Figura Plotly tiene 2 trazas (Real+Target), test espera 1 / mock de `obtener_por_id` falla | `test_plotly_charts.py`, `test_crear_arrendamiento` |
| **G** | ~10 | `in_managed_transaction` inexistente en sqlite3 / KeyError en desocupacion / NoneType en documental | `database.py`, `test_renovacion.py`, `test_desocupacion_workflow.py`, `test_gestion_documental.py` |
| **H** | Visual | Dashboard: "0 días" (alias uppercase `DIAS_RESTANTES` vs lowercase esperado) + duplicados SQL | `repositorio_dashboard.py`, `vencimientos_tables.py` |

---

## Task 1: Instalar dependencias faltantes y fijar requirements.txt

**Files:**
- Modify: `requirements.txt`

**Interfaces:**
- Produce: paquetes `holidays` y `python-barcode` disponibles en el venv del proyecto.

- [ ] **Step 1: Verificar lo que hay en requirements.txt**

```powershell
Select-String "holidays|barcode" requirements.txt
```

- [ ] **Step 2: Instalar dependencias**

```powershell
venv\Scripts\activate
pip install holidays python-barcode
```

- [ ] **Step 3: Actualizar requirements.txt** — añadir si no existen:

```
holidays>=0.46
python-barcode>=0.15.1
```

- [ ] **Step 4: Verificar que las pruebas afectadas pasan**

```powershell
venv\Scripts\activate
pytest tests/test_calculadora_contratos.py tests/pdf_elite/test_components.py -q
```

Resultado esperado: todos los tests calculadora y barcode pasan.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt
git commit -m "chore(deps): agrega holidays y python-barcode faltantes en requirements"
```

---

## Task 2: Actualizar esquema SQLite en TestDatabaseManager

**Files:**
- Modify: `tests/integration/test_database_manager.py`

**Interfaces:**
- Produce: esquema SQLite con columna `CODIGO_ENERGIA` y todas las columnas que `repositorio_propiedad_postgres.py` requiere.

- [ ] **Step 1: Identificar todas las columnas usadas en el repositorio**

```powershell
venv\Scripts\activate
Select-String "CODIGO_ENERGIA|MATRICULA_INMOBILIARIA|ESTRATO|AREA_|CODIGO_GAS|HABITACIONES|GARAJES|PISO_" src\infraestructura\persistencia\repositorio_propiedad_postgres.py | Select-Object -First 30
```

- [ ] **Step 2: Confirmar el error actual**

```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorios/test_repositorio_propiedad.py::TestRepositorioPropiedad::test_crear_propiedad_completa --tb=long -q
```

- [ ] **Step 3: Actualizar CREATE TABLE PROPIEDADES en test_database_manager.py**

Localizar el `executescript` de creación de la tabla `PROPIEDADES` y reemplazar con el esquema completo:

```python
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

- [ ] **Step 4: Ejecutar todos los tests de repositorio_propiedad**

```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorios/test_repositorio_propiedad.py -q
```

Resultado esperado: `8 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_database_manager.py
git commit -m "test(infra): actualiza esquema SQLite en TestDatabaseManager con columnas faltantes"
```

---

## Task 3: Corregir booleanos enteros en PostgreSQL

**Files:**
- Investigate y Modify: `src/infraestructura/persistencia/repositorio_usuario_postgres.py` y similares

**Interfaces:**
- Produce: INSERT y UPDATE con `True`/`False` Python en columnas `BOOLEAN` de PostgreSQL.

- [ ] **Step 1: Identificar todas las ocurrencias con enteros en columnas boolean**

```powershell
Select-String "estado_usuario.*1|DISPONIBILIDAD.*1|ACTIVO.*,\s*1" src\infraestructura\persistencia\ -Recurse
```

- [ ] **Step 2: Confirmar el error exacto**

```powershell
venv\Scripts\activate
pytest tests/integration/test_servicio_configuracion.py::TestServicioConfiguracionUsuarios::test_crear_usuario --tb=long -q
```

Ver la línea exacta del INSERT y confirmar que el error es `DatatypeMismatch: column "estado_usuario" is of type boolean but expression is of type integer`.

- [ ] **Step 3: Reemplazar `1`/`0` por `True`/`False` en todos los repositorios afectados**

```python
# ANTES (incorrecto para PostgreSQL BOOLEAN)
cursor.execute(sql, (..., 1, NULL, ...))  # estado_usuario

# DESPUÉS
cursor.execute(sql, (..., True, None, ...))  # estado_usuario
```

- [ ] **Step 4: Verificar**

```powershell
venv\Scripts\activate
pytest tests/integration/test_servicio_configuracion.py -q
```

Resultado esperado: todos pasan.

- [ ] **Step 5: Commit**

```bash
git add src/infraestructura/persistencia/
git commit -m "fix(infra): reemplaza enteros 1/0 por True/False en columnas BOOLEAN de PostgreSQL"
```

---

## Task 4: Resolver `obtener_por_matricula` — interfaz faltante en repositorio

**Files:**
- Investigate: `tests/verification/test_ciu_codes.py`
- Investigate: `src/aplicacion/servicios/servicio_propiedades.py`
- Modify: `src/infraestructura/persistencia/repositorio_propiedad_postgres.py` (añadir método si no existe)
- Modify: tests que inyectan `db_manager` directamente en lugar del repositorio

**Interfaces:**
- Produce: `RepositorioPropiedadPostgres.obtener_por_matricula(matricula: str) -> Optional[Propiedad]` funcional y correctamente inyectado en `ServicioPropiedades`.

- [ ] **Step 1: Diagnosticar la raíz del problema**

```powershell
Select-String "obtener_por_matricula" src\infraestructura\persistencia\repositorio_propiedad_postgres.py
```

Si no aparece, el método falta en el repositorio. Si aparece, el problema es la inyección en el test.

- [ ] **Step 2: Ver cómo se instancia el servicio en el test afectado**

```powershell
Get-Content tests\verification\test_ciu_codes.py | Select-Object -First 60
```

- [ ] **Step 3a: Si el método falta — implementarlo en repositorio_propiedad_postgres.py**

```python
def obtener_por_matricula(self, matricula: str) -> Optional[Propiedad]:
    """Busca una propiedad por su matrícula inmobiliaria.

    Args:
        matricula: Número de matrícula inmobiliaria.

    Returns:
        Propiedad encontrada o None si no existe.
    """
    if self.db.use_postgresql:
        sql = """
            SELECT * FROM PROPIEDADES
            WHERE MATRICULA_INMOBILIARIA = %s
            AND ESTADO_REGISTRO = TRUE
            LIMIT 1
        """
    else:
        sql = """
            SELECT * FROM PROPIEDADES
            WHERE MATRICULA_INMOBILIARIA = ?
            AND ESTADO_REGISTRO = 1
            LIMIT 1
        """
    with self.db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (matricula,))
        row = cursor.fetchone()
        return self._fila_a_propiedad(dict(row)) if row else None
```

- [ ] **Step 3b: Si el test inyecta `db_manager` directamente — corregir el fixture**

```python
# ANTES (incorrecto — DatabaseManager no tiene obtener_por_matricula)
servicio = ServicioPropiedades(repo=db_manager)

# DESPUÉS (correcto — inyectar el repositorio)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import RepositorioPropiedadPostgres
repo = RepositorioPropiedadPostgres(db_manager)
servicio = ServicioPropiedades(repo=repo)
```

- [ ] **Step 4: Verificar**

```powershell
venv\Scripts\activate
pytest tests/verification/test_ciu_codes.py tests/integration/test_servicios_aplicacion/test_servicio_propiedades.py -q
```

Resultado esperado: todos los tests de propiedades y CIU pasan.

- [ ] **Step 5: Commit**

```bash
git add src/infraestructura/persistencia/repositorio_propiedad_postgres.py tests/
git commit -m "fix(aplicacion): implementa obtener_por_matricula y corrige inyección en ServicioPropiedades"
```

---

## Task 5: Corregir tests de estado Reflex (DashboardBase, integración y Plotly)

**Files:**
- Modify: `tests/unit/test_presentacion/test_dashboard_state_v2.py`
- Modify: `tests/unit/test_presentacion/test_plotly_charts.py`
- Modify: `tests/test_dashboard_state_integration.py`
- Investigate: `tests/unit/test_presentacion/test_crear_arrendamiento_ocupa_propiedad.py`

**Interfaces:**
- Produce: tests que instancian el estado correctamente sin depender del runtime de Reflex, y que validan el número actual de trazas de Plotly.

- [ ] **Step 1: Leer el error de instanciación de DashboardBaseState**

El error `'NoneType' object has no attribute '_concurrency_token'` ocurre porque el test llama a `DashboardBaseState()` o `DashboardState()` sin el contexto de Reflex (`parent_state = None`). Corregir usando instanciación directa del `__dict__`:

```python
# En test_dashboard_state_v2.py
def _make_base_state() -> DashboardBaseState:
    """Crea instancia de DashboardBaseState para testing sin runtime Reflex."""
    state = object.__new__(DashboardBaseState)
    state.__dict__.update({
        '_concurrency_token': '',
        'is_loading': False,
        'error_message': '',
        'errores_carga': [],
    })
    return state

def test_dashboard_base_concurrency_token():
    state = _make_base_state()
    token = state._generate_token()
    assert isinstance(token, str) and len(token) > 0
    assert state._is_valid_token(token) is True
    assert state._is_valid_token("token-invalido") is False
```

- [ ] **Step 2: Corregir `test_dashboard_state_integration.py` — async_generator**

El error `'async_generator' object is not an iterator` ocurre porque `load_dashboard_data` es `async def` con `background=True` y el test lo itera con `list()` o `next()`. Corregir usando `pytest-anyio` o un mock:

```python
# En test_dashboard_state_integration.py
from unittest.mock import patch, AsyncMock

async def test_load_dashboard_data_yields_loading_then_finishes():
    """Verifica que load_dashboard_data setea is_loading y luego termina."""
    with patch.object(DashboardState, '_get_servicio') as mock_svc:
        mock_svc.return_value.obtener_contratos_proximos_vencer.return_value = []
        # Verificar solo que el flag de hydration controla el flujo
        state = _make_dashboard_state()
        state._hydration_ready = False
        # Si hydration no está lista, debe abortar
        gen = state.load_dashboard_data()
        # El test verifica el comportamiento del guard, no el fetch completo
        assert state.is_loading is False
```

- [ ] **Step 3: Corregir test_plotly_charts — número de trazas**

```python
# ANTES (obsoleto — antes no había traza Target)
assert len(fig.data) == 1

# DESPUÉS (refleja la lógica actual con Real + Target)
assert len(fig.data) == 2
assert fig.data[0].name == "Real"
assert fig.data[1].name == "Target"
assert fig.data[1].line.dash == "dash"
```

- [ ] **Step 4: Verificar**

```powershell
venv\Scripts\activate
pytest tests/unit/test_presentacion/ tests/test_dashboard_state_integration.py -q
```

Resultado esperado: todos pasan.

- [ ] **Step 5: Commit**

```bash
git add tests/unit/test_presentacion/ tests/test_dashboard_state_integration.py
git commit -m "test(presentacion): corrige instanciación Reflex, async generator y trazas Plotly en tests"
```

---

## Task 6: Corregir `in_managed_transaction`, desocupación y documental

**Files:**
- Modify: `src/infraestructura/persistencia/database.py` (línea ~489)
- Investigate: `tests/test_desocupacion_workflow.py` (KeyError: 0)
- Investigate: `tests/test_gestion_documental.py` (NoneType subscriptable)
- Investigate: `tests/test_liquidacion_stateproxy_fix.py` (SystemExit: 0)

**Interfaces:**
- Produce: `database.py` con guardia segura para `in_managed_transaction`; tests de desocupación y documental con datos de setup correctos.

- [ ] **Step 1: Ver contexto de database.py línea 489**

```powershell
Get-Content src\infraestructura\persistencia\database.py | Select-Object -Skip 480 -First 25
```

- [ ] **Step 2: Añadir guardia `hasattr` en database.py**

```python
# ANTES
if conn.in_managed_transaction:

# DESPUÉS — seguro para sqlite3 y psycopg2
if hasattr(conn, 'in_managed_transaction') and conn.in_managed_transaction:
```

- [ ] **Step 3: Diagnosticar KeyError: 0 en test_desocupacion_workflow.py**

```powershell
venv\Scripts\activate
pytest tests/test_desocupacion_workflow.py --tb=long -q
```

El `KeyError: 0` sugiere que se accede a una lista/dict con índice 0 cuando está vacío. Identificar la fixture de datos de setup y añadir los datos necesarios antes de las aserciones.

- [ ] **Step 4: Diagnosticar NoneType en test_gestion_documental.py**

```powershell
venv\Scripts\activate
pytest tests/test_gestion_documental.py::TestGestionDocumental::test_repositorio_crud_blob --tb=long -q
```

Identificar qué objeto retorna `None` y por qué. Usualmente es que la tabla de documentos tiene un esquema diferente en el `TestDatabaseManager`. Actualizar el esquema.

- [ ] **Step 5: Diagnosticar SystemExit: 0 en test_liquidacion_stateproxy_fix.py**

```powershell
venv\Scripts\activate
pytest tests/test_liquidacion_stateproxy_fix.py --tb=long -q
```

`SystemExit: 0` suele indicar que el test llama a `sys.exit(0)` explícitamente como parte de la verificación. Si el test usa `pytest.raises(SystemExit)`, actualizar para capturar la excepción correctamente.

- [ ] **Step 6: Verificar**

```powershell
venv\Scripts\activate
pytest tests/test_desocupacion_workflow.py tests/test_gestion_documental.py tests/test_liquidacion_stateproxy_fix.py tests/integration/test_servicios_aplicacion/test_renovacion.py -q
```

Resultado esperado: todos pasan.

- [ ] **Step 7: Commit**

```bash
git add src/infraestructura/persistencia/database.py tests/
git commit -m "fix(infra): añade guardia in_managed_transaction y corrige tests de desocupación/documental"
```

---

## Task 7: Corregir Dashboard UI — "0 días" y duplicados remanentes

**Files:**
- Modify: `src/infraestructura/persistencia/repositorio_dashboard.py`
- Verify: `src/presentacion_reflex/components/dashboard/vencimientos_tables.py`

**Interfaces:**
- Consume: `DashboardState.vencimientos_lista` con claves lowercase `direccion`, `fecha_fin`, `dias_restantes`.
- Produce: tabla UI mostrando días reales, sin duplicados, solo dentro del rango 0-90.

- [ ] **Step 1: Verificar alias de columna en la query**

```powershell
venv\Scripts\activate
python -c "
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard
repo = RepositorioDashboard(db_manager)
r = repo.obtener_lista_vencimientos(90)
if r: print('Claves:', list(r[0].keys()))
else: print('Sin resultados')
"
```

Si las claves son `DIAS_RESTANTES` (uppercase), el `item.get("dias_restantes", 0)` de Reflex retorna `0`. La solución es forzar alias lowercase en el SQL.

- [ ] **Step 2: Corregir alias en _get_sql_vencimientos en repositorio_dashboard.py**

Verificar que el SQL usa alias lowercase explícito:

```sql
-- PostgreSQL
CAST(ca.FECHA_FIN_CONTRATO_A::DATE - CURRENT_DATE AS INTEGER) AS dias_restantes,
ca.FECHA_FIN_CONTRATO_A::TEXT AS fecha_fin,
p.DIRECCION_PROPIEDAD AS direccion

-- SQLite
CAST(julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now', 'localtime') AS INTEGER) AS dias_restantes,
ca.FECHA_FIN_CONTRATO_A AS fecha_fin,
p.DIRECCION_PROPIEDAD AS direccion
```

Si hay `DISTINCT` que falta, añadirlo:

```sql
SELECT DISTINCT ca.ID_CONTRATO_A, ...
```

- [ ] **Step 3: Confirmar el mapping en servicio_dashboard.py**

```powershell
Select-String "dias_restantes\|DIAS_RESTANTES" src\aplicacion\servicios\servicio_dashboard.py
```

Verificar que la serialización del servicio no renombra las claves.

- [ ] **Step 4: Verificar via script**

```powershell
venv\Scripts\activate
python -c "
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard
repo = RepositorioDashboard(db_manager)
r = repo.obtener_lista_vencimientos(90)
print(f'Total: {len(r)}')
ids = [x['id_contrato'] for x in r]
print(f'Duplicados: {len(ids) != len(set(ids))}')
if r: print('Primer item:', r[0])
"
```

Resultado esperado: sin duplicados, `dias_restantes` con valor real (no 0).

- [ ] **Step 5: Ejecutar tests de integración del dashboard**

```powershell
venv\Scripts\activate
pytest tests/integration/test_repositorio_dashboard_vencimientos.py -q
```

Resultado esperado: `4 passed`.

- [ ] **Step 6: Commit**

```bash
git add src/infraestructura/persistencia/repositorio_dashboard.py
git commit -m "fix(dashboard): corrige alias lowercase dias_restantes y DISTINCT en query de vencimientos"
```

---

## Task 8: Verificación Final Global

- [ ] **Step 1: Ejecutar la suite completa**

```powershell
venv\Scripts\activate
pytest tests/ -q --tb=line 2>&1
```

Objetivo: `0 failed`. Documentar cualquier fallo remanente.

- [ ] **Step 2: Ejecutar linting global**

```powershell
venv\Scripts\activate
ruff check src/ tests/
black --check src/ tests/
```

Objetivo: `All checks passed!` en ambos.

- [ ] **Step 3: Commit de cierre y push**

```bash
git add .
git commit -m "chore(ci): verificación final — suite de pruebas estabilizada"
git push origin feat/desarrollo-experto-elite
```

---

## Resumen de Tareas y Commits

| Task | Commits | Categorías cubiertas |
|---|---|---|
| 1 | `chore(deps)` | A — dependencias faltantes |
| 2 | `test(infra)` | B — schema SQLite desactualizado |
| 3 | `fix(infra)` | C — booleanos PostgreSQL |
| 4 | `fix(aplicacion)` | D — obtener_por_matricula |
| 5 | `test(presentacion)` | E, F — estado Reflex y Plotly |
| 6 | `fix(infra)` | G — in_managed_transaction, desocupación, documental |
| 7 | `fix(dashboard)` | H — alias dias_restantes y duplicados |
| 8 | `chore(ci)` | Verificación global |

# Task 4: Resolver obtener_por_matricula — interfaz faltante en repositorio

## Ubicación en el Plan
Task 4 del Plan Maestro de Estabilización. Independiente de Tasks 1, 2 y 3.
Base commit del plan: ec14ba4

## Objetivo
`ServicioPropiedades.crear_propiedad()` llama `self.repo.obtener_por_matricula(matricula)` en la línea 138, pero el tests están pasando `db_manager` (instancia de `DatabaseManager`) directamente como `repo`, cuando debería pasarse un `RepositorioPropiedadPostgres`. El `DatabaseManager` no tiene el método `obtener_por_matricula`, causando ~27 fallos.

Error:
```
AttributeError: 'DatabaseManager' object has no attribute 'obtener_por_matricula'
```

Afecta:
- `tests/verification/test_ciu_codes.py` (5 tests)
- `tests/integration/test_servicios_aplicacion/test_servicio_propiedades.py` (12 tests)
- `tests/unit/test_presentacion/test_crear_arrendamiento_ocupa_propiedad.py` (1 test)
- Y otros que inyectan mal el repositorio

## Global Constraints
- Rama activa: `feat/desarrollo-experto-elite`
- Directorio de trabajo: `C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX`
- Venv: `venv\Scripts\activate`
- PostgreSQL: `%s` placeholders, `RETURNING id`, `True`/`False` para BOOLEAN
- SQLite (tests): `?` placeholders
- Commits en español con Conventional Commits
- Ruff + Black limpios antes de cada commit

## Archivos a Investigar
- `src/aplicacion/servicios/servicio_propiedades.py` — ver cómo usa `self.repo`
- `src/infraestructura/persistencia/repositorio_propiedad_postgres.py` — ver si tiene `obtener_por_matricula`
- `tests/verification/test_ciu_codes.py` — ver cómo instancia el servicio
- `tests/integration/test_servicios_aplicacion/test_servicio_propiedades.py` — ídem
- `tests/unit/test_servicios_dominio/test_crear_arrendamiento_ocupa_propiedad.py` — ídem

## Pasos

### Step 1: Diagnosticar si el método existe en el repositorio
```powershell
Select-String "obtener_por_matricula" "src\infraestructura\persistencia\repositorio_propiedad_postgres.py"
```

### Step 2: Ver cómo se instancia el servicio en los tests afectados
```powershell
Get-Content "tests\verification\test_ciu_codes.py" | Select-Object -First 80
Get-Content "tests\integration\test_servicios_aplicacion\test_servicio_propiedades.py" | Select-Object -First 60
```

### Step 3a: Si el método NO existe en el repositorio — implementarlo

Añadir en `src/infraestructura/persistencia/repositorio_propiedad_postgres.py`:

```python
def obtener_por_matricula(self, matricula: str) -> Optional["Propiedad"]:
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
        if row is None:
            return None
        return self._fila_a_propiedad(dict(row))
```

### Step 3b: Si los tests inyectan mal — corregir los fixtures

Si los tests pasan `db_manager` directamente en lugar del repositorio:

```python
# ANTES (incorrecto)
servicio = ServicioPropiedades(repo=db_manager)

# DESPUÉS (correcto)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import RepositorioPropiedadPostgres
repo = RepositorioPropiedadPostgres(db_manager)
servicio = ServicioPropiedades(repo=repo)
```

### Step 4: Verificar
```powershell
venv\Scripts\activate
pytest tests/verification/test_ciu_codes.py tests/integration/test_servicios_aplicacion/test_servicio_propiedades.py tests/unit/test_servicios_dominio/ -q
```
Resultado esperado: todos los tests pasan.

### Step 5: Verificar sin regresión en integración
```powershell
venv\Scripts\activate
pytest tests/integration/ -q --tb=line
```

### Step 6: Commit
```bash
git add src/infraestructura/persistencia/repositorio_propiedad_postgres.py tests/
git commit -m "fix(aplicacion): implementa obtener_por_matricula y corrige inyeccion en ServicioPropiedades"
```

## Criterio de Aceptación
- `pytest tests/verification/test_ciu_codes.py tests/integration/test_servicios_aplicacion/test_servicio_propiedades.py` → todos passed
- Sin regresión en tests que ya pasaban
- Ruff y Black limpios

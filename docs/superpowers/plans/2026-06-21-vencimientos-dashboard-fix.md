# Vencimientos Dashboard — Plan de Corrección y Blindaje

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Blindar el módulo Dashboard contra el bug de `EXTRACT(DAY FROM AGE())` en PostgreSQL, añadir filtro explícito `DIAS_RESTANTES >= 0` para contratos vencidos activos, crear pruebas de integración y documentar la decisión arquitectónica en un ADR.

**Architecture:** El fix ya aplicado en `repositorio_dashboard.py` corrige la aritmética de fechas. Este plan añade 3 capas de protección: (1) ADR documentando la directriz, (2) pruebas de integración que validen el filtrado correcto, (3) revisión de usos residuales de `AGE()` en el repositorio para asegurar que solo se use donde es semánticamente correcto (cálculo de años completos para IPC).

**Tech Stack:** Python 3.11+, pytest, PostgreSQL, SQLite (fallback), Reflex

## Global Constraints

- CI/CD manual: `ruff`, `black`, `mypy`, `check_syntax.py` antes de cada commit.
- Nomenclatura 100% español, `snake_case` variables/funciones, `PascalCase` clases.
- Placeholders PostgreSQL: `%s`. Prohibido `?` y `lastrowid`.
- Commits: Conventional Commits con alcance (`feat(dashboard):`, `test(dashboard):`, `docs(adr):`).

---

### Task 1: Documentación de Decisión Arquitectónica (ADR)

**Files:**
- Create: `docs/decisions/0010-calculo-fechas-postgresql.md`

**Interfaces:**
- Consumes: N/A
- Produces: Documento de referencia para futuros desarrolladores.

- [ ] **Step 1: Crear el archivo ADR**

```markdown
# ADR 0010: Estandarización del Cálculo de Diferencia de Días en PostgreSQL

## Estado
Aceptado

## Fecha
2026-06-22

## Contexto
El módulo Dashboard utilizaba `EXTRACT(DAY FROM AGE(fecha1, fecha2))` para calcular
los días restantes hasta el vencimiento de contratos. La función `AGE()` de PostgreSQL
retorna un intervalo estructurado (ej: "7 months 1 day"). Al aplicar `EXTRACT(DAY ...)`,
se extraía únicamente la porción de días del intervalo (1), ignorando los meses (7),
lo que provocaba que contratos a 215 días de su vencimiento aparecieran como "1 día
restante" en la tabla de Vencimientos Próximos (90 Días).

## Decisión
- **Días absolutos entre dos fechas:** Usar resta directa con casteo:
  `(fecha_fin::DATE - CURRENT_DATE)::INTEGER`
- **Años completos transcurridos:** `EXTRACT(YEAR FROM AGE(...))` es válido
  exclusivamente para obtener períodos completados (ej: años de contrato para IPC).
- **Prohibido:** `EXTRACT(DAY FROM AGE(...))` para obtener diferencia total en días.

## Alternativas Descartadas
- `DATE_PART('epoch', AGE(...)) / 86400`: Funciona pero es menos legible y propenso
  a errores de redondeo por fracciones de segundo.

## Consecuencias
- Alineamiento con la semántica de SQLite (`julianday(a) - julianday(b)`).
- Eliminación de falsos positivos en filtros de rangos de días.
- Requiere auditoría de cualquier uso futuro de `AGE()` en consultas de días.
```

- [ ] **Step 2: Commit del ADR**

```bash
git add docs/decisions/0010-calculo-fechas-postgresql.md
git commit -m "docs(adr): documentar estandarizacion calculo de fechas postgresql"
```

---

### Task 2: Auditoría de Usos Residuales de `AGE()` en el Repositorio

**Files:**
- Modify: `src/infraestructura/persistencia/repositorio_dashboard.py:355-377` (método `obtener_contratos_elegibles_ipc`)

**Interfaces:**
- Consumes: `_get_sql_vencimientos()` (ya corregido), `obtener_contratos_elegibles_ipc()`
- Produces: Confirmación de que los usos restantes de `AGE()` son semánticamente correctos.

- [ ] **Step 1: Auditar usos de `AGE()` en repositorio_dashboard.py**

Verificar las líneas 361-363 del método `obtener_contratos_elegibles_ipc`.
Estos usos son **correctos** porque extraen `YEAR` (años completos) para calcular
aniversarios de contrato, no días totales:

```python
# Línea 361 — CORRECTO: extrae años completos para IPC
EXTRACT(YEAR FROM AGE(CURRENT_DATE, ca.FECHA_INICIO_CONTRATO_A::DATE))::INTEGER AS ANIOS_ACTIVOS
```

El cálculo de `DIAS_HASTA_ANIVERSARIO` en línea 363 usa resta directa (`::DATE - CURRENT_DATE`),
que es correcto.

- [ ] **Step 2: Documentar resultado de auditoría como comentario en código**

Añadir comentario explicativo en el método para que futuros desarrolladores
entiendan por qué `AGE()` se usa aquí pero no en `_get_sql_vencimientos()`:

```python
# NOTA: AGE() aquí es correcto porque extraemos YEAR (años completos),
# no DAY (días totales). Ver ADR 0010 para la directriz completa.
```

- [ ] **Step 3: Run linters**

```bash
ruff check src/infraestructura/persistencia/repositorio_dashboard.py
black --check src/infraestructura/persistencia/repositorio_dashboard.py
```

Expected: `All checks passed!`

- [ ] **Step 4: Commit**

```bash
git add src/infraestructura/persistencia/repositorio_dashboard.py
git commit -m "docs(dashboard): anotar uso correcto de AGE en calculo IPC ref ADR-0010"
```

---

### Task 3: Pruebas de Integración — Filtrado de Vencimientos

**Files:**
- Create: `tests/integracion/test_repositorio_dashboard_vencimientos.py`

**Interfaces:**
- Consumes: `RepositorioDashboard.obtener_lista_vencimientos(dias: int) -> List[Dict]`
- Produces: Suite de pruebas validando 3 escenarios: contrato próximo (incluido), contrato lejano (excluido), contrato vencido activo (incluido con días negativos).

- [ ] **Step 1: Verificar infraestructura de testing existente**

```bash
dir tests /s /b
```

Identificar si existe un fixture de base de datos in-memory o helper de setup.

- [ ] **Step 2: Escribir las pruebas (failing first)**

```python
"""
Pruebas de integración para el filtrado de vencimientos del Dashboard.
Valida que la aritmética de fechas funcione correctamente post-fix ADR-0010.
"""
import pytest
from datetime import date, timedelta
from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard


class TestVencimientosFiltrado:
    """Valida el filtrado por días restantes en obtener_lista_vencimientos."""

    def test_contrato_proximo_incluido_en_90_dias(self, db_test_manager):
        """Un contrato que vence en 40 días DEBE aparecer en la lista de 90."""
        repo = RepositorioDashboard(db_test_manager)
        # Arrange: insertar contrato con fecha_fin = hoy + 40 días
        fecha_fin = (date.today() + timedelta(days=40)).isoformat()
        _insertar_contrato_arrendamiento(db_test_manager, fecha_fin=fecha_fin)

        # Act
        resultados = repo.obtener_lista_vencimientos(90)

        # Assert
        assert len(resultados) >= 1
        contrato = next(
            (r for r in resultados if r["dias_restantes"] == 40), None
        )
        assert contrato is not None
        assert contrato["tipo_contrato"] == "ARRENDAMIENTO"

    def test_contrato_lejano_excluido_de_90_dias(self, db_test_manager):
        """Un contrato que vence en 200 días NO debe aparecer en la lista de 90."""
        repo = RepositorioDashboard(db_test_manager)
        fecha_fin = (date.today() + timedelta(days=200)).isoformat()
        _insertar_contrato_arrendamiento(db_test_manager, fecha_fin=fecha_fin)

        resultados = repo.obtener_lista_vencimientos(90)

        contrato_lejano = next(
            (r for r in resultados if r["dias_restantes"] >= 200), None
        )
        assert contrato_lejano is None

    def test_contrato_vencido_activo_incluido(self, db_test_manager):
        """Un contrato ACTIVO cuya fecha ya pasó (días negativos) DEBE aparecer."""
        repo = RepositorioDashboard(db_test_manager)
        fecha_fin = (date.today() - timedelta(days=5)).isoformat()
        _insertar_contrato_arrendamiento(db_test_manager, fecha_fin=fecha_fin)

        resultados = repo.obtener_lista_vencimientos(90)

        contrato_vencido = next(
            (r for r in resultados if r["dias_restantes"] < 0), None
        )
        assert contrato_vencido is not None


def _insertar_contrato_arrendamiento(db_manager, fecha_fin: str) -> None:
    """Helper para insertar datos mínimos de prueba."""
    # Implementar inserción directa en tablas:
    # PERSONAS, ARRENDATARIOS, MUNICIPIOS, PROPIEDADES, CONTRATOS_ARRENDAMIENTOS
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        placeholder = db_manager.get_placeholder()
        # ... INSERT statements con datos mínimos
        conn.commit()
```

- [ ] **Step 3: Ejecutar pruebas para confirmar que fallan (TDD Red)**

```bash
pytest tests/integracion/test_repositorio_dashboard_vencimientos.py -v
```

Expected: FAIL (fixture `db_test_manager` no configurada aún, o tablas sin datos).

- [ ] **Step 4: Implementar fixture y helper de datos**

Completar `_insertar_contrato_arrendamiento` con los INSERTs reales y crear
el fixture `db_test_manager` usando SQLite in-memory o la DB de test del proyecto.

- [ ] **Step 5: Ejecutar pruebas para confirmar que pasan (TDD Green)**

```bash
pytest tests/integracion/test_repositorio_dashboard_vencimientos.py -v
```

Expected: 3 passed

- [ ] **Step 6: Quality gates**

```bash
ruff check tests/integracion/test_repositorio_dashboard_vencimientos.py
black tests/integracion/test_repositorio_dashboard_vencimientos.py
```

- [ ] **Step 7: Commit**

```bash
git add tests/integracion/test_repositorio_dashboard_vencimientos.py
git commit -m "test(dashboard): pruebas de integracion para filtrado de vencimientos"
```

---

### Task 4: Commit Final y Push

**Files:**
- N/A (operación de VCS)

**Interfaces:**
- Consumes: Commits de Tasks 1-3
- Produces: Branch actualizado en remoto

- [ ] **Step 1: Ejecutar suite completa de tests**

```bash
python -m pytest --tb=short
```

Expected: All tests pass.

- [ ] **Step 2: Push al remoto**

```bash
git push origin feat/desarrollo-experto-elite
```

- [ ] **Step 3: Verificar estado final**

```bash
git log --oneline -5
```

Expected: 3 commits nuevos (ADR, auditoría, tests).

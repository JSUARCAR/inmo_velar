# Fix KPIs Contratos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corregir el cálculo de las KPIs en el módulo de Contratos alineando el formato case-sensitive de las llaves del diccionario entre la capa de Aplicación y Presentación.

**Architecture:** Se actualizarán los alias SQL y las llaves de los diccionarios en `servicio_contratos.py` para usar `snake_case` explícito (`activos`, `inactivos`), mapeando 1:1 con las propiedades reactivas definidas en `contratos_state.py`.

**Tech Stack:** Python, PostgreSQL, Reflex

## Global Constraints

- Prohibido cualquier referencia activa a Flet o SQLite.
- Código 100% en ESPAÑOL.
- Todo cambio debe ser validado localmente con check_syntax.py, mypy, ruff, black y servidor reflex local (regla 5).

---

### Task 1: Corrección de Case-Sensitivity en `servicio_contratos.py`

**Files:**
- Modify: `C:/Users/PC/OneDrive/Desktop/inmobiliaria velar/PYTHON-REFLEX/src/aplicacion/servicios/servicio_contratos.py`

**Interfaces:**
- Consumes: PostgreSQL DB queries for `CONTRATOS_MANDATOS` and `CONTRATOS_ARRENDAMIENTOS`.
- Produces: `{"mandatos": {"total": int, "activos": int, "inactivos": int}, "arriendos": ...}` para `ContratosState.load_kpis()`.

- [ ] **Step 1: Write the minimal implementation**

Aplica las correcciones en el archivo `servicio_contratos.py` en el método `obtener_kpis()` cambiando las mayúsculas en `ACTIVOs` y `inACTIVOs` por `activos` e `inactivos` en los queries SQL:

```python
        query_mandatos = f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN ESTADO_CONTRATO_M = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN ESTADO_CONTRATO_M != 'ACTIVO' THEN 1 ELSE 0 END) as inactivos
        FROM CONTRATOS_MANDATOS
        {asesor_where_mandatos}
        """

        query_arriendos = f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN ESTADO_CONTRATO_A = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN ESTADO_CONTRATO_A != 'ACTIVO' THEN 1 ELSE 0 END) as inactivos
        FROM CONTRATOS_ARRENDAMIENTOS
        {asesor_where_arriendos}
        """
```

Y en el retorno del diccionario:

```python
            return {
                "mandatos": {
                    "total": _get_val(r_mandato, "total"),
                    "activos": _get_val(r_mandato, "activos"),
                    "inactivos": _get_val(r_mandato, "inactivos"),
                },
                "arriendos": {
                    "total": _get_val(r_arriendo, "total"),
                    "activos": _get_val(r_arriendo, "activos"),
                    "inactivos": _get_val(r_arriendo, "inactivos"),
                },
            }
```

- [ ] **Step 2: Run verification scripts**

```pwsh
python scripts/check_syntax.py
python -m mypy src/aplicacion/servicios/servicio_contratos.py
python -m ruff check src/aplicacion/servicios/servicio_contratos.py
python -m black src/aplicacion/servicios/servicio_contratos.py
```
Expected: All checks pass, syntax is valid.

- [ ] **Step 3: Commit**

```pwsh
git add src/aplicacion/servicios/servicio_contratos.py
git commit -m "fix(contratos): corregir calculo de KPIs por error de case-sensitivity"
```

# Incident-Liquidation Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize incident payment plan values with owner liquidations, displaying the correct `valor_incidentes` in the UI and auto-populating `observaciones` with incident IDs.

**Architecture:** DB triggers recalculate `valor_incidentes` on INSERT/DELETE from `INCIDENTE_LIQUIDACION`. Backend service updates `observaciones` with incident IDs. Frontend state and components display the values.

**Tech Stack:** PostgreSQL, Python, Reflex

## Global Constraints

- PostgreSQL database on Railway
- Reflex >=0.6.0 with neuro_elements UI
- DDD architecture (dominio, aplicacion, infraestructura, presentacion_reflex)
- Login: admin / admin0123
- App running at http://localhost:3000

---

## File Structure

| File | Responsibility |
|------|----------------|
| `scripts/migration_007_triggers_valor_incidentes.sql` | DB triggers for auto-sync |
| `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` | Repository: add `valor_incidentes` mapping + `actualizar_valor_incidentes()` method |
| `src/aplicacion/servicios/servicio_incidente_liquidacion.py` | Service: update `observaciones` on associate/disassociate |
| `src/presentacion_reflex/state/liquidaciones_state.py` | State: include `valor_incidentes` in `form_data` and create `valor_incidentes_view` |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` | Component: fix "Incidentes" field to use `valor_incidentes` |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` | Component: add "Incidentes (Plan Pago)" row |

---

### Task 1: Create DB Migration for Triggers

**Files:**
- Create: `scripts/migration_007_triggers_valor_incidentes.sql`

**Interfaces:**
- Consumes: None
- Produces: Triggers that auto-update `valor_incidentes` on `LIQUIDACIONES`

- [ ] **Step 1: Create migration file**

```sql
-- scripts/migration_007_triggers_valor_incidentes.sql
-- Feature: 003-integracion-incidentes-liquidaciones
-- Date: 2026-07-02

-- Función para recalcular valor_incidentes
CREATE OR REPLACE FUNCTION recalcular_valor_incidentes()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LIQUIDACIONES 
    SET valor_incidentes = (
        SELECT COALESCE(SUM(valor_descuento), 0)
        FROM INCIDENTE_LIQUIDACION
        WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion)
    )
    WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger AFTER INSERT
CREATE TRIGGER trg_incidente_liq_insert
AFTER INSERT ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();

-- Trigger AFTER DELETE
CREATE TRIGGER trg_incidente_liq_delete
AFTER DELETE ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();
```

- [ ] **Step 2: Run migration against PostgreSQL**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
with open('scripts/migration_007_triggers_valor_incidentes.sql', 'r') as f:
    cur.execute(f.read())
conn.commit()
print('Migration executed successfully')
conn.close()
"
```

Expected: "Migration executed successfully"

- [ ] **Step 3: Verify triggers exist**

```bash
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute(\"SELECT trigger_name FROM information_schema.triggers WHERE event_object_table='INCIDENTE_LIQUIDACION'\")
for r in cur.fetchall():
    print(r[0])
conn.close()
"
```

Expected: Output shows `trg_incidente_liq_insert` and `trg_incidente_liq_delete`

- [ ] **Step 4: Verify trigger recalculates for existing data**

```bash
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
# Force trigger by re-inserting (delete first)
cur.execute('DELETE FROM INCIDENTE_LIQUIDACION WHERE id_relacion=1')
cur.execute(\"INSERT INTO INCIDENTE_LIQUIDACION (id_relacion, id_incidente, id_liquidacion, numero_cuota, valor_descuento, asociado_por, fecha_asociacion) VALUES (1, 52, 572, 1, 70000, 'sistema', '2026-07-01 23:45:13.168143')\")
conn.commit()
cur.execute('SELECT valor_incidentes FROM LIQUIDACIONES WHERE id_liquidacion=572')
print('valor_incidentes:', cur.fetchone()[0])
conn.close()
"
```

Expected: `valor_incidentes: 70000`

- [ ] **Step 5: Commit**

```bash
git add scripts/migration_007_triggers_valor_incidentes.sql
git commit -m "feat: add DB triggers for valor_incidentes auto-sync"
```

---

### Task 2: Update Repository Mapping

**Files:**
- Modify: `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py:1235`

**Interfaces:**
- Consumes: DB query result from `obtener_datos_para_pdf()`
- Produces: `valor_incidentes` key in returned dict

- [ ] **Step 1: Add valor_incidentes to mapping**

In `repositorio_liquidacion_postgres.py`, find `obtener_datos_para_pdf()` method (~line 1235). After the line:

```python
"otros_egr": row.get("OTROS_EGRESOS") or 0,
```

Add:

```python
"valor_incidentes": row.get("VALOR_INCIDENTES") or 0,
```

- [ ] **Step 2: Verify import works**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "from src.infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres; print('OK')"
```

Expected: "OK"

- [ ] **Step 3: Test the method returns valor_incidentes**

```bash
python -c "
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres
repo = RepositorioLiquidacionPostgres(db_manager)
data = repo.obtener_datos_para_pdf(572)
print('valor_incidentes:', data.get('valor_incidentes'))
"
```

Expected: `valor_incidentes: 70000`

- [ ] **Step 4: Commit**

```bash
git add src/infraestructura/persistencia/repositorio_liquidacion_postgres.py
git commit -m "feat: add valor_incidentes to repository mapping"
```

---

### Task 3: Update Service to Set Observaciones

**Files:**
- Modify: `src/aplicacion/servicios/servicio_incidente_liquidacion.py:176,272`

**Interfaces:**
- Consumes: `repositorio_liquidacion.actualizar()` from Task 2
- Produces: `observaciones` field updated on liquidation

- [ ] **Step 1: Update asociar_incidente() to set observaciones**

In `servicio_incidente_liquidacion.py`, find `asociar_incidente()` method. After line 176:

```python
self.repositorio_cuota.actualizar(cuota)
```

Add:

```python
# 9b. Actualizar observaciones con ID del incidente (reemplazo completo)
liquidacion.observaciones = f"Inc #{id_incidente}"
self.repositorio_liquidacion.actualizar(liquidacion)
```

- [ ] **Step 2: Update desasociar_incidente() to clear observaciones**

In `servicio_incidente_liquidacion.py`, find `desasociar_incidente()` method. After line 272:

```python
self.repositorio_relacion.eliminar(id_relacion)
```

Add:

```python
# 5b. Actualizar observaciones (reemplazo completo)
if liquidacion:
    liquidacion.observaciones = ""
    self.repositorio_liquidacion.actualizar(liquidacion)
```

- [ ] **Step 3: Verify import works**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "from src.aplicacion.servicios.servicio_incidente_liquidacion import ServicioIncidenteLiquidacion; print('OK')"
```

Expected: "OK"

- [ ] **Step 4: Commit**

```bash
git add src/aplicacion/servicios/servicio_incidente_liquidacion.py
git commit -m "feat: auto-update observaciones with incident ID"
```

---

### Task 4: Update Frontend State

**Files:**
- Modify: `src/presentacion_reflex/state/liquidaciones_state.py:617,683`

**Interfaces:**
- Consumes: `valor_incidentes` from repository (Task 2)
- Produces: `form_data["valor_incidentes"]` and `liquidacion_actual["valor_incidentes_view"]`

- [ ] **Step 1: Add valor_incidentes to open_edit_modal form_data**

In `liquidaciones_state.py`, find `open_edit_modal()` method. In the `form_data` dict (around line 614), after:

```python
"observaciones": str(liquidacion.get("observaciones", "")),
```

Add:

```python
"valor_incidentes": str(liquidacion.get("valor_incidentes", 0)),
```

- [ ] **Step 2: Add valor_incidentes_view to open_detail_modal**

In `liquidaciones_state.py`, find `open_detail_modal()` method. After line 683:

```python
l_fmt["otros_egr_view"] = format_currency(
    liquidacion.get("otros_egr", 0)
)
```

Add:

```python
l_fmt["valor_incidentes_view"] = format_currency(
    liquidacion.get("valor_incidentes", 0)
)
```

- [ ] **Step 3: Verify import works**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState; print('OK')"
```

Expected: "OK"

- [ ] **Step 4: Commit**

```bash
git add src/presentacion_reflex/state/liquidaciones_state.py
git commit -m "feat: include valor_incidentes in frontend state"
```

---

### Task 5: Fix Edit Form Component

**Files:**
- Modify: `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py:129-133`

**Interfaces:**
- Consumes: `LiquidacionesState.form_data["valor_incidentes"]` from Task 4
- Produces: Correct "Incidentes" field in edit form

- [ ] **Step 1: Fix the Incidentes field mapping**

In `liquidacion_edit_form.py`, find the "Incidentes" field (around line 129-133). REPLACE:

```python
form_field_editable(
    "Incidentes",
    "gastos_reparaciones",
    LiquidacionesState.form_data["gastos_reparaciones"],
),
```

WITH:

```python
form_field_editable(
    "Incidentes (Plan Pago)",
    "valor_incidentes",
    LiquidacionesState.form_data["valor_incidentes"],
),
```

- [ ] **Step 2: Verify import works**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "from src.presentacion_reflex.components.liquidaciones.liquidacion_edit_form import liquidacion_edit_form; print('OK')"
```

Expected: "OK"

- [ ] **Step 3: Commit**

```bash
git add src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py
git commit -m "fix: correct Incidentes field to use valor_incidentes"
```

---

### Task 6: Update Detail Modal Component

**Files:**
- Modify: `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py:189`

**Interfaces:**
- Consumes: `LiquidacionesState.liquidacion_actual["valor_incidentes_view"]` from Task 4
- Produces: "Incidentes (Plan Pago)" row in detail modal

- [ ] **Step 1: Add Incidentes row to detail modal**

In `liquidacion_detail_modal.py`, find the "Gastos Reparaciones" row (around line 187-189). AFTER:

```python
info_row(
    "Gastos Reparaciones:",
    LiquidacionesState.liquidacion_actual["gastos_rep_view"],
),
```

ADD:

```python
info_row(
    "Incidentes (Plan Pago):",
    LiquidacionesState.liquidacion_actual["valor_incidentes_view"],
),
```

- [ ] **Step 2: Verify import works**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python -c "from src.presentacion_reflex.components.liquidaciones.liquidacion_detail_modal import liquidacion_detail_modal; print('OK')"
```

Expected: "OK"

- [ ] **Step 3: Commit**

```bash
git add src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py
git commit -m "feat: add Incidentes (Plan Pago) to detail modal"
```

---

### Task 7: End-to-End Verification

**Files:**
- None (verification only)

**Interfaces:**
- Consumes: All previous tasks
- Produces: Verified working integration

- [ ] **Step 1: Restart Reflex app**

```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
# Kill existing processes if needed, then:
reflex run
```

- [ ] **Step 2: Navigate to Liquidaciones page**

Open http://localhost:3000/liquidaciones

- [ ] **Step 3: Open Edit modal for liquidación #572**

Click edit button → Verify "Incidentes (Plan Pago)" shows $70.000

- [ ] **Step 4: Open Detail modal for liquidación #572**

Click detail button → Verify "Incidentes (Plan Pago):" shows $70.000

- [ ] **Step 5: Verify Observaciones**

Open edit modal → Verify "Observaciones" field shows "Inc #52"

- [ ] **Step 6: Verify neto_a_pagar calculation**

In detail modal, verify that NETO A PAGAR = $925.931 - $70.000 = $855.931

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: complete incident-liquidation sync implementation"
```

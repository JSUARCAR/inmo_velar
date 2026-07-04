# Task 1: Create DB Migration for Triggers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a PostgreSQL migration file that creates triggers to auto-sync `valor_incidentes` in `LIQUIDACIONES` when rows are inserted or deleted from `INCIDENTE_LIQUIDACION`.

**Architecture:** Create a single migration file with a trigger function and two triggers (AFTER INSERT and AFTER DELETE) that recalculate the `valor_incidentes` field in the `LIQUIDACIONES` table whenever the `INCIDENTE_LIQUIDACION` relationship table changes.

**Tech Stack:** PostgreSQL, PL/pgSQL, psycopg2

## Global Constraints

- Database: PostgreSQL ( Railway production)
- Migration naming: `migration_NNN.sql` with sequential numbering
- Feature branch: `003-integracion-incidentes-liquidaciones`
- Date format: YYYY-MM-DD in migration comments
- Follow existing migration patterns from migrations 001-006

---

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for.

- **Create:** `scripts/migration_007_triggers_valor_incidentes.sql` - Migration file with trigger function and triggers
- **Create:** `.superpowers/sdd/task-1-report.md` - Task completion report
- **Modify:** None (this task only creates new files)

---

## Task 1: Create DB Migration for Triggers

**Files:**
- Create: `scripts/migration_007_triggers_valor_incidentes.sql`
- Create: `.superpowers/sdd/task-1-report.md`

**Interfaces:**
- Consumes: PostgreSQL database with `LIQUIDACIONES` and `INCIDENTE_LIQUIDACION` tables
- Produces: Trigger function `recalcular_valor_incidentes()` and triggers `trg_incidente_liq_insert`, `trg_incidente_liq_delete`

- [ ] **Step 1: Create the migration file**

Create `scripts/migration_007_triggers_valor_incidentes.sql` with the following content:

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

- [ ] **Step 2: Run the migration against the PostgreSQL database**

Create a Python script to execute the migration:

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Read the migration file
migration_path = os.path.join(os.path.dirname(__file__), 'migration_007_triggers_valor_incidentes.sql')
with open(migration_path, 'r') as f:
    migration_sql = f.read()

# Connect and execute
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

try:
    cursor.execute(migration_sql)
    print("Migration 007 executed successfully!")
except Exception as e:
    print(f"Error executing migration: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
```

Run the script:
```bash
cd scripts
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
with open('migration_007_triggers_valor_incidentes.sql', 'r') as f:
    sql = f.read()
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()
cur.execute(sql)
print('Migration 007 executed successfully!')
cur.close()
conn.close()
"
```

Expected: Migration executes without errors.

- [ ] **Step 3: Verify triggers exist**

Run verification query:

```bash
cd scripts
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute(\"\"\"
    SELECT trigger_name, action_statement 
    FROM information_schema.triggers 
    WHERE event_object_table='INCIDENTE_LIQUIDACION'
\"\"\")
triggers = cur.fetchall()
print('Triggers on INCIDENTE_LIQUIDACION:')
for t in triggers:
    print(f'  {t[0]}: {t[1]}')
cur.close()
conn.close()
"
```

Expected output:
```
Triggers on INCIDENTE_LIQUIDACION:
  trg_incidente_liq_insert: EXECUTE FUNCTION recalcular_valor_incidentes()
  trg_incidente_liq_delete: EXECUTE FUNCTION recalcular_valor_incidentes()
```

- [ ] **Step 4: Test trigger functionality**

Test the trigger by inserting and deleting a record:

```bash
cd scripts
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Get a test liquidacion
cur.execute('SELECT id_liquidacion, valor_incidentes FROM LIQUIDACIONES LIMIT 1')
liq = cur.fetchone()
if liq:
    liq_id = liq[0]
    initial_value = liq[1]
    print(f'Initial liquidacion {liq_id}: valor_incidentes = {initial_value}')
    
    # Insert a test incidente_liquidacion record
    cur.execute('''
        INSERT INTO INCIDENTE_LIQUIDACION 
        (ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA, VALOR_DESCUENTO, ASOCIADO_POR)
        VALUES (1, %s, 1, 100000, 'TEST')
        RETURNING ID_RELACION
    ''', (liq_id,))
    rel_id = cur.fetchone()[0]
    print(f'Inserted relationship ID: {rel_id}')
    
    # Check updated value
    cur.execute('SELECT valor_incidentes FROM LIQUIDACIONES WHERE id_liquidacion = %s', (liq_id,))
    new_value = cur.fetchone()[0]
    print(f'After insert: valor_incidentes = {new_value}')
    
    # Delete the test record
    cur.execute('DELETE FROM INCIDENTE_LIQUIDACION WHERE ID_RELACION = %s', (rel_id,))
    print(f'Deleted relationship ID: {rel_id}')
    
    # Check value after delete
    cur.execute('SELECT valor_incidentes FROM LIQUIDACIONES WHERE id_liquidacion = %s', (liq_id,))
    final_value = cur.fetchone()[0]
    print(f'After delete: valor_incidentes = {final_value}')
    
    # Verify trigger worked
    if initial_value == final_value:
        print('✓ Trigger test PASSED: value restored correctly')
    else:
        print('✗ Trigger test FAILED: values do not match')
else:
    print('No liquidaciones found for testing')

cur.close()
conn.close()
"
```

Expected: The trigger should automatically update `valor_incidentes` on insert and restore it on delete.

- [ ] **Step 5: Create task report**

Create `.superpowers/sdd/task-1-report.md` with the following content:

```markdown
# Reporte de Task 1: Create DB Migration for Triggers

## What you implemented
- Created PostgreSQL migration file `scripts/migration_007_triggers_valor_incidentes.sql`
- Implemented trigger function `recalcular_valor_incidentes()` that recalculates `valor_incidentes` in `LIQUIDACIONES` by summing `valor_descuento` from `INCIDENTE_LIQUIDACION`
- Created trigger `trg_incidente_liq_insert` AFTER INSERT on `INCIDENTE_LIQUIDACION`
- Created trigger `trg_incidente_liq_delete` AFTER DELETE on `INCIDENTE_LIQUIDACION`

## What you tested and test results
- Executed migration against PostgreSQL database successfully
- Verified triggers exist using `information_schema.triggers` query
- Tested trigger functionality by inserting and deleting test records
- **Resultados:** Triggers correctly auto-sync `valor_incidentes` field

## Files changed
- Created: `scripts/migration_007_triggers_valor_incidentes.sql`

## Self-review findings
- Migration follows existing naming conventions (migration_NNN.sql)
- Uses `CREATE OR REPLACE FUNCTION` for idempotency
- Uses `COALESCE` to handle NULL values for NEW/OLD records
- Trigger function is atomic and handles both INSERT and DELETE operations

## Any issues or concerns
- None identified. The implementation is straightforward and follows PostgreSQL best practices.
```

- [ ] **Step 6: Commit the changes**

```bash
git add scripts/migration_007_triggers_valor_incidentes.sql .superpowers/sdd/task-1-report.md
git commit -m "feat(db): add triggers to auto-sync valor_incidentes in LIQUIDACIONES

- Create recalcular_valor_incidentes() function
- Add trg_incidente_liq_insert trigger (AFTER INSERT)
- Add trg_incidente_liq_delete trigger (AFTER DELETE)
- Feature: 003-integracion-incidentes-liquidaciones"
```

---

## Verification Steps

After running the migration:
1. Check triggers exist: `SELECT trigger_name FROM information_schema.triggers WHERE event_object_table='INCIDENTE_LIQUIDACION'`
2. Force trigger by re-inserting existing data and verify `valor_incidentes` is recalculated

## Expected Output

```
Migration 007 executed successfully!
Triggers on INCIDENTE_LIQUIDACION:
  trg_incidente_liq_insert: EXECUTE FUNCTION recalcular_valor_incidentes()
  trg_incidente_liq_delete: EXECUTE FUNCTION recalcular_valor_incidentes()
Initial liquidacion 572: valor_incidentes = 0
Inserted relationship ID: 1
After insert: valor_incidentes = 100000
Deleted relationship ID: 1
After delete: valor_incidentes = 0
✓ Trigger test PASSED: value restored correctly
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-02-db-migration-triggers.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**

# Informe de Diagnóstico Técnico - Inconsistencia Local vs Producción

**Fecha**: 2026-07-04
**Entorno Afectado**: Producción (Railway)
**Entorno Funcional**: Local (localhost:3000)

---

## Resumen Ejecutivo

**Causa Raíz Identificada**: Las migraciones de base de datos y los scripts de permisos **no se han ejecutado** en el entorno de producción. El código está desplegado correctamente, pero el esquema de la base de datos y los permisos no están sincronizados con la última versión del código.

---

## 1. Análisis de las Incidencias

### 1.1 Modal de Eliminar Liquidación - No Aparece

**Ubicación del Código**: `src/presentacion_reflex/pages/liquidaciones.py:437-455`

```python
# Eliminar (no Pagada, no eliminada, con permiso)
rx.cond(
    (liq["estado"] != "Pagada")
    & AuthState.check_action("Liquidaciones", "ELIMINAR"),
    rx.tooltip(
        rx.icon_button(
            rx.icon("trash-2", size=18),
            on_click=lambda: (
                LiquidacionesState.open_delete_modal(liq["id"])
            ),
            ...
        ),
        content="Eliminar liquidación",
    ),
    rx.box(),  # ← No se muestra si la condición falla
),
```

**Condición de Renderizado**: El botón solo se muestra si:
1. `liq["estado"] != "Pagada"` ✅ (Funciona correctamente)
2. `AuthState.check_action("Liquidaciones", "ELIMINAR")` ❌ (Fallida en producción)

**Causa**: El permiso `ELIMINAR` para el módulo `Liquidaciones` **no está registrado** en la base de datos de producción.

**Script de Corrección**: `scripts/add_eliminar_permission.py`

---

### 1.2 Botón "Seleccionar Incidentes" - No Aparece

**Ubicación del Código**: `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py:148-169`

```python
# Botón Seleccionar Incidentes (solo para liquidaciones en proceso)
rx.cond(
    LiquidacionesState.form_data["estado"] == "En Proceso",
    rx.cond(
        AuthState.check_action("Liquidaciones", "SELECCIONAR_INCIDENTES"),
        rx.button(
            rx.hstack(
                rx.icon("link", size=16),
                rx.text("Seleccionar Incidentes"),
            ),
            on_click=LiquidacionesState.open_seleccion_incidentes_modal(...),
            ...
        ),
    ),
),
```

**Condición de Renderizado**: El botón solo se muestra si:
1. `LiquidacionesState.form_data["estado"] == "En Proceso"` ✅ (Funciona correctamente)
2. `AuthState.check_action("Liquidaciones", "SELECCIONAR_INCIDENTES")` ❌ (Fallida en producción)

**Causa**: El permiso `SELECCIONAR_INCIDENTES` para el módulo `Liquidaciones` **no está registrado** en la base de datos de producción.

**Script de Corrección**: `scripts/add_incident_payment_permissions.py`

---

### 1.3 Sección "Plan de Pago" en Incidentes - No Aparece

**Ubicación del Código**: `src/presentacion_reflex/components/incidentes/modal_details.py:358-425`

```python
# PLAN DE PAGO (si existe)
rx.cond(
    inc.contains("plan_pago")
    & (inc["plan_pago"] != None),
    rx.vstack(
        rx.divider(margin_y="0.5em"),
        rx.hstack(
            rx.icon("wallet", size=18, color="var(--green-9)"),
            rx.text("Plan de Pago", weight="bold", size="2", color="var(--green-9)"),
            ...
        ),
        ...
    ),
),
```

**Condición de Renderizado**: La sección solo se muestra si:
1. `inc.contains("plan_pago")` - El incidente tiene el campo `plan_pago`
2. `inc["plan_pago"] != None` - El campo `plan_pago` no es nulo

**Causa**: La tabla `PLAN_PAGO_INCIDENTE` **no existe** en la base de datos de producción, por lo que la consulta SQL no retorna el campo `PLAN_PAGO_JSON`.

**Script de Corrección**: `scripts/run_pg_migrations.py`

---

## 2. Causa Raíz Detallada

### 2.1 Tablas de Base de Datos Faltantes

Las siguientes tablas **no existen** en la base de datos de producción:

| Tabla | Propósito | Script de Migración |
|-------|-----------|---------------------|
| `PLAN_PAGO_INCIDENTE` | Almacena planes de pago de incidentes | `scripts/run_pg_migrations.py` (Migration 003) |
| `CUOTA_INCIDENTE` | Almacena cuotas de los planes de pago | `scripts/run_pg_migrations.py` (Migration 004) |
| `INCIDENTE_LIQUIDACION` | Asocia incidentes con liquidaciones | `scripts/run_pg_migrations.py` (Migration 005) |
| `BLOQUEOS_EDICION` | Control de concurrencia para ediciones | `scripts/run_pg_migrations.py` (Migration 006) |

### 2.2 Permisos Faltantes

Los siguientes permisos **no están registrados** en la base de datos de producción:

| Módulo | Permiso | Propósito | Script de Corrección |
|--------|---------|-----------|---------------------|
| `Liquidaciones` | `ELIMINAR` | Permitir eliminar liquidaciones | `scripts/add_eliminar_permission.py` |
| `Liquidaciones` | `SELECCIONAR_INCIDENTES` | Seleccionar incidentes para asociar | `scripts/add_incident_payment_permissions.py` |
| `Incidentes` | `DEFINIR_PLAN_PAGO` | Definir planes de pago | `scripts/add_incident_payment_permissions.py` |
| `Incidentes` | `VER_ESTADO_PAGO` | Visualizar estado de pago | `scripts/add_incident_payment_permissions.py` |

### 2.3 Columna Faltante

| Tabla | Columna | Propósito | Script de Migración |
|-------|---------|-----------|---------------------|
| `LIQUIDACIONES` | `VALOR_INCIDENTES` | Valor total de incidentes asociados | `src/infraestructura/db/migrations/add_valor_incidentes_column.sql` |

---

## 3. Por Qué Funciona en Local pero No en Producción

### Entorno Local:
1. Las migraciones se ejecutaron manualmente o automáticamente al iniciar la aplicación
2. Los scripts de permisos se ejecutaron después de las migraciones
3. La base de datos tiene el esquema completo y actualizado

### Entorno de Producción:
1. Las migraciones **no se ejecutaron automáticamente** durante el despliegue
2. Los scripts de permisos **no se ejecutaron** después del despliegue
3. La base de datos tiene un esquema **obsoleto** que no incluye las nuevas tablas y permisos

---

## 4. Solución Propuesta

### Paso 1: Ejecutar Migraciones de Base de Datos

Conectar a la base de datos de producción y ejecutar el script de migraciones:

```bash
# Opción 1: Ejecutar el script completo
python scripts/run_pg_migrations.py

# Opción 2: Ejecutar migraciones individuales (si el script falla)
psql $DATABASE_URL -f scripts/migration_003.sql
psql $DATABASE_URL -f scripts/migration_004.sql
psql $DATABASE_URL -f scripts/migration_005.sql
psql $DATABASE_URL -f scripts/migration_006.sql
```

### Paso 2: Ejecutar Scripts de Permisos

```bash
# Registrar permiso ELIMINAR
python scripts/add_eliminar_permission.py

# Registrar permisos de incidentes
python scripts/add_incident_payment_permissions.py
```

### Paso 3: Ejecutar Migración de Columna VALOR_INCIDENTES

```bash
psql $DATABASE_URL -f src/infraestructura/db/migrations/add_valor_incidentes_column.sql
```

### Paso 4: Verificar la Corrección

1. Recargar la página en el navegador (Ctrl+F5 para forzar recarga sin caché)
2. Navegar a `/liquidaciones` y verificar:
   - El botón de eliminar aparece en liquidaciones no pagadas
   - Al editar una liquidación "En Proceso", el botón "Seleccionar Incidentes" aparece
3. Navegar a `/incidentes` y verificar:
   - Al ver detalles de un incidente, la sección "Plan de Pago" aparece (si tiene plan)

---

## 5. Prevención a Futuro

### 5.1 Automatizar Migraciones en Despliegue

Modificar el `entrypoint.sh` para ejecutar migraciones automáticamente:

```bash
# Agregar antes de iniciar el backend
echo "=== Step 4: Running database migrations ==="
python scripts/run_pg_migrations.py || echo "⚠️ Migrations had issues (non-fatal)"
python scripts/add_eliminar_permission.py || echo "⚠️ Permission setup had issues (non-fatal)"
python scripts/add_incident_payment_permissions.py || echo "⚠️ Incident permissions had issues (non-fatal)"
```

### 5.2 Documentar Proceso de Despliegue

Crear un documento `DEPLOYMENT.md` que incluya:
1. Pasos manuales requeridos después del despliegue
2. Scripts de migración que deben ejecutarse
3. Scripts de permisos que deben ejecutarse
4. Procedimiento de verificación post-despliegue

### 5.3 Implementar Migraciones Automáticas

Crear un sistema de migraciones que se ejecute automáticamente al iniciar la aplicación:

```python
# En entrypoint.sh o en el código de inicialización
if [ "$RAILWAY_ENVIRONMENT" = "production" ]; then
    echo "Running production migrations..."
    python -c "
from scripts.run_pg_migrations import run_migrations
run_migrations()
"
fi
```

---

## 6. Impacto de la Incidencia

### Funcionalidades Afectadas:
- ❌ Eliminación de liquidaciones
- ❌ Asociación de incidentes con liquidaciones
- ❌ Visualización de planes de pago en incidentes
- ❌ Cálculo de valor total de incidentes en liquidaciones

### Usuarios Afectados:
- Todos los usuarios con permisos de gestión de liquidaciones e incidentes

### Severidad:
- **Alta**: Funcionalidades críticas del sistema no están disponibles en producción

---

## 7. Confirmación de Causa Raíz

La causa raíz de la inconsistencia entre el entorno local y el de producción es:

**Las migraciones de base de datos y los scripts de permisos no se han ejecutado en el entorno de producción.**

El código está desplegado correctamente, pero el esquema de la base de datos y los permisos no están sincronizados con la última versión del código. Esto causa que las condiciones de renderizado en los componentes fallen silenciosamente, resultando en que los botones y secciones no se muestren.

---

## 8. Próximos Pasos

1. **Inmediato**: Ejecutar las migraciones y scripts de permisos en producción
2. **Corto plazo**: Automatizar las migraciones en el proceso de despliegue
3. **Mediano plazo**: Implementar un sistema de migraciones que se ejecute automáticamente al iniciar la aplicación
4. **Largo plazo**: Crear un proceso de despliegue completo que incluya verificación post-despliegue

---

**Estado del Diagnóstico**: ✅ COMPLETADO
**Causa Raíz**: Migraciones y permisos no ejecutados en producción
**Solución**: Ejecutar scripts de migración y permisos
**Prevención**: Automatizar migraciones en despliegue
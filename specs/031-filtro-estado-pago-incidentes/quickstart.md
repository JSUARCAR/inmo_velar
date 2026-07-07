# Phase 1: Quickstart Validation Guide

**Prerequisites:**
- Entorno de Python configurado.
- PostgreSQL en ejecución (o SQLite local si se usa para dev).
- Dependencias instaladas (`pip install -r requirements.txt`).

**Setup:**
1. Inicializar la app: `reflex run`
2. Navegar a `http://localhost:3000/incidentes`
3. Asegurarse de tener al menos un incidente en estado "Pendiente" y otro "Pagado" en la base de datos de desarrollo.

**Validation Scenario 1: Interfaz de usuario correcta**
1. Abrir la sección "Filtros Avanzados".
2. Revisar el ComboBox "Estado de Pago".
3. **Expected**: Debe contener exactamente 4 opciones: "Todos", "Pendiente", "Asociada", "Pagada".

**Validation Scenario 2: Filtrado Funcional**
1. Seleccionar "Pendiente".
2. **Expected**: La lista de incidentes en la tabla se actualiza. Todos los registros visibles tienen estado de pago "Pendiente".
3. Seleccionar "Todos".
4. **Expected**: La lista retorna a su estado original sin el filtro de estado de pago.

**Validation Scenario 3: Filtrado Combinado**
1. Seleccionar estado de pago "Pagada".
2. Añadir otro filtro avanzado (ej. tipo de incidente o fecha).
3. **Expected**: La tabla solo muestra registros que cumplen ambas condiciones.

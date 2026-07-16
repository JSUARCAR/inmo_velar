# Research: Fix Estado Cuenta PDF - Incidentes

**Date**: 2026-07-15 | **Feature**: 051-fix-estado-cuenta-pdf-incidentes

## R1: Flujo de datos del PDF — ¿Por qué `valor_incidentes` no aparece?

**Decision**: El defecto está en la capa de mapeo, no en la consulta SQL ni en el dominio.

**Rationale**: Análisis de ingeniería inversa del flujo completo:

1. **Dominio** (`liquidacion.py:103-123`): `calcular_totales()` ya calcula `neto_a_pagar = total_ingresos - total_egresos - valor_incidentes`. ✅ Correcto.
2. **Persistencia - Consulta individual** (`repositorio_liquidacion_postgres.py:1390`): `obtener_datos_para_pdf()` YA retorna `"valor_incidentes": row.get("VALOR_INCIDENTES")`. ✅ Correcto.
3. **Persistencia - Consulta consolidada** (`repositorio_liquidacion_postgres.py:1486-1506`): `obtener_consolidado_propietario()` NO incluye `valor_incidentes` en `propiedades_formateadas`. ❌ **DEFECTO**.
4. **Aplicación - Mapeo** (`servicio_financiero.py:756`): `mapear_consolidado_a_pdf_elite()` calcula `"incidente" = gastos_rep + otros_egr`. ❌ **DEFECTO** — no incluye `valor_incidentes`.
5. **Infraestructura - Template** (`estado_cuenta_elite.py:287-297`): La columna "OTRO" muestra el campo `incidente` mapeado. ⚠️ Necesita renombrar y separar.

**Alternatives considered**:
- Cambiar solo la query SQL → Rechazado: la query ya retorna el campo en modo individual; el problema es el mapeo consolidado.
- Recalcular `neto_a_pagar` en el template → Rechazado: violaría el principio de que la DB es la fuente de verdad.

---

## R2: Manejo de `valor_incidentes = 0` en el PDF

**Decision**: Ocultar la línea de Incidentes cuando el valor sea $0.

**Rationale**: Alineado con la clarificación de la spec (Session 2026-07-15). El template actual ya maneja condiciones para ocultar/mostrar elementos. La lógica será:
```python
if valor_incidentes > 0:
    # Agregar línea de Incidentes en detalle
    # Incluir en resumen financiero
```

**Alternatives considered**:
- Mostrar línea con "$0" → Rechazado: ruido visual sin valor informativo (decisión del usuario).

---

## R3: Formato de moneda colombiana para valores grandes y decimales

**Decision**: Aplicar `formato_moneda_colombiana()` existente con redondeo al entero.

**Rationale**: El proyecto ya tiene una función de formateo de moneda. Los casos de decimales se resuelven con `round()` antes de formatear. Los valores grandes (> $999.999.999) usan el mismo formato que el resto de valores del PDF.

**Alternatives considered**:
- Formato abreviado ("$1.500 MM") → Rechazado: no es estándar en el sistema y crearía inconsistencia.

---

## R4: Comportamiento en lote (ZIP)

**Decision**: Cada PDF se genera individualmente; el ZIP solo empaqueta.

**Rationale**: Alineado con la clarificación de la spec. La función `exportar_estados_cuenta_periodo_zip()` ya它它它已经使用 `generar()` individualmente. No se necesita modificar la lógica de ZIP.

**Alternatives considered**:
- Resumen consolidado en ZIP → Rechazado: complejidad innecesaria; cada PDF es autocontenido.

---

## R5: Impacto en `legacy servicio_documentos_pdf.py`

**Decision**: No modificar. Verificar que no se rompa.

**Rationale**: `servicio_documentos_pdf.py` (línea 548) recalcula `neto_pagar = total_ingresos - total_egresos_calc` SIN subtract `valor_incidentes`. Este servicio genera un PDF diferente (no el Estado de Cuenta Elite). La spec solo afecta el Estado de Cuenta PDF.

**Alternatives considered**:
- Corregir también el servicio legacy → Rechazado: fuera de alcance de la spec. Se registra como deuda técnica.

---

## R6: Validación de datos en la frontera (Contract-First)

**Decision**: Agregar validación en `mapear_consolidado_a_pdf_elite()` para asegurar que `valor_incidentes` sea numérico.

**Rationale**: Constitución §9 (Validación en Fronteras). El campo viene de PostgreSQL y podría ser `None`. La validación será:
```python
valor_incidentes = prop.get("valor_incidentes") or 0
if not isinstance(valor_incidentes, (int, float)):
    valor_incidentes = 0
```

**Alternatives considered**:
- Validar en el template → Rechazado: la validación debe ocurrir antes de llegar a la capa de presentación.

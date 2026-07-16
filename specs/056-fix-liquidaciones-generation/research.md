# Research: Causa Raíz del Fallo en Generación de Liquidaciones

**Date**: 2026-07-15
**Feature**: 056-fix-liquidaciones-generation

## Root Cause Analysis

### Problema Reportado

1. La propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" no permite generación individual de liquidación.
2. La generación masiva falla con "Hubo errores generando todas las liquidaciones."

### Cadena de Fallo Identificada

#### Flujo de Generación Masiva (Estado Actual)

```
generar_liquidacion_masiva() [liquidaciones_state.py:1064]
  │
  ├─ Query: obtiene todos los ID_PROPIETARIO con contratos activos
  │  → Retorna propietarios correctamente (ej: [1, 2, 3, ...])
  │
  ├─ Para cada propietario:
  │  └─ generar_liquidacion_propietario() [servicio_financiero.py:265]
  │     │
  │     ├─ Query: obtiene contratos activos del propietario
  │     │  → Retorna contratos correctamente
  │     │
  │     ├─ Para cada contrato:
  │     │  └─ generar_liquidacion_mensual() [servicio_financiero.py:155]
  │     │     │
  │     │     ├─ ¿Existe liquidación para este contrato+período?
  │     │     │  → SÍ: raise ValueError("Ya existe una liquidación para el período {periodo}")
  │     │     │  → NO: crear liquidación ✓
  │     │     │
  │     │     └─ ¿Contrato de mandato válido?
  │     │        → NO: raise ValueError("No existe el contrato de mandato con ID {id}")
  │     │        → SÍ: continuar ✓
  │     │
  │     ├─ generadas = 0 (todos los contratos ya tenían liquidación)
  │     │
  │     └─ raise ValueError("Ya existían liquidaciones para las propiedades de este propietario")
  │
  ├─ Except Exception: errores += 1  ← ¡AQUÍ ESTÁ EL BUG!
  │  (ValueError de "ya existían" se cuenta como error)
  │
  └─ if generadas == 0 and errores > 0:
       raise ValueError("Hubo errores generando todas las liquidaciones.")
       ← ¡MENSAJE ENGAÑOSO! No es un error real, son duplicados.
```

### Identificación del Bug

**Archivo**: `src/aplicacion/servicios/servicio_financiero.py`
**Función**: `generar_liquidacion_propietario()` (línea 312-315)

```python
# CÓDIGO ACTUAL (BUG):
if generadas == 0:
    raise ValueError(
        f"Ya existían liquidaciones para las propiedades de este propietario en el período {periodo}"
    )
```

**Problema**: Cuando TODOS los contratos de un propietario ya tienen liquidaciones para el período, la función lanza `ValueError`. Esto es técnicamente correcto (no hay nada que generar), pero el handler de masiva lo trata como un **error** en lugar de una **omisión**.

**Archivo**: `src/presentacion_reflex/state/liquidaciones_state.py`
**Función**: `generar_liquidacion_masiva()` (línea 1113-1120)

```python
# CÓDIGO ACTUAL (BUG):
except Exception as e:  # ← Captura ValueError como error
    print(f"Error generando liquidacion masiva para id_propietario={id_propietario}: {e}")
    errores += 1  # ← Cuenta "ya existían" como error

if generadas == 0 and errores > 0:
    raise ValueError("Hubo errores generando todas las liquidaciones.")  # ← Mensaje engañoso
```

### ¿Por qué falla para TODOS los propietarios?

Si se ejecuta la generación masiva para un período donde **ya existen** liquidaciones (ej: segundo intento, o período ya procesado), TODOS los propietarios devuelven `ValueError` de "ya existían", que se cuentan como errores. Como `generadas == 0` y `errores > 0`, se muestra el mensaje genérico de error.

### Caso Específico: "BRR EL SILENCIO ET 2 MZ D CS 4"

La propiedad no aparece en el formulario de creación individual. Esto puede deberse a:
1. La query de propiedades filtra por `cm.ESTADO_CONTRATO_M = 'ACTIVO'` - verificar que el contrato esté activo
2. La propiedad no tiene contrato de mandato asociado
3. La propiedad está en estado de registro inactivo

**Nota**: Este caso requiere verificación en base de datos de producción para confirmar el estado del contrato.

## Decisions

### Decision 1: Modificar retorno de `generar_liquidacion_propietario`

**Decision**: Cambiar el retorno de `int` a un diccionario con tres contadores: `generadas`, `omitidas`, `errores`.

**Rationale**: Permite al handler masivo distinguir entre los tres estados posibles y mostrar mensajes precisos.

**Alternatives considered**:
- Mantener `int` y usar un contador separado en el handler: Rechazado porque mezcla lógica de negocio con presentación.
- Lanzar excepción personalizada para "omitidas": Rechazado porque las excepciones deben ser para errores, no para estados válidos.

### Decision 2: Clasificar "ya existían" como omitida, no como error

**Decision**: Un contrato que ya tiene liquidación para el período se clasifica como "omitido", no como "error".

**Rationale**: Consistente con la clarificación del usuario (Q2). "Ya existían" es un estado válido, no un fallo.

**Alternatives considered**:
- Mantener como error con mensaje específico: Rechazado porque genera confusión en el usuario.
- Silenciar completamente: Rechazado porque el usuario necesita saber que el proceso se ejecutó.

### Decision 3: Toast informativo vs de error

**Decision**: Si Z = 0 (sin errores reales), el toast es informativo. Si Z > 0, el toast es de warning.

**Rationale**: Consistente con FR-006 y la clarificación del usuario (Q1).

**Alternatives considered**:
- Siempre mostrar toast de error: Rechazado porque confunde al usuario cuando no hay fallos reales.
- Usar diferentes tipos de toast (success/warning/error): Aceptado como parte de la implementación.

## Validation

### Escenarios de Prueba

1. **Generación masiva, período nuevo**: Todas las liquidaciones se generan. Toast: "N generadas"
2. **Generación masiva, período ya procesado**: Todas las liquidaciones ya existen. Toast: "0 generadas, N ya existían"
3. **Generación masiva, mixto**: Algunas se generan, otras ya existen. Toast: "X generadas, Y ya existían"
4. **Generación masiva, con errores reales**: Algunas fallan por datos inválidos. Toast: "X generadas, Y ya existían, Z con error"
5. **Generación individual, propiedad sin contrato activo**: La propiedad no aparece en el formulario
6. **Generación individual, propiedad con contrato activo**: Se carga el contrato y se crea la liquidación

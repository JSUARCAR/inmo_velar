# Implementation Plan: Ingeniería Inversa Estado de Cuenta PDF Individual

**Branch**: `058-reverse-engineer-pdf-statement` | **Date**: 2026-07-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/058-reverse-engineer-pdf-statement/spec.md`

## Summary

Corrección de dos inconsistencias en la sección RESUMEN FINANCIERO del Estado de Cuenta PDF en vista individual:
1. **Textos descriptivos faltantes**: Los conceptos financieros no muestran el texto descriptivo entre paréntesis (ej: "(Total Canon Mandato)", "(Gravamen sobre la comisión)", etc.)
2. **Porcentaje de comisión**: El dato YA EXISTE correctamente en BD pero no se visualiza correctamente en el PDF

El problema está SOLO en la capa de renderización del template `estado_cuenta_elite.py`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: 
- ReportLab (generación PDF)
- Pydantic (validación de datos)
- SQLAlchemy/psycopg2 (PostgreSQL)

**Storage**: PostgreSQL (ya implementado, no requiere cambios)

**Testing**: pytest, pruebas de renderizado PDF

**Target Platform**: Web application (Reflex frontend + Python backend)

**Project Type**: Web application con generación de documentos PDF

**Performance Goals**: Sin incremento significativo en tiempo de generación (<10%)

**Constraints**: 
- Mantener consistencia con el sistema de diseño Claude/Anthropic
- No modificar la lógica de cálculo financiero existente
- Cambios atómicos (~100 líneas máximo)

**Scale/Scope**: 
- Template específico: `estado_cuenta_elite.py`
- Método principal: `_add_resumen_financiero()`
- Entidades afectadas: Liquidacion, ContratoMandato

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture | ✅ PASS | Cambios solo en capa de Infraestructura (templates) |
| 100% Español | ✅ PASS | Todo el código y documentación en español |
| Type Hints | ✅ PASS | Se mantendrán los type hints existentes |
| Sin SQLite/Flet | ✅ PASS | No se usan tecnologías obsoletas |
| Cambios Atómicos | ✅ PASS | Cambios concentrados en un solo método |
| Contract-First | ✅ PASS | Contratos de datos ya definidos en spec |

## Project Structure

### Documentation (this feature)

```text
specs/058-reverse-engineer-pdf-statement/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Análisis de código fuente
├── data-model.md        # Fase 1: Modelo de datos afectado
├── quickstart.md        # Fase 1: Guía de validación
├── contracts/           # Fase 1: Contratos de datos
└── tasks.md             # Fase 2: Tareas de implementación
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── liquidacion.py
│       └── contrato_mandato.py
├── aplicacion/
│   └── servicios/
│       └── servicio_financiero.py
├── infraestructura/
│   ├── repositorios/
│   │   └── repositorio_liquidacion_postgres.py
│   └── servicios/
│       ├── servicio_pdf_facade.py
│       └── pdf_elite/
│           └── templates/
│               └── estado_cuenta_elite.py  ← ARCHIVO A MODIFICAR
└── presentacion_reflex/
    └── components/
        └── liquidaciones/
            └── pdf_state.py
```

**Structure Decision**: Se mantiene la estructura existente. Los cambios se concentran únicamente en `estado_cuenta_elite.py`.

## Complexity Tracking

No hay violaciones de la Constitución que justificar.

## Phase 0: Research

### Análisis del Código Fuente

**Archivo**: `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`

**Método `_add_resumen_financiero()`** (líneas 328-371):

```python
def _add_resumen_financiero(self, data: Dict[str, Any]) -> None:
    """Agrega resumen financiero"""
    self.add_heading("RESUMEN FINANCIERO", level=3)

    resumen = data["resumen"]
    comision_pct = resumen.get("comision_porcentaje", 0) / 100

    # Tabla de resumen
    headers = ["Concepto", "Valor"]
    rows = [
        ["Total Ingresos", f"${resumen.get('total_ingresos', 0):,.2f}"],
        [f"Comisión ({comision_pct:.0f}%)", f"${resumen.get('comision_monto', 0):,.2f}"],
        ["IVA 19%", f"${resumen.get('iva_comision', 0):,.2f}"],
        ["Administración", f"${resumen.get('gastos_administracion', 0):,.2f}"],
        ["Servicios", f"${resumen.get('gastos_servicios', 0):,.2f}"],
        ["Predial", f"${resumen.get('pago_predial', 0):,.2f}"],
        ["Incidentes", f"${resumen.get('valor_incidentes', 0):,.2f}"],
    ]
```

**Problemas Identificados**:

1. **Textos descriptivos faltantes**: La tabla solo muestra "Concepto" y "Valor", pero no hay segunda línea para el texto descriptivo.

2. **Porcentaje de comisión**: 
   - Se divide por 100 (línea 333): `comision_pct = resumen.get("comision_porcentaje", 0) / 100`
   - Si el dato está en base 10000 (ej: 500 = 5%), la división por 100 daría 5, lo cual es correcto
   - Pero si el dato ya está en porcentaje (ej: 5 = 5%), la división daría 0.05, lo cual sería incorrecto
   - **NECESITA VERIFICACIÓN**: Confirmar el formato del dato en BD

### Decisión de Investigación

| Decisión | Alternativa A | Alternativa B | Selección |
|----------|---------------|---------------|-----------|
| Formato de texto descriptivo | Segunda fila en tabla | Texto inline con salto de línea | **B** - Más limpio visualmente |
| División porcentaje | Mantener /100 | Quitar división | **PENDIENTE** - Requiere verificación en BD |

## Phase 1: Design

### data-model.md

```markdown
# Modelo de Datos - Estado de Cuenta PDF

## Entidades Afectadas

### Liquidacion
- `comision_porcentaje`: Porcentaje de comisión del contrato (almacenado en BD)
- `valor_incidentes`: Valor total de incidentes
- `total_ingresos`: Total de ingresos (canon)
- `iva_comision`: IVA calculado sobre comisión
- `gastos_administracion`: Gastos de administración
- `gastos_servicios`: Gastos de servicios públicos
- `pago_predial`: Pago de impuesto predial

### ContratoMandato
- `comision_porcentaje`: Porcentaje de comisión acordado

## Relaciones
- Liquidacion → ContratoMandato (muchos a uno)
- ContratoMandato → Liquidacion (uno a muchos)

## Formato de Datos
- `comision_porcentaje`: Almacenado como entero en base 10000
  - Ejemplo: 500 = 5%, 800 = 8%, 1200 = 12%
  - Cálculo para mostrar: `valor / 100` = porcentaje a mostrar
```

### contracts/

No se requieren contratos externos adicionales. Los contratos de datos internos ya están definidos en el data-model.

### quickstart.md

```markdown
# Guía de Validación - Estado de Cuenta PDF

## Prerrequisitos
- Liquidación con datos financieros completos
- Contrato de mandato asociado con porcentaje de comisión registrado

## Escenarios de Prueba

### 1. Textos Descriptivos
**Entrada**: Liquidación con todos los conceptos
**Esperado**: 
- Total Ingresos → "(Total Canon Mandato)" debajo
- IVA 19% → "(Gravamen sobre la comisión)" debajo
- Administración → "(Solo aplica para propiedad horizontal)" debajo
- Servicio → "(Solo aplica para Energía, Agua y Gas)" debajo
- Predial → "(Pago anual del impuesto predial de la vivienda)" debajo
- Incidentes → "(Valor del incidente...)" debajo
- NETO A PAGAR → Sin texto descriptivo

### 2. Porcentaje de Comisión
**Entrada**: Contrato con comisión al 8%
**Esperado**: "Comisión (8%)" en el resumen

### 3. Comisión sin Registrar
**Entrada**: Contrato sin porcentaje
**Esperado**: "Comisión (0%)" como valor por defecto

### 4. Comisión Decimal
**Entrada**: Contrato con comisión al 8.5%
**Esperado**: "Comisión (9%)" redondeado

## Comandos de Validación
```bash
# Generar PDF de prueba
python -c "from src.infraestructura.servicios.pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite; ..."

# Verificar conteúdo do PDF gerado
# Abrir PDF y verificar sección RESUMEN FINANCIERO
```
```

## Re-evaluation Post-Design

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture | ✅ PASS | Cambios solo en template (Infraestructura) |
| 100% Español | ✅ PASS | Comentarios y documentación en español |
| Type Hints | ✅ PASS | Se mantienen firmas existentes |
| Cambios Atómicos | ✅ PASS | Cambio concentrado en un método |
| Zero Guessing | ✅ PASS | Se identificó necesidad de verificar formato porcentaje |

## Pending Verification

**CRÍTICO**: Se debe verificar el formato exacto del `comision_porcentaje` en la base de datos antes de implementar:
- Si está en base 10000 (500 = 5%) → Mantener división por 100
- Si está en porcentaje directo (5 = 5%) → Quitar división por 100

Esto se verificará en la fase de implementación ejecutando una consulta SQL directa.
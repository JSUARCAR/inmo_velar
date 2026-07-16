# Research: Ingeniería Inversa Estado de Cuenta PDF Individual

**Date**: 2026-07-16
**Feature**: 058-reverse-engineer-pdf-statement

## Research Tasks

### 1. Análisis del Template `estado_cuenta_elite.py`

**Objetivo**: Comprender la estructura actual del método `_add_resumen_financiero()` y identificar los puntos de modificación.

**Archivos Analizados**:
- `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`

**Hallazgos**:

#### Método `_add_resumen_financiero()` (Líneas 328-371)

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

| # | Problema | Ubicación | Severidad |
|---|----------|-----------|-----------|
| 1 | Textos descriptivos no se muestran | Líneas 337-345 | Alta |
| 2 | Formato de porcentaje de comisión requiere verificación | Línea 333 | Media |

### 2. Análisis de la Clase Base `BaseDocumentTemplate`

**Objetivo**: Comprender qué métodos están disponibles para agregar contenido al PDF.

**Archivos Analizados**:
- `src/infraestructura/servicios/pdf_elite/templates/base_template.py`

**Métodos Disponibles**:
- `add_heading(text, level)` - Agrega encabezado
- `add_paragraph(text, style_name)` - Agrega párrafo
- `add_spacer(height)` - Agrega espacio vertical
- `story.append(flowable)` - Agrega elemento directo al story

**Conclusión**: No hay método nativo para agregar texto descriptivo debajo de una celda de tabla. Se debe implementar una solución personalizada.

### 3. Análisis de `AdvancedTable`

**Objetivo**: Comprender si `AdvancedTable` soporta texto multilínea o celdas con contenido múltiple.

**Archivos Analizados**:
- `src/infraestructura/servicios/pdf_elite/components/tables.py`

**Hallazgos**:
- `AdvancedTable.create_data_table()` acepta `headers` y `rows`
- Cada fila es una lista de strings
- No hay soporte nativo para texto descriptivo en segunda línea

**Solución Propuesta**: Usar ReportLab `Paragraph` dentro de las celdas para permitir texto con formato (negrita + normal).

### 4. Verificación del Formato `comision_porcentaje`

**Objetivo**: Determinar el formato exacto del porcentaje de comisión en la base de datos.

**Método**: Consulta SQL directa en PostgreSQL

**Consulta Sugerida**:
```sql
SELECT cm.comision_porcentaje, l.id as liquidacion_id
FROM contrato_mandato cm
JOIN liquidaciones l ON l.contrato_mandato_id = cm.id
WHERE cm.comision_porcentaje > 0
LIMIT 5;
```

**Resultado Pendiente**: Se verificará durante la implementación.

## Decisiones Tomadas

| Decisión | Alternativas | Selección | Justificación |
|----------|--------------|-----------|---------------|
| Texto descriptivo | 1. Segunda fila en tabla<br>2. Paragraph en celda | **Opción 2** | Más limpio, respeta estructura de tabla existente |
| Formato porcentaje | 1. Mantener /100<br>2. Quitar /100 | **PENDIENTE** | Requiere verificación en BD |
| Valor por defecto | 1. "Comisión (0%)"<br>2. "Comisión (N/D)" | **Opción 1** | Más consistente con el formato |

## Alternativas Evaluadas

### Alternativa 1: Segunda Fila en Tabla
- **Ventaja**: Separación clara entre concepto y descripción
- **Desventaja**: Complejiza la estructura de la tabla, requiere merge de celdas
- **Rechazada por**: Complejidad innecesaria

### Alternativa 2: Paragraph en Celda (SELECCIONADA)
- **Ventaja**: Mantiene estructura simple, permite formato (negrita + normal)
- **Desventaja**: Requiere usar ReportLab `Paragraph` en lugar de strings
- **Seleccionada por**: Equilibrio entre funcionalidad y simplicidad

### Alternativa 3: Tabla Anidada
- **Ventaja**: Control total sobre layout
- **Desventaja**: Excesivamente compleja para este caso
- **Rechazada por**: Sobre-ingeniería

## Research Artifacts

### Estructura de Datos Actual

```python
data = {
    "resumen": {
        "total_ingresos": 747000,
        "comision_porcentaje": 800,  # 8% en base 10000
        "comision_monto": 88893,
        "iva_comision": 14193,
        "gastos_administracion": 0,
        "gastos_servicios": 0,
        "pago_predial": 0,
        "valor_incidentes": 282000,
        "valor_neto": 373107
    }
}
```

### Estructura de Datos Esperada (Post-Implementación)

```python
data = {
    "resumen": {
        "total_ingresos": 747000,
        "comision_porcentaje": 800,  # 8% en base 10000
        "comision_monto": 88893,
        "iva_comision": 14193,
        "gastos_administracion": 0,
        "gastos_servicios": 0,
        "pago_predial": 0,
        "valor_incidentes": 282000,
        "valor_neto": 373107
    }
}
# Nota: La estructura de datos NO cambia, solo la renderización
```

## Next Steps

1. **Verificar formato `comision_porcentaje`** en BD durante implementación
2. **Implementar textos descriptivos** usando `Paragraph` en celdas
3. **Validar renderizado** con diferentes escenarios de prueba
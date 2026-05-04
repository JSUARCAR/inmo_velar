# Plan: Optimización Tipográfica - Sistema 10%

## Objetivo
Optimizar la jerarquía tipográfica del sistema tras aplicar reducción del 10% (14.4px base), manteniendo legibilidad y consistencia.

---

## Fase 1: Auditoría y Mapeo (Completado ✅)

### Estado Actual (Post-Reducción 10%)

| Nivel Reflex | Tamaño Original | Nuevo Tamaño (10%) | Uso Principal |
|--------------|-----------------|--------------------|---------------|
| size="1"     | 12px            | **10.8px** ⚠️      | Labels sidebar, contadores* |
| size="2"     | 14px            | **12.6px** ✅      | Etiquetas formularios |
| size="3"     | 16px            | **14.4px** ✅      | Texto base, inputs |
| size="4"     | 18px            | **16.2px** ✅      | Títulos tarjetas |
| size="6"     | 24px            | **21.6px** ✅      | Subtítulos sección |
| size="8"     | 35-48px         | **31.5-43.2px**    | Títulos maestros |

> ⚠️ **Issue**: size="1" ahora es 10.8px, potencialmente muy pequeño para legibilidad

---

## Fase 2: Tareas Identificadas

### Tarea 1: Corregir size="1" para legibilidad
- **Problema**: 10.8px puede ser ilegible en algunos contextos
- **Solución**: Aumentar a 11px mínimo (11.7px efectivo)
- **Archivo**: `assets/custom_layout.css`
- **Criterio**: size="1" debe ser mínimo 11px (11.7px post-reducción)

### Tarea 2: Estandarizar size="8" en todo el sistema
- **Problema**: Inconsistencia entre Login (35px) y Dashboard (48px)
- **Solución**: Uniformar con breakpoint responsivo
- **Archivos**: `pages/login.py`, `pages/dashboard.py`
- **Criterio**: Todos los size="8" usan font_size responsivo

### Tarea 3: Optimizar breakpoints móviles
- **Problema**: Escala móvil podría ser muy pequeña
- **Solución**: Añadir override para viewports < 768px
- **Archivo**: `assets/custom_layout.css`
- **Criterio**: Mínimo 12px en móvil

### Tarea 4: Ajustar KPI cards
- **Problema**: Los KPIs精英 usan font_size explícito en px
- **Solución**: Consolidar en scale CSS
- **Archivo**: `components/dashboard/kpi_card.py`
- **Criterio**: Usar --font-size variables

---

## Fase 3: Dependencias

```
Tarea 1 (Crítica)
    ↓
Tarea 2 (Importante)
    ↓
Tarea 3 (Opcional)
    ↓
Tarea 4 (Sugerencia)
```

---

## Fase 4: Verificación

1. **Import**: `python -c "from src.presentacion_reflex import styles"`
2. **Pages**: `python -c "from src.presentacion_reflex.pages import dashboard, propiedades"`
3. **Visual**: Verificar en navegador que hierarchy es legible

---

## Priorización Recomendada

| # | Tarea | Severidad | Esfuerzo |
|---|-------|-----------|----------|
| 1 | Corregir size="1" | 🔴 Alta | Bajo |
| 2 | Estandarizar size="8" | 🟡 Media | Medio |
| 3 | Breakpoints móvil | 🟢 Baja | Bajo |
| 4 | Ajustar KPIs | 🟢 Sugerencia | Medio |

---

## Estado: Listo para revisión humana

¿Procedemos con la ejecución de las tareas priorizadas?
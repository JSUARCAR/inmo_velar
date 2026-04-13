# Todo: Optimización Tipográfica

## Estado: En revisión

### Tareas Pendientes

#### [🔴 Alta] Tarea 1: Corregir size="1" para legibilidad
- **Problema**: 10.8px (post-reducción) muy pequeño
- **Solución**: Aumentar variable --font-size-xs a mínimo 11px
- **Archivo**: `assets/custom_layout.css`
- **Criterio**: size="1" = mínimo 11px (11.7px post-reducción)

#### [🟡 Media] Tarea 2: Estandarizar size="8" en todo el sistema
- **Problema**: Inconsistencia Login vs Dashboard
- **Solución**: Uniformar con breakpoint responsivo
- **Archivos**: `pages/login.py`, `pages/dashboard.py`
- **Criterio**: Todos los size="8" usan font_size responsivo

#### [🟢 Baja] Tarea 3: Optimizar breakpoints móviles
- **Problema**: Escala móvil podría ser muy pequeña
- **Solución**: Añadir override para viewports < 768px
- **Archivo**: `assets/custom_layout.css`
- **Criterio**: Mínimo 12px en móvil

#### [🟢 Sugerencia] Tarea 4: Ajustar KPI cards
- **Problema**: KPIs usan font_size explícito en px
- **Solución**: Consolidar en scale CSS
- **Archivo**: `components/dashboard/kpi_card.py`
- **Criterio**: Usar --font-size variables

---

## Dependencias

```
Tarea 1 → Tarea 2 → Tarea 3 → Tarea 4
```

## Acciones

- [ ] Ejecutar Tarea 1: Corregir size="1"
- [ ] Ejecutar Tarea 2: Estandarizar size="8"
- [ ] Ejecutar Tarea 3: Breakpoints móvil
- [ ] Ejecutar Tarea 4: Ajustar KPIs
- [ ] Verificar con imports de Python
- [ ] Commit cambios
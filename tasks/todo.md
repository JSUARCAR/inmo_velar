# Todo: Optimización Tipográfica

## Estado: ✅ Completado

### Tareas Completadas

#### [🔴 Alta] Tarea 1: Corregir size="1" para legibilidad ✅
- **Solución**: `--font-size-xs` y `--font-size-1` → `0.917rem` (11px @ 12px base)
- **Archivos**: `assets/custom_layout_v2.css`
- **Resultado**: 4/4 tests pass

#### [🟡 Media] Tarea 2: Estandarizar size="8" en todo el sistema ✅
- **Solución**: Eliminados `font_size=[...]` hardcoded en login.py y propiedades.py
- **Archivos**: `pages/login.py`, `pages/propiedades.py`
- **Resultado**: 4/4 tests pass — todos usan `--font-size-8` CSS

#### [🟢 Baja] Tarea 3: Optimizar breakpoints móviles ✅
- **Solución**: Base móvil 10px → 12px + override `--font-size-1: 1rem` en @media
- **Archivo**: `assets/custom_layout_v2.css`
- **Resultado**: 3/3 tests pass — mínimo 12px en móvil

#### [🟢 Sugerencia] Tarea 4: Ajustar KPI cards ✅
- **Solución**: Eliminados `rx.breakpoints()` y `font_size=[...]` — usa Radix `size=` prop
- **Archivo**: `components/dashboard/kpi_card.py`
- **Resultado**: 3/3 tests pass

#### Corrección adicional: Escala tipográfica monótona ✅
- **Detección**: Test TDD detectó que `--font-size-sm` (0.875rem) < `--font-size-xs` (0.917rem)
- **Solución**: Ajustada escala: xs=0.917, sm=1.0, base=1.042, md=1.083rem
- **Resultado**: Escala creciente validada

---

## Verificación

- [x] Ejecutar Tarea 1: Corregir size="1"
- [x] Ejecutar Tarea 2: Estandarizar size="8"
- [x] Ejecutar Tarea 3: Breakpoints móvil
- [x] Ejecutar Tarea 4: Ajustar KPIs
- [x] Verificar con imports de Python
- [x] Tests automatizados: **19/19 PASSED**
- [ ] Commit cambios
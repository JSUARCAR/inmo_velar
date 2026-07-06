# Quickstart Validation: Floating Labels y Tooltips

**Feature**: 027-fix-floating-labels-tooltips
**Date**: 2026-07-05

## Prerequisites

1. Servidor Reflex ejecutándose: `reflex run --env dev`
2. Navegador web abierto en `http://localhost:3000`
3. Acceso a al menos 3 módulos del sistema

## Validation Scenarios

### Scenario 1: Floating Labels en Filtros Avanzados

**Steps**:
1. Navegar al módulo **Personas**
2. Hacer clic en "Filtros Avanzados" (si existe sección colapsable)
3. Hacer clic en un campo de texto (ej. "Buscar por nombre")
4. Observar que el label flota hacia arriba con animación suave
5. Escribir texto y verificar que label no se superpone
6. Borrar texto y verificar que label regresa a posición interior

**Expected**:
- Label se eleva al enfocar
- Transición suave (~0.3s)
- Sin superposición con placeholder o texto
- Label regresa al borrar contenido

**Pass Criteria**: SC-001, SC-006

---

### Scenario 2: Floating Labels en Modales

**Steps**:
1. Navegar al módulo **Liquidaciones**
2. Hacer clic en "Nueva Liquidación Mensual" (o botón similar)
3. Observar todos los campos del formulario
4. Hacer clic en cada campo y verificar floating label
5. Verificar campos con valores prellenados (si aplica)
6. Cerrar y reabrir modal, verificar reset de labels

**Expected**:
- Todos los campos tienen floating labels
- Labels funcionan en inputs, selects, datepickers
- Labels con valor prellenado muestran estado elevado
- Reset correcto al reabrir modal

**Pass Criteria**: SC-002, SC-006, SC-007

---

### Scenario 3: Tooltips en Filtros Avanzados

**Steps**:
1. Navegar al módulo **Propiedades**
2. Abrir Filtros Avanzados
3. Buscar iconos de información (ℹ️) junto a los campos
4. Pasar mouse sobre cada icono
5. Verificar que aparece tooltip con texto descriptivo
6. Mover mouse fuera y verificar que se oculta

**Expected**:
- Tooltip aparece con delay sutil (~0.15s)
- Texto descriptivo y relevante
- Tooltip se oculta al salir del icono
- Z-index correcto (visible sobre otros elementos)

**Pass Criteria**: SC-003

---

### Scenario 4: Tooltips en Modales

**Steps**:
1. Navegar al módulo **Contratos**
2. Abrir modal de creación/edición
3. Buscar iconos ℹ️ en los campos
4. Pasar mouse sobre iconos
5. Verificar tooltips dentro del modal
6. Verificar que tooltip no queda detrás del modal

**Expected**:
- Tooltips visibles dentro del modal
- Z-index mayor al del modal
- Texto legible y no truncado

**Pass Criteria**: SC-004

---

### Scenario 5: Consistencia entre Módulos

**Steps**:
1. Abrir **Personas** → Filtros Avanzados
2. Abrir **Propiedades** → Filtros Avanzados
3. Abrir **Contratos** → Filtros Avanzados
4. Comparar visualmente floating labels y tooltips
5. Repetir con modales de cada módulo

**Expected**:
- Mismo estilo de floating labels
- Misma animación de transición
- Mismo estilo de tooltips
- Sin diferencias visuales entre módulos

**Pass Criteria**: SC-005

---

### Scenario 6: Estados de Error

**Steps**:
1. Abrir cualquier modal con formulario
2. Dejar campos requeridos vacíos
3. Intentar guardar/enviar
4. Observar comportamiento de labels en campos con error

**Expected**:
- Label permanece elevado
- Label cambia a color de error (rojo)
- Mensaje de error aparece debajo del campo
- Sin superposición label-error

**Pass Criteria**: SC-006 (nuevo criterio de error)

---

### Scenario 7: Accesibilidad Básica

**Steps**:
1. Inspeccionar HTML de un tooltip (F12 → Elements)
2. Verificar atributo `role="tooltip"`
3. Verificar `aria-describedby` en el trigger
4. Probar en dispositivo táctil (o emulador)

**Expected**:
- Tooltips tienen `role="tooltip"`
- Trigger tiene `aria-describedby` apuntando al tooltip
- En táctil: tap muestra tooltip, tap fuera lo oculta

**Pass Criteria**: FR-010

---

## Test Commands

```bash
# Iniciar servidor de desarrollo
reflex run --env dev

# Verificar syntax (opcional)
python -c "from src.presentacion_reflex.styles import BASE_STYLE"
python -c "from src.presentacion_reflex.components.shared.floating_label import floating_input"

# Exportar frontend (para validación de producción)
DATABASE_URL=sqlite:///test.db reflex export --frontend-only --no-zip
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Label no se eleva | Verificar CSS selectors en `BASE_STYLE` |
| Tooltip detrás de modal | Verificar `Z_TOOLTIP_IN_MODAL` |
| Sin animación | Verificar `FL_TRANSITION` en styles.py |
| Label superpuesto | Verificar `padding_top` del input |

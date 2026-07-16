# Quickstart Validation: Fix ID Seguro - Personas

**Date**: 2026-07-15

## Prerequisites

- Servidor Reflex ejecutándose: `reflex run --env dev`
- Navegador web abierto en `http://localhost:3000`
- Consola del navegador abierta (F12 → Console)
- Base de datos con al menos un tipo de seguro registrado

## Validation Scenarios

### Scenario 1: Renderizado sin errores (P1)

**Objetivo**: Verificar que el combobox ID Seguro renderiza sin errores de Radix UI

**Pasos**:
1. Navegar a `/personas`
2. Click en "Nueva Persona"
3. Completar Paso 1 con datos válidos → Click "Siguiente"
4. Seleccionar "Arrendatario" en Paso 2 → Click "Siguiente"
5. Verificar Paso 3 muestra "Información de Seguro"

**Resultado esperado**:
- ✅ Campo "ID Seguro" visible
- ✅ Consola del navegador SIN errores `PopoverPortal must be used within Popover`
- ✅ No hay errores de JavaScript en consola

---

### Scenario 2: Funcionalidad del combobox (P1)

**Objetivo**: Verificar que el dropdown funciona correctamente

**Pasos**:
1. Continuar desde Scenario 1
2. Click en el campo "ID Seguro"
3. Verificar que el dropdown se abre
4. Escribir texto de búsqueda
5. Verificar que las opciones se filtran
6. Click en una opción

**Resultado esperado**:
- ✅ Dropdown aparece debajo del input
- ✅ Opciones se muestran correctamente
- ✅ Búsqueda filtra las opciones
- ✅ Selección actualiza el valor del campo
- ✅ Dropdown se cierra después de seleccionar

---

### Scenario 3: Guardado completo (P2)

**Objetivo**: Verificar que la persona se guarda con el seguro

**Pasos**:
1. Continuar desde Scenario 2
2. Completar campos restantes (Nombre Habitante, Teléfono)
3. Click "Guardar"
4. Verificar mensaje de éxito
5. Buscar la persona creada en la lista
6. Ver detalles de la persona

**Resultado esperado**:
- ✅ Persona se crea exitosamente
- ✅ En detalles, tab "Arrendatario" muestra el seguro seleccionado
- ✅ Campo "Código Aprobación Seguro" se guardó correctamente

---

### Scenario 4: Cambio de rol (P2)

**Objetivo**: Verificar comportamiento al cambiar de rol

**Pasos**:
1. Abrir modal de nueva persona
2. Seleccionar "Arrendatario" en Paso 2
3. Avanzar a Paso 3
4. Volver a Paso 2
5. Deseleccionar "Arrendatario"
6. Avanzar a Paso 3

**Resultado esperado**:
- ✅ Campo "ID Seguro" no se muestra cuando Arrendatario no está seleccionado
- ✅ No hay errores en consola al cambiar de rol

---

### Scenario 5: Consola limpia (P1)

**Objetivo**: Verificar que no hay errores residuales

**Pasos**:
1. Abrir consola del navegador (F12)
2. Ejecutar todos los escenarios anteriores
3. Revisar pestaña "Console" para errores

**Resultado esperado**:
- ✅ 0 errores de JavaScript
- ✅ 0 errores de Radix UI
- ✅ 0 errores de renderizado

## Commands

```bash
# Iniciar servidor en modo desarrollo
reflex run --env dev

# Verificar errores de Python
python -m py_compile src/presentacion_reflex/components/personas/modal_form.py

# Ejecutar tests (si existen)
pytest tests/ -k personas -v
```

## Rollback

Si el fix causa regresiones:
1. Revertir cambios en `modal_form.py`
2. El `selector_busqueda()` original se restaura
3. Verificar que el error original vuelve (confirmar que el fix era necesario)

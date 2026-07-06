# Quickstart: Floating Labels en Filtros Avanzados

**Date**: 2026-07-05 | **Feature**: 016-floating-labels-filters

## Validación Rápida

### Prerequisitos

- Python 3.11+ instalado
- Reflex 0.8.x instalado
- Servidor de desarrollo Reflex funcionando

### Setup

```bash
# Navegar al directorio del proyecto
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"

# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt
```

### Escenarios de Validación

#### ESC-01: Floating Label Básico

**Objetivo**: Verificar que el label se desplaza al recibir foco

```bash
# Ejecutar servidor de desarrollo
reflex run --env dev
```

**Pasos**:
1. Navegar al Dashboard
2. Hacer clic en el campo "Mes"
3. Verificar que la etiqueta "Mes" se desplaza hacia arriba
4. Ingresar un valor
5. Verificar que la etiqueta permanece arriba

**Resultado Esperado**:
- Label inicia en posición centrada
- Al hacer foco, label se anima hacia arriba
- Transición suave de 200ms con cubic-bezier

#### ESC-02: Floating Label con Valor Preseleccionado

**Objetivo**: Verificar campos con valores iniciales

**Pasos**:
1. Navegar al Dashboard
2. Observar el campo "Asesor" (tiene valor por defecto "Todos los asesores")
3. Verificar que la etiqueta "Asesor" está en posición arriba

**Resultado Esperado**:
- Label en posición superior desde el inicio
- Valor visible debajo del label

#### ESC-03: Estado de Error

**Objetivo**: Verificar comportamiento en error

**Pasos**:
1. Navegar a un formulario con validación
2. Dejar un campo requerido vacío
3. Intentar enviar
4. Verificar color de label

**Resultado Esperado**:
- Label cambia color a `var(--red-9)`
- Label permanece visible y legible

#### ESC-04: Responsividad Móvil

**Objetivo**: Verificar en viewport móvil

**Pasos**:
1. Abrir DevTools del navegador
2. Cambiar a vista móvil (iPhone 12/13)
3. Navegar al Dashboard
4. Interactuar con los filtros

**Resultado Esperado**:
- Labels legibles en pantalla pequeña
- No interfiere con teclado virtual
- Transiciones suaves sin lag

#### ESC-05: Navegación por Teclado

**Objetivo**: Verificar accesibilidad

**Pasos**:
1. Usar Tab para navegar entre campos
2. Verificar que el label responde al foco por teclado
3. Usar Enter para abrir selects
4. Verificar que lectores de pantalla anuncian el label

**Resultado Esperado**:
- Focus visible en todos los campos
- Labels se animan correctamente con teclado
- aria-label announce correctamente

## Comandos de Verificación

```bash
# Verificar que no hay errores de sintaxis
python -m py_compile src/presentacion_reflex/components/shared/floating_label.py

# Ejecutar tests de renderizado (si existen)
python -m pytest tests/ -k "floating"

# Verificar lint
ruff check src/presentacion_reflex/components/shared/floating_label.py
mypy src/presentacion_reflex/components/shared/floating_label.py
```

## Troubleshooting

### Problema: Label no se desplaza

**Causa**: Placeholder no está configurado como `" "` (espacio vacío)

**Solución**: Asegurar que `placeholder=" "` en el componente

### Problema: Transición lenta

**Causa**: CSS transition no está aplicado

**Solución**: Verificar que `transition` está en el estilo del componente

### Problema: Label no cambia a rojo en error

**Causa**: Prop `error` no está pasándose correctamente

**Solución**: Verificar que `error={True}` se pasa como prop

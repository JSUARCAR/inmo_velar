# Quickstart Validation: Columnas Condicionales en Tabla de Contratos

**Date**: 2026-07-21

## Prerrequisitos

- Aplicación Reflex corriendo en modo desarrollo
- Base de datos PostgreSQL con datos de prueba
- Al menos 1 contrato de Mandato con consignatario registrado
- Al menos 1 contrato de Arrendamiento con codeudor registrado

## Setup

```bash
# 1. Asegurar que la BD tiene datos de prueba
# (verificar que existen contratos con consignatario y codeudor)

# 2. Iniciar servidor en modo desarrollo
reflex run --env dev
```

## Escenarios de Validación

### Escenario 1: Columna Visible

**Acción**: Navegar a la página de Contratos

**Resultado Esperado**:
- La columna "Información Adicional" es visible en la tabla
- El encabezado muestra "Información Adicional"
- La columna se posiciona después de las columnas existentes (antes de Acciones)

### Escenario 2: Contrato Mandato con Datos

**Acción**: Localizar un contrato de tipo Mandato que tenga consignatario registrado

**Resultado Esperado**:
- La columna muestra formato: `"Nombre | Banco | Cuenta"`
- Ejemplo: `"Juan Pérez | Bancolombia | 1234567890"`
- Los valores corresponden a los campos del contrato

### Escenario 3: Contrato Arrendamiento con Codeudor

**Acción**: Localizar un contrato de tipo Arrendamiento que tenga codeudor

**Resultado Esperado**:
- La columna muestra formato: `"Nombre Codeudor | Teléfono"`
- Ejemplo: `"María García | 3101234567"`
- El nombre y teléfono corresponden al codeudor registrado

### Escenario 4: Contrato sin Información Adicional

**Acción**: Localizar un contrato sin consignatario (Mandato) o sin codeudor (Arrendamiento)

**Resultado Esperado**:
- La columna muestra: `"No registrado"`
- No se muestra información incompleta o errónea

### Escenario 5: Filtro por Tipo

**Acción**: Filtrar la tabla por tipo "Mandato"

**Resultado Esperado**:
- Solo se muestran contratos de Mandato
- La columna muestra datos de consignatario/banco/cuenta
- No se muestra información de codeudor (no aplica)

### Escenario 6: Ordenamiento

**Acción**: Hacer clic en el encabezado "Información Adicional"

**Resultado Esperado**:
- La tabla se ordena alfabéticamente por el contenido de la columna
- El orden se invierte al hacer clic nuevamente

### Escenario 7: Responsive

**Acción**: Reducir el ancho del navegador a formato móvil

**Resultado Esperado**:
- La tabla permite scroll horizontal
- La columna es accesible mediante scroll
- No se rompe el layout

## Validación Técnica

### Consulta de Verificación SQL

```sql
-- Verificar contratos Mandato con consignatario
SELECT id_contrato_m, consignatario, banco_propietario, numero_cuenta_propietario
FROM CONTRATOS_MANDATOS
WHERE consignatario IS NOT NULL
LIMIT 5;

-- Verificar contratos Arrendamiento con codeudor
SELECT ca.id_contrato_a, p.nombre, pe.telefono
FROM CONTRATOS_ARRENDAMIENTOS ca
LEFT JOIN CODEUDORES cd ON ca.id_codeudor = cd.id_codeudor
LEFT JOIN PERSONA p ON cd.id_persona = p.id_persona
LEFT JOIN PERSONA pe ON cd.id_persona = pe.id_persona
WHERE ca.id_codeudor IS NOT NULL
LIMIT 5;
```

### Verificación en Consola del Navegador

1. Abrir DevTools (F12)
2. Pestaña Network: verificar que no hay errores 500
3. Pestaña Console: verificar que no hay errores de JavaScript/Reflex

## Criterios de Aceptación

- [ ] Columna "Información Adicional" visible en tabla
- [ ] Mandatos muestran: Consignatario | Banco | Cuenta
- [ ] Arrendamientos muestran: Codeudor | Teléfono
- [ ] Contratos sin datos muestran "No registrado"
- [ ] Filtro por tipo funciona correctamente
- [ ] Ordenamiento funciona en la nueva columna
- [ ] Layout responsive se mantiene
- [ ] No hay errores en consola del navegador

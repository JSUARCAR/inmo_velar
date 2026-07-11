# Quickstart: Validación de Filtros Avanzados Recaudos

**Date**: 2026-07-11

## Prerrequisitos

- Servidor Reflex ejecutándose (`reflex run --env dev`)
- Base de datos PostgreSQL con datos de prueba (recaudos con contratos y liquidaciones)
- Al menos 3 contratos de arrendamiento con diferentes días de pago (ej: 1, 15, 31)
- Al menos 2 grupos operativos configurados en CONTRATOS_MANDATOS

## Escenarios de Validación

### ESC-01: Filtro Pago Contrato - Selección Única

**Pasos**:
1. Abrir módulo Recaudos
2. Desplegar filtro "Pago Contrato"
3. Seleccionar día "15"
4. Verificar que la tabla muestra solo recaudos con FECHA_PAGO = "15" o el día 15 de FECHA_INICIO_CONTRATO_A

**Resultado esperado**: Tabla filtrada, columna "Pago Contrato" muestra solo "15"

### ESC-02: Filtro Pago Contrato - Selección Múltiple

**Pasos**:
1. Desplegar filtro "Pago Contrato"
2. Seleccionar días "1" y "15"
3. Verificar que la tabla muestra recaudos con día 1 O día 15

**Resultado esperado**: Tabla contiene registros de ambos días (OR intra-filtro)

### ESC-03: Filtro Ciclo Operativo - Selección Única

**Pasos**:
1. Desplegar filtro "Ciclo Operativo"
2. Seleccionar "Grupo 1"
3. Verificar que la tabla muestra solo recaudos cuyo contrato de mandato activo tiene GRUPO_OPERATIVO = 1

**Resultado esperado**: Tabla filtrada, columna "Ciclo Operativo" muestra solo "Grupo 1"

### ESC-04: Filtro Ciclo Operativo - Selección Múltiple

**Pasos**:
1. Desplegar filtro "Ciclo Operativo"
2. Seleccionar "Grupo 1" y "Grupo 3"
3. Verificar que la tabla muestra recaudos de Grupo 1 O Grupo 3

**Resultado esperado**: Tabla contiene registros de ambos grupos

### ESC-05: Combinación de Filtros

**Pasos**:
1. Activar filtro Pago Contrato: día "15"
2. Activar filtro Ciclo Operativo: "Grupo 2"
3. Verificar que la tabla muestra solo recaudos que cumplen AMBOS criterios

**Resultado esperado**: Intersección AND de ambos filtros

### ESC-06: Combinación con Filtros Existentes

**Pasos**:
1. Activar filtro Estado: "Pendiente"
2. Activar filtro Pago Contrato: día "1"
3. Activar filtro Ciclo Operativo: "Grupo 1"
4. Verificar que la tabla muestra recaudos Pendientes del día 1 del Grupo 1

**Resultado esperado**: Intersección AND de los tres filtros

### ESC-07: Limpieza de Filtros

**Pasos**:
1. Activar múltiples filtros
2. Limpiar filtro Pago Contrato (seleccionar "Todos" o deseleccionar)
3. Verificar que los filtros restantes siguen activos

**Resultado esperado**: Solo se remueve el filtro limpiado

### ESC-08: Sin Resultados

**Pasos**:
1. Activar filtros que no tienen coincidencias (ej: día "31" + Grupo "99")
2. Verificar que se muestra estado vacío informativo

**Resultado esperado**: Mensaje "No se encontraron resultados" o similar

### ESC-09: Consistencia Columna vs Filtro

**Pasos**:
1. Filtrar por Pago Contrato = "15"
2. Verificar que TODOS los registros mostrados tienen "15" en la columna "Pago Contrato"
3. Filtrar por Ciclo Operativo = "Grupo 2"
4. Verificar que TODOS los registros mostrados tienen "Grupo 2" en la columna "Ciclo Operativo"

**Resultado esperado**: 100% de consistencia entre filtro y columna

## Comandos de Validación

```bash
# Verificar que el servidor compila sin errores
reflex run --env dev

# Verificar consultas SQL generadas (logging)
# Revisar logs del servidor para confirmar que los filtros generan IN (...) clauses

# Verificar rendimiento
# Medir tiempo de respuesta con múltiples filtros activos
```

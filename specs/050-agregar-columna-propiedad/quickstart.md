# Quickstart: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Date**: 2026-07-11
**Feature**: 050-agregar-columna-propiedad

## Prerrequisitos

1. Python 3.11+ instalado
2. PostgreSQL ejecutándose (local o Railway)
3. Variables de entorno configuradas (DATABASE_URL)
4. Dependencias instaladas: `pip install -r requirements.txt`

## Validación Rápida

### 1. Verificar que la columna existe en la UI

```bash
# Iniciar servidor en modo desarrollo
reflex run --env dev

# Navegar a http://localhost:3000/recaudos
# Verificar que la columna "Propiedad" está visible
```

### 2. Verificar ordenamiento

```bash
# En la UI:
# 1. Hacer clic en el encabezado "Propiedad"
# 2. Verificar que la tabla se ordena alfabéticamente
# 3. Hacer clic nuevamente para invertir el orden
```

### 3. Verificar filtro de propiedad

```bash
# En la UI:
# 1. Buscar el filtro de Propiedad en el toolbar
# 2. Seleccionar una propiedad específica
# 3. Verificar que solo se muestran recaudos de esa propiedad
# 4. Limpiar el filtro y verificar que vuelven todos los recaudos
```

### 4. Verificar datos

```bash
# En la consola del navegador (F12):
# 1. Verificar que cada fila muestra la dirección de la propiedad
# 2. Verificar que no hay errores en la consola
# 3. Verificar que el loading indicator funciona correctamente
```

## Escenarios de Prueba

### Escenario 1: Visualización de columna

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a /recaudos | Tabla carga correctamente |
| 2 | Verificar columna PROPIEDAD | Columna visible entre CICLO OPERATIVO y CANON |
| 3 | Verificar datos | Cada fila muestra dirección de propiedad |

### Escenario 2: Ordenamiento

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Hacer clic en encabezado PROPIEDAD | Tabla se ordena A-Z |
| 2 | Hacer clic nuevamente | Tabla se ordena Z-A |
| 3 | Hacer clic en otra columna | Orden cambia a la nueva columna |

### Escenario 3: Filtrado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir filtro de Propiedad | Dropdown muestra propiedades disponibles |
| 2 | Seleccionar una propiedad | Tabla filtra solo esa propiedad |
| 3 | Seleccionar otra propiedad | Tabla muestra ambas propiedades |
| 4 | Limpiar filtro | Tabla muestra todos los recaudos |

### Escenario 4: Datos faltantes

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Buscar recaudo sin propiedad | Muestra "Sin dirección" o ID |
| 2 | Verificar que no hay errores | UI no se rompe |

## Comandos de Verificación

```bash
# Verificar sintaxis del código
python -m py_compile src/presentacion_reflex/pages/recaudos.py

# Ejecutar tests (si existen)
pytest tests/ -v -k recaudos

# Verificar linting
ruff check src/presentacion_reflex/pages/recaudos.py
```

## Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Columna no aparece | CSS oculta la columna | Verificar breakpoints responsive |
| Datos vacíos | campo `direccion` es NULL | Implementar fallback "Sin dirección" |
| Error de loading | Query SQL falla | Verificar JOIN con tabla propiedades |
| Filtro no funciona | Estado no se actualiza | Verificar `filter_propiedad` en state |

# Quickstart Validation Guide

Esta guía permite a un desarrollador o tester validar rápidamente que las mejoras a la tabla de Liquidaciones funcionan de extremo a extremo.

## Prerrequisitos
- El servidor de desarrollo de Reflex debe estar corriendo.
- Base de datos PostgreSQL activa con datos de prueba de liquidaciones (que incluyan distintos ciclos operativos y montos).

## Pasos de Validación

### 1. Iniciar la aplicación
```bash
reflex run --env dev
```

### 2. Validar Ordenamiento de Columnas
1. Navegar a la página de **Liquidaciones**.
2. Hacer clic en la cabecera de la columna **Monto** (o equivalente numérico).
3. **Resultado Esperado**: La tabla se recarga y los registros se muestran de menor a mayor. Aparece un indicador (ícono/flecha) en la cabecera apuntando hacia arriba o indicando ascensión.
4. Hacer clic nuevamente en la misma cabecera.
5. **Resultado Esperado**: La tabla se ordena de mayor a menor. El indicador cambia visualmente.
6. Inspeccionar la cabecera de la columna **Acciones**.
7. **Resultado Esperado**: No debe ser cliqueable ni alterar el orden de la tabla.

### 3. Validar Filtro Ciclo Operativo
1. En la misma página, abrir el panel o sección de **Filtros Avanzados**.
2. Seleccionar un ciclo en el nuevo filtro desplegable o campo de **Ciclo Operativo** (ej. "2026-06").
3. Hacer clic en el botón de aplicar filtros (si el filtrado no es automático).
4. **Resultado Esperado**: La tabla se actualiza mostrando únicamente las liquidaciones correspondientes al ciclo seleccionado. El ordenamiento actual se mantiene si había uno activo.

### 4. Validar UI/UX y Bugs Visuales (Filtros Avanzados)
1. Con la sección de **Filtros Avanzados** abierta, inspeccionar visualmente los componentes.
2. Achicar y agrandar la ventana del navegador.
3. **Resultado Esperado**: Los botones (como "Aplicar", "Limpiar") no deben superponerse. Los márgenes (spacing) entre inputs deben ser consistentes y respirables, respetando los estándares del Claude Design System descritos en el protocolo.

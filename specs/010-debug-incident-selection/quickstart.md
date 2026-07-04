# Quickstart Validation Guide: debug-incident-selection

Esta guía documenta los pasos para verificar localmente que el fallo ha sido reparado.

## Requisitos Previos
- Servidor PostgreSQL levantado (local o remoto configurado en `.env`).
- Entorno virtual Python activo con dependencias instaladas.

## Configuración y Ejecución
1. Arrancar la aplicación en modo desarrollo:
   ```bash
   reflex run --env dev
   ```

2. Acceder en el navegador a: `http://localhost:3000/liquidaciones`

## Escenario de Validación
1. Localizar una liquidación existente en la tabla.
2. Hacer clic en el botón para editar la liquidación.
3. En el formulario de edición, hacer clic en el botón **"Seleccionar Incidentes"**.
4. **Verificación Esperada 1**: El modal se abre sin recargar la página.
5. **Verificación Esperada 2**: La lista de incidentes dentro del modal muestra resultados.
6. **Verificación Esperada 3**: Ninguno de los incidentes en la lista tiene estado "Pagado".

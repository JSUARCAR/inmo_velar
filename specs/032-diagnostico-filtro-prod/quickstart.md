# Guía de Verificación Rápida (Quickstart)

## Pre-requisitos
- Acceso al repositorio Git en `feat/desarrollo-experto-elite`.
- Acceso remoto (Railway o URL de producción).

## Pasos de Ejecución

1. **Sincronización Git**:
   ```bash
   git checkout main
   git merge feat/desarrollo-experto-elite
   git push origin main
   ```

2. **Verificación de Despliegue**:
   - Ingresar a Railway dashboard.
   - Confirmar que el build se inicia automáticamente tras el push a `main`.
   - Esperar a que el estado cambie a "Success" / "Deployed".

3. **Verificación Funcional en UI**:
   - Abrir el navegador en `https://extraordinary-joy-production-2fd2.up.railway.app/incidentes`
   - Buscar el componente **Estado de Pago**.
   - **Resultado Esperado**: El menú desplegable contiene: `Todos` (por defecto), `Pendiente`, `Asociada`, `Pagada`.
   - Al seleccionar cada uno, la tabla debe filtrar correctamente (sin errores de SQL).

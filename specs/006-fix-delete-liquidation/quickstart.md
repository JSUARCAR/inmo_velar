# Validation Guide: Fix Delete Liquidation

## Escenarios de Validación Manual

### Escenario 1: Confirmación de Eliminación Muestra Modal
**Objetivo:** Verificar que el evento de clic en el botón Eliminar esté correctamente enlazado.
1. Iniciar la aplicación y navegar al módulo de "Liquidaciones".
2. Identificar una liquidación en la tabla que se encuentre en estado "Pendiente".
3. Hacer clic en el botón con icono de basura ("Eliminar").
4. **Resultado Esperado:** Un modal/diálogo de confirmación debe aparecer en la pantalla superior. No se debe realizar la eliminación de manera silenciosa en este paso.

### Escenario 2: Interfaz del Modal y Confirmación (Validación UX/Pointer-Events)
**Objetivo:** Verificar las lógicas de pointer-events, Z-Index y la regla de confirmación explícita obligatoria.
1. Con el modal abierto, observar que el botón "Eliminar" se encuentra inactivo (deshabilitado).
2. Hacer clic en el checkbox que indica "Confirmo que deseo eliminar esta liquidación...".
3. **Resultado Esperado:** El botón "Eliminar" se habilita. Toda interacción en este modal debe reaccionar inmediatamente (comprobando que no hay bloqueos por el `DismissableLayer` de Radix UI o fallos de Z-Index).

### Escenario 3: Ejecución Exitosa (Soft Delete y Actualización UI)
**Objetivo:** Validar que el flujo envía la petición al backend, procesa la respuesta y actualiza la tabla de manera asíncrona.
1. Con el checkbox de confirmación marcado, hacer clic en el botón "Eliminar" (rojo) dentro del modal.
2. **Resultado Esperado:** 
   - El modal de confirmación se cierra automáticamente.
   - Aparece una Notificación/Toast de éxito en la interfaz.
   - El registro de la liquidación eliminada desaparece inmediatamente del listado visible en la pantalla (sin recargar el navegador).

### Escenario 4: Validación de Eliminación Lógica y Orphaning (Backend)
**Objetivo:** Verificar mediante inspección directa que la regla del "Soft Delete" y la desvinculación de documentos se ejecuta de manera correcta y segura.
1. Conectar a la base de datos de pruebas o inspeccionar a través del visor de datos.
2. Consultar la tabla de liquidaciones buscando el ID recién eliminado.
3. **Resultado Esperado:** El registro debe seguir existiendo físicamente, pero debe estar marcado lógicamente como eliminado o inactivo.
4. Consultar los documentos asociados previamente a esa liquidación.
5. **Resultado Esperado:** Deben estar con la referencia `ID_ENTIDAD_REFERENCIA = NULL` (desvinculados / orphaned).

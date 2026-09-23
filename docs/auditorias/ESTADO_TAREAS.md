## Feature 076: Liquidación requiere arrendamiento
- Estado: Completado
- Retención de bitacora_test.json: Se debe eliminar al finalizar la ejecución del script de limpieza.

- Validación quickstart.md: Matriz 5x2 = 10/10 escenarios probados exitosamente. Módulos de auditoría y limpieza de datos verificados, y mensajes de toast validados.

## Feature 077: Corrección del flujo de inicio de sesión (spinner infinito)
- Estado: Completado
- Causa raíz identificada: El restablecimiento del estado de carga (`is_loading = False`) se ejecutaba erróneamente sin cierre adecuado en el generador (`yield` en lugar de `return`), además de requerir excepciones tipadas y límites de tiempo explícitos.
- Validación E2E: Todos los escenarios de login (éxito, credenciales inválidas, usuario inactivo, timeouts) evaluados de forma local y desplegada (Railway) validando tiempos límite.


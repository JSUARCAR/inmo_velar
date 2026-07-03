# Data Model: Eliminación de Liquidación

Dado que este feature trata de una corrección sobre una funcionalidad preexistente, el modelo de datos de la entidad principal ya existe. A continuación se documenta su estructura relevante para el flujo de eliminación, conforme a la ingeniería inversa.

## Entidad: `Liquidacion` (Referencia)

Representa el documento financiero calculado para pagarle al propietario sus ingresos (menos deducciones).

### Campos Relevantes para Eliminación
- `id` (int, PK): Identificador único de la liquidación. Requerido por el servicio y repositorio para su eliminación.
- `estado_liquidacion` (varchar): Estado en el que se encuentra (Ej: "Pendiente", "Pagada", "Eliminada").
- `eliminada` (bool): Flag o marca booleana adicional (si es usada en el backend `liquidacion.eliminada`).
- `usuario_sistema` (varchar): Registra quién realizó la operación de eliminación.

### Relaciones (Referential Integrity / Cascades)
- **Documentos (1:N)**: Las liquidaciones pueden tener documentos PDF o comprobantes adjuntos (ej. en la tabla `DOCUMENTOS`). La operación de eliminación *desvincula* (orphaning) los documentos estableciendo `ID_ENTIDAD_REFERENCIA = NULL` para la entidad 'liquidacion'.

### Reglas de Validación
1. **Idempotencia**: Si la liquidación ya ha sido marcada como eliminada previamente (`eliminada == True` o equivalente), la operación retorna éxito inmediatamente sin generar errores ni intentar reprocesar, devolviendo mensaje de "ya eliminada".
2. **Protección de Historial (Estado)**: Una liquidación NO puede ser eliminada si su `estado_liquidacion` es `"Pagada"`. Intentar esto lanzará una excepción indicando que pertenece al histórico financiero protegido.

### Transiciones de Estado
- `Pendiente` -> `Eliminada` (Válido, usando el flujo `confirmar_eliminar`)
- `Pagada` -> `Eliminada` (Inválido, regla de negocio bloquea la operación)

# Data Model: Migración de Grupo Operativo en Contratos de Mandato

Esta tarea no requiere crear nuevas entidades, atributos ni relaciones, sino **recalibrar** registros existentes en la entidad `ContratoMandato`.

## Entidad Principal: `CONTRATOS_MANDATOS`

### Atributos Afectados (Targets de Escritura)

| Campo (PostgreSQL) | Tipo | Descripción | Regla de Validación (Dominio) |
| :--- | :--- | :--- | :--- |
| `GRUPO_OPERATIVO` | `INT` | Identificador del grupo de corte para liquidaciones. | Debe coincidir con `CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_inicio)[0]`. Valores permitidos: 1, 2, 3. |
| `FECHA_PAGO` | `VARCHAR(2)` / `INT` | El día del mes en que se programa el pago. | Debe coincidir con `CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_inicio)[1]`. Valores permitidos: '10', '20', '30'. |

### Atributos de Lectura (Dependencias)

| Campo (PostgreSQL) | Tipo | Uso en la Migración |
| :--- | :--- | :--- |
| `ID_CONTRATO_M` | `SERIAL` | PK usada para la condición `WHERE` en el `UPDATE`. |
| `FECHA_INICIO_CONTRATO_M` | `DATE/VARCHAR` | Se extrae su día (`.day`) para determinar el grupo y fecha de pago. |
| `ESTADO_CONTRATO_M` | `VARCHAR` | Condición de filtro `WHERE ESTADO_CONTRATO_M = 'Activo'`. |

## Transiciones de Estado
No aplican cambios de estado al contrato. Se restringe la modificación de forma que el estado (`ESTADO_CONTRATO_M`) permanezca inalterado.

## Reglas de Integridad
- **Transaccionalidad (ACID)**: Los campos `GRUPO_OPERATIVO` y `FECHA_PAGO` deben actualizarse de manera conjunta en un único bloque `UPDATE` para evitar que un contrato quede con Grupo 1 pero Pago 30.
- El script debe emplear la cláusula `RETURNING id_contrato_m` (o ejecutar un `SELECT` previo para comparar) para validar los IDs afectados, acorde a las directivas generales de PostgreSQL del proyecto.

# Quickstart: Validación de Migración de Grupo Operativo

Esta guía describe cómo verificar y ejecutar de manera segura el script de migración que recalibra el `grupo_operativo` y `fecha_pago` de los contratos de Mandato.

## 1. Prerrequisitos
- El sistema debe estar configurado para conectarse a la base de datos PostgreSQL local o de desarrollo.
- El módulo de Dominio (`src/dominio/servicios/calculadora_contratos.py`) no requiere modificaciones adicionales.

## 2. Ejecución en Modo Diagnóstico (Dry-Run)
Por seguridad, el script ejecuta por defecto en modo solo-lectura (identificando discrepancias sin realizar commits).

```bash
# Ejecutar desde la raíz del proyecto
python scripts/migraciones/migrar_grupos_mandatos_v2.py
```
**Resultado Esperado**:
El sistema imprimirá en consola una lista de los contratos con discrepancias (incluyendo ID 47, 55, 56).
```text
INFO: [DRY-RUN] Se encontraron 8 discrepancias en contratos de Mandato activos.
INFO: Contrato ID 56 - Grupo Actual: 2, Esperado: 3 | Pago Actual: 20, Esperado: 30
INFO: Contrato ID 47 - Grupo Actual: 2, Esperado: 3 | Pago Actual: 20, Esperado: 30
...
```

## 3. Ejecución Efectiva (Commit)
Una vez validada la lista de contratos afectados, ejecuta el script con el flag para modificar la base de datos de manera atómica:

```bash
python scripts/migraciones/migrar_grupos_mandatos_v2.py --commit
```
**Resultado Esperado**:
```text
INFO: [COMMIT] Iniciando transacción...
INFO: Actualizando 8 contratos de Mandato...
INFO: Transacción exitosa. Cambios confirmados.
```

## 4. Validación de la Corrección
Para verificar que el sistema fue reparado, puedes ejecutar un query rápido en PostgreSQL o usar el script de validación provisto:

```bash
# Validar en terminal que el ID 56 ya está en el grupo correcto
python -c "
from src.infraestructura.persistencia.database import db_manager
with db_manager.obtener_conexion() as conn:
    cursor = db_manager.get_dict_cursor(conn)
    cursor.execute('SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = 56')
    print(cursor.fetchone())
"
```
**Resultado Esperado**: `{'grupo_operativo': 3, 'fecha_pago': '30'}`

Adicionalmente, se puede ingresar a la interfaz de Reflex (UI), abrir el **Contrato ID 56**, y validar que el *Badge* de Grupo de Pago indica correctamente **Grupo 3**.

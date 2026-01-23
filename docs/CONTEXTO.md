# CONTEXTO GENERAL DEL SISTEMA Y GOBIERNO DE DATOS

**Versión del Documento:** 1.0.0
**Rol Responsable:** Arquitectura de Software y Datos
**Fecha de Emisión:** Diciembre 2025

---

## 1. Visión Arquitectónica: Data-Centric Architecture

Este documento establece las directrices fundamentales para el desarrollo, evolución y mantenimiento del Sistema de Gestión Inmobiliaria (**InmoVelar**). Se define una arquitectura donde la integridad, consistencia y persistencia de los datos rigen sobre las abstracciones de la capa de aplicación.

El sistema se adhiere al principio de **"Single Source of Truth"** (Fuente Única de Verdad), materializado estrictamente en el componente de base de datos relacional.

---

## 2. Componente Central de Persistencia

### 2.1 Definición del Core de Datos
El núcleo inamovible y obligatorio del sistema es la base de datos:

*   **Identificador del Recurso:** `DB_Inmo_Velar.db`
*   **Tecnología**: SQLite Version 3.x
*   **Carácter:** **OBLIGATORIO Y NO NEGOCIABLE.**

### 2.2 Rol en la Arquitectura
La base de datos `DB_Inmo_Velar.db` no es un simple repositorio pasivo; es la **autoridad final** sobre el estado del sistema. 
1.  **Modelo Físico == Modelo de Dominio:** Las entidades de software deben reflejar fielmente las estructuras de datos definidas en el esquema SQL.
2.  **Integridad Referencial:** La integridad de los datos se garantiza a nivel de motor de base de datos (FOREIGN KEYS, CHECK CONSTRAINTS, TRIGGERS), no exclusivamente en la capa de aplicación.

---

## 3. Reglas de Gobierno de Datos y Acceso

### 3.1 Política de Fuente Única de Verdad
*   Toda información transaccional, paramétrica, de configuración o de auditoría debe residir exclusivamente en `DB_Inmo_Velar.db`.
*   **Regla de Oro:** Si un dato no existe en la base de datos, no existe en el sistema.

### 3.2 Protocolos de Acceso
*   El acceso a la base de datos debe realizarse a través de una **Capa de Infraestructura Controlada** (Repositorios/DAOs) que encapsule la lógica SQL.
*   Está **prohibido** el acceso directo o "hardcoded" desde las capas de Presentación (UI) o desde los Controladores.
*   Se debe implementar el patrón **Unit of Work** o gestión transaccional robusta para garantizar la atomicidad de las operaciones críticas (ACID).

---

## 4. Restricciones y Prohibiciones Críticas

Para garantizar la estabilidad y mantenibilidad a largo plazo, se establecen las siguientes prohibiciones estrictas:

1.  **Prohibición de Persistencia Alterna:** Queda terminantemente prohibido el uso de archivos planos (CSV, JSON, XML, TXT), bases de datos embebidas alternativas o almacenamiento en memoria volátil como mecanismo de persistencia principal o secundario para datos de negocio.
2.  **Prohibición de "Campos Fantasma":** Las entidades de software (Clases/Structs) no pueden contener atributos de negocio que no tengan una columna correspondiente en la tabla SQL física. Los campos calculados deben ser explícitamente marcados como tales o generados bajo demanda, nunca almacenados en memoria como estado persistente.
3.  **Prohibición de Enmascaramiento de Datos:** La aplicación no debe transformar silenciosamente los datos de manera que el estado en memoria difiera semánticamente del estado en disco de forma irrecuperable.

---

## 5. Impacto en el Diseño del Sistema

Estas reglas imponen un diseño de software **impulsado por el esquema (Schema-Driven Design)** en las capas inferiores:

*   **Sincronización:** Cualquier cambio en los requisitos de información debe comenzar con una migración de base de datos (DDL) antes de reflejarse en el código fuente.
*   **Validación:** Las validaciones de negocio en Python deben complementar, **nunca contradecir**, las restricciones definidas en el esquema SQL (tipos de datos, nulabilidad, longitud).
*   **Auditoría:** El sistema debe respetar y facilitar los mecanismos de auditoría a nivel de base de datos (Triggers, columnas `CREATED_BY`, `UPDATED_AT`), asegurando que cada transacción inyecte el contexto necesario (ej. ID de usuario) para que la base de datos pueda registrar la trazabilidad.

---

## 6. Entidades de Dominio Críticas

### 6.1 ReciboPublico (Módulo de Servicios Públicos)

**Propósito:** Entidad que representa un recibo de servicio público (Agua, Luz, Gas, Internet, Teléfono, Aseo, Otros) asociado a una propiedad inmobiliaria.

**Tabla de Base de Datos:** `RECIBOS_PUBLICOS`

**Reglas de Negocio:**

1. **Constraint de Unicidad:** Cada propiedad puede tener ÚNICAMENTE un recibo por tipo de servicio y período.
   - `UNIQUE (ID_PROPIEDAD, PERIODO_RECIBO, TIPO_SERVICIO)`
   - Esto previene duplicados y asegura integridad de datos.

2. **Validación de Valores:**
   - `valor_recibo >= 0` (no puede ser negativo)
   - `tipo_servicio` debe pertenecer al enum: `['Agua', 'Luz', 'Gas', 'Internet', 'Teléfono', 'Aseo', 'Otros']`
   - `estado` debe pertenecer al enum: `['Pendiente', 'Pagado', 'Vencido']`
   - `periodo_recibo` debe seguir formato `YYYY-MM` (ej: 2025-12)

3. **Transiciones de Estado:**
   - **Pendiente → Pagado:** Solo mediante método `marcar_como_pagado()` 
     - Requiere: `fecha_pago` y `comprobante`
   - **Pendiente → Vencido:** Automático si `fecha_vencimiento < date.today()` y `estado == 'Pendiente'`
   - **Inmutabilidad:** Los recibos con estado `Pagado` NO pueden ser editados ni eliminados

4. **Propiedades Calculadas:**
   - `esta_pagado`: Verifica si `estado == "Pagado"`
   - `esta_vencido`: Verifica si `estado == "Vencido"` o si está pendiente con fecha vencida
   - `dias_para_vencimiento`: Calcula días restantes (negativo si ya venció)

5. **Auditoría Automática:**
   - Registro de `created_by`, `created_at`, `updated_by`, `updated_at` en todas las operaciones
   - Los triggers de base de datos registran cambios en `AUDITORIA_CAMBIOS`

**Integración con el Sistema:**
- Se relaciona con la entidad `Propiedad` mediante `ID_PROPIEDAD` (FK)
- El servicio `ServicioRecibosPublicos` gestiona toda la lógica de negocio
- El repositorio `RepositorioReciboPublicoSQLite` maneja la persistencia
- Las vistas UI en `recibos_publicos_list_view.py` y `recibo_publico_form_view.py` proporcionan la interfaz de usuario

**Job Automático:**
- Método `verificar_vencimientos()` debe ejecutarse periódicamente (diariamente) para actualizar estados de recibos pendientes que hayan vencido

---

### 6.2 LiquidacionAsesor (Módulo de Liquidación de Asesores)

**Propósito:** Entidad que representa una liquidación de comisión para un asesor inmobiliario por la gestión de propiedades en arrendamiento.

**Tabla de Base de Datos:** `LIQUIDACIONES_ASESORES`

**Fórmula de Cálculo de Comisiones:**
```
COMISIÓN BRUTA = CANON_ARRENDAMIENTO × (PORCENTAJE_COMISION / 10000)
VALOR NETO = COMISIÓN BRUTA - TOTAL_DESCUENTOS
```

> [!NOTE]
> El porcentaje de comisión se almacena en formato entero (0-10000) representando 0.00% - 100.00%. Por ejemplo: 550 = 5.50%

**Reglas de Negocio:**

1. **Constraint de Unicidad:** Cada asesor puede tener ÚNICAMENTE una liquidación por período.
   - `UNIQUE (ID_ASESOR, PERIODO)` (desde migración multi-contrato)
   - LEGACY: `UNIQUE (ID_CONTRATO_A, PERIODO)` (descontinuado)

2. **Validación de Valores:**
   - `porcentaje_comision` debe estar entre 0 y 10000 (representa 0.00% - 100.00%)
   - `comision_bruta >= 0`
   - `total_descuentos >= 0`
   - `valor_neto_asesor >= 0`
   - `periodo_liquidacion` debe seguir formato `YYYY-MM`

3. **Transiciones de Estado:**
   ```
   Pendiente → Aprobada → Pagada
        ↓           ↓
      Anulada ← ─ ─ ┘ (No desde Pagada)
   ```
   - **Pendiente → Aprobada:** Via método `aprobar()` - Requiere usuario aprobador
   - **Aprobada → Pagada:** Via método `marcar_como_pagada()` - Solo después de aprobar
   - **Pendiente/Aprobada → Anulada:** Via método `anular()` - Requiere motivo
   - **Inmutabilidad:** Las liquidaciones en estado `Pagada` NO pueden ser anuladas ni editadas

4. **Propiedades Calculadas:**
   - `esta_pendiente`: Estado == "Pendiente"
   - `esta_aprobada`: Estado == "Aprobada"  
   - `esta_pagada`: Estado == "Pagada"
   - `puede_aprobarse`: Solo si está pendiente
   - `puede_anularse`: No si está pagada o ya anulada
   - `puede_editarse`: Solo si está pendiente
   - `porcentaje_real`: Retorna el porcentaje como decimal (ej: 5.5 para 5.50%)

5. **Soporte Multi-Contrato:**
   - Una liquidación puede incluir múltiples contratos del mismo asesor
   - Tabla intermedia: `LIQUIDACIONES_CONTRATOS (ID_LIQUIDACION_A, ID_CONTRATO_A, CANON_CONTRATO)`
   - El canon total es la suma de todos los cánones de los contratos incluidos

---

### 6.3 DescuentoAsesor (Descuentos de Liquidación)

**Propósito:** Entidad que representa un descuento aplicado a una liquidación de asesor.

**Tabla de Base de Datos:** `DESCUENTOS_ASESORES`

**Reglas de Negocio:**

1. **Validación de Valores:**
   - `valor_descuento >= 0`
   - `descripcion_descuento` es obligatoria (no puede estar vacía)
   - `tipo_descuento` debe pertenecer al enum:
     - `['Préstamo', 'Anticipo', 'Sanción', 'Ajuste', 'Otros']`

2. **Tipos de Descuento:**
   | Tipo | Descripción |
   |------|-------------|
   | Préstamo | Abono a préstamo otorgado al asesor |
   | Anticipo | Deducción de anticipo previo |
   | Sanción | Penalización por incumplimiento |
   | Ajuste | Corrección por errores previos |
   | Otros | Cualquier otro concepto |

3. **Impacto en Liquidación:**
   - Al agregar/eliminar un descuento, el `valor_neto_asesor` de la liquidación padre se recalcula automáticamente

---

### 6.4 PagoAsesor (Pagos a Asesores)

**Propósito:** Entidad que representa un pago realizado o programado a un asesor por concepto de comisiones.

**Tabla de Base de Datos:** `PAGOS_ASESORES`

**Reglas de Negocio:**

1. **Validación de Valores:**
   - `valor_pago > 0` (debe ser positivo)
   - `referencia_pago` debe ser ÚNICA
   - `medio_pago` debe pertenecer al enum:
     - `['Transferencia', 'Cheque', 'Efectivo', 'PSE']`
   - `estado_pago` debe pertenecer al enum:
     - `['Pendiente', 'Programado', 'Pagado', 'Rechazado', 'Anulado']`

2. **Transiciones de Estado:**
   ```
   Pendiente → Programado → Pagado
        ↓           ↓
   Rechazado   Rechazado/Anulado
        ↓
     Anulado
   ```
   - **Pendiente → Programado:** Via `programar()` - Requiere fecha programada
   - **Pendiente/Programado → Pagado:** Via `marcar_como_pagado()` - Requiere fecha_pago y comprobante
   - **Pendiente/Programado → Rechazado:** Via `rechazar()` - Requiere motivo
   - **Pendiente/Programado/Rechazado → Anulado:** Via `anular()`
   - **Inmutabilidad:** Los pagos en estado `Pagado` NO pueden ser anulados

3. **Requisitos por Estado:**
   | Estado | Campos Requeridos |
   |--------|-------------------|
   | Pagado | `fecha_pago`, `comprobante_pago` |
   | Rechazado | `motivo_rechazo` |
   | Programado | `fecha_programada` |

4. **Propiedades Calculadas:**
   - `puede_pagarse`: Solo si está Pendiente o Programado
   - `puede_rechazarse`: Solo si está Pendiente o Programado
   - `puede_anularse`: No si ya está Pagado o Anulado

---

### 6.5 Integración del Módulo de Liquidación de Asesores

**Archivos del Sistema:**
- **Entidades:** `liquidacion_asesor.py`, `descuento_asesor.py`, `pago_asesor.py`
- **Repositorios:** `repositorio_liquidacion_asesor_sqlite.py`, `repositorio_descuento_asesor_sqlite.py`, `repositorio_pago_asesor_sqlite.py`
- **Servicio:** `servicio_liquidacion_asesores.py`
- **Vistas UI:** `liquidaciones_asesores_list_view.py`, `liquidacion_asesor_form_view.py`, `liquidacion_asesor_detail_view.py`, `pagos_asesores_list_view.py`

**Flujo de Trabajo Típico:**
1. Usuario genera liquidación para un asesor y período
2. Sistema calcula comisión bruta automáticamente
3. Usuario agrega descuentos (opcional)
4. Sistema recalcula valor neto
5. Usuario aprueba la liquidación
6. Sistema programa pago
7. Usuario registra pago efectivo con comprobante
8. Liquidación queda cerrada como "Pagada"

---

### 6.6 ParametroSistema (Módulo de Configuración)

**Propósito:** Entidad que representa parámetros globales configurables del sistema (comisiones, impuestos, alertas).

**Tabla de Base de Datos:** `PARAMETROS_SISTEMA`

**Reglas de Negocio:**

1. **Tipos de Datos Soportados:**
   - `INTEGER`: Números enteros (ej. días alerta)
   - `DECIMAL`: Valores decimales (ej. porcentajes, dinero)
   - `BOOLEAN`: Banderas activo/inactivo (1/0)
   - `TEXT`: Cadenas de texto

2. **Inmutabilidad de Definición:**
   - Hay parámetros marcados como `modificable=0` que NO pueden ser editados por usuarios, ni siquiera administradores (ej. Impuesto 4x1000). Son constantes del sistema.

3. **Categorización:**
   - Los parámetros se agrupan por `CATEGORIA` (ej. 'COMISIONES', 'IMPUESTOS') para organización en la UI.

4. **Auditoría:**
   - Registro de último usuario que modificó el parámetro (`updated_by`).

**Integración del Módulo:**
- **Servicio Unificado:** `ServicioConfiguracion` gestiona:
  - Usuarios (CRUD, Password Reset)
  - IPC (Índice de Precios al Consumidor)
  - Parámetros del Sistema
- **Vista:** `configuracion_view.py` centraliza la gestión en 3 pestañas.
- **Acceso:** Restringido exclusivamente al rol **Administrador**.

---

**NOTA FINAL:** El incumplimiento de estas directrices constituye una violación crítica de la arquitectura y deuda técnica inaceptable. Cualquier desviación requiere autorización explícita y documentada del equipo de Arquitectura.

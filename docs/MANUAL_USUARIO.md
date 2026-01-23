# Manual de Usuario - Sistema de Gestión Inmobiliaria Velar

**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Sistema:** InmoVelar Desktop

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Inicio Rápido](#inicio-rápido)
3. [Módulo de Personas](#módulo-de-personas)
4. [Módulo de Propiedades](#módulo-de-propiedades)
5. [Módulo de Contratos](#módulo-de-contratos)
6. [Módulo Financiero](#módulo-financiero)
7. [Módulo de Incidentes](#módulo-de-incidentes)
8. [Dashboard y Alertas](#dashboard-y-alertas)
9. [Generación de Documentos](#generación-de-documentos)
10. [Troubleshooting](#troubleshooting)

---

## Introducción

### ¿Qué es InmoVelar?

InmoVelar es un sistema de gestión inmobiliaria integral diseñado para administrar propiedades, contratos, pagos, mantenimientos y relaciones con clientes de manera eficiente y profesional.

### Características Principales

- ✅ **Gestión de Terceros**: Administre propietarios, arrendatarios, asesores, codeudores y proveedores
- ✅ **Inventario de Propiedades**: Control completo del portafolio inmobiliario
- ✅ **Contratos Digitales**: Mandatos y arrendamientos con alertas automáticas
- ✅ **Módulo Financiero**: Recaudos, liquidaciones y generación de PDFs
- ✅ **Gestión de Incidentes**: Sistema Kanban para mantenimientos y reparaciones
- ✅ **Dashboard en Tiempo Real**: Métricas y alertas de negocio

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10 o superior
- **Python**: 3.10 o superior (incluido en la instalación)
- **Espacio en Disco**: 100 MB mínimo
- **Resolución de Pantalla**: 1366x768 o superior (recomendado: 1920x1080)

### Convenciones del Manual

- 🔹 **Nota**: Información adicional importante
- ⚠️ **Advertencia**: Precaución necesaria
- ✅ **Tip**: Sugerencia para mejorar la experiencia
- 📝 **Ejemplo**: Caso de uso práctico

---

## Inicio Rápido

### Primer Acceso al Sistema

1. **Ejecutar la aplicación**
   - Haga doble clic en el icono de InmoVelar
   - Espere a que se cargue la pantalla de login

2. **Iniciar Sesión**
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
   - Haga clic en **"Iniciar Sesión"**

   🔹 **Nota**: Las credenciales por defecto deben cambiarse después del primer acceso.

3. **Pantalla Principal**
   - Después del login exitoso, verá el **Dashboard** con métricas en tiempo real
   - En el lado izquierdo encontrará el **Menú de Navegación** (Sidebar)
   - En la parte superior está la **Barra de Alertas**

### Navegación Básica

#### Menú Lateral (Sidebar)

El menú lateral contiene todas las secciones del sistema:

- 🏠 **Dashboard**: Página principal con métricas
- 👥 **Personas**: Gestión de terceros
- 🏢 **Propiedades**: Inventario inmobiliario
- 📄 **Contratos**: Mandatos y arrendamientos
- 💰 **Recaudos**: Registro de pagos
- 📊 **Liquidaciones**: Estados de cuenta
- 🔧 **Incidentes**: Mantenimientos
- 🏪 **Proveedores**: Empresas de servicio
- 🔔 **Alertas**: Centro de notificaciones

✅ **Tip**: Haga clic en cualquier ítem del menú para navegar a esa sección.

---

## Módulo de Personas

El módulo de Personas implementa el **Party Model**, permitiendo que una misma persona tenga múltiples roles en el sistema.

### Roles Disponibles

- **Propietario**: Dueño de propiedades
- **Arrendatario**: Inquilino que renta propiedades
- **Asesor**: Agente inmobiliario
- **Codeudor**: Garante de contratos
- **Proveedor**: Empresa de mantenimiento

🔹 **Nota**: Una persona puede tener varios roles simultáneamente (ej: ser Propietario y Asesor).

### Crear Nueva Persona

1. **Acceder al módulo**
   - Clic en **"Personas"** en el menú lateral
   - Clic en el botón **"+ Nueva Persona"**

2. **Datos Básicos**
   - **Tipo de Persona**: Natural o Jurídica
   - **Nombres**: Nombre completo (o razón social)
   - **Apellidos**: Apellidos (solo para personas naturales)
   - **Tipo de Documento**: CC, CE, NIT, Pasaporte
   - **Número de Documento**: Sin puntos ni guiones

3. **Información de Contacto**
   - **Celular Principal**: Número de contacto
   - **Celular Secundario**: (Opcional)
   - **Correo Principal**: Email de contacto
   - **Correo Secundario**: (Opcional)

4. **Ubicación**
   - **Municipio**: Seleccione de la lista
   - **Dirección**: Dirección completa
   - **Barrio**: (Opcional)

5. **Asignación de Roles**
   - Marque los checkboxes de los roles que desea asignar
   - Algunos roles requieren información adicional:

   **Propietario:**
   - Banco para consignaciones
   - Tipo de cuenta
   - Número de cuenta

   **Asesor:**
   - Porcentaje de comisión
   - Observaciones

   **Proveedor:**
   - Especialidad (Plomería, Electricidad, etc.)
   - Observaciones

6. **Guardar**
   - Clic en **"Guardar"**
   - El sistema mostrará un mensaje de confirmación

📝 **Ejemplo**: Para crear un propietario que también es asesor, marque ambos checkboxes y complete los datos bancarios y el porcentaje de comisión.

### Editar Persona

1. En la lista de personas, haga clic en el ícono de **edición** (lápiz)
2. Modifique los campos necesarios
3. Puede agregar o quitar roles
4. Clic en **"Guardar"** para confirmar cambios

### Buscar y Filtrar

- **Búsqueda**: Escriba nombre o número de documento en el campo de búsqueda
- **Filtro por Rol**: Use el dropdown para ver solo personas con un rol específico
- **Activos/Inactivos**: Use el switch para ver personas desactivadas

### Desactivar Persona

⚠️ **Advertencia**: Desactivar una persona no la elimina, solo la oculta de las listas activas.

1. Clic en el ícono de **desactivar** (ojo tachado)
2. Confirme la acción
3. La persona ya no aparecerá en las listas de selección

---

## Módulo de Propiedades

Gestione el inventario completo de propiedades disponibles para arrendamiento o venta.

### Registrar Nueva Propiedad

1. **Acceder al módulo**
   - Clic en **"Propiedades"** en el menú lateral
   - Clic en **"+ Nueva Propiedad"**

2. **Identificación**
   - **Matrícula Inmobiliaria**: Número único de registro
   - **Fecha de Registro**: Fecha de ingreso al sistema

3. **Ubicación**
   - **Municipio**: Seleccione de la lista
   - **Dirección**: Dirección completa del inmueble
   - **Barrio**: Nombre del barrio

4. **Características**
   - **Tipo de Inmueble**: Casa, Apartamento, Local, Oficina, Bodega, Lote
   - **Área (m²)**: Área construida
   - **Habitaciones**: Número de habitaciones
   - **Baños**: Número de baños
   - **Parqueaderos**: Número de parqueaderos
   - **Estrato**: 1 a 6

5. **Información Financiera**
   - **Valor Administración**: Cuota de administración mensual
   - **Canon Arrendamiento**: Valor de arriendo mensual
   - **Valor Venta**: Precio de venta (si aplica)
   - **% Comisión**: Porcentaje de comisión para el asesor

6. **Disponibilidad**
   - **Disponible para Arriendo**: Sí/No
   - **Disponible para Venta**: Sí/No

7. **Observaciones**
   - Notas adicionales sobre la propiedad

8. **Guardar**
   - Clic en **"Guardar"**

### Vistas de Propiedades

El sistema ofrece dos vistas:

#### Vista de Tarjetas (Cards)
- Muestra propiedades en formato de tarjetas visuales
- Ideal para ver fotos y características rápidas
- Use el botón **"Vista Cards"** para activar

#### Vista de Tabla
- Muestra propiedades en formato tabular
- Ideal para comparar múltiples propiedades
- Use el botón **"Vista Tabla"** para activar

### Filtros Disponibles

- **Tipo de Inmueble**: Casa, Apartamento, Local, etc.
- **Disponibilidad**: Disponible, Ocupada
- **Municipio**: Filtrar por ubicación
- **Búsqueda**: Por matrícula o dirección

✅ **Tip**: Use los filtros combinados para encontrar propiedades específicas rápidamente.

### Editar Propiedad

1. Clic en el ícono de **edición** en la tarjeta o fila
2. Modifique los campos necesarios
3. Clic en **"Guardar"**

### Cambiar Disponibilidad

- Use el switch **"Disponible"** para marcar una propiedad como ocupada o disponible
- Esto afecta la visibilidad en búsquedas de propiedades disponibles

---

## Módulo de Contratos

Gestione contratos de mandato (con propietarios) y contratos de arrendamiento (con inquilinos).

### Tipos de Contratos

1. **Contrato de Mandato**: Acuerdo con el propietario para administrar su propiedad
2. **Contrato de Arrendamiento**: Acuerdo con el inquilino para rentar la propiedad

### Crear Contrato de Mandato

1. **Acceder al módulo**
   - Clic en **"Contratos"** en el menú lateral
   - Pestaña **"Mandatos"**
   - Clic en **"+ Nuevo Mandato"**

2. **Información Básica**
   - **Propiedad**: Seleccione de la lista de propiedades disponibles
   - **Propietario**: Seleccione de la lista de personas con rol Propietario
   - **Fecha Inicio**: Fecha de inicio del contrato
   - **Fecha Fin**: Fecha de finalización
   - **Duración (meses)**: Se calcula automáticamente

3. **Condiciones Económicas**
   - **% Comisión Administración**: Porcentaje que cobra la inmobiliaria
   - **Observaciones**: Notas adicionales

4. **Guardar**
   - Clic en **"Guardar"**

🔹 **Nota**: Solo puede haber **un contrato de mandato activo** por propiedad.

### Crear Contrato de Arrendamiento

1. **Acceder al módulo**
   - Pestaña **"Arrendamientos"**
   - Clic en **"+ Nuevo Arrendamiento"**

2. **Información Básica**
   - **Propiedad**: Solo propiedades con mandato activo
   - **Arrendatario**: Persona con rol Arrendatario
   - **Codeudor**: (Opcional) Persona con rol Codeudor
   - **Fecha Inicio**: Fecha de inicio del arriendo
   - **Fecha Fin**: Fecha de finalización
   - **Duración (meses)**: Se calcula automáticamente

3. **Condiciones Económicas**
   - **Canon Mensual**: Valor del arriendo
   - **Valor Administración**: Cuota de administración
   - **Depósito**: Valor del depósito en garantía
   - **Día de Pago**: Día del mes para pago (1-31)

4. **Incrementos**
   - **Incremento Anual (%)**: Porcentaje de incremento IPC
   - **Fecha Último Incremento**: Fecha del último ajuste

5. **Observaciones**
   - Notas adicionales del contrato

6. **Guardar**
   - Clic en **"Guardar"**

🔹 **Nota**: Solo puede haber **un contrato de arrendamiento activo** por propiedad.

### Ver Detalles de Contrato

1. En la lista de contratos, haga clic en el ícono de **"Ver Detalle"** (ojo)
2. Se abrirá un modal con información completa:
   - Datos del contrato
   - Información de las partes
   - Condiciones económicas
   - Fechas importantes
   - Historial de cambios

### Alertas de Vencimiento

El sistema genera alertas automáticas:

- **90 días antes**: Alerta temprana
- **60 días antes**: Alerta de planificación
- **30 días antes**: Alerta urgente
- **Al vencimiento**: Alerta crítica

✅ **Tip**: Revise regularmente el centro de alertas para no perder vencimientos importantes.

### Renovar Contrato

⚠️ **Advertencia**: La renovación de contratos debe hacerse antes del vencimiento.

1. Desde el detalle del contrato, identifique la fecha de vencimiento
2. Cree un nuevo contrato con las nuevas condiciones
3. El sistema marcará el contrato anterior como renovado

---

## Módulo Financiero

Gestione recaudos (pagos de inquilinos) y liquidaciones (estados de cuenta de propietarios).

### Sección: Recaudos

#### Registrar Nuevo Recaudo

1. **Acceder al módulo**
   - Clic en **"Recaudos"** en el menú lateral
   - Clic en **"+ Registrar Pago"**

2. **Información del Pago**
   - **Contrato**: Seleccione el contrato de arrendamiento
   - **Fecha de Pago**: Fecha en que se recibió el pago
   - **Método de Pago**: Efectivo, Transferencia, Cheque, etc.
   - **Referencia Bancaria**: (Requerido para transferencias)

3. **Conceptos de Pago**
   
   El sistema calcula automáticamente los conceptos:
   
   - **Canon de Arrendamiento**: Valor del arriendo mensual
   - **Administración**: Cuota de administración
   - **Mora**: Se calcula automáticamente si hay retraso (6% anual)
   - **Otros Conceptos**: (Opcional) Servicios adicionales

4. **Total**
   - El sistema suma todos los conceptos automáticamente
   - **No se permiten pagos parciales**

5. **Guardar**
   - Clic en **"Registrar Pago"**
   - El sistema genera un comprobante PDF automáticamente

📝 **Ejemplo**: Si un inquilino paga el 15 de enero y su fecha de pago es el 5, el sistema calculará mora por 10 días de retraso.

#### Cálculo de Mora

El sistema calcula mora automáticamente:

```
Mora = (Canon + Administración) × (6% / 365) × Días de Retraso
```

🔹 **Nota**: La tasa de mora es del 6% anual según la configuración del sistema.

#### Estados de Recaudo

- **Pendiente**: Pago registrado pero no aplicado
- **Aplicado**: Pago confirmado y aplicado al contrato
- **Reversado**: Pago anulado (requiere autorización)

#### Aprobar/Reversar Recaudo

1. En la lista de recaudos, identifique el pago
2. Clic en **"Aprobar"** para aplicar el pago
3. Clic en **"Reversar"** para anular (solo Gerente)

### Sección: Liquidaciones

Las liquidaciones son estados de cuenta mensuales para propietarios.

#### Generar Nueva Liquidación

1. **Acceder al módulo**
   - Clic en **"Liquidaciones"** en el menú lateral
   - Clic en **"+ Nueva Liquidación"**

2. **Información Básica**
   - **Contrato de Arrendamiento**: Seleccione el contrato
   - **Período**: Mes y año (formato: YYYY-MM)

3. **Ingresos** (Calculados automáticamente)
   - **Canon Bruto**: Valor del arriendo recibido
   - **Otros Ingresos**: Conceptos adicionales

4. **Egresos** (Calculados automáticamente)
   - **Comisión Administración**: % según contrato de mandato
   - **IVA sobre Comisión**: 19% sobre la comisión
   - **4x1000**: Impuesto sobre transacciones financieras
   - **Costos de Incidentes**: Reparaciones del mes

5. **Neto a Pagar**
   ```
   Neto = Ingresos - Egresos
   ```

6. **Guardar**
   - Clic en **"Generar Liquidación"**

#### Estados de Liquidación

- **Generada**: Liquidación creada, pendiente de revisión
- **Aprobada**: Revisada y aprobada por Contabilidad
- **Pagada**: Pago realizado al propietario
- **Cancelada**: Liquidación anulada

#### Flujo de Aprobación

1. **Generar**: Contabilidad crea la liquidación
2. **Aprobar**: Gerente revisa y aprueba
3. **Pagar**: Se registra el comprobante de pago
4. **Imprimir**: Se genera PDF del estado de cuenta

✅ **Tip**: Solo puede haber **una liquidación por contrato por mes**.

#### Ver Detalle de Liquidación

1. Clic en el ícono de **"Ver Detalle"** (ojo)
2. Se muestra:
   - Desglose completo de ingresos y egresos
   - Información del propietario
   - Datos bancarios para consignación
   - Historial de cambios

---

## Módulo de Incidentes

Gestione mantenimientos, reparaciones y solicitudes de servicio mediante un sistema Kanban visual.

### Vista Kanban

El módulo de incidentes utiliza una vista Kanban con 5 columnas:

1. **Reportado**: Incidente recién creado
2. **Cotizado**: Con cotización de proveedor
3. **Aprobado**: Cotización aprobada
4. **En Reparación**: Trabajo en progreso
5. **Finalizado**: Incidente resuelto

### Reportar Nuevo Incidente

1. **Acceder al módulo**
   - Clic en **"Incidentes"** en el menú lateral
   - Clic en **"+ Reportar Incidente"**

2. **Información Básica**
   - **Propiedad**: Seleccione la propiedad afectada
   - **Título**: Descripción breve del problema
   - **Descripción**: Detalle completo del incidente
   - **Prioridad**: Baja, Media, Alta, Crítica

3. **Clasificación**
   - **Categoría**: Plomería, Electricidad, Pintura, etc.
   - **Responsable del Costo**: Propietario o Arrendatario

4. **Asignación** (Opcional)
   - **Proveedor**: Seleccione un proveedor si ya sabe quién atenderá

5. **Evidencias**
   - 🔹 **Nota**: La carga de imágenes está pendiente de implementación

6. **Guardar**
   - Clic en **"Reportar"**
   - El incidente aparecerá en la columna **"Reportado"**

### Gestionar Cotizaciones

#### Registrar Cotización

1. Desde el detalle del incidente, clic en **"Agregar Cotización"**
2. Complete:
   - **Proveedor**: Empresa que cotiza
   - **Valor Cotizado**: Monto del presupuesto
   - **Descripción del Trabajo**: Detalle de la reparación
   - **Tiempo Estimado**: Días de ejecución

3. Clic en **"Guardar Cotización"**
4. El incidente se mueve a la columna **"Cotizado"**

#### Aprobar Cotización

1. Desde el detalle del incidente, revise la cotización
2. Clic en **"Aprobar Cotización"**
3. El incidente se mueve a la columna **"Aprobado"**

#### Rechazar Cotización

1. Clic en **"Rechazar Cotización"**
2. Ingrese el motivo del rechazo
3. El incidente regresa a **"Reportado"** para nueva cotización

🔹 **Nota**: Puede haber múltiples cotizaciones rechazadas antes de aprobar una.

### Flujo de Estados

```
Reportado → Cotizado → Aprobado → En Reparación → Finalizado
                ↓
            Cancelado
```

#### Avanzar Estado

1. Desde el detalle del incidente, use el botón **"Avanzar Estado"**
2. El sistema valida que se cumplan las condiciones:
   - Para pasar a **Cotizado**: Debe tener al menos una cotización
   - Para pasar a **Aprobado**: Debe tener una cotización aprobada
   - Para pasar a **En Reparación**: Debe estar aprobado
   - Para pasar a **Finalizado**: Debe estar en reparación

⚠️ **Advertencia**: No se puede saltar estados. El flujo es secuencial.

### Finalizar Incidente

1. Cuando el trabajo esté completo, clic en **"Finalizar"**
2. Ingrese:
   - **Costo Final**: Valor real del trabajo
   - **Comentarios**: Observaciones finales
3. El sistema:
   - Marca el incidente como **Finalizado**
   - Registra la fecha de finalización
   - Carga el costo a la liquidación del mes (si aplica)

### Filtros Avanzados

- **Búsqueda**: Por título o descripción
- **Propiedad**: Filtrar por inmueble
- **Prioridad**: Baja, Media, Alta, Crítica
- **Rango de Fechas**: Desde - Hasta
- **Proveedor Asignado**: Filtrar por empresa
- **Días sin Resolver**: Incidentes antiguos

✅ **Tip**: Use el filtro "Días sin Resolver" para identificar incidentes que llevan mucho tiempo abiertos.

### Indicadores Visuales

- 🟢 **Verde**: Prioridad Baja
- 🟡 **Amarillo**: Prioridad Media
- 🟠 **Naranja**: Prioridad Alta
- 🔴 **Rojo**: Prioridad Crítica

---

## Módulo de Proveedores

Gestione empresas y profesionales que prestan servicios de mantenimiento y reparación.

### ¿Qué es un Proveedor?

Un proveedor es una persona (natural o jurídica) que ofrece servicios especializados para atender incidentes en las propiedades. Los proveedores pueden ser:

- Plomeros
- Electricistas
- Pintores
- Cerrajeros
- Empresas de mantenimiento
- Técnicos especializados

🔹 **Nota**: Los proveedores son un **rol** dentro del sistema de Personas. Una persona puede ser Proveedor y tener otros roles simultáneamente.

### Registrar Nuevo Proveedor

#### Opción 1: Desde el Módulo de Personas

1. **Acceder al módulo**
   - Clic en **"Personas"** en el menú lateral
   - Clic en **"+ Nueva Persona"**

2. **Completar datos básicos**
   - Tipo de Persona, Documento, Nombre, Contacto, Ubicación

3. **Asignar rol Proveedor**
   - Marque el checkbox **"Proveedor"**
   - Complete los campos adicionales:
     - **Especialidad**: Plomería, Electricidad, Pintura, etc.
     - **Observaciones**: Notas sobre servicios, horarios, etc.

4. **Guardar**
   - Clic en **"Guardar"**

#### Opción 2: Desde el Módulo de Proveedores

1. **Acceder al módulo**
   - Clic en **"Proveedores"** en el menú lateral
   - Clic en **"+ Nuevo Proveedor"**

2. **Datos de la Persona**
   - Complete todos los datos básicos de contacto

3. **Datos del Proveedor**
   - **Especialidad**: Seleccione o escriba la especialidad
   - **Observaciones**: Información adicional relevante

4. **Guardar**
   - Clic en **"Guardar"**

### Listar Proveedores

1. **Acceder al módulo**
   - Clic en **"Proveedores"** en el menú lateral

2. **Vista de Lista**
   - Se muestra una tabla con todos los proveedores activos
   - Columnas: Nombre, Documento, Especialidad, Teléfono, Acciones

### Buscar y Filtrar

- **Búsqueda**: Escriba nombre, documento o especialidad en el campo de búsqueda
- **Filtro por Especialidad**: Use el dropdown para ver solo proveedores de un tipo
- **Activos/Inactivos**: Use el switch para ver proveedores desactivados

✅ **Tip**: Use el filtro de especialidad cuando necesite encontrar rápidamente un proveedor para un tipo específico de incidente.

### Editar Proveedor

1. En la lista de proveedores, clic en el ícono de **edición** (lápiz)
2. Modifique los campos necesarios:
   - Datos de contacto
   - Especialidad
   - Observaciones
3. Clic en **"Guardar"**

### Desactivar Proveedor

⚠️ **Advertencia**: Desactivar un proveedor no elimina su historial de cotizaciones e incidentes atendidos.

1. Clic en el ícono de **desactivar** (ojo tachado)
2. Confirme la acción
3. El proveedor ya no aparecerá en las listas de selección para nuevos incidentes

### Integración con Incidentes

Los proveedores se integran directamente con el módulo de incidentes:

#### Asignar Proveedor a Incidente

1. Al reportar un incidente, puede seleccionar un proveedor en el campo **"Proveedor Asignado"**
2. El proveedor recibirá la notificación del incidente (funcionalidad futura)

#### Registrar Cotización

1. Desde el detalle del incidente
2. Clic en **"Agregar Cotización"**
3. Seleccione el **Proveedor** que cotiza
4. Complete valor y descripción del trabajo

#### Ver Historial de Proveedor

📝 **Ejemplo**: Para ver todos los incidentes atendidos por un proveedor:

1. Vaya al módulo de **Incidentes**
2. Use el filtro **"Proveedor Asignado"**
3. Seleccione el proveedor deseado
4. Se mostrarán todos sus incidentes

### Datos Importantes del Proveedor

Cada proveedor almacena:

- **Datos de Contacto**: Teléfonos, correos, dirección
- **Especialidad**: Tipo de servicio que ofrece
- **Observaciones**: Horarios, tarifas, notas importantes
- **Historial**: Todos los incidentes y cotizaciones

✅ **Tip**: Mantenga actualizada la información de contacto de los proveedores para facilitar la comunicación en caso de emergencias.

---

## Dashboard y Alertas


### Dashboard Principal

El Dashboard muestra métricas en tiempo real del negocio.

#### Métricas Disponibles

1. **Propiedades**
   - Total de propiedades
   - Ocupadas vs Disponibles
   - Tasa de ocupación (%)

2. **Contratos**
   - Contratos activos
   - Contratos por vencer (próximos 30 días)
   - Contratos vencidos

3. **Recaudos**
   - Recaudos del mes
   - Recaudos pendientes
   - Recaudos pagados
   - Mora acumulada

4. **Liquidaciones**
   - Liquidaciones generadas
   - Liquidaciones aprobadas
   - Liquidaciones pagadas
   - Liquidaciones pendientes

5. **Incidentes**
   - Total de incidentes
   - Por estado (Reportado, Cotizado, etc.)
   - Por prioridad

#### Gráficos Estadísticos

- **Gráfico de Ocupación**: Propiedades ocupadas vs disponibles
- **Gráfico de Recaudos**: Evolución mensual de ingresos
- **Gráfico de Incidentes**: Distribución por estado

✅ **Tip**: El Dashboard se actualiza automáticamente al navegar a la página principal.

### Centro de Alertas

#### Acceder a Alertas

- Clic en el ícono de **campana** (🔔) en la barra superior
- El badge muestra el número de alertas no leídas

#### Tipos de Alertas

1. **Alertas de Mora**
   - Se generan cuando un pago tiene más de 5 días de retraso
   - Prioridad: Alta

2. **Alertas de Vencimiento de Contratos**
   - 90 días antes: Prioridad Baja
   - 60 días antes: Prioridad Media
   - 30 días antes: Prioridad Alta
   - Al vencimiento: Prioridad Crítica

3. **Alertas de Aniversario IPC**
   - Se generan 60 días antes del aniversario del contrato
   - Recordatorio para ajustar canon por IPC

#### Gestionar Alertas

1. **Ver Detalle**: Clic en la alerta para ver información completa
2. **Marcar como Leída**: Clic en el ícono de check
3. **Filtrar**: Use los filtros para ver solo ciertos tipos de alertas

✅ **Tip**: Revise las alertas diariamente para no perder eventos importantes.

---

## Generación de Documentos

El sistema genera documentos PDF automáticamente para ciertos procesos.

### Comprobantes de Recaudo

**Cuándo se genera**: Al registrar un nuevo recaudo

**Contenido**:
- Número de comprobante
- Fecha de pago
- Datos del arrendatario
- Datos del contrato
- Desglose de conceptos (Canon, Administración, Mora)
- Total pagado
- Método de pago
- Firma digital

**Ubicación**: `documentos_generados/recaudos/`

### Estados de Cuenta (Liquidaciones)

**Cuándo se genera**: Al aprobar una liquidación

**Contenido**:
- Período de liquidación
- Datos del propietario
- Datos de la propiedad
- Ingresos del mes
- Egresos del mes
- Neto a pagar
- Datos bancarios para consignación
- Firma digital

**Ubicación**: `documentos_generados/liquidaciones/`

### Imprimir Documentos

1. Desde la lista de recaudos o liquidaciones
2. Clic en el ícono de **"Imprimir"** (impresora)
3. El sistema genera el PDF y lo abre automáticamente
4. Use las opciones de su visor PDF para imprimir o guardar

✅ **Tip**: Los PDFs se guardan automáticamente en la carpeta `documentos_generados` para consulta posterior.

---

## Troubleshooting

### Problemas Comunes

#### No puedo iniciar sesión

**Síntoma**: Error "Usuario o contraseña incorrectos"

**Solución**:
1. Verifique que está usando las credenciales correctas
2. Credenciales por defecto: `admin` / `admin123`
3. Asegúrese de no tener CAPS LOCK activado
4. Si olvidó su contraseña, contacte al administrador del sistema

#### No aparecen las propiedades en el formulario de contrato

**Síntoma**: El dropdown de propiedades está vacío

**Solución**:
1. Verifique que existan propiedades registradas en el sistema
2. Para contratos de arrendamiento, la propiedad debe tener un mandato activo
3. La propiedad debe estar marcada como "Disponible"

#### Error al generar liquidación: "Ya existe una liquidación para este período"

**Síntoma**: No se puede crear la liquidación

**Solución**:
1. Solo puede haber una liquidación por contrato por mes
2. Verifique si ya existe una liquidación para ese período
3. Si necesita corregir, cancele la liquidación existente primero

#### No se calcula la mora automáticamente

**Síntoma**: El campo de mora aparece en $0

**Solución**:
1. Verifique que la fecha de pago sea posterior al día de pago del contrato
2. El sistema calcula mora solo si hay retraso
3. La tasa de mora es del 6% anual (configurable en parámetros del sistema)

#### El PDF no se genera o no se abre

**Síntoma**: Error al imprimir comprobante

**Solución**:
1. Verifique que la carpeta `documentos_generados` exista
2. Asegúrese de tener permisos de escritura en esa carpeta
3. Cierre otros PDFs que puedan estar bloqueando el archivo
4. Verifique que tenga un visor PDF instalado (Adobe Reader, etc.)

#### No puedo avanzar el estado de un incidente

**Síntoma**: El botón "Avanzar Estado" no funciona

**Solución**:
1. Verifique que el incidente cumpla las condiciones:
   - **Cotizado**: Debe tener al menos una cotización registrada
   - **Aprobado**: Debe tener una cotización aprobada
   - **En Reparación**: Debe estar en estado Aprobado
   - **Finalizado**: Debe estar en estado En Reparación
2. No se puede saltar estados

### Preguntas Frecuentes

**¿Puedo eliminar una persona del sistema?**

No se eliminan registros, solo se desactivan. Esto preserva la integridad histórica de contratos y transacciones.

**¿Cuántos roles puede tener una persona?**

Una persona puede tener todos los roles que necesite simultáneamente (Propietario, Arrendatario, Asesor, Codeudor, Proveedor).

**¿Puedo tener dos contratos de arrendamiento en la misma propiedad?**

No. Solo puede haber un contrato de arrendamiento activo por propiedad. Debe finalizar el contrato actual antes de crear uno nuevo.

**¿Cómo se calcula la comisión de administración?**

La comisión se define en el contrato de mandato como un porcentaje del canon de arrendamiento. Se aplica en cada liquidación mensual.

**¿Qué pasa si rechazo una cotización?**

El incidente regresa al estado "Reportado" y puede solicitar una nueva cotización al mismo proveedor o a otro diferente. El historial de cotizaciones rechazadas se conserva.

**¿Puedo modificar una liquidación ya aprobada?**

No. Una vez aprobada, la liquidación no se puede modificar. Si hay un error, debe cancelarla (solo Gerente) y generar una nueva.

**¿Cómo se registra el pago de una liquidación?**

Desde la lista de liquidaciones, use el botón "Marcar como Pagada" e ingrese el número de comprobante bancario.

**¿El sistema calcula el IPC automáticamente?**

El sistema genera alertas 60 días antes del aniversario del contrato para recordar el ajuste IPC, pero el nuevo valor debe ingresarse manualmente al renovar o modificar el contrato.

### Contacto de Soporte

Para asistencia técnica adicional:

- **Email**: soporte@inmobiliaravelar.com
- **Teléfono**: +57 (XXX) XXX-XXXX
- **Horario**: Lunes a Viernes, 8:00 AM - 6:00 PM

---

**Fin del Manual de Usuario**

*Última actualización: Diciembre 2025*  
*Versión del Sistema: 1.0*

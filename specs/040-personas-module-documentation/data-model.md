# Data Model: Manual de Usuario - Módulo Personas

**Date**: 2026-07-08

## Entities Documented

### 1. Persona

Entidad central del módulo. Representa una persona física o jurídica en el sistema.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| ID | Integer | Sí | Identificador único autoincremental |
| Nombre | String | Sí | Nombre completo de la persona |
| Tipo Documento | String | Sí | CC, TI, NIT, etc. |
| Número Documento | String | Sí | Número único de identificación |
| Teléfono | String | No | Número de contacto |
| Correo | String | Sí | Dirección de email válida |
| Dirección | String | No | Dirección de residencia |
| Fecha Creación | DateTime | Automático | Timestamp de registro |
| Estado | Enum | Automático | ACTIVO / INACTIVO |

**Relaciones**:
- Persona → Roles (muchos a muchos)
- Persona → Contratos (uno a muchos, via Arrendatario)
- Persona → Propiedades (uno a muchos, via Propietario)
- Persona → Auditoría (uno a muchos)

### 2. Rol

Clasificación de la persona dentro del ecosistema inmobiliario.

| Valor | Color UI | Descripción |
|-------|----------|-------------|
| Propietario | Azul | Posee inmuebles |
| Arrendatario | Verde | Alquila inmuebles |
| Asesor | Violeta | Asesor comercial |
| Codeudor | Naranja | Garante de contratos |
| Proveedor | Cyan | Proveedor de servicios |

**Reglas**:
- Una persona puede tener uno o múltiples roles
- Los roles se asignan durante la creación o edición
- El color del avatar depende del primer rol asignado

### 3. KPI (Indicadores Clave)

Conteos por rol mostrados en el header del módulo.

| KPI | Fórmula | Actualización |
|-----|---------|---------------|
| Propietarios Activos | COUNT(personas WHERE rol=Propietario AND estado=ACTIVO) | Tiempo real |
| Propietarios Inactivos | COUNT(personas WHERE rol=Propietario AND estado=INACTIVO) | Tiempo real |
| Arrendatarios Activos | COUNT(personas WHERE rol=Arrendatario AND estado=ACTIVO) | Tiempo real |
| Arrendatarios Inactivos | COUNT(personas WHERE rol=Arrendatario AND estado=INACTIVO) | Tiempo real |
| Asesores Activos | COUNT(personas WHERE rol=Asesor AND estado=ACTIVO) | Tiempo real |
| Asesores Inactivos | COUNT(personas WHERE rol=Asesor AND estado=INACTIVO) | Tiempo real |
| Codeudores Activos | COUNT(personas WHERE rol=Codeudor AND estado=ACTIVO) | Tiempo real |
| Codeudores Inactivos | COUNT(personas WHERE rol=Codeudor AND estado=INACTIVO) | Tiempo real |
| Proveedores Activos | COUNT(personas WHERE rol=Proveedor AND estado=ACTIVO) | Tiempo real |
| Proveedores Inactivos | COUNT(personas WHERE rol=Proveedor AND estado=INACTIVO) | Tiempo real |

### 4. Auditoría

Registro de operaciones realizadas sobre personas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID | Integer | Identificador del registro |
| Persona ID | Integer | FK a Persona |
| Acción | String | CREAR, EDITAR, CAMBIAR_ESTADO |
| Usuario | String | Quién realizó la acción |
| Fecha | DateTime | Cuándo se realizó |
| Detalle | JSON | Cambios realizados |

## State Transitions

### Estado de Persona

```
[CREADO] → ACTIVO → INACTIVO → ACTIVO (reactivación)
```

**Reglas de Transición**:
- Solo se puede desactivar personas en estado ACTIVO
- Solo se puede reactivar personas en estado INACTIVO
- El soft delete preserva integridad referencial

### Wizard de Creación

```
[Paso 1: Datos Básicos] → [Paso 2: Roles] → [Paso 3: Info Adicional] → [Guardado]
```

**Validación por Paso**:
- Paso 1: Nombre, documento, correo (obligatorios)
- Paso 2: Al menos un rol seleccionado
- Paso 3: Campos adicionales según roles

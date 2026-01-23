# Arquitectura del Sistema - InmoVelar

**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Tipo:** Documentación Técnica

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Diagrama C4 - Nivel de Contexto](#diagrama-c4---nivel-de-contexto)
3. [Diagrama C4 - Nivel de Contenedores](#diagrama-c4---nivel-de-contenedores)
4. [Diagrama C4 - Nivel de Componentes](#diagrama-c4---nivel-de-componentes)
5. [Diagrama de Flujo de Datos](#diagrama-de-flujo-de-datos)
6. [Diagramas de Estados](#diagramas-de-estados)
7. [Diagrama ER Simplificado](#diagrama-er-simplificado)

---

## Introducción

Este documento presenta la arquitectura del Sistema de Gestión Inmobiliaria InmoVelar mediante diagramas visuales utilizando Mermaid. La arquitectura sigue los principios de **Clean Architecture** con clara separación de responsabilidades en capas.

### Principios Arquitectónicos

- **Clean Architecture**: Separación en capas con dependencias unidireccionales
- **SOLID**: Aplicación de principios de diseño orientado a objetos
- **Data-Centric**: La base de datos es la fuente única de verdad
- **Schema-Driven**: Los cambios comienzan en el esquema de base de datos

---

## Diagrama C4 - Nivel de Contexto

El diagrama de contexto muestra el sistema InmoVelar y sus interacciones con actores externos.

```mermaid
C4Context
    title Diagrama de Contexto - Sistema InmoVelar

    Person(admin, "Administrador", "Gestiona el sistema completo")
    Person(contador, "Contador", "Gestiona finanzas y liquidaciones")
    Person(asesor, "Asesor Inmobiliario", "Gestiona propiedades y contratos")
    
    System(inmovelar, "InmoVelar", "Sistema de gestión inmobiliaria integral")
    
    System_Ext(email, "Sistema de Email", "Envío de notificaciones")
    System_Ext(banco, "Sistema Bancario", "Validación de transacciones")
    
    Rel(admin, inmovelar, "Administra usuarios y configuración")
    Rel(contador, inmovelar, "Gestiona recaudos y liquidaciones")
    Rel(asesor, inmovelar, "Gestiona propiedades y contratos")
    
    Rel(inmovelar, email, "Envía notificaciones")
    Rel(inmovelar, banco, "Consulta transacciones")
```

---

## Diagrama C4 - Nivel de Contenedores

El diagrama de contenedores muestra los principales componentes tecnológicos del sistema.

```mermaid
C4Container
    title Diagrama de Contenedores - InmoVelar

    Person(usuario, "Usuario del Sistema", "Administrador, Contador, Asesor")

    Container_Boundary(desktop, "Aplicación Desktop") {
        Container(app, "Aplicación Flet", "Python + Flet", "Interfaz de usuario desktop")
    }

    Container_Boundary(data, "Capa de Datos") {
        ContainerDb(db, "Base de Datos", "SQLite", "Almacena toda la información del sistema")
    }

    Container_Boundary(files, "Sistema de Archivos") {
        Container(pdfs, "Documentos PDF", "FPDF", "Comprobantes y estados de cuenta")
    }

    Rel(usuario, app, "Usa", "Desktop UI")
    Rel(app, db, "Lee/Escribe", "SQL")
    Rel(app, pdfs, "Genera", "PDF")
```

---

## Diagrama C4 - Nivel de Componentes

El diagrama de componentes muestra la arquitectura interna de la aplicación siguiendo Clean Architecture.

```mermaid
graph TB
    subgraph "Capa de Presentación"
        Views["Views<br/>(Vistas Flet)"]
        Components["Components<br/>(Componentes UI)"]
        Theme["Theme<br/>(Estilos y Colores)"]
        Router["Router<br/>(Navegación)"]
    end

    subgraph "Capa de Aplicación"
        Services["Services<br/>(Servicios de Aplicación)"]
        DTOs["DTOs<br/>(Data Transfer Objects)"]
        Mappers["Mappers<br/>(Entity ↔ DTO)"]
    end

    subgraph "Capa de Dominio"
        Entities["Entities<br/>(Entidades de Negocio)"]
        ValueObjects["Value Objects<br/>(Dinero, Email, etc.)"]
        Interfaces["Interfaces<br/>(Protocols)"]
        Strategies["Strategies<br/>(Cálculos)"]
    end

    subgraph "Capa de Infraestructura"
        Repositories["Repositories<br/>(Implementaciones SQLite)"]
        Database["Database Manager<br/>(Conexión BD)"]
        Config["Config<br/>(Configuración)"]
        PDFGen["PDF Generator<br/>(Generación Documentos)"]
    end

    Views --> Router
    Views --> Components
    Views --> Theme
    Views --> Services
    
    Services --> DTOs
    Services --> Mappers
    Services --> Interfaces
    
    Mappers --> Entities
    Mappers --> DTOs
    
    Repositories --> Interfaces
    Repositories --> Database
    Repositories --> Entities
    
    Entities --> ValueObjects
    Services --> Strategies
    
    Services --> PDFGen

    style Views fill:#e1f5ff
    style Services fill:#fff4e1
    style Entities fill:#e8f5e9
    style Repositories fill:#fce4ec
```

---

## Diagrama de Flujo de Datos

Muestra el flujo completo de datos desde la UI hasta la base de datos.

```mermaid
sequenceDiagram
    participant UI as Vista (UI)
    participant Router as Router
    participant Service as Servicio
    participant Mapper as Mapper
    participant Entity as Entidad
    participant Repo as Repositorio
    participant DB as Base de Datos

    UI->>Router: Acción del usuario
    Router->>Service: Llamada a método
    Service->>Mapper: Convertir DTO a Entity
    Mapper->>Entity: Crear/Actualizar entidad
    Service->>Repo: Guardar entidad
    Repo->>DB: Ejecutar SQL INSERT/UPDATE
    DB-->>Repo: Confirmación
    Repo-->>Service: Entidad guardada
    Service->>Mapper: Convertir Entity a DTO
    Mapper-->>Service: DTO
    Service-->>UI: Resultado (DTO)
    UI->>UI: Actualizar vista
```

### Flujo de Lectura

```mermaid
sequenceDiagram
    participant UI as Vista (UI)
    participant Service as Servicio
    participant Repo as Repositorio
    participant DB as Base de Datos
    participant Mapper as Mapper

    UI->>Service: Solicitar datos (filtros)
    Service->>Repo: Consultar repositorio
    Repo->>DB: Ejecutar SELECT
    DB-->>Repo: Filas de datos
    Repo->>Repo: Mapear SQL → Entity
    Repo-->>Service: Lista de entidades
    Service->>Mapper: Convertir Entity → DTO
    Mapper-->>Service: Lista de DTOs
    Service-->>UI: Datos para mostrar
    UI->>UI: Renderizar componentes
```

---

## Diagramas de Estados

### Estados de Incidente

```mermaid
stateDiagram-v2
    [*] --> Reportado: Crear incidente
    
    Reportado --> Cotizado: Registrar cotización
    Reportado --> Cancelado: Cancelar
    
    Cotizado --> Reportado: Rechazar cotización
    Cotizado --> Aprobado: Aprobar cotización
    Cotizado --> Cancelado: Cancelar
    
    Aprobado --> EnReparacion: Iniciar trabajo
    Aprobado --> Cancelado: Cancelar
    
    EnReparacion --> Finalizado: Completar trabajo
    EnReparacion --> Cancelado: Cancelar
    
    Finalizado --> [*]
    Cancelado --> [*]

    note right of Reportado
        Incidente recién creado
        Esperando cotización
    end note

    note right of Cotizado
        Tiene cotización registrada
        Pendiente de aprobación
    end note

    note right of Aprobado
        Cotización aprobada
        Listo para iniciar
    end note

    note right of EnReparacion
        Trabajo en progreso
        Proveedor ejecutando
    end note

    note right of Finalizado
        Trabajo completado
        Costo registrado
    end note
```

### Estados de Contrato

```mermaid
stateDiagram-v2
    [*] --> Activo: Crear contrato
    
    Activo --> PorVencer: 90 días antes
    
    PorVencer --> Vencido: Fecha fin alcanzada
    PorVencer --> Renovado: Renovar contrato
    
    Vencido --> Renovado: Renovar contrato
    Vencido --> Terminado: Finalizar sin renovar
    
    Renovado --> [*]
    Terminado --> [*]

    note right of Activo
        Contrato vigente
        Más de 90 días para vencer
    end note

    note right of PorVencer
        Alerta de vencimiento
        Menos de 90 días
    end note

    note right of Vencido
        Fecha fin superada
        Requiere acción
    end note

    note right of Renovado
        Nuevo contrato creado
        Contrato anterior cerrado
    end note
```

### Estados de Liquidación

```mermaid
stateDiagram-v2
    [*] --> Generada: Crear liquidación
    
    Generada --> Aprobada: Aprobar (Gerente)
    Generada --> Cancelada: Cancelar
    
    Aprobada --> Pagada: Registrar pago
    Aprobada --> Cancelada: Cancelar (Gerente)
    
    Pagada --> [*]
    Cancelada --> [*]

    note right of Generada
        Liquidación creada
        Pendiente de revisión
    end note

    note right of Aprobada
        Revisada y aprobada
        Lista para pago
    end note

    note right of Pagada
        Pago realizado
        Comprobante registrado
    end note

    note right of Cancelada
        Liquidación anulada
        No se procesará
    end note
```

### Estados de Recaudo

```mermaid
stateDiagram-v2
    [*] --> Pendiente: Registrar pago
    
    Pendiente --> Aplicado: Aprobar pago
    Pendiente --> Reversado: Reversar (Gerente)
    
    Aplicado --> [*]
    Reversado --> [*]

    note right of Pendiente
        Pago registrado
        Pendiente de aplicación
    end note

    note right of Aplicado
        Pago confirmado
        Aplicado al contrato
    end note

    note right of Reversado
        Pago anulado
        Requiere autorización
    end note
```

---

## Diagrama ER Simplificado

Muestra las entidades principales y sus relaciones.

```mermaid
erDiagram
    PERSONA ||--o{ PROPIETARIO : "es"
    PERSONA ||--o{ ARRENDATARIO : "es"
    PERSONA ||--o{ ASESOR : "es"
    PERSONA ||--o{ CODEUDOR : "es"
    PERSONA ||--o{ PROVEEDOR : "es"
    
    PROPIEDAD ||--o| CONTRATO_MANDATO : "tiene"
    PROPIEDAD ||--o| CONTRATO_ARRENDAMIENTO : "tiene"
    PROPIEDAD ||--o{ INCIDENTE : "tiene"
    
    PROPIETARIO ||--o{ CONTRATO_MANDATO : "firma"
    ARRENDATARIO ||--o{ CONTRATO_ARRENDAMIENTO : "firma"
    CODEUDOR ||--o{ CONTRATO_ARRENDAMIENTO : "garantiza"
    ASESOR ||--o{ CONTRATO_MANDATO : "gestiona"
    
    CONTRATO_ARRENDAMIENTO ||--o{ RECAUDO : "genera"
    CONTRATO_ARRENDAMIENTO ||--o{ LIQUIDACION : "genera"
    
    INCIDENTE ||--o{ COTIZACION : "tiene"
    PROVEEDOR ||--o{ COTIZACION : "emite"
    
    LIQUIDACION ||--o{ INCIDENTE : "incluye costos"

    PERSONA {
        int ID_PERSONA PK
        string TIPO_PERSONA
        string NOMBRES
        string APELLIDOS
        string TIPO_DOCUMENTO
        string NUMERO_DOCUMENTO
        string CELULAR_PRINCIPAL
        string CORREO_PRINCIPAL
        int ID_MUNICIPIO FK
        string DIRECCION
        int ESTADO_REGISTRO
    }

    PROPIEDAD {
        int ID_PROPIEDAD PK
        string MATRICULA_INMOBILIARIA
        string TIPO_INMUEBLE
        int ID_MUNICIPIO FK
        string DIRECCION
        decimal AREA_M2
        int NUM_HABITACIONES
        int NUM_BANOS
        decimal VALOR_ADMINISTRACION
        decimal CANON_ARRENDAMIENTO
        bool DISPONIBLE_ARRIENDO
    }

    CONTRATO_MANDATO {
        int ID_CONTRATO_MANDATO PK
        int ID_PROPIEDAD FK
        int ID_PROPIETARIO FK
        int ID_ASESOR FK
        date FECHA_INICIO
        date FECHA_FIN
        decimal PORCENTAJE_COMISION
        string ESTADO
    }

    CONTRATO_ARRENDAMIENTO {
        int ID_CONTRATO_ARRENDAMIENTO PK
        int ID_PROPIEDAD FK
        int ID_ARRENDATARIO FK
        int ID_CODEUDOR FK
        date FECHA_INICIO
        date FECHA_FIN
        decimal CANON_MENSUAL
        decimal VALOR_ADMINISTRACION
        int DIA_PAGO
        string ESTADO
    }

    RECAUDO {
        int ID_RECAUDO PK
        int ID_CONTRATO_ARRENDAMIENTO FK
        date FECHA_PAGO
        decimal VALOR_TOTAL
        string METODO_PAGO
        string ESTADO
    }

    LIQUIDACION {
        int ID_LIQUIDACION PK
        int ID_CONTRATO_ARRENDAMIENTO FK
        string PERIODO
        decimal INGRESOS_TOTALES
        decimal EGRESOS_TOTALES
        decimal NETO_PAGAR
        string ESTADO
    }

    INCIDENTE {
        int ID_INCIDENTE PK
        int ID_PROPIEDAD FK
        string TITULO
        string DESCRIPCION
        string PRIORIDAD
        string ESTADO
        string RESPONSABLE_COSTO
        int ID_PROVEEDOR_ASIGNADO FK
    }

    COTIZACION {
        int ID_COTIZACION PK
        int ID_INCIDENTE FK
        int ID_PROVEEDOR FK
        decimal VALOR_COTIZADO
        string DESCRIPCION_TRABAJO
        bool APROBADA
        string MOTIVO_RECHAZO
    }
```

### Relaciones Clave

1. **Party Model**: Una `PERSONA` puede tener múltiples roles simultáneamente
2. **Propiedad-Contratos**: Una propiedad puede tener un mandato y un arrendamiento activos
3. **Contratos-Finanzas**: Los contratos de arrendamiento generan recaudos y liquidaciones
4. **Incidentes-Proveedores**: Los incidentes tienen cotizaciones de proveedores
5. **Liquidaciones-Incidentes**: Los costos de incidentes se cargan a las liquidaciones

---

## Arquitectura de Capas

### Dependencias entre Capas

```mermaid
graph LR
    subgraph "Clean Architecture - Dependencias"
        Presentacion["Presentación<br/>(UI)"]
        Aplicacion["Aplicación<br/>(Services)"]
        Dominio["Dominio<br/>(Entities)"]
        Infraestructura["Infraestructura<br/>(Repositories)"]
    end

    Presentacion --> Aplicacion
    Aplicacion --> Dominio
    Infraestructura --> Dominio
    Presentacion -.-> Infraestructura

    style Dominio fill:#4caf50,color:#fff
    style Aplicacion fill:#ff9800,color:#fff
    style Presentacion fill:#2196f3,color:#fff
    style Infraestructura fill:#e91e63,color:#fff
```

### Reglas de Dependencia

> [!IMPORTANT]
> **Regla de Dependencia**: Las capas externas dependen de las internas, nunca al revés.

- ✅ **Presentación** puede depender de **Aplicación** y **Dominio**
- ✅ **Aplicación** puede depender de **Dominio**
- ✅ **Infraestructura** puede depender de **Dominio**
- ❌ **Dominio** NO puede depender de ninguna otra capa
- ❌ **Aplicación** NO puede depender de **Infraestructura** directamente

---

## Patrones Arquitectónicos Aplicados

### 1. Repository Pattern

```mermaid
classDiagram
    class IRepositorio~T~ {
        <<interface>>
        +crear(entidad: T) T
        +obtener_por_id(id: int) Optional~T~
        +actualizar(entidad: T) T
        +eliminar(id: int) bool
        +listar_todos() List~T~
    }

    class RepositorioPersonaSQLite {
        -db: DatabaseManager
        +crear(persona: Persona) Persona
        +obtener_por_id(id: int) Optional~Persona~
        +actualizar(persona: Persona) Persona
        +eliminar(id: int) bool
        +listar_todos() List~Persona~
        +buscar_por_documento(doc: str) Optional~Persona~
    }

    class Persona {
        +id_persona: int
        +nombres: str
        +apellidos: str
        +documento: DocumentoIdentidad
    }

    IRepositorio~T~ <|.. RepositorioPersonaSQLite
    RepositorioPersonaSQLite ..> Persona
```

### 2. Service Layer Pattern

```mermaid
classDiagram
    class ServicioPersonas {
        -repo_persona: IRepositorioPersona
        -repo_propietario: IRepositorioPropietario
        -repo_arrendatario: IRepositorioArrendatario
        +crear_persona_con_roles(datos, roles) PersonaConRoles
        +listar_personas(filtros) List~PersonaConRoles~
        +asignar_rol(id, rol, datos) bool
        +desactivar_persona(id) bool
    }

    class PersonaConRoles {
        +persona: Persona
        +datos_roles: Dict
        +roles() List~str~
        +nombre_completo() str
    }

    ServicioPersonas ..> PersonaConRoles
```

### 3. Strategy Pattern

```mermaid
classDiagram
    class EstrategiaComision {
        <<interface>>
        +calcular(monto: Decimal) Decimal
    }

    class EstrategiaComisionFija {
        -porcentaje: Decimal
        +calcular(monto: Decimal) Decimal
    }

    class EstrategiaComisionEscalonada {
        -rangos: List~Tuple~
        +calcular(monto: Decimal) Decimal
    }

    EstrategiaComision <|.. EstrategiaComisionFija
    EstrategiaComision <|.. EstrategiaComisionEscalonada
```

---

## Conclusiones

La arquitectura de InmoVelar está diseñada para:

1. **Mantenibilidad**: Separación clara de responsabilidades
2. **Testabilidad**: Cada capa puede probarse independientemente
3. **Escalabilidad**: Fácil agregar nuevas funcionalidades
4. **Integridad**: La base de datos es la fuente única de verdad
5. **Flexibilidad**: Uso de interfaces y estrategias para extensibilidad

> [!NOTE]
> Esta arquitectura sigue los principios SOLID y Clean Architecture, garantizando un código limpio, mantenible y profesional.

---

**Fin de la Documentación de Arquitectura**

*Última actualización: Diciembre 2025*  
*Versión del Sistema: 1.0*

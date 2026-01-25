# Módulo de Reportes - Diseño de Nivel Experto Elite

## Visión General
El módulo de reportes centralizará la generación de archivos CSV delimitados por comas para todos los módulos del sistema inmobiliario. Ofrecerá filtros avanzados basados en la información específica de cada módulo, permitiendo reportes personalizados y de alta precisión.

## Arquitectura del Módulo

### Estructura de Componentes
```
src/
├── presentacion_reflex/
│   ├── pages/
│   │   └── reportes.py
│   ├── state/
│   │   └── reportes_state.py
│   └── components/
│       └── reportes/
│           ├── module_selector.py
│           ├── advanced_filters.py
│           ├── preview_table.py
│           └── export_controls.py
├── aplicacion/
│   └── servicios/
│       └── servicio_reportes.py
└── dominio/
    └── interfaces/
        └── repositorio_reportes.py
```

## Módulos Soportados y Filtros Avanzados

### 1. Personas
**Campos principales:**
- ID, Nombre completo, Documento, Tipo documento, Número documento
- Contacto, Teléfono, Correo, Dirección, Roles, Estado, Fecha creación

**Filtros avanzados:**
- Búsqueda por texto (nombre, documento, correo)
- Filtro por rol (Propietario, Arrendatario, Codeudor, Asesor, Proveedor)
- Rango de fechas (creación)
- Estado (Activo/Inactivo)
- Tipo de documento
- Roles múltiples (combinaciones)

### 2. Propiedades
**Campos principales:**
- ID propiedad, Matrícula inmobiliaria, Dirección, Tipo propiedad
- Municipio, Disponibilidad, Valor canon, Área m², Habitaciones, Baños
- Parqueadero, Valor venta, Comisión venta, Códigos servicios

**Filtros avanzados:**
- Búsqueda por texto (dirección, matrícula)
- Tipo de propiedad
- Disponibilidad (Disponible/Ocupada)
- Municipio
- Rango de valor canon
- Rango de área
- Número de habitaciones/baños
- Solo propiedades activas

### 3. Contratos
**Campos principales:**
- ID contrato, Tipo (Mandato/Arrendamiento), Estado
- Propiedad, Arrendatario/Propietario, Asesor
- Fechas (inicio, fin, firma), Valor canon, Depósito
- Comisión, Renovaciones

**Filtros avanzados:**
- Tipo de contrato (Mandato/Arrendamiento/Todos)
- Estado (Activo/Cancelado)
- Propiedad específica
- Persona específica (arrendatario/propietario)
- Asesor específico
- Rango de fechas (inicio/fin)
- Rango de valor canon
- Búsqueda por texto

### 4. Proveedores
**Campos principales:**
- ID proveedor, ID persona, Nombre, Contacto
- Especialidad, Calificación, Observaciones

**Filtros avanzados:**
- Búsqueda por texto (nombre, especialidad)
- Especialidad específica
- Rango de calificación
- Estado activo

### 5. Liquidaciones
**Campos principales:**
- ID liquidación, Período, Estado, Propietario, Propiedad
- Ingresos totales, Egresos totales, Total neto
- Fecha creación, Fecha pago

**Filtros avanzados:**
- Período específico (YYYY-MM)
- Estado (En Proceso/Aprobada/Pagada/Cancelada)
- Propiedad específica
- Propietario específico
- Rango de fechas
- Rango de totales
- Vista individual vs consolidada

### 6. Liquidación Asesores
**Campos principales:**
- ID liquidación, Asesor, Período, Estado
- Comisiones ganadas, Descuentos, Total a pagar
- Fecha creación, Fecha pago

**Filtros avanzados:**
- Período específico
- Asesor específico
- Estado
- Rango de comisiones
- Rango de fechas

### 7. Recaudos
**Campos principales:**
- ID recaudo, Contrato, Período, Valor
- Fecha vencimiento, Fecha pago, Estado
- Método pago, Referencia

**Filtros avanzados:**
- Período
- Estado (Pendiente/Pagado/Vencido)
- Contrato específico
- Rango de valores
- Rango de fechas vencimiento/pago
- Método de pago

### 8. Desocupaciones
**Campos principales:**
- ID desocupación, Propiedad, Arrendatario
- Fecha desocupación, Estado checklist
- Motivo, Observaciones

**Filtros avanzados:**
- Propiedad específica
- Arrendatario específico
- Estado checklist
- Rango de fechas
- Motivo

### 9. Incidentes
**Campos principales:**
- ID incidente, Propiedad, Reportado por
- Tipo incidente, Severidad, Estado
- Fecha reporte, Fecha resolución
- Descripción, Solución

**Filtros avanzados:**
- Propiedad específica
- Tipo de incidente
- Severidad
- Estado
- Rango de fechas reporte/resolución
- Reportado por

### 10. Seguros
**Campos principales:**
- ID seguro, Propiedad, Aseguradora
- Tipo cobertura, Valor asegurado, Prima
- Fecha inicio, Fecha fin, Estado

**Filtros avanzados:**
- Propiedad específica
- Aseguradora
- Tipo cobertura
- Estado
- Rango de fechas
- Rango de valores

### 11. Recibos Públicos
**Campos principales:**
- ID recibo, Servicio, Valor, Período
- Fecha emisión, Fecha vencimiento, Estado pago
- Referencia pago

**Filtros avanzados:**
- Servicio específico
- Período
- Estado pago
- Rango de valores
- Rango de fechas

### 12. IPC / Incrementos
**Campos principales:**
- ID IPC, Año, Mes, Valor IPC
- Fecha aplicación, Contratos afectados
- Porcentaje incremento

**Filtros avanzados:**
- Año/Mes específico
- Rango de valores IPC
- Rango de porcentajes
- Fecha aplicación

### 13. Usuarios
**Campos principales:**
- ID usuario, Nombre, Email, Rol
- Estado, Fecha creación, Último acceso
- Permisos

**Filtros avanzados:**
- Rol específico
- Estado
- Rango de fechas creación/acceso
- Búsqueda por email/nombre

## Funcionalidades Elite

### 1. Interfaz de Usuario
- Selector de módulo con íconos intuitivos
- Filtros dinámicos que cambian según el módulo seleccionado
- Vista previa de datos antes de exportar
- Contador de registros que coinciden con filtros
- Historial de reportes generados

### 2. Sistema de Filtros Avanzados
- Filtros combinables (AND/OR lógica)
- Rango de fechas con calendario
- Búsqueda inteligente (autocomplete)
- Filtros guardados como plantillas
- Validación en tiempo real de filtros

### 3. Generación de CSV
- Codificación UTF-8 con BOM para Excel
- Nombres de columnas descriptivos
- Formato consistente de fechas (YYYY-MM-DD)
- Valores numéricos sin formato
- Manejo de campos nulos

### 4. Características de Rendimiento
- Paginación en preview (máx 1000 registros)
- Generación asíncrona para grandes datasets
- Compresión ZIP para archivos grandes
- Límites de seguridad (máx 50,000 registros por export)

### 5. Seguridad y Auditoría
- Logs de todas las exportaciones
- Validación de permisos por módulo
- Enmascaramiento de datos sensibles si es necesario
- Rate limiting para prevenir abuso

## Flujo de Usuario

1. **Selección de Módulo**: Usuario elige el módulo deseado
2. **Configuración de Filtros**: Aparecen filtros específicos del módulo
3. **Aplicación de Filtros**: Usuario configura filtros avanzados
4. **Vista Previa**: Se muestra tabla con resultados (primeros 100 registros)
5. **Confirmación**: Usuario confirma generación del reporte completo
6. **Exportación**: Se genera y descarga el archivo CSV

## Implementación Técnica

### Estado (reportes_state.py)
```python
class ReportesState(rx.State):
    # Selección de módulo
    selected_module: str = ""
    
    # Filtros dinámicos
    filters: Dict[str, Any] = {}
    
    # Vista previa
    preview_data: List[Dict] = []
    total_records: int = 0
    
    # Configuración export
    export_filename: str = ""
    is_exporting: bool = False
```

### Servicio (servicio_reportes.py)
- Método `generar_reporte_csv(module, filters)` que delega a servicios específicos
- Validación de filtros
- Generación de CSV con StringIO
- Integración con repositorios de cada módulo

### Componentes UI
- `ModuleSelector`: Grid de tarjetas para elegir módulo
- `AdvancedFilters`: Formulario dinámico de filtros
- `PreviewTable`: Tabla paginada con resultados
- `ExportControls`: Botones de export y configuración

## Próximos Pasos
1. Crear estructura de archivos
2. Implementar estado base
3. Desarrollar componentes UI
4. Integrar con servicios existentes
5. Testing exhaustivo con datos reales
6. Optimización de rendimiento
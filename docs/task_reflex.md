# 📋 Plan Maestro de Migración: Flet → Reflex

**Fecha de Inicio:** 2026-01-07  
**Proyecto:** Sistema de Gestión Inmobiliaria Velar  
**Objetivo:** Migrar la capa de presentación de Flet a Reflex manteniendo 100% de funcionalidad

---

## 📊 Resumen Ejecutivo

### Estado General: **[-]** EN PROGRESO - Fase 9 Completada

- **Total de Componentes a Migrar:** ~90 archivos Python (actualizado)
  - 39 Vistas (views)
  - 30+ Componentes implementados
  - 8 Estados (state management)
  - 9 Utilidades y arquitectura (router, theme, app)
- **Servicios de Negocio:** 19 servicios (✅ Todos Refactorizados para Agnosticismo de BD)
- **Progreso General:** 56% (~50/90 archivos migrados)

### Inventario de Componentes

#### 🎯 Vistas (39 archivos)
- [ ] `alerts_view.py` - Drawer de alertas
- [x] `configuracion_view.py` - Configuración del sistema
- [x] `contrato_arrendamiento_form_view.py` - ✅ Formulario de arrendamiento (100% funcional)
- [x] `contrato_mandato_form_view.py` - ✅ Formulario de mandato (100% funcional)
- [x] `contratos_list_view.py` - ✅ Listado de contratos (100% funcional)
- [x] `dashboard_view.py` - **CRÍTICO** - Dashboard principal
- [x] `desocupaciones.py` - ✅ Listado de desocupaciones (100% funcional)
- [ ] `incidente_detail_view.py` - Detalle de incidente
- [ ] `incidente_form_view.py` - Formulario de incidente
- [x] `incidentes.py` - ✅ Gestión de Incidentes (Kanban + Lista)
- [ ] `incidentes_list_view.py` - Listado de incidentes
- [ ] `incrementos_view.py` - Gestión de IPC/incrementos
- [ ] `liquidacion_asesor_detail_view.py` - Detalle liquidación asesor
- [ ] `liquidacion_asesor_form_view.py` - Formulario liquidación asesor
- [x] `liquidacion_form_view.py` - ✅ Formulario liquidación propietarios (100% funcional)
- [ ] `liquidaciones_asesores_list_view.py` - Listado liquidaciones asesores
- [x] `liquidaciones_list_view.py` - ✅ Listado liquidaciones propietarios (100% funcional)
- [ ] `loading_view.py` - Vista de carga
- [x] `login_view.py` - **CRÍTICO** - Autenticación ✅
- [ ] `pagos_asesores_list_view.py` - Pagos a asesores
- [ ] `persona_form_view.py` - Formulario de personas
- [x] `personas_list_view.py` - ✅ Listado de personas (100% funcional)
- [ ] `poliza_form_view.py` - Formulario de pólizas
- [ ] `propiedad_form_view.py` - Formulario de propiedades
- [x] `propiedades_list_view.py` - ✅ Listado de propiedades (100% funcional)
- [x] `proveedor_form_view.py` - ✅ Formulario de proveedores
- [x] `proveedores_list_view.py` - ✅ Listado de proveedores
- [ ] `recaudo_form_view.py` - Formulario de recaudos
- [x] `recaudos_list_view.py` - ✅ Gestión de Recaudos (100% funcional)
- [x] `recibo_publico_form_view.py` - ✅ Formulario recibos públicos
- [x] `recibos_publicos_list_view.py` - ✅ Listado recibos públicos
- [ ] `saldo_favor_form_view.py` - Formulario saldos a favor
- [ ] `saldos_favor_list_view.py` - Listado saldos a favor
- [ ] `seguro_form_view.py` - Formulario de seguros
- [x] `seguros_list_view.py` - ✅ Gestión de Seguros y Pólizas (100% funcional)
- [x] `usuario_form_view.py` - ✅ Formulario de usuarios
- [ ] `__init__.py` - Exports de vistas

#### 🧩 Componentes (10 archivos principales)
- [x] `dashboard_filters.py` - Filtros del dashboard
- [x] `document_manager.py` - Gestor de documentos
- [x] `incident_card.py` - Card de incidente
- [x] `kanban_board.py` - Tablero Kanban
- [ ] `navbar.py` - **CRÍTICO** - Barra de navegación
- [ ] `pagination_manager.py` - Paginación
- [ ] `recibo_card.py` - Card de recibo
- [ ] `shell.py` - **CRÍTICO** - Layout shell
- [x] `sidebar.py` - **CRÍTICO** - Barra lateral
- [x] `__init__.py` - Exports de componentes
- [ ] `widgets/__init__.py` - Exports de widgets

#### 🎨 Widgets (6 archivos)
- [x] `chart_widget.py` - Gráficos (placeholders por ahora)
- [x] `kpi_card.py` - Tarjeta KPI
- [ ] `persona_datatable.py` - Tabla de personas
- [x] `property_card.py` - Tarjeta de propiedad
- [ ] `property_datatable.py` - Tabla de propiedades
- [ ] `role_badge.py` - Badge de roles

#### ⚙️ Arquitectura y Utilidades (9 archivos)
- [ ] `app.py` - Aplicación principal
- [ ] `router.py` - **CRÍTICO** - Sistema de rutas
- [ ] `theme/__init__.py` - Exports de tema
- [ ] `theme/colors.py` - Paleta de colores
- [ ] `theme/styles.py` - Estilos compartidos
- [ ] `utils/__init__.py` - Exports de utilidades
- [ ] `utils/debouncer.py` - Debouncing de eventos
- [ ] `utils/lazy_loader.py` - Carga perezosa
- [ ] `__init__.py` - Exports raíz presentación

---

## 🗂️ Fases de Migración (Incremental)

### **FASE 3: Dashboard Principal** ✅ COMPLETADA - 2026-01-08

#### 3.1 State Management
- [x] Crear `dashboard_state.py` con `@rx.event(background=True)`
- [x] Integración con `ServicioDashboard` (9 métodos)
- [x] Manejo de filtros (mes, año, asesor)
- [x] Estado de loading y errores

#### 3.2 Componentes KPI
- [x] Crear `kpi_card.py` reutilizable
- [x] 6 KPIs: Mora, Recaudo, Ocupación, Comisiones, Contratos, Recibos
- [x] Iconos Lucide y colores adaptativos
- [x] Subtítulos descriptivos

#### 3.3 Filtros Interactivos
- [x] Crear `dashboard_filters.py`
- [x] Dropdowns: Mes (1-12), Año (últimos 5), Asesor
- [x] Botones Aplicar y Reiniciar
- [x] Integración con state para recarga de datos

#### 3.4 Gráficos (Placeholders)
- [x] `chart_components.py` con 4 tipos de gráficos
- [x] Placeholders temporales (Recharts requiere computed vars)
- [ ] TODO: Implementar Recharts con datos formateados en backend

#### 3.5 Debugging Sistemático
- [x] 7 bugs identificados y corregidos:
  1. `@rx.background` → `@rx.event(background=True)`
  2. Import path `dashboard_layout`
  3. `rx.select()` syntax
  4. `.format()` en Reflex vars
  5. Comparaciones `>` en compile-time
  6. `len()` y `range()` en vars
  7. `on_mount` placement

### **FASE 0: Preparación y Setup** ✅ COMPLETADA

#### 0.1 Análisis de Dependencias
- [x] Inventariar todos los archivos de presentación
- [x] Identificar servicios de aplicación
- [x] Analizar conflictos entre flet y reflex (ninguno detectado)
- [x] Crear diagrama de arquitectura actual
- [x] Crear diagrama de arquitectura objetivo

#### 0.2 Configuración de Entorno
- [x] Crear rama `feature/migration-reflex` (no aplicable - repo sin git)
- [x] Instalar Reflex: `pip install reflex` (v0.8.24 instalado)
- [x] Crear `pyproject.toml` actualizado (requirements.txt actualizado)
- [x] Configurar puerto dual (Frontend:3000, Backend:8000)
- [x] Actualizar `.gitignore` para Reflex

#### 0.3 Estructura de Directorios
- [x] Crear `inmobiliaria_velar/` (módulo principal)
- [x] Crear `inmobiliaria_velar/inmobiliaria_velar.py` (entry point)
- [x] Crear `src/presentacion_reflex/` (estructura futura)
- [x] Crear `src/presentacion_reflex/pages/`
- [x] Crear `src/presentacion_reflex/components/`
- [x] Crear `src/presentacion_reflex/state/`
- [x] Crear `src/presentacion_reflex/assets/`
- [x] Crear `rxconfig.py` en raíz

### **FASE 1: Core Architecture** ✅ COMPLETADA

#### 1.1 Autenticación (Login)
- [x] Crear `src/presentacion_reflex/state/auth_state.py`
  - [x] Lógica de login/logout
  - [x] Persistencia de sesión (básica)
  - [x] Integración con `ServicioAutenticacion` existente
- [x] Crear página de Login (`src/presentacion_reflex/pages/login.py`)
  - [x] Formulario con validación
  - [x] Manejo de errores visuales
- [x] Implementar protección de rutas (`@rx.require_login`)

#### 1.2 Layout Base
- [x] Crear `src/presentacion_reflex/components/layout/sidebar.py`
  - [x] Navegación principal
  - [x] Información de usuario actual
  - [x] Botón logout
- [ ] Crear `src/presentacion_reflex/components/layout/navbar.py` (No necesario por diseño de sidebar completo)
- [x] Implementar wrapper para páginas protegidas (`dashboard_layout`)

#### 0.4 Documentación Base
- [x] Crear `docs/task_reflex.md` (este archivo)
- [x] Crear `docs/implementation_plan.md`
- [x] Crear diagrama Mermaid de migración
- [x] Crear tabla de mapeo Flet→Reflex

#### 0.5 Proof of Concept
### **FASE 2: Gestión de Personas** ✅ COMPLETADA

#### 2.1 Módulo de Personas
- [x] Crear `src/presentacion_reflex/state/personas_state.py`
  - [x] Paginación (prev_page, next_page)
  - [x] Búsqueda por texto
  - [x] Filtro por rol
  - [x] Lógica CRUD: `save_persona` (crear/editar)
  - [x] Control de modal: `open_create_modal`, `open_edit_modal`, `close_modal`
- [x] Crear página de Personas (`src/presentacion_reflex/pages/personas.py`)
  - [x] Tabla con datos desde BD
  - [x] Toolbar con búsqueda y filtros
  - [x] Indicador de loading
  - [x] Modal de creación integrado
  - [x] Modal de edición integrado
  - [x] Botón refresh manual
- [x] Crear `src/presentacion_reflex/components/personas/modal_form.py`
  - [x] Componente `rx.dialog` reutilizable
  - [x] Formulario dinámico (Crear vs Editar)
  - [x] Validación de campos requeridos
  - [x] Select de Tipo Documento y Rol Principal
  - [x] Manejo de errores visuales (Callout)

#### 2.2 Componentes Reutilizables
- [x] Formulario adaptativo persona (dentro de modal_form)

---

## 📈 Métricas de Progreso

### Por Tipo de Componente
| Tipo | Total | Completado | % |
|------|-------|------------|---|
| Vistas | 39 | 11 | 28% |
| Estados | 19 | 9 | 47% |
| Componentes | 30+ | 30+ | 100% |
| Arquitectura | 9 | 9 | 100% |
| **TOTAL** | **~90** | **~50** | **56%** |

---

## 🗂️ Fases Completadas

### **FASE 6: Liquidaciones de Propietarios** ✅ COMPLETADA - 2026-01-10

#### 6.1 State Management
- [x] Crear `liquidaciones_state.py` con gestión completa
- [x] Integración con `ServicioFinanciero` (Enhanced)
- [x] Gestión de filtros SQL nativos (período, estado)
- [x] Transiciones de estado seguras (En Proceso -> Aprobada -> Pagada)
- [x] Cálculos automáticos de comisiones e impuestos

#### 6.2 Página Principal
- [x] Crear `liquidaciones.py` con tabla paginada
- [x] Toolbar con filtros de período (últimos 24 meses)
- [x] Badges de estado coloreados
- [x] Botones de acción contextuales según estado

#### 6.3 Formularios y Modales
- [x] `liquidacion_detail_modal.py` - Breakdown financiero completo
- [x] `liquidacion_create_form.py` - Generación con pre-cálculo
- [x] `liquidacion_edit_form.py` - Edición segura de borradores
- [x] `payment_form.py` - Registro de pagos

### **FASE 7: Refactorización Backend (Global Database Migration)** ✅ COMPLETADA - 2026-01-11

#### 7.1 Abstracción de Base de Datos
- [x] Implementar `get_dict_cursor` en `DatabaseManager` (soporte híbrido SQLite/Postgres)
- [x] Implementar manejo dinámico de placeholders (`?` vs `%s`)
- [x] Estandarización de acceso a diccionarios (keys en minúscula)

#### 7.2 Migración de Servicios
- [x] `servicio_contratos.py`: Eliminación de dependencias `sqlite3`
- [x] `servicio_desocupaciones.py`: Actualización de métodos CRUD y reportes
- [x] `servicio_dashboard.py`: Optimización de queries analíticas
- [x] `servicio_seguros.py` y `servicio_propiedades.py`: Limpieza de consultas raw
- [x] `servicio_personas.py`: Refactorización completa de filtros y paginación
- [x] Eliminación global de imports directos de `sqlite3` en capa de aplicación

### **FASE 8: Gestión de Desocupaciones** ✅ COMPLETADA - 2026-01-11

#### 8.1 State Management
- [x] Crear `desocupaciones_state.py`
- [x] Integración con `ServicioDesocupaciones`
- [x] Lógica de filtrado y paginación
- [x] Manejo de checklist (toggle tareas)

#### 8.2 Componentes
- [x] `document_manager.py`: Componente reutilizable de upload
- [x] `modal_form.py`: Formulario de creación
- [x] `checklist_modal.py`: Modal de inspección
- [x] `desocupaciones.py`: Página principal con tabla y filtros

### **FASE 9: Gestión de Incidentes** ✅ COMPLETADA - 2026-01-11

#### 9.1 State Management
- [x] Crear `incidentes_state.py`
- [x] Lógica de agrupación Kanban
- [x] Toggle Vista (Lista vs Kanban)
- [x] Filtros y CRUD

#### 9.2 Componentes
- [x] `incident_card.py`: Tarjeta visual de incidente
- [x] `kanban_board.py`: Tablero de columnas
- [x] `modal_form.py`: Formulario de reporte
- [x] `incidentes.py`: Página principal integrada

### **FASE 5: Gestión de Contratos** ✅ COMPLETADA - 2026-01-10

#### 5.1 State Management
- [x] Crear `contratos_state.py` con gestión unificada
- [x] Integración con `ServicioContratos` (20 métodos)
- [x] Manejo de filtros (tipo, estado, propiedad, persona)
- [x] Paginación y búsqueda de texto
- [x] CRUD para Mandatos y Arrendamientos
- [x] Toggle estado (cancelar contratos)

#### 5.2 Página Principal
- [x] Crear `contratos.py` con listado unificado
- [x] Toolbar con filtros y botones de acción
- [x] Tabla con 9 columnas de información
- [x] Badges para Tipo y Estado
- [x] Paginación funcional
- [x] Loading states y manejo de errores

#### 5.3 Funcionalidades Implementadas
- [x] Vista unificada de Mandatos y Arrendamientos
- [x] Filtros por tipo (Todos/Mandato/Arrendamiento)
- [x] Filtros por estado (Todos/Activo/Cancelado)
- [x] Búsqueda por propiedad, persona y documento
- [x] Cancelar contratos (toggle estado)
- [x] Estructura de eventos para modal forms

#### 5.4 Formularios Modales ✅ COMPLETADO
- [x] `contrato_mandato_form.py` - Modal UI para crear/editar mandatos (218 líneas)
- [x] `contrato_arrendamiento_form.py` - Modal UI para crear/editar arrendamientos (204 líneas)
- [x] Validación de campos requeridos
- [x] Dropdowns con opciones dinámicas (propiedades, personas)
- [x] Conversión correcta de tipos de datos (int, float, porcentajes)
- [x] Manejo de errores visuales con callouts

### Fase 18: Saldos a Favor (Implementada) ✅

#### 18.1 Debugging
- [x] Fix `VarAttributeError` by mapping `SaldoFavor` entity to `SaldoModel(rx.Base)`.
- [x] Fix input type handlers with safe setters.

### Fase 19: Auditoría (Implementada) ✅
- [x] **State**: Create `auditoria_state.py` (Model adapter + Loading).
- [x] **UI**: Create `pages/auditoria.py` (Table + Filters).
- [x] **Nav**: Add sidebar item.
- [x] **Integration**: Connect to `ServicioConfiguracion.listar_auditoria`.

#### 1. State Management (`SaldosState`)propiedades_state.py` con gestión completa
- [x] Integración con `ServicioPropiedades` (20 métodos)
- [x] Manejo de filtros (tipo, disponibilidad, municipio)
- [x] Paginación y búsqueda
- [x] Toggle solo activas
- [x] Vista cards/tabla switcheable

### ✅ Fase 4 Completada - 2026-01-10

#### 4.1 State Management
- [x] Crear `propiedades_state.py` con gestión completa
- [x] Integración con `ServicioPropiedades` (20 métodos)
- [x] Manejo de filtros (tipo, disponibilidad, municipio)
- [x] Paginación y búsqueda
- [x] Toggle solo activas
- [x] Vista cards/tabla switcheable

#### 4.2 Página Principal
- [x] Crear `propiedades.py` con listado completo
- [x] Toolbar con filtros avanzados
- [x] Vista de tarjetas y tabla
- [x] Paginación funcional
- [x] Indicadores de loading

#### 4.3 Componentes
- [x] `property_card.py` - Tarjeta de propiedad
- [x] `modal_form.py` - Formulario modal CRUD
- [x] Validación de campos
- [x] Manejo de errores visuales

#### 4.4 Integración
- [x] CRUD completo funcionando
- [x] Toggle disponibilidad
- [x] Búsqueda por dirección/código
- [x] Filtros múltiples simultáneos

### ✅ Fase 3 Completada - 2026-01-08

### Logros de la Fase 3:
- ✅ **Dashboard Funcional**: 6 KPIs con datos reales de BD (`ServicioDashboard`)
- ✅ **Filtros Dinámicos**: Mes, Año y Asesor con recarga automática
- ✅ **State Asíncrono**: `@rx.event(background=True)` para carga sin bloqueo de UI
- ✅ **KPI Cards**: Componente reutilizable con iconos, colores y subtítulos
- ✅ **Charts Placeholder**: 4 gráficos preparados (implementación Recharts pendiente)
- ✅ **Debugging Sistemático**: 7 bugs identificados y corregidos siguiendo workflow
- ✅ **Servidor Compilado**: App corriendo en http://localhost:3000/dashboard

### Componentes Migrados (8 archivos):
1. `dashboard_state.py` - State management con background tasks
2. `kpi_card.py` - Tarjetas KPI reutilizables
3. `chart_components.py` - 4 tipos de gráficos (placeholders)
4. `dashboard_filters.py` - Filtros interactivos
5. `dashboard.py` - Página principal del dashboard
6. `__init__.py` (dashboard components) - Exports

---

## ✅ Fase 2 Completada - 2026-01-07

### Logros de la Fase 2:
- ✅ **CRUD Completo**: Crear y Editar personas desde la interfaz web.
- ✅ **Modal Moderno**: Formulario adaptativo en `rx.dialog` con validación.
- ✅ **Integración BD**: Conexión directa con `ServicioPersonas` sin modificar lógica de negocio.
- ✅ **UX Premium**: Búsqueda en tiempo real, filtros por rol, paginación funcional.
- ✅ **Manejo de Errores**: Callouts visuales para duplicados o errores de validación.

## ✅ Fase 1 Completada - 2026-01-07

### Logros de la Fase 1:
- ✅ **Sistema de Autenticación**: Login funcional integrado con base de datos real.
- ✅ **Seguridad**: Rutas protegidas que redirigen a login si no hay sesión.
- ✅ **UI Premium**: Página de Login con diseño moderno y feedback visual.
- ✅ **Layout Base**: Sidebar profesional y estructura de Dashboard implementada.
- ✅ **Integración**: Reutilización exitosa de `ServicioAutenticacion` sin cambios.


### Logros de la Fase 0:
- ✅ Reflex v0.8.24 instalado exitosamente
- ✅ Estructura de módulos creada: `inmobiliaria_velar/inmobiliaria_velar.py`
- ✅ Configuración `rxconfig.py` con puertos duales (3000/8000)
- ✅ Proof of Concept funcional con 2 páginas:
  - `/` - Página de bienvenida con gradiente  
  - `/progreso` - Estadísticas de migración
- ✅ Servidor compiló 24 componentes sin errores
- ✅ App corriendo en: http://localhost:3000
- ✅ Backend API en: http://localhost:8000
- ✅ Scripts de inicio `start_reflex.ps1` creados
- ✅ `requirements.txt` y `.gitignore` actualizados
- ✅ Documentación completa: task_reflex.md, implementation_plan.md, arquitectura_migracion.md

---

## 🔗 Mapeo Flet → Reflex (Referencia Rápida)

| Flet | Reflex | Notas |
|------|--------|-------|
| `ft.Text` | `rx.text` | Directo |
| `ft.TextField` | `rx.input` | Eventos diferentes |
| `ft.ElevatedButton` | `rx.button` | Estilos CSS |
| `ft.Column` | `rx.vstack` | Spacing diferente |
| `ft.Row` | `rx.hstack` | Spacing diferente |
| `ft.Container` | `rx.box` o `rx.container` | Padding/margin diferentes |
| `ft.DataTable` | `rx.data_table` | API diferente |
| `ft.Dropdown` | `rx.select` | Items diferentes |
| `ft.Card` | `rx.card` o custom | Crear componente |
| `ft.AlertDialog` | `rx.dialog` o `rx.modal` | Lógica diferente |
| `ft.Drawer` | Custom sidebar | No hay equivalente directo |
| `ft.SnackBar` | `rx.toast` | Temporal |
| `ft.FilePicker` | `rx.upload` | API completamente diferente |
| `page.update()` | Automático con `State` | No necesita llamadas |
| `page.add()` | `return componente` | Declarativo |

---

## 🎯 Próximos Pasos (Prioridad Alta)

### ~~FASE 10: Módulo de Seguros Completo~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%  
**Dependencias**: ✅ Contratos, ✅ Propiedades

### ~~FASE 11: Módulo de Recaudos~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%  
**Dependencias**: ✅ Contratos, ✅ Personas, ✅ Propiedades
**Debugging**: 6 errores críticos resueltos

---

### ~~FASE 12: Liquidaciones de Asesores~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%
**Dependencias**: ✅ Contratos, ✅ Liquidaciones Propietarios

#### Tareas Completadas:
- [x] Crear `liquidacion_asesores_state.py` (CRUD, Descuentos, Estados)
- [x] Implementar componentes de formulario (`modal_form`, `detail`, `discount`)
- [x] Actualizar página con tabla y filtros
- [x] Integración con `ServicioLiquidacionAsesores`

---

### ~~FASE 13: Gestión de Proveedores~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%
**Dependencias**: Ninguna

#### Tareas Completadas:
- [x] Crear `proveedores_state.py`
- [x] Migrar formulario de proveedores
- [x] Implementar listado y búsqueda
- [x] Integración con `ServicioProveedores`

### ~~FASE 14: Recibos Públicos~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%
**Componentes**: `recibos_state.py`, `recibos_publicos.py`
- [x] CRUD Completo
- [x] Control de Vencimientos
- [x] Alertas Visuales

### ~~FASE 15: Gestión de Usuarios~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%
**Componentes**: `usuarios_state.py`, `usuarios.py`
- [x] Administración de roles
- [x] Seguridad mejorada (Hashing)

### ~~FASE 16: Alertas y Configuración~~ ✅ COMPLETADA - 2026-01-12
**Estado**: ✅ Completado al 100%
**Componentes**: `bell_icon.py`, `alertas_state.py`, `configuracion.py`
- [x] Centro de Notificaciones (Campana)
- [x] Página de Ajustes Globales

### FASE 17: Mejoras Funcionales (Roles Múltiples)
**Estado**: [-] EN PROGRESO
**Componentes**: `personas_state.py`, `modal_form.py`
- [ ] Soporte para selección múltiple de roles (CheckBox)
- [ ] UI dinámica para campos de múltiples roles
- [ ] Lógica de guardado y actualización de roles múltiples


---

**Última actualización:** 2026-01-12 01:45:00
**Próxima revisión:** Antes de iniciar Fase 13

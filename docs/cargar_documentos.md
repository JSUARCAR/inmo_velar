# PROMPT TÉCNICO PARA IMPLEMENTACIÓN DE CARGA DE DOCUMENTOS E IMÁGENES - NIVEL ÉLITE

## 🎯 OBJETIVO

Implementar funcionalidad completa de carga, gestión y visualización de documentos e imágenes a nivel empresarial en los módulos: **Contratos**, **Liquidaciones**, **Liquidación Asesores**, **Recaudos**, **Desocupaciones**, **Incidentes**, y **Recibos Públicos**.

## 🏗️ FASE 1: INFRAESTRUCTURA BASE

- [x] **1.1 Configuración Global**
  - [x] Crear `src/dominio/constantes/tipos_documento.py` con `TIPOS_DOCUMENTO_MODULO` y `DOCUMENTOS_REQUERIDOS_POR_ESTADO`.
- [x] **1.2 Extensión Servicio Documental**
  - [x] Crear/Extender `ServicioDocumentalElite` en `src/aplicacion/servicios/servicio_documental.py`.
    - [x] `validar_documento_modulo`
    - [x] `generar_thumbnail` (PIL)
    - [x] `extraer_texto_ocr` (Placeholder/Tesseract)
    - [x] `comprimir_imagen`
    - [x] `procesar_upload_multiple`
- [x] **1.3 Componentes UI Especializados**
  - [x] Crear `src/presentacion_reflex/components/document_manager_elite.py`.
    - [x] Drag & Drop zone.
    - [x] File preview cards.
    - [x] Progress bars.
  - [x] Crear `src/presentacion_reflex/components/image_gallery.py`.
    - [x] Grid layout.
    - [x] Lightbox support.
- [x] **1.4 Estado Base**
  - [x] Crear Mixin o Clase Base para manejo de documentos en el state.

## 🏗️ FASE 2: INTEGRACIÓN POR MÓDULOS

### 2.1 Contratos

- [x] **Backend (State)**:
  - [x] Actualizar `ContratosState` (variables `documentos_contrato`, `upload_progress`).
  - [x] Implementar `handle_upload_documentos`.
- [x] **Frontend (UI)**:
  - [x] Modificar `contrato_arrendamiento_form.py` y `contrato_mandato_form.py`.
  - [x] Agregar Tab "Documentos".
  - [x] Integrar `document_manager_elite`.

### 2.2 Incidentes

- [x] **Backend**:
    - [x] Heredar `DocumentosStateMixin` en `IncidentesState`.
    - [x] Configurar `current_entidad_tipo = "INCIDENTE"`.
    - [x] Implementar carga de documentos al seleccionar incidente.
- [x] **Frontend**:
    - [x] Modificar `modal_details.py` de Incidentes (Implementar Tabs).
    - [x] Integrar `document_manager_elite` con validación de estado.

### 2.3 Desocupaciones

- [x] **Backend**:
    - [x] Heredar `DocumentosStateMixin` en `DesocupacionesState`.
    - [x] Configurar `current_entidad_tipo = "DESOCUPACION"`.
- [x] **Frontend**:
    - [x] Modificar `checklist_modal.py` (Implementar Tabs).
    - [x] Agregar soporte para checklist y fotos de estado.

### 2.4 Recaudos

- [x] **Backend**:
    - [x] Heredar `DocumentosStateMixin` en `RecaudosState`.
    - [x] Configurar `current_entidad_tipo = "RECAUDO"`.
- [x] **Frontend**:
    - [x] Integrar en modal de detalle (`detail_modal.py`).

### 2.5 Liquidaciones (Propietarios)

- [x] **Backend**:
  - [x] Heredar `DocumentosStateMixin` en `LiquidacionesState`.
  - [x] Configurar `current_entidad_tipo = "LIQUIDACION"`.
- [x] **Frontend**:
  - [x] Integrar en modal de detalle (`liquidacion_detail_modal.py`).

### 2.6 Liquidación Asesores (Nuevo)

- [x] **Backend**:
  - [x] Heredar `DocumentosStateMixin` en `LiquidacionAsesoresState`.
  - [x] Configurar `current_entidad_tipo = "LIQUIDACION_ASESOR"`.
- [x] **Frontend**:
  - [x] Integrar en modal de detalle.

### 2.7 Recibos Públicos (Nuevo)

- [x] **Backend**:
  - [x] Heredar `DocumentosStateMixin` en `RecibosState`.
  - [x] Configurar `current_entidad_tipo = "RECIBO_PUBLICO"`.
- [x] **Frontend**:
  - [x] Integrar en modal de detalle.

## 🏗️ FASE 3: CARACTERÍSTICAS AVANZADAS

- [x] **Validaciones de Negocio**: `ValidadorDocumentos`.
- [x] **Procesamiento Asíncrono**: `ProcesadorDocumentosAsync`.
- [x] **API Documentos**: Endpoints en `documentos_api.py`.

## 🏗️ FASE 4: TESTING & OPTIMIZACIÓN

- [x] Tests de carga de archivos grandes.
- [x] Tests de validación de extensiones/mime-types.
- [x] Verificación de miniaturas.

---

**Registro de Cambios y Progreso**
*Fecha Actualización: 2026-01-24*
*Mensaje: PROYECTO COMPLETADO. Fase 4 terminada exitosamente con script de pruebas automatizadas (`tests/test_documentos_elite.py`) validando reglas de negocio y procesamiento de imágenes.*

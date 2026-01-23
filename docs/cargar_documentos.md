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
- [ ] **Backend**: Actualizar State.
- [ ] **Frontend**: Integrar en formulario de incidentes (Fotos daño).

### 2.3 Desocupaciones
- [ ] **Backend**: Actualizar State.
- [ ] **Frontend**: Integrar Checklists y Fotos.

### 2.4 Recaudos & Liquidaciones
- [ ] **Backend**: Actualizar State.
- [ ] **Frontend**: Soporte para comprobantes de pago.

## 🏗️ FASE 3: CARACTERÍSTICAS AVANZADAS
- [ ] **Validaciones de Negocio**: `ValidadorDocumentos`.
- [ ] **Procesamiento Asíncrono**: `ProcesadorDocumentosAsync`.
- [ ] **API Documentos**: Endpoints en `documentos_api.py`.

## 🏗️ FASE 4: TESTING & OPTIMIZACIÓN
- [ ] Tests de carga de archivos grandes.
- [ ] Tests de validación de extensiones/mime-types.
- [ ] Verificación de miniaturas.

---
**Registro de Cambios y Progreso**
*Iniciado: 2026-01-22*

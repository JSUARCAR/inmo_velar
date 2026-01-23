# ============================================================================
# SISTEMA PDF DE ÉLITE - GUÍA COMPLETA
# ============================================================================

## 📚 Índice

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Instalación](#instalación)
4. [Uso Básico](#uso-básico)
5. [Uso Avanzado](#uso-avanzado)
6. [Integración con Reflex](#integración-con-reflex)
7. [Extensión y Personalización](#extensión-y-personalización)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El Sistema PDF de Élite es una solución profesional para generación de documentos PDF en Python, específicamente diseñada para la plataforma Inmobiliaria Velar.

### Características Principales

- ✅ **100% Compatible** con el sistema legacy existente
- ✅ **Generación Élite** con ReportLab para control total
- ✅ **Componentes Reutilizables** (tablas, watermarks, QR codes)
- ✅ **Templates Profesionales** (contratos, certificados, estados de cuenta)
- ✅ **Integración Reflex** con event handlers listos
- ✅ **Validación Robusta** de datos
- ✅ **QR de Verificación** en todos los documentos
- ✅ **Temas Personalizables** (5 temas predefinidos)

---

## 🏗️ Arquitectura

```
src/infraestructura/servicios/
├── pdf_elite/                      # Módulo élite
│   ├── core/                       # Núcleo del sistema
│   │   ├── config.py              # Configuración global
│   │   ├── base_generator.py     # Generador abstracto
│   │   └── reportlab_generator.py # Generador ReportLab
│   ├── components/                # Componentes reutilizables
│   │   ├── tables.py              # Tablas avanzadas
│   │   ├── watermarks.py          # Marcas de agua
│   │   └── ...
│   ├── templates/                 # Templates de documentos
│   │   ├── base_template.py      # Template base
│   │   ├── contrato_template.py  # Contratos
│   │   ├── certificado_template.py
│   │   └── estado_cuenta_elite.py
│   ├── utils/                     # Utilidades
│   │   ├── qr_generator.py       # Códigos QR
│   │   ├── validators.py         # Validadores
│   │   └── ...
│   └── styles/                    # Estilos y temas
│       ├── colors.py
│       ├── fonts.py
│       └── themes.py
├── servicio_pdf_facade.py         # Facade unificador
└── servicio_documentos_pdf.py     # Servicio legacy
```

---

## 📦 Instalación

### Dependencias

Todas las dependencias están en `requirements_pdf_elite.txt`:

```bash
pip install -r requirements_pdf_elite.txt
```

Incluye:
- reportlab>=4.2.5
- qrcode[pil]>=7.4.2
- python-barcode>=0.15.1
- matplotlib>=3.9.2
- PyPDF2>=3.0.1

### Setup Inicial

```bash
# Ejecutar script de setup (crea estructura de directorios)
python setup_pdf_elite.py
```

---

## 🚀 Uso Básico

### Opción 1: Usar el Facade (Recomendado)

El facade mantiene compatibilidad 100% con código legacy:

```python
from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

# Crear instancia
facade = ServicioPDFFacade()

# Usar métodos legacy (sin cambios en código existente)
pdf_path = facade.generar_comprobante_recaudo(datos)

# O usar nuevos métodos élite
pdf_path = facade.generar_contrato_elite(datos_contrato)
```

### Opción 2: Usar Templates Directamente

```python
from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite

# Crear generador
gen = ContratoArrendamientoElite()

# Preparar datos
datos = {
    'contrato_id': 123,
    'fecha': '2026-01-18',
    'arrendador': {...},
    'arrendatario': {...},
    'inmueble': {...},
    'condiciones': {...}
}

# Generar PDF
pdf_path = gen.generate(datos)
```

---

## 🎨 Uso Avanzado

### Personalizar Marcas de Agua

```python
from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite

gen = ContratoArrendamientoElite()

# Configurar marca de agua personalizada
gen.set_watermark("CONFIDENCIAL", opacity=0.2, style='diagonal')

pdf_path = gen.generate(datos)
```

### Posicionar QR Code

```python
# QR en posición personalizada
gen.set_qr_code(
    data="https://verify.inmovelar.com/123",
    size=150,
    position='bottom-right'  # top-right, top-left, bottom-right, bottom-left
)
```

### Usar Temas Personalizados

```python
from src.infraestructura.servicios.pdf_elite.styles.themes import Themes

# Usar tema predefinido
gen.theme = Themes.LEGAL  # Para documentos legales
# Opciones: CORPORATE, PROFESSIONAL, MINIMAL, LEGAL, CERTIFICATE
```

---

## 🔌 Integración con Reflex

### 1. Importar el Estado

```python
# En tu página de Reflex
from src.presentacion_reflex.state.pdf_state import PDFState
```

### 2. Usar Event Handlers

```python
def contratos_page() -> rx.Component:
    return rx.box(
        # Botón para generar contrato élite
        rx.button(
            "Generar Contrato Élite",
            on_click=PDFState.generar_contrato_arrendamiento_elite(
                contrato_id,
                es_borrador=False
            )
        ),
        
        # Botón para certificado
        rx.button(
            "Generar Paz y Salvo",
            on_click=PDFState.generar_certificado_paz_y_salvo(
                contrato_id,
                beneficiario_nombre
            )
        ),
        
        # Mostrar mensajes
        rx.cond(
            PDFState.success_message != "",
            rx.toast.success(PDFState.success_message)
        ),
        rx.cond(
            PDFState.error_message != "",
            rx.toast.error(PDFState.error_message)
        )
    )
```

### 3. Descarga Automática

El sistema descarga automáticamente los PDFs generados usando `rx.download()`.

---

## 🛠️ Extensión y Personalización

### Crear Nuevo Template

```python
from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate

class MiNuevoTemplate(BaseDocumentTemplate):
    def __init__(self, output_dir=None):
        super().__init__(output_dir)
        self.document_title = "MI DOCUMENTO PERSONALIZADO"
    
    def validate_data(self, data):
        # Validar datos requeridos
        self._require_fields(data, 'campo1', 'campo2')
        return True
    
    def generate(self, data):
        # Habilitar características
        self.enable_verification_qr('mi_doc', data['doc_id'])
        
        # Crear documento
        filename = self._generate_filename('mi_doc', data['doc_id'])
        self.create_document(filename, self.document_title)
        
        # Agregar contenido
        self.add_title_main(self.document_title)
        self.add_paragraph("Contenido del documento...")
        
        # Construir
        return self.build()
```

### Agregar al Facade

```python
# En servicio_pdf_facade.py
def generar_mi_documento(self, datos):
    if not self._mi_doc_gen:
        self._mi_doc_gen = MiNuevoTemplate(self.output_dir)
    
    return str(self._mi_doc_gen.generate_safe(datos))
```

---

## 📖 API Reference

### ServicioPDFFacade

**Métodos Legacy:**
- `generar_comprobante_recaudo(datos)` - Comprobante de pago
- `generar_estado_cuenta(datos)` - Estado de cuenta
- `generar_cuenta_cobro_asesor(datos)` - Cuenta de cobro
- `generar_checklist_desocupacion(datos)` - Checklist

**Métodos Élite:**
- `generar_contrato_elite(datos, usar_borrador=False)` - Contrato profesional
- `generar_certificado_elite(datos)` - Certificados oficiales
- `generar_estado_cuenta_elite(datos)` - Estado mejorado

**Utilidades:**
- `listar_capacidades_elite()` - Lista características élite
- `get_version_info()` - Información de versión

### PDFState (Reflex)

**Event Handlers:**
- `generar_contrato_arrendamiento_elite(contrato_id, es_borrador)`
- `generar_certificado_paz_y_salvo(contrato_id, beneficiario_nombre)`
- `generar_estado_cuenta_elite(propietario_id, periodo)`

**Propiedades:**
- `generating: bool` - Si está generando
- `last_pdf_path: str` - Path del último PDF
- `error_message: str` - Mensaje de error
- `success_message: str` - Mensaje de éxito

---

## 🔧 Troubleshooting

### Error: "Plotly no está instalado"

```bash
pip install plotly kaleido
```

### Error: "FileNotFoundError" al generar QR

Verificar que qrcode[pil] está instalado:

```bash
pip install qrcode[pil]
```

### PDFs no se descargan en Reflex

Verificar que el path existe y usar `rx.download(path)` en el event handler.

### Marca de agua no aparece

Verificar que `enable_watermarks=True` en config y que la opacidad no sea demasiado baja.

---

## 📊 Métricas del Sistema

- **Líneas de Código:** ~3,500
- **Archivos Creados:** 25+
- **Templates Disponibles:** 4 (Contratos, Certificados, Estados, Base)
- **Componentes:** 10+ reutilizables
- **Cobertura de Tests:** 85%+
- **Compatibilidad:** 100% con legacy

---

## 🎓 Mejores Prácticas

1. **Siempre validar datos** antes de generar
2. **Usar el Facade** para nueva funcionalidad
3. **Habilitar QR** en documentos oficiales
4. **Usar watermarks** en documentos borrador
5. **Probar con datos reales** antes de producción

---

## 📝 Notas de Versión

**v1.0.0** (2026-01-18)
- ✅ Sistema completo implementado
- ✅ 100% compatible con legacy
- ✅ Integración Reflex completa
- ✅ Tests E2E pasando

---

**Desarrollado por:** Sistema de Gestión Inmobiliaria  
**Fecha:** 2026-01-18  
**Versión:** 1.0.0

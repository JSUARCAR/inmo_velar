# 🎨 Guía de Integración UI - Botones PDF en Reflex

## 📋 Resumen

Esta guía muestra cómo agregar botones PDF en los módulos de Reflex.

---

## 🔧 Paso 1: Importar PDFState

En cada archivo de página, importa el estado:

```python
from src.presentacion_reflex.state.pdf_state import PDFState
```

---

## 📄 Ejemplo 1: Módulo de Contratos

### Ubicación del archivo
`src/presentacion_reflex/pages/contratos.py` (o similar)

### Código para agregar

```python
import reflex as rx
from src.presentacion_reflex.state.pdf_state import PDFState

def boton_generar_contrato_elite(contrato_id: int) -> rx.Component:
    """Botón para generar contrato élite"""
    return rx.hstack(
        # Botón principal
        rx.button(
            rx.icon("file-text", size=16),
            "Contrato Élite",
            on_click=PDFState.generar_contrato_arrendamiento_elite(
                contrato_id,
                es_borrador=False
            ),
            loading=PDFState.generating,
            color_scheme="blue",
            size="2",
        ),
        
        # Botón borrador
        rx.button(
            rx.icon("file-edit", size=16),
            "Borrador",
            on_click=PDFState.generar_contrato_arrendamiento_elite(
                contrato_id,
                es_borrador=True
            ),
            loading=PDFState.generating,
            variant="outline",
            color_scheme="gray",
            size="2",
        ),
        
        spacing="2"
    )

# Agregar en la tabla de contratos
def tabla_contratos() -> rx.Component:
    return rx.table.root(
        rx.table.header(...),
        rx.table.body(
            rx.foreach(
                ContratoState.contratos,
                lambda contrato: rx.table.row(
                    rx.table.cell(contrato.id),
                    rx.table.cell(contrato.arrendatario),
                    # ... otras columnas
                    rx.table.cell(
                        # AGREGAR AQUÍ:
                        boton_generar_contrato_elite(contrato.id)
                    )
                )
            )
        )
    )
```

---

## 💰 Ejemplo 2: Módulo de Liquidaciones

### Ubicación
`src/presentacion_reflex/pages/liquidaciones.py` (o similar)

### Código para agregar

```python
import reflex as rx
from src.presentacion_reflex.state.pdf_state import PDFState

def boton_estado_cuenta_elite(propietario_id: int, periodo: str) -> rx.Component:
    """Botón para generar estado de cuenta élite"""
    return rx.button(
        rx.icon("file-spreadsheet", size=16),
        "Estado de Cuenta",
        on_click=PDFState.generar_estado_cuenta_elite(
            propietario_id,
            periodo
        ),
        loading=PDFState.generating,
        color_scheme="green",
        size="2",
    )

# Uso en la página
def seccion_liquidacion(liquidacion_id: int, propietario_id: int) -> rx.Component:
    periodo_actual = rx.moment().format("YYYY-MM")
    
    return rx.card(
        rx.vstack(
            rx.heading(f"Liquidación #{liquidacion_id}"),
            
            # Información de la liquidación...
            
            # AGREGAR BOTÓN:
            rx.hstack(
                boton_estado_cuenta_elite(propietario_id, periodo_actual),
                rx.button("Ver Detalle", ...),
                spacing="2"
            )
        )
    )
```

---

## 🏠 Ejemplo 3: Módulo de Propiedades

### Ubicación
`src/presentacion_reflex/pages/propiedades.py` (o similar)

### Código para agregar

```python
import reflex as rx
from src.presentacion_reflex.state.pdf_state import PDFState

def boton_certificado_paz_y_salvo(contrato_id: int, beneficiario: str) -> rx.Component:
    """Botón para generar certificado de paz y salvo"""
    return rx.button(
        rx.icon("award", size=16),
        "Certificado Paz y Salvo",
        on_click=PDFState.generar_certificado_paz_y_salvo(
            contrato_id,
            beneficiario
        ),
        loading=PDFState.generating,
        color_scheme="purple",
        size="2",
    )

# Uso en modal o sección de propiedad
def modal_acciones_propiedad(propiedad, contrato_actual) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Acciones", variant="outline")
        ),
        rx.dialog.content(
            rx.dialog.title(f"Acciones - {propiedad.direccion}"),
            
            rx.vstack(
                # Otras acciones...
                
                # AGREGAR BOTÓN:
                rx.cond(
                    contrato_actual,  # Solo si hay contrato
                    boton_certificado_paz_y_salvo(
                        contrato_actual.id,
                        contrato_actual.arrendatario_nombre
                    ),
                    rx.text("Sin contrato activo", color="gray")
                ),
                
                spacing="3"
            )
        )
    )
```

---

## 🎨 Componente Reutilizable Avanzado

Para máxima reutilización:

```python
# src/presentacion_reflex/components/pdf_buttons.py

import reflex as rx
from src.presentacion_reflex.state.pdf_state import PDFState

class PDFButtons:
    """Componentes reutilizables para botones PDF"""
    
    @staticmethod
    def contrato_elite(contrato_id: int) -> rx.Component:
        return rx.menu.root(
            rx.menu.trigger(
                rx.button(
                    rx.icon("file-text"),
                    "PDF",
                    loading=PDFState.generating
                )
            ),
            rx.menu.content(
                rx.menu.item(
                    "Contrato Oficial",
                    on_click=PDFState.generar_contrato_arrendamiento_elite(
                        contrato_id, False
                    )
                ),
                rx.menu.item(
                    "Borrador",
                    on_click=PDFState.generar_contrato_arrendamiento_elite(
                        contrato_id, True
                    )
                ),
                rx.menu.separator(),
                rx.menu.item(
                    "Certificado Paz y Salvo",
                    on_click=lambda: ...  # Necesita beneficiario
                ),
            )
        )
    
    @staticmethod
    def estado_cuenta(propietario_id: int) -> rx.Component:
        return rx.button(
            rx.icon("file-spreadsheet"),
            "Estado Cuenta",
            on_click=PDFState.generar_estado_cuenta_elite(
                propietario_id,
                rx.moment().format("YYYY-MM")
            ),
            loading=PDFState.generating,
            color_scheme="green"
        )

# Uso:
# from src.presentacion_reflex.components.pdf_buttons import PDFButtons
# PDFButtons.contrato_elite(contrato.id)
```

---

## 💡 Mejores Prácticas

### 1. Manejo de Estado Loading
```python
rx.button(
    "Generar PDF",
    on_click=PDFState.generar_contrato(...),
    loading=PDFState.generating,  # ← Deshabilita mientras genera
)
```

### 2. Feedback Visual
```python
# PDFState ya tiene toast notifications integradas
# Se muestran automáticamente al generar

# Opcionalmente, muestra mensajes:
rx.cond(
    PDFState.success_message != "",
    rx.callout.root(
        rx.callout.text(PDFState.success_message),
        color="green"
    )
)
```

### 3. Validación Antes de Generar
```python
rx.button(
    "Generar Contrato",
    on_click=PDFState.generar_contrato(...),
    disabled=contrato.estado != "ACTIVO",  # ← Solo contratos activos
)
```

---

## 🧪 Testing

Prueba los botones:

1. **Desarrollo:** Funcionan con datos mock del repository
2. **Producción:** Cambia `USE_MOCK_PDF_DATA=false` en `.env`

---

## 📝 Checklist de Implementación

- [ ] Importar `PDFState` en archivo de página
- [ ] Crear función de botón
- [ ] Agregar botón en la UI (tabla, modal, etc.)
- [ ] Probar con IDs reales
- [ ] Verificar descarga automática
- [ ] Confirmar toast notifications

---

**¡Listo! Tus botones PDF están integrados** 🎉

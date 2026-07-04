# Generación de Paz y Salvo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar un botón "Generar Paz y Salvo" en las vistas de contratos (tabla y cuadrícula) para contratos inactivos, permitiendo la generación manual del documento.

**Architecture:** El botón se agregará en los componentes visuales de Reflex (`contratos.py` y `tarjeta_contrato.py`), utilizando condicionales `rx.cond` para renderizarse solo cuando el contrato no esté activo. Llamará a la función `PDFState.generar_certificado_paz_y_salvo` y pasará dinámicamente el beneficiario basado en el tipo de contrato.

**Tech Stack:** Python, Reflex

## Global Constraints

- Estándar de colores Elite (teal para esta acción).
- Código en español (Reglas del proyecto).
- Zero leaks, convenciones strictas.
- Verificación con `check_syntax.py`, `mypy`, `ruff`, `black`.

---

### Task 1: Modificar Tarjeta Contrato (Vista Cuadrícula)

**Files:**
- Modify: `src/presentacion_reflex/components/contratos/tarjeta_contrato.py`

**Interfaces:**
- Consumes: `PDFState.generar_certificado_paz_y_salvo`
- Produces: Botón en la interfaz de tarjeta.

- [ ] **Step 1: Agregar el botón en tarjeta_contrato.py**

Modificar el `rx.scroll_area` de las acciones (alrededor de la línea 265, después del botón de terminar o antes).

```python
                    # Paz y Salvo (Para inactivos)
                    rx.cond(
                        contrato.estado_contrato != "ACTIVO",
                        neuro_icon_action_button(
                            "shield-check",
                            on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
                                contrato.id_contrato,
                                rx.cond(
                                    contrato.tipo_contrato == "Mandato",
                                    contrato.propietario_nombre,
                                    contrato.arrendatario_nombre,
                                )
                            ),
                            color_scheme="teal",
                            tooltip_content="Generar Paz y Salvo",
                        ),
                    ),
```

- [ ] **Step 2: Verificar la sintaxis**

Run: `python scripts/check_syntax.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/presentacion_reflex/components/contratos/tarjeta_contrato.py
git commit -m "feat(presentacion): agregar boton de paz y salvo en tarjeta de contrato inactivo"
```

---

### Task 2: Modificar Tabla Contratos (Vista Lista)

**Files:**
- Modify: `src/presentacion_reflex/pages/contratos.py`

**Interfaces:**
- Consumes: `PDFState.generar_certificado_paz_y_salvo`
- Produces: Botón en la interfaz de tabla.

- [ ] **Step 1: Agregar el botón en _tabla_acciones**

Dentro de `_tabla_acciones` en `src/presentacion_reflex/pages/contratos.py`, agregar el botón de paz y salvo junto a los otros botones condicionales.

```python
            # Paz y Salvo — solo si está inactivo
            rx.cond(
                c.estado_contrato != "ACTIVO",
                neuro_icon_action_button(
                    "shield-check",
                    color_scheme="teal",
                    size="1",
                    tooltip_content="Generar Paz y Salvo",
                    on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
                        c.id_contrato,
                        rx.cond(
                            c.tipo_contrato == "Mandato",
                            c.propietario_nombre,
                            c.arrendatario_nombre,
                        ),
                    ),
                ),
            ),
```

- [ ] **Step 2: Verificar la sintaxis**

Run: `python scripts/check_syntax.py src/presentacion_reflex/pages/contratos.py`
Expected: PASS

- [ ] **Step 3: Ejecutar QA tools (Linter y Formatter)**

Run: `ruff check src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`
Run: `black src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`

- [ ] **Step 4: Commit**

```bash
git add src/presentacion_reflex/pages/contratos.py
git commit -m "feat(presentacion): agregar boton de paz y salvo en tabla de contratos inactivos"
```

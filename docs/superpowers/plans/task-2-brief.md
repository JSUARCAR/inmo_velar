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

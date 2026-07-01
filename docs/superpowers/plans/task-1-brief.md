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

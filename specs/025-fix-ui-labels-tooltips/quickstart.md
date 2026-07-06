# Quickstart Validation Guide: Etiquetas Flotantes y Tooltips

Este documento proporciona los pasos para validar visual y funcionalmente la reparación de las etiquetas flotantes (Floating Labels) y tooltips.

## Prerequisites
- Dependencias de Reflex instaladas (entorno virtual activo).
- Base de datos configurada (o SQLite por defecto de desarrollo si se encuentra en uso).

## Pasos para Validar Localmente

1. **Ejecutar el entorno de desarrollo:**
   ```bash
   reflex run --env dev
   ```

2. **Acceder a la aplicación:**
   Abre un navegador en `http://localhost:3000`.

3. **Validación de Floating Labels:**
   - Navega hacia cualquier módulo con formularios (ej. `Liquidaciones`, `Recaudos` o `Contratos`).
   - Observa un input vacío. La etiqueta debe estar contenida como placeholder.
   - Haz clic en el input. La etiqueta debe desplazarse hacia el borde superior.
   - Escribe un texto y haz clic fuera del input (blur). La etiqueta debe mantenerse en la posición superior.
   - Borra el contenido y quita el foco. La etiqueta debe regresar a su posición inicial.

4. **Validación de Tooltips:**
   - Navega a un área con acciones principales (botones de acciones en tablas, filtros o edición).
   - Posiciona el cursor (hover) sobre un botón que no sea auto-explicativo (ej. botones con iconos como basura, editar, ojo).
   - Verifica que aparezca un pequeño cuadro con el texto explicativo de la acción y que la superposición z-index sea correcta (no queda tapado por modales o tablas).

## Expected Outcomes
- Ningún error de compilación en el terminal.
- Transiciones fluidas en formularios.
- Tooltips visibles y accesibles en botones de acción.

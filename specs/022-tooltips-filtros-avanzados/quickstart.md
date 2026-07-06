# Quickstart & Validation Guide: Tooltips en Filtros Avanzados

## Requisitos Previos
- Entorno local de Reflex configurado y dependencias instaladas.
- Aplicación de Inmobiliaria Velar corriendo localmente.

## Ejecución Local
1. Iniciar la aplicación en modo desarrollo:
   ```bash
   reflex run --env dev
   ```

2. Abrir el navegador en `http://localhost:3000`.

## Pasos de Validación

### 1. Validación de Presencia (Desktop)
- Navega a los distintos módulos (ej. Dashboard, Personas, Contratos, etc.).
- Ubica la sección de "Filtros Avanzados".
- Pasa el cursor (`hover`) por encima de cada botón.
- **Resultado Esperado:** Aparece un tooltip en la parte superior del botón. El texto es breve y está redactado en infinitivo (ej. "Limpiar filtros", "Aplicar búsqueda").

### 2. Validación de Accesibilidad (Teclado)
- Usa la tecla `Tab` para navegar por la interfaz hasta hacer foco en uno de los botones de "Filtros Avanzados".
- **Resultado Esperado:** El tooltip aparece igual que en el caso del hover, indicando la acción correspondiente.

### 3. Validación de Z-Index / Pointer Events
- Abre modales o elementos adyacentes si es posible, y verifica que el tooltip no quede escondido detrás de modales, asegurando que respeta el `Z_TOOLTIP=1100`.
- Verifica que el tooltip no impida hacer click en el propio botón (pointer-events correcto).

### 4. Validación Responsiva / Táctil (Móvil)
- Abre las herramientas de desarrollo del navegador (DevTools) y selecciona el modo de vista de dispositivo móvil.
- Refresca la página.
- Haz clic (simulando un tap) en los botones de "Filtros Avanzados".
- **Resultado Esperado:** El tooltip NO debe aparecer y el botón debe reaccionar de manera inmediata a la acción, manteniendo la UI limpia.

# Quickstart: Validación de Tooltips

Este documento describe cómo verificar que la corrección de los tooltips faltantes ha sido exitosa.

## 1. Prerrequisitos

Tener el entorno local levantado y funcionando con Reflex.

## 2. Iniciar el Servidor

Ejecuta el servidor de Reflex en modo desarrollo:
```bash
reflex run --env dev
```

## 3. Verificación de QA (Pasos Manuales)

1. Ingresa a la URL local (usualmente `http://localhost:3000`).
2. Navega por las diferentes páginas de la aplicación prestando especial atención a:
   - Botones tipo ícono (sin texto) como: exportación, edición, eliminación, actualizar, o limpiar filtros.
   - Botones ubicados en encabezados de tabla o ventanas modales.
3. Posiciona el cursor (`hover`) sobre cada uno de estos botones.
4. **Resultado esperado**: Debe aparecer un tooltip de manera inmediata en la parte superior del botón, con el texto en formato infinitivo (ej. "Editar registro"), sin quedar oculto por otros elementos gracias al `Z_TOOLTIP=1100`.
5. Inspecciona la vista en un emulador de dispositivo móvil (DevTools).
6. **Resultado esperado**: Los tooltips no deben aparecer al realizar `tap` sobre los botones, asegurando la usabilidad táctil.

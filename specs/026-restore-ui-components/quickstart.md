# Quickstart & Validation Guide

## 1. Prerequisites
- Entorno virtual de Python activo (`.venv`).
- Instancias locales de PostgreSQL configuradas en caso de correr el dev mode.

## 2. Validation Steps
1. Compilar y exportar el frontend localmente en modo producción para validar la sintaxis:
```bash
$env:DATABASE_URL="sqlite:///test.db"; reflex export --frontend-only --no-zip
```
(El comando debe finalizar en 100% exitosamente sin errores `AttributeError` o sintaxis React).

2. Correr la aplicación de Reflex en entorno de desarrollo:
```bash
reflex run --env dev
```

3. **Verificación Visual**:
   - Abrir el navegador en `http://localhost:3000`.
   - Navegar a la página `/personas` (Personas) y verificar que los inputs tienen el layout correcto de "Etiquetas Flotantes" al hacer focus.
   - Pasar el cursor sobre el botón de crear (ej. icono "+") y validar que un tooltip descriptivo (ej. "Crear persona") aparece por encima del resto del contenido UI, sin recortes.
   - Repetir la validación visual en el módulo de Contratos (`/contratos`) y Liquidaciones (`/liquidaciones`).

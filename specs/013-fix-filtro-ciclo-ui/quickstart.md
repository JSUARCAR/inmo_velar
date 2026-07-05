# Quickstart & Validation Guide

Esta guía describe cómo verificar la correcta resolución del bug del filtro por "Ciclo Operativo" y la adaptación responsiva de la UI.

## Prerequisites
- La base de datos PostgreSQL debe estar inicializada con la tabla de `Propiedades` y `Liquidaciones` (debe haber datos de prueba).
- Reflex instalado y entorno virtual activo.

## Setup
1. Iniciar la aplicación en modo desarrollo:
   ```bash
   reflex run --env dev
   ```
2. Abrir el navegador en la URL `http://localhost:3000`.

## Validation Scenarios

### Scenario 1: Validación del Filtro SQL (Backend)
1. Iniciar sesión y navegar al módulo de **Liquidaciones**.
2. En la barra de filtros avanzados (parte superior), localizar el desplegable de **Ciclo**.
3. Seleccionar un ciclo específico (ej. "Ciclo 1").
4. **Expected Outcome**: La tabla de liquidaciones se actualiza reflejando solo las filas correspondientes. En la consola (terminal) NO debe aparecer ningún error de PostgreSQL (`column prop.grupo_operativo does not exist`).
5. Limpiar el filtro devolviéndolo a estado vacío y comprobar que cargan todos los registros nuevamente.

### Scenario 2: Validación Visual Responsiva (Frontend)
1. Estando en la vista de **Liquidaciones** (pantalla completa / desktop).
2. Inspeccionar que los filtros en la barra superior (Búsqueda, Período, Estado, Ciclo, Asesor) tienen espacios regulares y no se superponen.
3. Utilizar las herramientas de desarrollador del navegador (F12) para simular la vista de un dispositivo móvil (ej. iPhone 12, anchura ~390px).
4. **Expected Outcome**: Cada control (input o select) se colapsa de manera ordenada (usualmente 1 filtro por fila o distribuidos proporcionalmente) conservando el 100% de su ancho contenedor sin que los botones ni los inputs se encimen.

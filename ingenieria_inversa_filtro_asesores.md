# Reporte de Ingeniería Inversa: Error en el Filtro de Asesores (Módulo Liquidaciones)

## 1. Identificación del Problema
El selector de **Asesores** en los filtros avanzados del módulo de **Liquidaciones** (Propietarios) no se carga con los nombres de los asesores activos, mostrando únicamente la opción por defecto ("Todos") o permaneciendo vacío.

## 2. Análisis del Código Fuente (Reverse Engineering)

### A. Ubicación del Fallo en el Estado (Frontend)
El error se localiza en el archivo `src/presentacion_reflex/state/liquidaciones_state.py`. 

Dentro del manejador de eventos `load_filter_options` (alrededor de la línea 189), se observa el siguiente patrón de ejecución:

```python
# Bloque de actualización de estado para otros filtros
async with self:
    self.periodos_options = ["Todos"] + periodos
    # ... otras actualizaciones ...
    self.propietarios_select_options = propietarios_select

# LLAMADA AL ERROR (Línea 189 aprox.)
LiquidacionesState.load_asesores_options()
```

### B. Causas Raíz del Error Técnico

1.  **Llamada a Nivel de Clase (TypeError):**
    El método `load_asesores_options` está definido como un método de instancia (`def load_asesores_options(self):`). Al llamarlo como `LiquidacionesState.load_asesores_options()` (usando el nombre de la clase), se produce un error de Python: `TypeError: load_asesores_options() missing 1 required positional argument: 'self'`. Esto detiene la ejecución del hilo de fondo antes de que se realice la consulta a la base de datos.

2.  **Mutación de Estado fuera del Lock (Reflex Error):**
    `load_filter_options` es un evento de fondo (`background=True`). En Reflex, cualquier actualización de variables de estado dentro de estos eventos DEBE ocurrir dentro de un bloque `async with self:`. El método `load_asesores_options` intenta actualizar `self.asesores_select_options` directamente y de forma síncrona, lo cual es incompatible con el flujo de trabajo de Reflex para tareas asíncronas de fondo.

3.  **Falta de Decorador de Evento:**
    A diferencia de `load_filter_options` o `load_liquidaciones`, el método `load_asesores_options` no está decorado con `@rx.event`. Aunque esto no es estrictamente necesario para un método auxiliar, su invocación incorrecta impide que Reflex maneje el ciclo de vida del estado.

4.  **Inconsistencia en la Lógica de Filtrado (SQL):**
    La consulta SQL actual en `load_asesores_options` es:
    ```sql
    SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
    FROM ASESORES a 
    JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
    WHERE p.ESTADO_REGISTRO = 1
    ORDER BY p.NOMBRE_COMPLETO
    ```
    Solo valida el estado de la persona (`p.ESTADO_REGISTRO = 1`), pero no el estado del rol de asesor (`a.ESTADO = 1`). Esto podría causar que aparezcan personas que ya no cumplen funciones de asesor en la inmobiliaria.

## 3. Recomendación de Solución

Para corregir el fallo sin alterar la arquitectura, se recomienda:
1.  **Convertir a Asíncrono:** Cambiar la definición a `async def load_asesores_options(self)`.
2.  **Asegurar el Lock:** Envolver la actualización de la lista en un bloque `async with self:`.
3.  **Corregir Invocación:** Llamar al método usando `await self.load_asesores_options()` dentro de `load_filter_options`.
4.  **Refinar SQL:** Añadir la condición `AND a.ESTADO = 1` para garantizar la integridad de los datos mostrados.

---
**Elaborado por:** Gemini CLI (Ingeniería Inversa)
**Fecha:** 23 de marzo de 2026
**Proyecto:** Inmobiliaria Velar

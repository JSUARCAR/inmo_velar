# Análisis de Ingeniería Inversa: Filtros por Asesor en Liquidaciones

## Objetivo
El requerimiento establece integrar un filtro avanzado por asesor en la vista de Liquidaciones de Propietarios, tanto en su "Vista Individual" como en la "Vista Agrupada" (Por Propietario). Esto implica hacer que los datos reaccionen en función del asesor comercial asociado a la propiedad o al contrato.

---

## 1. Identificación de Componentes en Interfaz y Estado
El módulo en Reflex emplea dos archivos principales:
1. **Vista (`src/presentacion_reflex/pages/liquidaciones.py`)**: Aquí se renderiza la UI. La barra de herramientas se encuentra en la función `liquidaciones_toolbar()`. Actualmente existen filtros por **Búsqueda**, **Período** y **Estado**.
2. **Estado (`src/presentacion_reflex/state/liquidaciones_state.py`)**: El controlador central maneja variables como `filter_periodo` y `filter_estado`. Tiene implementadas variables base que no se están usando visualmente para otros filtros como `filter_propietario_id` y `filter_propiedad_id`. **Carece** completamente de un parámetro `filter_asesor_id`.

Para añadir el filtro en la UI se requiere:
- Declarar variables de estado: `filter_asesor_id: str = "Todos"` y listas `asesores_options: List[Dict]`, `asesores_select_options: List[str]`.
- En `load_filter_options`, hacer un `SELECT` a `ASESORES` y `PERSONAS` para popular las opciones del Select.
- Añadir el componente UI `rx.select` (o equivalente en tu UI kit como `neuro_select_root`) en `liquidaciones_toolbar` que conecte a un nuevo mutador `set_filter_asesor`.

---

## 2. Ingeniería de Orquestación (Servicio de Aplicación)
El archivo `src/aplicacion/servicios/servicio_financiero.py` funciona como capa intermedia entre el frontend y el repositorio de base de datos. 

Tiene dos métodos clave para las vistas:
1. **`listar_liquidaciones_paginado`** (Vista Individual)
2. **`listar_liquidaciones_propietarios_paginado`** (Vista Agrupada)

Ambos métodos actualmente reciben parámetros de filtro opcionales (`estado`, `periodo`, `busqueda`), pero **no** reciben un parámetro `asesor` o `id_asesor`.

Para integrar el filtro se deberá:
- Modificar la firma de los métodos en `ServicioFinanciero` para aceptar un nuevo parámetro de dominio `id_asesor: Optional[int] = None`.
- Pasar este parámetro en los llamados a los métodos subyacentes de la capa de persistencia (`repo_liquidacion.listar_paginado`, `repo_liquidacion.contar_con_filtros`, y las versiones de agrupadas).

---

## 3. Ingeniería del Repositorio de Datos (Persistencia SQLite/PostgreSQL)
El núcleo de la filtración está en el archivo `src/infraestructura/persistencia/repositorio_liquidacion_sqlite.py` (y su equivalente en postgres si lo hay). 
Para lograr que la base de datos filtre por asesor, es crucial entender el modelo relacional actual.

Las tablas base de los queries para listar liquidaciones son:
```sql
FROM LIQUIDACIONES l
JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
```

El modelo Entidad-Relación de Velar indica que el asesor comercial NO está vinculado directamente a la liquidación, sino que está vinculado al contrato que la generó a través de la columna `ID_ASESOR` en la tabla `CONTRATOS_MANDATOS`.

### Cambios a realizar en el Repositorio

Se deben intervenir 4 métodos:
1. `contar_con_filtros`
2. `listar_paginado`
3. Método subyacente para validaciones de `contar_agrupadas...` (si existe lógica de validación).
4. `listar_agrupadas_por_propietario_paginado`

**Acción Requerida en SQL:**
Para todos estos métodos, se debe agregar el argumento `id_asesor: Optional[int] = None`. Si se recibe un `id_asesor` numérico válido, se debe añadir de manera dinámica al arreglo de `conditions` (cláusula WHERE) la siguiente regla vinculando la tabla `cm` (Contratos Mandatos):

```python
if id_asesor:
    # Usar el placeholder de la DB (? o %s según aplique)
    conditions.append(f"cm.ID_ASESOR = {placeholder}")
    query_params.append(id_asesor)
```

En la vista agrupada (`listar_agrupadas_por_propietario_paginado`), el conteo total para la paginación dinámica ya se realiza en la misma consulta a través de una función de ventana u subquery. Añadir esta condición dinámica al bloque `WHERE` afectará correctamente a los agregados (`SUM`, `COUNT`) y asegurará que el propietario solo consolide lo correspondiente al asesor filtrado.

---

## 4. Plan Táctico de Ejecución (Paso a Paso Inverso / Bottom-Up)

Para implementar esta funcionalidad sin afectar la integridad de las liquidaciones de los clientes, el flujo de desarrollo será Bottom-Up:

**Fase 1: Capa de Infraestructura (DB) - El Motor**
1. En `repositorio_liquidacion_sqlite.py`: Añadir el argumento `id_asesor: Optional[int] = None` a `contar_con_filtros`, `listar_paginado`, y `listar_agrupadas_por_propietario_paginado`.
2. Inyectar la condición SQL `cm.ID_ASESOR = {placeholder}` a `conditions` y agregar la variable a `query_params` si el parámetro no es `None` o "Todos".

**Fase 2: Capa de Aplicación (Servicios) - El Orquestador**
3. En `servicio_financiero.py`: Actualizar las firmas de `listar_liquidaciones_paginado` y `listar_liquidaciones_propietarios_paginado` para aceptar `id_asesor`.
4. Transmitir el parámetro recibido hacia los métodos del repositorio intervenidos en la Fase 1.

**Fase 3: Capa de Presentación (Estado Reflex) - El Controlador**
5. En `liquidaciones_state.py`: Declarar las variables de estado UI (`filter_asesor_id`, listas dinámicas de opciones `asesores_options` y `asesores_select_options`).
6. Modificar el bloque `load_filter_options` para ejecutar un query que obtenga la lista de Asesores activos cruzando `ASESORES` con `PERSONAS` para obtener sus nombres, e inyectarlos a las opciones del combobox.
7. Añadir la función mutadora `set_filter_asesor(self, value: str)`.
8. Modificar la función principal `load_liquidaciones` para leer el valor en memoria de `self.filter_asesor_id` (pasarlo a `int` extrayéndolo del ID si el select contiene nombre-id) y enviarlo en el argumento `id_asesor=` de las llamadas al servicio financiero.

**Fase 4: Capa UI (Componentes Reflex) - La Interfaz**
9. En `liquidaciones.py`: En el método `liquidaciones_toolbar()`, agregar el control visual nativo `neuro_select_root` iterando sobre las opciones de `LiquidacionesState.asesores_select_options` y enganchando su evento `on_change` al método `set_filter_asesor`.

---
*Este análisis representa la arquitectura actual extraída rigurosamente y expone la hoja de ruta técnica precisa para inyectar un nuevo flujo de filtrado integral (Full-Stack) manteniendo los principios de Clean Architecture del proyecto inmobiliario Velar.*
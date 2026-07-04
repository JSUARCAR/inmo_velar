# Diseño: Generación de Paz y Salvo para Contratos Inactivos

## Contexto
Actualmente, el documento de Paz y Salvo sólo se genera de manera automática durante la transición de estado cuando un contrato es finalizado. No existe una acción en la interfaz para regenerar o generar este documento una vez el contrato está en estado inactivo.

## Objetivo
Implementar un botón "Generar Paz y Salvo" en el módulo de Contratos que permita su ejecución manual para aquellos contratos (Mandato o Arrendamiento) cuyo estado sea distinto a `ACTIVO`.

## Arquitectura y Componentes
1. **Interfaz (UI):**
   - Modificación de `src/presentacion_reflex/components/contratos/tarjeta_contrato.py` para incluir el botón de acción en la vista de cuadrícula.
   - Modificación de `src/presentacion_reflex/pages/contratos.py` para incluir el botón en la columna de acciones de la vista tabular.

2. **Propiedades Visuales del Botón:**
   - **Icono:** `shield-check` o similar que denote certificación/seguridad.
   - **Color (Color Scheme):** `"teal"` o una tonalidad que contraste adecuadamente con las otras opciones y respete el diseño Elite.
   - **Tooltip:** "Generar Paz y Salvo".

3. **Lógica de Negocio y Data Flow:**
   - **Condición de Visibilidad:** El componente sólo se renderizará si el contrato cumple con `estado_contrato != "ACTIVO"`.
   - **Manejador de Eventos (On Click):** Invocar al método existente `PDFState.generar_certificado_paz_y_salvo(contrato_id, beneficiario_nombre)`.
   - **Paso de Parámetros Dinámico:** El nombre del beneficiario se resolverá evaluando dinámicamente en el frontend usando `rx.cond`. Si es Mandato, será el nombre del propietario; si es Arrendamiento, será el del arrendatario.

4. **Reglas de Seguridad y Control de Acceso:**
   - El botón podrá visualizarse sin necesidad de permisos adicionales de escritura, o dependerá de la visualización base del contrato (`AuthState.check_action("Contratos", "VER")` si aplica).

## Conclusión
Este diseño evita duplicar lógica en el backend y maximiza el reúso de las funciones de Reflex y los servicios de generación de PDF ya definidos, asegurando un mantenimiento limpio y conforme a los lineamientos del manifiesto.

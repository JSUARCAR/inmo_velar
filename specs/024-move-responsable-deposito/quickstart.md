# Quickstart & Validation Guide: move-responsable-deposito

## Prerequisites
1. Base de datos local inicializada (`test.db` o servidor PostgreSQL configurado en `DATABASE_URL`).
2. Migración SQL aplicada manualmente a la base de datos (según [data-model.md](./data-model.md)).

## Validación 1: Contrato de Mandato
1. Inicia el servidor `reflex run`.
2. Ve al módulo **Contratos** en la UI.
3. Haz clic en "Nuevo Contrato" y selecciona **Mandato**.
4. Desplázate a la sección final del formulario ("Recepción e Inventario" o similar).
5. **Verifica:** El campo "Responsable del Depósito" NO debe aparecer.
6. Completa un formulario de prueba y guarda.
7. **Verifica:** La creación debe ser exitosa y sin errores de base de datos.
8. Edita el contrato de mandato recién creado.
9. **Verifica:** El campo sigue sin aparecer y la edición guarda correctamente sin fallos.

## Validación 2: Contrato de Arrendamiento
1. Estando en el módulo **Contratos**, haz clic en "Nuevo Contrato" y selecciona **Arrendamiento**.
2. Desplázate al final del formulario.
3. **Verifica:** Debe aparecer un campo (ComboBox) para "Responsable del Depósito".
4. Abre el campo.
5. **Verifica:** Deben listar los Asesores Activos del sistema.
6. Selecciona un asesor, llena el resto del formulario y guárdalo.
7. **Verifica:** El contrato se crea exitosamente.
8. Busca el contrato recién creado y presiona "Ver Detalles" (el ojo).
9. **Verifica:** El modal de detalles debe mostrar al Asesor Responsable del Depósito.
10. Edita el contrato.
11. **Verifica:** El ComboBox del responsable debe aparecer pre-seleccionado con el asesor que elegiste previamente.

## Validación 3: Ausencia de Responsable
1. Crea otro Contrato de Arrendamiento, pero deja el "Responsable del Depósito" en blanco.
2. Guarda el contrato.
3. **Verifica:** El sistema guarda sin arrojar errores (campo es verdaderamente opcional).

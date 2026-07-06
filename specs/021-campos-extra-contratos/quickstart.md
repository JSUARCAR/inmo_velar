# Quickstart Validation: campos-extra-contratos

## Prerrequisitos
1. Asegúrate de tener tu archivo `.env` configurado con la conexión a PostgreSQL local. No se debe usar `sqlite`.
2. Activar el entorno virtual: `.\.venv\Scripts\Activate.ps1`.

## Ejecución Local
1. Ejecuta el servidor Reflex en modo desarrollo:
   ```bash
   reflex run --env dev
   ```

## Escenarios de Validación (UI)

1. **Creación de Contrato de Mandato**
   - Inicia sesión y ve a la vista de Contratos de Mandato.
   - Haz clic en crear un nuevo contrato.
   - Observa que existen dos campos nuevos: "Enlace de video" y "Responsable del depósito".
   - En el campo "Enlace de video", ingresa `https://www.youtube.com/watch?v=ejemplo`.
   - En el selector de "Responsable", elige un asesor de la lista.
   - Guarda el contrato y verifica que en el listado general los datos persisten.

2. **Edición de Contrato de Mandato**
   - Abre el contrato recién creado.
   - El enlace y el responsable deben aparecer pre-cargados.
   - Cambia el enlace a otro valor válido o borralo, y guarda. Verifica la persistencia.

3. **Creación/Edición de Contrato de Arrendamiento**
   - Repite el mismo flujo en la vista de Contratos de Arrendamiento, asegurando que el campo "Enlace de video" se guarde y recupere correctamente (aquí no hay selector de responsable).

4. **Reglas Limite**
   - Intenta ingresar un texto sin formato HTTP en el campo de enlace de video (ej: `holamundo`); el formulario debería mostrar un error de validación o ser rechazado.

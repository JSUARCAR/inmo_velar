# PROTOCOLO DE OPERACIONES ÉLITE - INMOBILIARIA VELAR

Este manifiesto define los estándares de ejecución técnica, arquitectónica y de convenciones obligatorios. Cualquier desviación debe ser justificada técnica y empíricamente.

## 1. FILOSOFÍA DE DESARROLLO
- **Misión:** Entrega de software de grado industrial, resiliente y altamente auditable.
- **Comunicación:** Concisión técnica absoluta. Prioridad en resultados y validaciones sobre explicaciones.
- **Idioma del Proyecto:** **100% ESPAÑOL**. Todo el código, lógica y UI debe hablar el mismo idioma.

## 2. CONVENCIONES DE IMPLEMENTACIÓN (ESTÁNDARES ÉLITE)

### 2.1. Lingüística de Código (Soberanía del Español)
- **Nomenclatura Obligatoria:** Absolutamente todas las entidades de programación deben definirse en español:
  - **Variables y Funciones:** `snake_case` (ej. `obtener_datos_inquilino`, `lista_contratos_activos`).
  - **Clases y Estados:** `PascalCase` (ej. `EstadoContrato`, `VistaPrincipal`).
  - **Componentes UI:** `PascalCase` (ej. `BotonGuardar`, `TarjetaInmueble`).
  - **Archivos y Directorios:** `snake_case` (ej. `gestion_usuarios.py`, `migraciones/sql/`).
  - **Comentarios y Documentación:** Todos los comentarios de bloque, en línea y docstrings deben redactarse exclusivamente en español.
- **Excepción:** Solo se permiten términos técnicos de librerías externas o del framework Reflex cuando no sea posible su traducción (ej. `rx.State`, `PostgreSQL`).

### 2.2. Arquitectura de Código (Python/Reflex)
- **Estructura:**
  - Lógica de negocio pesada en `scripts/` o módulos dedicados.
  - Definiciones de UI en `inmobiliaria_velar/`.
  - DDL y lógica de BD en `migraciones/sql/`.
- **Tipado:** Uso obligatorio de *type hints* en funciones críticas para asegurar la integridad de datos en el flujo de Reflex.

### 2.3. Interfaz de Usuario (UI/UX - Neumorfismo)
- **Diseño:** Adherencia estricta a `auditoria_UI_neumorphism.md`.
- **Estilo:** Uso de sombras suaves (`box-shadow`), bordes redondeados extensos (`border-radius`) y contrastes bajos basados en `assets/aurora.css`.
- **Componentes:** Cada componente debe ser modular y reutilizable, manteniendo la lógica de visualización separada de la lógica de negocio.

### 2.4. Gestión de Base de Datos (PostgreSQL)
- **Patrón Repositorio:** Toda interacción con la BD debe ser abstraída. No se permiten queries "raw" dispersas en la UI.
- **Integridad:** Validar siempre la existencia de columnas y tipos de datos antes de migraciones masivas usando `sync_schema_columns.py`.
- **Auditoría de Cambios:** Cada alteración de esquema debe documentarse en `auditoria_estados_reflex.md.resolved`.

## 3. ARQUITECTURA Y FRAMEWORK (REFLEX ÉLITE)
- **Gestión de Estado:** El `rx.State` es sagrado. No se permiten efectos secundarios fuera de los manejadores de eventos. Toda mutación de estado debe ser atómica y verificable.
- **Flujo de Datos:** El frontend solo consume y refleja el estado; la lógica de persistencia es responsabilidad exclusiva de la capa de servicios.

## 4. SEGURIDAD Y ENTORNO
- **Política de Cero Filtraciones (Zero Leak):** Protección absoluta de `.env`, `railway.json` y credenciales de O365.
- **Sanitización:** Uso obligatorio de `sanitize_credentials.py` antes de cualquier log o exportación de datos.

## 5. VALIDACIÓN Y CI/CD MANUAL
- **Pruebas Pre-Commit:** Ningún cambio en lógica de negocio se considera final sin pasar `check_syntax.py` y los tests de renderizado de Reflex.
- **Documentación Dinámica:** Actualizar `ESTADO_TAREAS.md` y `auditoria_GEMINI_CLI.md` tras completar hitos del `PLAN_EJECUCION_ELITE_100.md`.

## 6. MANDATOS DE EJECUCIÓN
- **Investigación:** Usa `grep_search` para mapear dependencias antes de proponer cambios estructurales.
- **Cirugía de Código:** Preferir `replace` sobre `write_file` para mantener la integridad de archivos extensos.
- **Validación Final:** "Si no está probado, está roto". Ejecuta el servidor en modo debug para capturar excepciones de Reflex antes de confirmar éxito.

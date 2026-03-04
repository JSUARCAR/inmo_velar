# PROTOCOLO DE OPERACIONES ÉLITE - INMOBILIARIA VELAR

Este manifiesto define los estándares de ejecución técnica, arquitectónica y de convenciones obligatorios. Cualquier desviación debe ser justificada técnica y empíricamente.

## 1. FILOSOFÍA DE DESARROLLO (ESTADO FINAL)
- **Misión:** Entrega de software de grado industrial, resiliente y 100% basado en la nube (Railway/PostgreSQL).
- **Consolidación Tecnológica:** El proyecto ha migrado de Flet/SQLite a **Reflex/PostgreSQL**. Se prohíbe cualquier referencia activa a Flet o SQLite en lógica de negocio o infraestructura nueva.
- **Comunicación:** Concisión técnica absoluta. Prioridad en resultados y validaciones sobre explicaciones.
- **Idioma del Proyecto:** **100% ESPAÑOL**. Todo el código, lógica y UI debe hablar el mismo idioma.

## 2. CONVENCIONES DE IMPLEMENTACIÓN (ESTÁNDARES ÉLITE)

### 2.1. Lingüística de Código (Soberanía del Español)
- **Nomenclatura Obligatoria:** Absolutamente todas las entidades de programación deben definirse en español:
  - **Variables y Funciones:** `snake_case` (ej. `obtener_datos_inquilino`).
  - **Clases y Estados:** `PascalCase` (ej. `EstadoContrato`).
  - **Componentes UI:** `PascalCase` (ej. `BotonGuardar`).
  - **Archivos y Directorios:** `snake_case` (ej. `gestion_usuarios.py`).
- **Excepción:** Solo términos técnicos de librerías (ej. `rx.State`, `psycopg2`).

### 2.2. Arquitectura de Código (Clean Architecture Elite)
- **Estructura Obligatoria:**
  - **Dominio (`src/dominio/`):** Entidades y lógica pura. No debe importar NADA de otras capas.
  - **Aplicación (`src/aplicacion/`):** Servicios de orquestación. No debe tocar la base de datos directamente.
  - **Infraestructura (`src/infraestructura/`):** 
    - **Persistencia:** Repositorios agnósticos. **PROHIBIDO** el sufijo `_sqlite.py`. Todos deben renombrarse a `repositorio_[entidad].py`.
  - **Presentación (`src/presentacion_reflex/`):** Vistas y estado de Reflex.
- **Tipado:** Uso obligatorio de *type hints* (`typing`) en todas las capas.

### 2.3. Ingeniería de Datos (PostgreSQL Native)
- **Soberanía de PostgreSQL:**
  - **INSERT:** Obligatorio usar `INSERT INTO ... RETURNING id`. Prohibido el uso de `lastrowid` o `get_last_insert_id()`.
  - **Placeholders:** Usar ÚNICAMENTE `%s`. Prohibido el uso de `?`.
  - **Tipos de Datos:** Validar tipos booleanos (`True/False`) y fechas (`ISO 8601`) antes de la persistencia. PostgreSQL es estricto; SQLite no lo era.
- **Abstracción:** Toda consulta SQL debe residir en la capa de persistencia. Prohibido "SQL in-line" en vistas o servicios.

### 2.4. Gestión de Estado (Reflex Elite)
- **Centralización:** El `rx.State` es la única fuente de verdad. Las mutaciones deben ser atómicas y verificables.
- **Rendimiento:** Minimizar las variables de estado redundantes. Usar `@rx.var` (computed properties) para datos derivados.
- **Validación de UI:** Cada componente de entrada debe tener validación de tipo en el backend (State) antes de procesarse.

## 3. HIGIENE Y SEGURIDAD (PROTOCOLO ZERO LEAK)
- **Cero Filtraciones:** Protección absoluta de `.env`, `railway.json` y credenciales de O365.
- **Higiene de Raíz:** El directorio raíz NO es un vertedero. 
  - Scripts de diagnóstico (`debug_*.py`, `repro_*.py`, `check_*.py`) deben moverse a `scripts/diagnostico/` o eliminarse tras su uso.
  - Los archivos `.txt` informativos deben ser consolidados en `docs/`.
- **Sanitización:** Uso obligatorio de `sanitize_credentials.py` antes de cualquier log o exportación de datos.

## 4. VALIDACIÓN Y CALIDAD (CI/CD MANUAL)
- **Pruebas Pre-Commit:** Ningún cambio en lógica de negocio se considera final sin pasar `check_syntax.py` y los tests de renderizado de Reflex.
- **Integridad de Reportes:** Los generadores de PDF deben validar la existencia de assets (logos, fuentes) y datos mínimos antes de iniciar el renderizado para evitar fallos silenciosos.
- **Documentación Dinámica:** Mantener `ESTADO_TAREAS.md` y `auditoria_GEMINI_CLI.md` actualizados tras completar cada hito.

## 5. MANDATOS DE EJECUCIÓN (CIRUGÍA TÉCNICA)
- **Investigación:** Usa `grep_search` para mapear dependencias antes de proponer cambios estructurales.
- **Cirugía de Código:** Preferir `replace` sobre `write_file` para mantener la integridad de archivos extensos.
- **Validación Final:** "Si no está probado, está roto". Ejecuta el servidor en modo debug para capturar excepciones de Reflex antes de confirmar éxito.

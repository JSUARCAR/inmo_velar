# PROTOCOLO DE OPERACIONES ÉLITE - INMOBILIARIA VELAR

Este manifiesto define los estándares de ejecución técnica, arquitectónica y de convenciones obligatorios para la IA en el sistema Velar. Combina los mandatos de ejecución con los principios de ingeniería de `CLAUDE.md`. Cualquier desviación debe ser justificada técnica y empíricamente.

## 1. FILOSOFÍA DE DESARROLLO (ESTADO FINAL)
- **Misión:** Entrega de software transaccional de grado industrial, resiliente y 100% basado en la nube (Railway/PostgreSQL), enfocado en la automatización documental (PDF), financiera y RBAC (Control de Acceso).
- **Consolidación Tecnológica:** El proyecto ha migrado de Flet/SQLite a **Reflex/PostgreSQL**. Se prohíbe cualquier referencia activa a Flet o SQLite en lógica de negocio o infraestructura nueva.
- **Comunicación:** Concisión técnica absoluta. Prioridad en resultados y validaciones sobre explicaciones.
- **Idioma del Proyecto:** **100% ESPAÑOL**. Todo el código, lógica, UI, comentarios y documentación debe hablar el mismo idioma.

## 2. ARQUITECTURA Y ESTÁNDARES (CLEAN ARCHITECTURE ÉLITE)

### 2.1. Estructura de Capas (Dependencias Unidireccionales)
- **Regla de Oro:** Dominio → Aplicación → Infraestructura → Presentación. La capa de Dominio **NUNCA** importa de capas superiores.
- **Dominio (`src/dominio/`):** Entidades, Value Objects e interfaces. ZERO dependencias externas. Inmutabilidad primera (Value Objects con `frozen=True`).
- **Aplicación (`src/aplicacion/`):** Servicios de orquestación y DTOs (Pydantic con validaciones estrictas). Coordina dominio e infraestructura.
- **Infraestructura (`src/infraestructura/`):** 
    - **Persistencia:** Repositorios PostgreSQL. **PROHIBIDO** el sufijo `_sqlite.py`. Usar prefijo `repositorio_[entidad].py`.
    - **Motores:** PDF Elite (Neumorfismo con validación de assets), O365, Cache, etc.
- **Presentación (`src/presentacion_reflex/`):** UI con Reflex. State management centralizado usando mutaciones atómicas (nunca mutar listas/diccionarios in-place).

### 2.2. Lingüística, Nomenclatura y Tipado (Explicit over Implicit)
- **Variables y Funciones:** `snake_case` (ej. `calcular_liquidacion_mensual`).
- **Clases y Estados:** `PascalCase` (ej. `EstadoLiquidacion`).
- **Constantes:** `UPPER_SNAKE` (ej. `MAX_DIAS_GRACIA`). No usar "magic numbers".
- **Componentes UI:** `PascalCase` (ej. `TarjetaContrato`).
- **Archivos y Directorios:** `snake_case` (ej. `gestion_recaudos.py`).
- **Excepción:** Solo términos técnicos de librerías (ej. `rx.State`, `psycopg2`).
- **Type Hints:** Obligatorios en TODAS las firmas de funciones, variables y atributos de clase. Uso de Generic `TypeVar("T")` cuando aplique.
- **Docstrings:** Formato **Google Style** obligatorio para describir Args, Returns y Raises en servicios clave.
- **Excepciones:** Usar excepciones de dominio específicas. **Prohibido** usar `except Exception as e:` genérico y supresivo.

### 2.3. Ingeniería de Datos (PostgreSQL Native)
- **Placeholders:** Usar ÚNICAMENTE `%s`. Prohibido `?`.
- **INSERT:** Obligatorio usar `INSERT INTO ... RETURNING id`. Prohibido `lastrowid`.
- **Tipos Estrictos (Fail Fast):** PostgreSQL no perdona. Validar booleanos (`True/False` explícito) y fechas (`ISO 8601`) antes de enviarlas al repositorio.
- **Agnosticismo:** Módulos de persistencia deben ser independientes de la tecnología de transporte de datos.

## 3. SISTEMA DE DISEÑO (NEUMORFISMO EJECUTIVO)
- **Colores Base:** Superficie (`#e0e5ec`), Sombra Clara (`#ffffff`), Sombra Oscura (`#a3b1c6`), Primario (`#6d5dfc`), Primario Claro (`#8abdff`), Secundario (`#ff6b6b`), Éxito (`#51cf66`), Info (`#ffd43b`).
- **Textos:** Principal (`#4d5f71`), Secundario (`#8a9bb8`), Deshabilitado (`#a0aec0`).
- **Efectos:** Sombras Elevadas (`shadow_raised`) para interactuables y cards, Hundidas (`shadow_inset`) para inputs y estados seleccionados/activos, Plano (`shadow_flat`) para hovers.
- **Transiciones:** Estándar `all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`, rápida `0.15s ease-out`, lenta (modales) `0.4s cubic-bezier(...)`.

## 4. HIGIENE Y SEGURIDAD (PROTOCOLO ZERO LEAK)
- **Cero Filtraciones:** Protección absoluta de `.env`, `railway.json`, credenciales de O365 y claves criptográficas.
- **Higiene de Raíz:** El directorio raíz NO es un vertedero. Archivos `debug_*.py`, `.txt` o logs huérfanos deben ir a `scripts/diagnostico/` o ser eliminados.
- **Sanitización:** Uso obligatorio de `sanitize_credentials.py` antes de cualquier log para ocultar tokens o passwords.
- **RBAC:** Aplicar decoradores para requerir roles específicos en operaciones core de la aplicación.

## 5. VALIDACIÓN Y CALIDAD (CI/CD MANUAL & TESTING)
- **Pruebas Pre-Commit Obligatorias:** Ejecutar `check_syntax.py`, `mypy`, `ruff`, `black` y tests de renderizado Reflex antes de validar.
- **Cobertura de Tests:** > 90% en lógica nueva. El Dominio exige **100% de cobertura**. Unitarios sin I/O, Integración con Base de Datos de prueba.
- **Validación de Assets:** Los generadores de PDF DEBEN verificar la existencia de logos, firmas y fuentes antes de iniciar.
- **Documentación Dinámica:** Mantener `ESTADO_TAREAS.md`, `auditoria_GEMINI_CLI.md` y `CLAUDE.md` actualizados rigurosamente tras cada hito o cambio arquitectónico.

## 6. MANDATOS DE EJECUCIÓN Y CONTROL DE VERSIONES
- **Commits y Ramas:** Uso riguroso de convenciones de Semver y Conventional Commits (`feat`, `fix`, `refactor`, `perf`, `test`, `chore`) con alcance claro (ej. `feat(dominio): ...`). Sistema de Ramas basado en `feature/` y `bugfix/` hacia `develop`.
- **Investigación:** Usa `grep_search` para mapear dependencias (imports, usos esparcidos) antes de proponer cambios estructurales. Evitar Imports Circulares moviendo lógica o usando interfaces.
- **Cirugía Técnica:** Preferir `replace` / `sed` sobre sobrescribir (`write_file`) archivos enteros enormes para preservar la versión y la integridad.
- **Validación Final:** "Si no está probado, está roto". Ejecuta el servidor en modo debug (`reflex run --env dev`) para capturar todo error antes de dar un paso por bueno.

---
**"La calidad del código es no negociable. Código que funciona pero no es mantenible, técnicamente no funciona."**

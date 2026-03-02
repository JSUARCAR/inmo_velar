# 🚀 PLAN DE EJECUCIÓN ÉLITE: OPERACIÓN "ZERO DEBT" (100/100)

Este documento detalla el diagnóstico de auditoría y la hoja de ruta técnica para transformar el sistema **inmo_velar** en una plataforma de grado empresarial, segura y escalable.

---

## 🔍 RESULTADOS DE LA AUDITORÍA TÉCNICA (SITUACIÓN ACTUAL)

El sistema ha sido evaluado bajo un estándar de arquitectura empresarial, arrojando un **Score de Salud: 45/100**. Se identificaron los siguientes hallazgos críticos:

### 🔴 HALLAZGOS CRÍTICOS (Nivel de Riesgo: Extremo)
1.  **Seguridad - Bypass de RBAC:** Ausencia de validación de permisos en los *event handlers* del backend. El sistema confía en la UI y hardcodea usuarios como `"admin"`.
2.  **Seguridad - Sesiones Vulnerables:** El `session_token` se transmite con el flag `secure=False`, permitiendo la interceptación en redes no cifradas.

### 🟠 HALLAZGOS ALTOS (Nivel de Riesgo: Elevado)
3.  **Arquitectura - God Classes:** El repositorio de liquidaciones y los estados de Reflex presentan un tamaño excesivo (>50KB) mezclando lógica de negocio, SQL y presentación.
4.  **Calidad - Exposición de Secretos:** Presencia de más de 20 scripts de depuración en la raíz con contraseñas hardcodeadas (`7323`) expuestas en el historial de Git.

### 🟡 HALLAZGOS MEDIOS (Nivel de Riesgo: Moderado)
5.  **Rendimiento - Bloqueos de Event Loop:** Uso de I/O síncrono para operaciones pesadas de base de datos, lo que degrada la experiencia de usuario bajo carga.

---

## 🎯 OBJETIVOS DEL PLAN 100/100
1.  **Seguridad:** RBAC inquebrantable, hardening de sesiones y erradicación de secretos.
2.  **Arquitectura:** Clean Architecture real, CQRS y desacoplamiento total.
3.  **Calidad:** Cobertura de pruebas >85%, tipado estático estricto y CI/CD automatizado.
4.  **Rendimiento:** Concurrencia asíncrona y procesamiento en segundo plano (workers).
5.  **Observabilidad:** Logging estructurado y auditoría financiera inmutable.

---

## 📅 CRONOGRAMA DE IMPLEMENTACIÓN

### FASE 1: SEGURIDAD CRÍTICA Y LIMPIEZA TÓXICA (Días 1-15)
*Objetivo: Cerrar vectores de ataque y limpiar el repositorio.*

| ID | Tarea Técnica | Mitiga Hallazgo | DoD |
| :--- | :--- | :--- | :--- |
| **1.1** | **RBAC en Backend (Server-Side)** | Hallazgo 1 | Validación de permisos en cada `rx.event`. Eliminación de `"admin"` hardcodeado. |
| **1.2** | **Hardening de Cookies de Sesión** | Hallazgo 2 | Configurar `session_token` con `secure=True` y `httponly=True`. |
| **1.3** | **Sanitización de Git History** | Hallazgo 4 | Limpieza de secretos del historial usando `git-filter-repo`. |
| **1.4** | **CLI de Gestión (manage.py)** | Hallazgo 4 | Centralizar mantenimiento en CLI y eliminar scripts `debug_*.py`. |

### FASE 2: REFACTORIZACIÓN "CLEAN CORE" (Días 16-40)
*Objetivo: Desacoplamiento y estandarización del acceso a datos.*

| ID | Tarea Técnica | Mitiga Hallazgo | DoD |
| :--- | :--- | :--- | :--- |
| **2.1** | **CQRS en Repositorios** | Hallazgo 3 | División en modelos de Escritura (Commands) y Lectura (Queries). |
| **2.2** | **Migraciones con Alembic** | Hallazgo 3 | Eliminación de `CREATE TABLE` del código; gestión vía migraciones SQL. |
| **2.3** | **SQLAlchemy 2.0 Async** | Hallazgo 1, 5 | Prevención de inyección SQL y soporte para I/O asíncrono. |
| **2.4** | **Inyección de Dependencias** | Hallazgo 3 | Desacoplamiento total entre capas (State -> Service -> Repo). |

### FASE 3: PERFORMANCE Y CONCURRENCIA (Días 41-60)
*Objetivo: UX fluida y procesamiento offload.*

| ID | Tarea Técnica | Mitiga Hallazgo | DoD |
| :--- | :--- | :--- | :--- |
| **3.1** | **Refactor Asíncrono (Reflex)** | Hallazgo 5 | 100% de I/O del State convertido a `async/await`. |
| **3.2** | **Background Workers (Celery)** | Hallazgo 5 | Procesamiento de PDFs y cálculos pesados fuera del hilo principal. |
| **3.3** | **Caché de Catálogos (Redis)** | Hallazgo 5 | Reducción de latencia en carga de selectores y configuraciones. |

### FASE 4: INGENIERÍA DE CALIDAD (Días 61-80)
*Objetivo: Automatización del estándar de excelencia.*

| ID | Tarea Técnica | Objetivo |
| :--- | :--- | :--- |
| **4.1** | **Testing Unitario Core** | Cobertura >85% en lógica financiera con `Pytest`. |
| **4.2** | **Pipeline CI (GitHub Actions)** | Linter, Tipado, Seguridad y Pruebas automatizadas en cada PR. |
| **4.3** | **Pruebas E2E (Playwright)** | Validación automatizada de flujos críticos de negocio. |

### FASE 5: OBSERVABILIDAD Y SRE (Días 81-100)
*Objetivo: Trazabilidad y auditoría de grado bancario.*

| ID | Tarea Técnica | Objetivo |
| :--- | :--- | :--- |
| **5.1** | **Logging Estructurado (JSON)** | Trazabilidad de transacciones mediante `request_id` y `trace_id`. |
| **5.2** | **Auditoría Financiera Inmutable** | Triggers en base de datos para versionado automático de registros. |
| **5.3** | **APM e Instrumentación** | Monitoreo en tiempo real de errores y performance vía Sentry. |

---

## 📈 KPIs DE ÉXITO (Métricas Finales)
- **Vulnerabilidades:** 0 reportadas por herramientas de SAST.
- **Deuda Técnica:** 0 archivos con más de 500 líneas (SRP estricto).
- **Latencia UI (P95):** < 300ms en operaciones estándar.
- **Score de Salud Final:** 100/100.

---
**Firmado:**
*Senior Software Architect & Security Auditor*

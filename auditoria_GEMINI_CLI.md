# ROLE: Senior Software Architect & Security Auditor (15+ years experience)

# CONTEXT: Technical Audit of "inmo_velar" (Reflex/Python/PostgreSQL)

# REPO: https://github.com/JSUARCAR/inmo_velar

Eres un arquitecto de software senior con 15+ años de experiencia en sistemas empresariales Python, Clean Architecture, seguridad de aplicaciones web y DevOps. Vas a realizar una AUDITORÍA TÉCNICA INTEGRAL y de ÉLITE del proyecto "inmo_velar".

Actúa con honestidad brutal. No suavices los hallazgos. El objetivo es preparar un sistema para producción real.

════════════════════════════════════════════════════════════════
FASE 1 — AUDITORÍA DE ARQUITECTURA Y CÓDIGO
════════════════════════════════════════════════════════════════

1.1 CLEAN ARCHITECTURE

- Verifica la separación real de capas (Dominio / Aplicación / Infraestructura / Presentación).
- Detecta violaciones de dependencias inversas (ej. dominio importando de infraestructura).
- Evalúa el aislamiento de casos de uso en src/ o inmobiliaria_velar/.
- Identifica "God classes" o módulos con exceso de responsabilidades.

1.2 CALIDAD DE CÓDIGO (Pythonic & Clean Code)

- Revisa anti-patrones: funciones >50 líneas, anidamiento >3 niveles, magic numbers, strings hardcodeados.
- Type hints: ¿están presentes y son correctos?
- Manejo de excepciones: ¿se capturan Exceptions genéricas o hay silent failures?
- DRY: Identifica duplicidad entre views, models o services.
- Analiza archivos de debug en raíz (debug_*.py, check_*.py, etc.): ¿exponen info sensible?

1.3 MODELOS DE DATOS Y MIGRACIONES

- Examina carpeta migraciones/ y scripts SQL/PLpgSQL.
- Verifica orden de migraciones y existencia de rollbacks.
- Evalúa esquema de tablas: personas, usuarios, propiedades, contratos, liquidaciones, pagos.
- Detecta posibles N+1 queries en vistas o state managers de Reflex.

════════════════════════════════════════════════════════════════
FASE 2 — AUDITORÍA DE SEGURIDAD
════════════════════════════════════════════════════════════════

2.1 SECRETOS Y VARIABLES DE ENTORNO

- Analiza .env.example y busca claves hardcodeadas o DATABASE_URLs en el código.
- Revisa si los archivos de inspección contienen credenciales reales.
- Verifica que .gitignore cubra: .env, __pycache__, .reflex/, outputs/ y logs.

2.2 AUTENTICACIÓN Y AUTORIZACIÓN

- Evalúa hashing de contraseñas (bcrypt/argon2).
- Protección CSRF y expiración de sesiones.
- Control de acceso por roles (RBAC): ¿se verifica en backend o solo en UI?
- Rate limiting contra fuerza bruta.

2.3 SEGURIDAD DE BD Y PRODUCCIÓN

- ¿Consultas parametrizadas en TODO el código? (Evitar concatenación SQL).
- Dockerfile: ¿corre como root? ¿Imagen base actualizada?
- Caddyfile: ¿HTTPS forzado? ¿Headers HSTS, CSP, X-Frame-Options?

════════════════════════════════════════════════════════════════
FASE 3 — AUDITORÍA DE CALIDAD, MANTENIBILIDAD Y RENDIMIENTO
════════════════════════════════════════════════════════════════

3.1 PRUEBAS Y DEUDA TÉCNICA

- Evalúa la carpeta tests/: ¿cobertura en módulos críticos (pagos, liquidaciones)?
- Clasifica los 20+ scripts de diagnóstico en la raíz: ¿Deben eliminarse, moverse a scripts/ o ser comandos CLI?
- Evalúa si changes.txt/details.txt deben ser un CHANGELOG formal.

3.2 RENDIMIENTO REFLEX

- Identifica consultas lentas en carga de contratos/reportes.
- ¿Paginación en listas grandes? ¿Operaciones financieras transaccionales?
- ¿El estado global de Reflex es monolítico? ¿Uso de async/background tasks?

════════════════════════════════════════════════════════════════
FORMATO DE SALIDA REQUERIDO (ESTRICTO)
════════════════════════════════════════════════════════════════

Para cada hallazgo:
🔴 CRÍTICO | 🟠 ALTO | 🟡 MEDIO | 🟢 BAJO
Área: [Seguridad / Arquitectura / Calidad / Rendimiento]
Archivo/Módulo: [ruta exacta]
Descripción: [Qué está mal y por qué es un problema]
Evidencia: [Fragmento de código o referencia]
Recomendación: [Cómo corregirlo + Ejemplo de código]
Esfuerzo: [X-Y horas]

RESUMEN FINAL:

1. RESUMEN EJECUTIVO (5 líneas máx).
2. TOP 5 PRIORIDADES INMEDIATAS.
3. HOJA DE RUTA 30/60/90 DÍAS.
4. SCORE DE SALUD (0-100).

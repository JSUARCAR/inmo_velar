# Tareas de Implementación: Investigacion de Error 404 en Descarga de PDF

**Estado**: Draft
**Plan**: [plan.md](./plan.md)
**Especificación**: [spec.md](./spec.md)

## Estrategia de Implementación

**Alcance del MVP (Fase 3)**:
Implementar la corrección principal de los imports en las dependencias y la configuración CORS, incluyendo las medidas críticas de seguridad (Path Traversal, Rate Limiting) para restaurar la descarga en el módulo de Contratos.

**Oportunidades de Paralelización**:
- La configuración de CORS y Rate Limiting puede desarrollarse en paralelo a la corrección de imports, aunque convergen en el mismo módulo.
- La creación de la suite de pruebas (Fase 5) puede iniciarse en paralelo definiendo los tests HTTP con resultados esperados de fallo (TDD) antes de aplicar las correcciones finales.

---

## Fase 1: Configuración (Setup)
*(Configuración compartida e inicialización)*

- [x] T001 Auditar el estado actual de `src/presentacion_reflex/api/deps.py` y `pdf_download_api.py` para confirmar las líneas exactas a modificar.
- [x] T002 Verificar que las variables de entorno necesarias (ej. `FRONTEND_URL`) estén declaradas en la configuración base del proyecto o en el `.env` local para el uso estricto de CORS.

---

## Fase 2: Tareas Fundamentales (Foundational)
*(Prerrequisitos bloqueantes)*

- [x] T003 Actualizar las sentencias de importación en `src/presentacion_reflex/api/deps.py` para apuntar correctamente a `src.infraestructura.persistencia.repositorio_sesion` y `src.infraestructura.persistencia.repositorio_usuario`.
- [x] T004 Envolver el montaje del router de PDF (`target_app.mount("/api/pdf", ...)`) en un bloque `try...except` con un logger explícito de nivel `CRITICAL` para registrar fallos silenciosos durante el arranque en `src/presentacion_reflex/api/pdf_download_api.py`.

---

## Fase 3: [US1] Resolución del Error 404 en Contratos y Seguridad Base
**Objetivo de la Historia**: Restaurar la descarga de PDFs con seguridad y sin errores 404.
**Criterio de Prueba Independiente**: Descargar exitosamente un PDF válido de contrato y recibir un HTTP 200, bloqueando peticiones maliciosas (path traversal).

- [x] T005 [P] [US1] Actualizar el `CORSMiddleware` en `src/presentacion_reflex/api/pdf_download_api.py` para establecer `allow_credentials=True` y restringir `allow_origins` explícitamente a producción y `http://localhost:3000`.
- [x] T006 [P] [US1] Implementar validación estricta contra Path Traversal en el endpoint de descarga usando `pathlib.Path.resolve().is_relative_to(BASE_DIR)`, y garantizar la correcta **decodificación (URL-decode)** del nombre de archivo para soportar caracteres especiales.
- [x] T007 [P] [US1] Implementar un mecanismo de Rate Limiting estricto por usuario (ej. máximo 10 descargas por minuto) en el endpoint para prevenir abusos (DoS).
- [x] T008 [US1] Asegurar que si la validación del middleware falla (cookie `_s` ausente o inválida), el endpoint retorne explícitamente un error `HTTP 401 Unauthorized`.
- [x] T009 [US1] Asegurar que si el archivo físico ya no existe (True 404), el endpoint retorne explícitamente `HTTP 404 Not Found`, y ante cualquier fallo interno inesperado emita un JSON de error estructurado (`HTTP 500`).

---

## Fase 4: [US2] Validación Transversal de Consumidores de PDF
**Objetivo de la Historia**: Garantizar que la solución implementada para los contratos no afecte la generación en otros módulos.
**Criterio de Prueba Independiente**: Consumir el endpoint `/api/pdf/download/...` de manera transversal sin regresiones.

- [x] T010 [US2] Revisar y documentar/validar que las rutas de descarga en módulos paralelos (Estados de Cuenta, Liquidaciones) se resuelvan correctamente y sean coherentes con la nueva configuración de dependencias de `src/presentacion_reflex/api/deps.py`.

---

## Fase 5: [US3] Cobertura de Pruebas y Trazabilidad
**Objetivo de la Historia**: Asegurar pruebas automatizadas que certifiquen el flujo de PDF y eviten regresiones.
**Criterio de Prueba Independiente**: La suite de pruebas debe pasar al 100% evaluando HTTP 200, 401, 404, 429 y cabeceras estrictas.

- [x] T011 [P] [US3] Escribir prueba de integración en `tests/integracion/api/test_pdf_download_api.py` (o equivalente) que valide un HTTP 200 exitoso con las cabeceras `Content-Type='application/pdf'` y `Content-Disposition='attachment'`, y que el archivo contiene el nombre decodificado correctamente.
- [x] T012 [US3] Escribir pruebas para validar fallos esperados: `401 Unauthorized` por falta de cookie, `429 Too Many Requests` por límite excedido, y `404 Not Found` por archivo físico inexistente.
- [x] T013 [US3] Escribir prueba de seguridad que intente una descarga con Path Traversal y valide el rechazo seguro.

---

## Fase 6: Pulido y Transversal (Polish)
*(Limpieza final)*

- [x] T014 Revisar todo el código modificado para asegurar el cumplimiento estricto del estándar de tipado, naming conventions en español, y remover logs o código muerto.
- [x] T015 Ejecutar `check_syntax.py`, `mypy`, `ruff`, y `black` localmente antes de dar por finalizada la tarea.
- [x] T016 Generar un documento final (ej. `docs/resolucion_404_pdf.md` o dentro del mismo Issue) detallando la arquitectura analizada, la causa raíz encontrada (imports) y la solución implementada, para cumplir con la trazabilidad exigida en el requerimiento FR-006.

## Dependencias
- **Fase 2** depende de **Fase 1**.
- **Fase 3** depende de **Fase 2**.
- **Fase 4** y **Fase 5** dependen de **Fase 3**.
- **Fase 6** depende de todas las fases anteriores.

# Contrato — Inventario enmascarado y evidencia

**Versión**: 1.0 · **Fecha**: 2026-09-14 · **Referencias**: FR-016, FR-020, FR-021, SC-001, SC-002, SC-008

## Propósito

Definir la estructura y las reglas del documento versionado que sirve como fuente única de verificación de la remediación, sin reimprimir valores reales.

## Ubicación

`docs/security/INVENTARIO_REMEDIACION_074.md` (proyecto-relative), en español.

## Estructura mínima

1. **Resumen**: alcance, fecha, responsable de seguridad, estado global (pendiente/en curso/cerrado).
2. **Hallazgos** (`H-01`…`H-03`): tipo, sistemas afectados, estado (`pendiente`/`rotada`/`eliminada`), fecha de rotación y responsable. Sin valores.
3. **Ubicaciones** (`U-###`): ruta, líneas, categoría (`código`, `script_diagnóstico`, `prueba`, `documentación`, `informe`, `historial`, `canal_externo`) y estado de limpieza/purga.
4. **Artefactos con PII**: rutas retiradas, tipo de dato y destino de conservación (si aplica).
5. **Evidencia** (`E-###`): fecha, responsable, tipo (`rotación`, `búsqueda_árbol`, `búsqueda_historial`, `escaneo`, `limpieza_canal`, `re_clonado`, `revisión_accesos`, `bloqueo_prueba`) y resultado verificable.
6. **Estado de criterios de éxito**: SC-001…SC-011 con resultado y referencia de evidencia.

## Reglas de enmascaramiento

- Los valores comprometidos **no se reproducen** en ninguna forma (ni completos, ni fragmentados, ni patrones reversibles).
- Cada valor se identifica únicamente por su hallazgo (`H-01`, etc.).
- Los ejemplos de configuración usan marcadores (`••••••`) o nombres de variables.
- El documento debe pasar el escaneo Gitleaks (no puede contener literales ni fragmentos significativos).

## Reglas de contenido

| Regla | Descripción |
|---|---|
| IDs únicos | `H-##`, `U-###`, `E-###` sin reutilización |
| Cobertura | Todo hallazgo tiene ≥ 1 ubicación y ≥ 1 evidencia de rotación |
| Trazabilidad | Ubicaciones y evidencias referencian su hallazgo; los SC referencian evidencias |
| Actualización | Se actualiza al completar cada verificación (misma operación que genera la evidencia) |
| Fuente de verdad | Es la base de las búsquedas de "cero ocurrencias"; el informe de auditoría es solo origen histórico |

## Verificación del contrato

- Un escaneo sobre el documento devuelve cero coincidencias.
- Una revisión manual confirma que ninguna celda contiene valores reales.
- Las búsquedas de verificación (`git grep`, escaneo de historial) se registran como `E-###` con resultado "0 coincidencias".

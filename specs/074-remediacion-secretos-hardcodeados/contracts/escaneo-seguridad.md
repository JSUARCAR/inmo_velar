# Contrato — Gate de escaneo de secretos (`.github/workflows/security-scan.yml`)

**Versión**: 1.0 · **Fecha**: 2026-09-14 · **Referencias**: FR-013, FR-014, FR-019, SC-005, SC-010

## Propósito

Definir el comportamiento observable del gate de seguridad que impide que credenciales entren o permanezcan en el repositorio. Es un contrato de CI: qué se ejecuta, con qué configuración, qué bloquea y qué evidencia produce.

## Entradas

| Entrada | Origen | Obligatoria | Regla |
|---|---|---|---|
| Eventos | `push` a `main`/`develop` y `pull_request` a `main` | Sí | El gate no admite omisión (FR-013) |
| Configuración base | `.gitleaks.toml` versionado | Sí | Solo patrones de riesgo generalizados; sin literales (FR-003) |
| Denylista exacta | Secreto de repositorio `GITLEAKS_KNOWN_LEAKS_REGEX` | Sí | Alternancia regex de los valores comprometidos; jamás versionada |
| Configuración final | Compuesta en `$RUNNER_TEMP/gitleaks-protegido.toml` | Sí | Base + regla `inmo-velar-known-leaked-literals`; archivo efímero |
| Historial | Checkout con `fetch-depth: 0` | Sí | Permite escanear el historial completo |

## Salidas

| Salida | Formato | Regla |
|---|---|---|
| Resultado del job | Estado `success`/`failure` | `failure` ante hallazgo o indisponibilidad (FR-014/FR-019) |
| Check requerido | `security-scan` en la protección de la rama | Ninguna fusión sin `success` (FR-014) |
| Evidencia | Entrada `E-###` con fecha, responsable y resultado | El fallo y su causa se registran (FR-019/FR-016) |

## Comportamiento

1. **Composición protegida**: un paso previo exige que `GITLEAKS_KNOWN_LEAKS_REGEX` exista y no esté vacío; si falta, el job **falla de inmediato** con mensaje explícito (fail-closed). Luego escribe la configuración final en `$RUNNER_TEMP` combinando `.gitleaks.toml` + la regla exacta.
2. **Escaneo**: el escaneo usa la configuración final mediante `GITLEAKS_CONFIG` (precedencia de Gitleaks: `--config` → `GITLEAKS_CONFIG` → `GITLEAKS_CONFIG_TOML` → `.gitleaks.toml` → default).
3. **Detección**: cualquier coincidencia produce salida distinta de cero y, por tanto, `failure` del job.
4. **Bloqueo**: al ser check requerido, la fusión queda impedida hasta un escaneo exitoso.
5. **Indisponibilidad**: si el escáner no puede ejecutarse (runner, red o error de configuración), el job permanece en `failure`; no existe modo de continuación ni excepción de urgencia.
6. **Falsos positivos**: solo se resuelven con entradas acotadas en la allowlist de la configuración, justificadas y revisadas por el responsable de seguridad; **nunca** aplican a los valores comprometidos. No se admite desactivar reglas.
7. **Allowlists prohibidas**: queda prohibido excluir del escaneo el informe de auditoría o la propia configuración para ocultar literales.

## Invariantes

- Ningún literal comprometido existe en archivos versionados, incluida la configuración (FR-003).
- La denylista exacta solo reside en configuración protegida y en la configuración efímera del runner.
- El gate es determinista: mismo contenido, mismo resultado.

## Errores y mensajes

| Condición | Comportamiento esperado |
|---|---|
| Secreto ausente/vacío | Falla el paso de composición: `[ERROR DE SEGURIDAD] Falta GITLEAKS_KNOWN_LEAKS_REGEX; no se puede verificar la denylista.` |
| Hallazgo | Job `failure`; reporte sin valores (redactado) como evidencia |
| Escáner no disponible | Job `failure`; se registra causa y se reintenta en la siguiente ejecución |

## Fuera de alcance

- Herramienta concreta distinta de la ya adoptada (se mantiene `gitleaks/gitleaks-action@v2`).
- Escaneo programado adicional a push/PR (decisión diferida, no exigida por la spec).

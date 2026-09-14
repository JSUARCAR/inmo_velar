# Contrato — Configuración externa de credenciales

**Versión**: 1.0 · **Fecha**: 2026-09-14 · **Referencias**: FR-002, FR-004, FR-005, FR-006

## Propósito

Definir los únicos mecanismos y nombres admitidos para obtener credenciales, y el comportamiento de fallo cuando no están configuradas. Ningún componente puede usar valores por defecto para credenciales.

## Mecanismos admitidos

- Variables de entorno del proceso (incluidas las inyectadas por la plataforma de despliegue).
- Gestor de secretos que las exponga como variables de entorno al proceso.

Prohibido: archivos versionados con valores, defaults literales en código, valores en documentación real.

## Variables

| Variable | Consumidor(es) | Obligatoria | Validación | Default |
|---|---|---|---|---|
| `DATABASE_URL` | `rxconfig.py`, app | En producción | DSN válido, esquema `postgresql://` o `postgres://` | Ninguno |
| `DB_HOST` | `config/shared_db_config.py`, `migraciones/**` | En local/scripts sin DSN | No vacía | `localhost` (no es credencial) |
| `DB_PORT` | ídem | No | Entero 1–65535 | `5432` |
| `DB_NAME` | ídem | No | No vacía | `db_inmo_velar` |
| `DB_USER` | ídem | No | No vacía | `inmo_user` |
| `DB_PASSWORD` | ídem | Sí cuando no hay `DATABASE_URL` | No vacía; **sin default** | Prohibido |
| `PLAYWRIGHT_TEST_USER` | `tests/e2e/**` | En e2e | No vacía | Prohibido |
| `PLAYWRIGHT_TEST_PASSWORD` | `tests/e2e/**` | En e2e | No vacía; **sin default** | Prohibido |
| `PLAYWRIGHT_ADMIN_USER` | `tests/**`, `scripts/diagnostico/**` | Solo scripts administrativos | No vacía | Prohibido |
| `PLAYWRIGHT_ADMIN_PASSWORD` | `tests/**`, `scripts/diagnostico/**` | Solo scripts administrativos | No vacía; **sin default** | Prohibido |
| `API_URL` | `rxconfig.py` | No | URL (`http`/`https`) | Permitido (no es credencial) |

> Nota: los valores de ejemplo se referencian por nombre de variable; el contrato no reproduce literales reales.

## Comportamiento de fallo (fail-fast)

1. Al consumir una credencial ausente o vacía, el componente MUST terminar o abortar de inmediato.
2. El mensaje MUST indicar la variable faltante y el componente, sin imprimir el valor esperado ni valores de otras variables.
3. Formato de referencia: `[ERROR DE CONFIGURACIÓN] Falta la variable <NOMBRE> requerida por <componente>. Configure el entorno y reintente.`
4. Se prohíben reintentos con supuestos, defaults vacíos silenciosos y registros que expongan valores.

## Invariantes

- `os.getenv("<CREDENCIAL>", "<literal>")` está prohibido en todo el repositorio.
- La documentación operativa describe las variables requeridas por nombre y muestra ejemplos enmascarados (`PLAYWRIGHT_TEST_PASSWORD=••••••`).
- Los tests usan señuelos sintéticos o valores inyectados por entorno; nunca credenciales reales.

## Verificación

- Prueba unitaria de los validadores de `Settings` (variable ausente ⇒ aborta con mensaje esperado).
- Ejecución de un script consumidor sin variables ⇒ error explícito y salida distinta de cero.
- Escaneo Gitleaks ⇒ cero hallazgos de fallback literal.

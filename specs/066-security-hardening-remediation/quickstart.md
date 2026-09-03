# Quickstart: Validación de Remediación de Seguridad

**Feature**: 066-security-hardening-remediation
**Propósito**: Guía de validación end-to-end para confirmar que cada control de seguridad funciona.

---

## Prerequisitos

- `curl` disponible en la terminal
- `gitleaks` instalado (`pip install gitleaks` o binario en PATH)
- `git filter-repo` instalado (`pip install git-filter-repo`)
- Acceso a Railway Dashboard (para verificar variables y logs)
- URL de producción: `https://inmovelar-production.up.railway.app`

---

## Escenario 1 — SC-001: Cero Credenciales en Repositorio

**Valida**: FR-006, FR-007

```bash
# Clonar el repositorio post-purga
git clone https://github.com/JSUARCAR/inmo_velar.git /tmp/inmo_velar_test
cd /tmp/inmo_velar_test

# Verificar que archivos purgados no existen en árbol de trabajo
ls check_db.py 2>&1                       # Debe: "No such file or directory"
ls check_db_id.py 2>&1                    # Debe: "No such file or directory"
ls .playwright-mcp/ 2>&1                  # Debe: "No such file or directory"
ls migraciones/esquemas/ 2>&1             # Debe: "No such file or directory"

# Verificar que no aparecen en el historial
git log --all --full-history -- check_db.py   # Debe: (sin output)
git log --all --full-history -- "migraciones/run_migration_ipc.py"  # Debe: (sin output)

# Escaneo de secretos en historial completo
gitleaks detect --source . --no-git
```

**Resultado esperado**: Cero archivos encontrados. `gitleaks` reporta: `No leaks found`

---

## Escenario 2 — SC-002: Endpoints sin Sesión Retornan HTTP 401

**Valida**: FR-004, FR-005

```bash
BASE="https://inmovelar-production.up.railway.app"

# Sin cookie — debe retornar 401 en todos los endpoints
curl -s -o /dev/null -w "%{http_code}" "$BASE/api/documentos/list/contrato/1"
# Esperado: 401

curl -s -o /dev/null -w "%{http_code}" "$BASE/api/documentos/download/1"
# Esperado: 401

curl -s -o /dev/null -w "%{http_code}" "$BASE/api/storage/1/download"
# Esperado: 401

curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/documentos/upload/contrato/1" \
     -F "file=@/tmp/test.txt"
# Esperado: 401
```

**Resultado esperado**: Todos los endpoints retornan `401`.

---

## Escenario 3 — SC-003: Cabeceras HTTP de Seguridad en Producción

**Valida**: FR-010

```bash
BASE="https://inmovelar-production.up.railway.app"

curl -sI "$BASE/" | grep -iE "strict-transport|x-frame|x-content-type|referrer-policy|server"
```

**Resultado esperado**:
```
strict-transport-security: max-age=31536000; includeSubDomains
x-frame-options: DENY
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
# "server:" NO debe aparecer o no debe revelar versión
```

También verificar en [securityheaders.com](https://securityheaders.com/?q=https://inmovelar-production.up.railway.app): calificación **A o superior**.

---

## Escenario 4 — SC-004: Contenedor Ejecuta como No-Root

**Valida**: FR-013

```bash
# Si tienes acceso al contenedor via Railway shell o imagen local:
docker run --rm <imagen_tag> whoami
# Esperado: appuser

docker run --rm <imagen_tag> id
# Esperado: uid=1001(appuser) gid=1001(appgroup)
```

---

## Escenario 5 — SC-007: Fail-Fast si SECRET_KEY No Configurada

**Valida**: FR-008

```bash
# En entorno local, sin SECRET_KEY:
cd /ruta/al/proyecto
SECRET_KEY="" DATABASE_URL="postgresql://..." python -c "from src.infraestructura.configuracion.settings import obtener_configuracion; obtener_configuracion()"
# Esperado: Proceso termina con sys.exit(1) y mensaje de error en stderr:
# [ERROR FATAL DE CONFIGURACIÓN]
# CRÍTICO: SECRET_KEY no configurada o usa valor inseguro...

# Con valor inseguro:
SECRET_KEY="CHANGE_ME_IN_PRODUCTION" DATABASE_URL="postgresql://..." python -c "..."
# Esperado: mismo error fatal
```

---

## Escenario 6 — SC-006: Sesiones Expiran a las 8 Horas (Absoluto)

**Valida**: FR-015

```bash
# Test de integración (requiere acceso a BD de test):
# 1. Crear sesión con fecha_fin = hace 1 segundo
# 2. Intentar validar el token
# 3. Verificar que lanza SesionInvalida

# En código de test:
# sesion = SesionUsuario(
#     id_usuario=1,
#     fecha_inicio=(datetime.now() - timedelta(hours=9)).isoformat(),
#     fecha_fin=(datetime.now() - timedelta(seconds=1)).isoformat(),
#     token_sesion="test_token",
# )
# assert not sesion.esta_activa()  # Debe ser False

# Validar que esta_activa() verifica fecha_fin contra datetime.now()
python -c "
from datetime import datetime, timedelta
from src.dominio.entidades.sesion_usuario import SesionUsuario
sesion = SesionUsuario(
    id_usuario=1,
    fecha_inicio=(datetime.now() - timedelta(hours=9)).isoformat(),
    fecha_fin=(datetime.now() - timedelta(seconds=1)).isoformat(),
    token_sesion='test_token',
    activa=True
)
print('esta_activa:', sesion.esta_activa())  # Debe imprimir: False
"
```

---

## Escenario 7 — SC-008: Repositorio Limpio Post-Purga

**Valida**: FR-007

```bash
git clone https://github.com/JSUARCAR/inmo_velar.git /tmp/clean_test
cd /tmp/clean_test

# Verificar directorios sensibles ausentes
[ -d ".playwright-mcp" ] && echo "FAIL: .playwright-mcp existe" || echo "OK: .playwright-mcp ausente"
[ -d "migraciones/esquemas" ] && echo "FAIL: migraciones/esquemas existe" || echo "OK: esquemas ausente"
[ -d "outputs" ] && echo "FAIL: outputs existe" || echo "OK: outputs ausente"
```

**Resultado esperado**: Los 3 verifica imprimen `OK`.

---

## Escenario 8 — Rate Limiting (Caddy caddy-ratelimit)

**Valida**: FR-010

```bash
BASE="https://inmovelar-production.up.railway.app"

# Enviar 6 peticiones POST rápidas al endpoint de autenticación
for i in $(seq 1 6); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/_event/auth_state.login" \
    -H "Content-Type: application/json" \
    -d '{"payload": {"nombre_usuario": "test", "password": "wrong"}}')
  echo "Intento $i: HTTP $STATUS"
done
# Esperado: primeros 5 intentos con HTTP 400/401/200; intento 6: HTTP 429
```

---

## Checklist de Verificación Final

| SC | Descripción | Comando de verificación | Estado |
|----|-------------|------------------------|--------|
| SC-001 | Cero credenciales en repo | `gitleaks detect --source .` | ⬜ |
| SC-002 | 401 en endpoints sin sesión | `curl` sin cookie | ⬜ |
| SC-003 | Cabeceras HTTP en prod | `curl -I` + securityheaders.com | ⬜ |
| SC-004 | Contenedor no-root | `docker run whoami` | ⬜ |
| SC-005 | pip-audit sin CVEs | `pip-audit -r requirements.txt` | ⬜ |
| SC-006 | Sesiones expiran a 8h | Test unitario `esta_activa()` | ⬜ |
| SC-007 | Fail-fast SECRET_KEY | Test de arranque sin variable | ⬜ |
| SC-008 | Repo limpio post-purga | Verificar directorios ausentes | ⬜ |
| SC-009 | Madurez ≥7.5/10 | Re-auditoría en 30 días | ⬜ |
| SC-010 | Cero accesos no-auth en logs | Revisar Railway logs 30 días | ⬜ |

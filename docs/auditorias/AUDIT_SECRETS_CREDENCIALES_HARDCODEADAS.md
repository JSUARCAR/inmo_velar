# Auditoría de Seguridad — Credenciales Hardcodeadas en `inmo_velar`

**Fecha**: 2026-09-08
**Repositorio**: https://github.com/JSUARCAR/inmo_velar
**Commit auditado (HEAD)**: `d20f78d2` — 2026-09-03 — "correccion(api): resolver error 404 en descarga de pdf y blindar endpoint"
**Método**: Clonado completo del repositorio, escaneo de patrones de credenciales (contraseñas, DSNs, API keys de proveedores conocidos), revisión manual de configuración, CI/CD, `.gitignore`, historial de `git log` e inspección de artefactos versionados (CSV, PDF, SQLite).
**Alcance de esta auditoría**: exclusivamente claves/contraseñas hardcodeadas y exposición de información sensible. No cubre inyección SQL, XSS, control de acceso ni lógica de negocio (ver `AUDIT_REPORT.md` / `specs/066-security-hardening-remediation/` para esos ejes).

---

## Resumen Ejecutivo

| # | Hallazgo | Severidad | Archivos afectados | Vigente en HEAD |
|---|---|---|---|---|
| 1 | Credenciales admin `admin/admin0123` hardcodeadas, una referencia apunta directo a la URL de producción | 🔴 Crítico | 10 | ✅ Sí |
| 2 | Password de PostgreSQL `7323` hardcodeada como fallback y documentada en texto plano | 🟠 Alto | ~40 | ✅ Sí |
| 3 | Credenciales de test de la app `jsuarcar/velarjoan2026` hardcodeadas | 🟡 Medio | 11 | ✅ Sí |
| 4 | PII real (nombres, cédulas, teléfonos, correos, contratos, estados de cuenta) versionada en `assets/` | 🟡 Medio | 18 | ✅ Sí |
| 5 | Gitleaks (CI ya configurado) no detecta ninguno de los 4 hallazgos anteriores | ℹ️ Informativo | — | — |

**Conclusión principal**: existe un intento previo de remediación (`specs/066-security-hardening-remediation/`, tarea `T008` marcada `[X]`) que corrigió **un solo archivo** (`rxconfig.py` de la raíz), pero dejó sin tocar ~39 archivos adicionales que replican exactamente el mismo patrón, además de las credenciales de producción y de test. El riesgo real hoy es equivalente a no haber remediado nada, porque las mismas contraseñas siguen públicas en decenas de ubicaciones y, lo más grave, en historial de commits desde el **2026-05-25**.

---

## 1. 🔴 CRÍTICO — Credenciales de administrador apuntando a producción

**Credencial expuesta**: usuario `admin`, contraseña `admin0123`.

| Archivo | Línea(s) | Detalle |
|---|---|---|
| `scripts/diagnostico/test_login_produccion.py` | 16, 22, 25 | Navega a `https://inmovelar-production.up.railway.app/login` y rellena el formulario con `admin` / `admin0123` |
| `scripts/diagnostico/auditoria_reportes.py` | 13 | `PASSWORD = "admin0123"` |
| `scripts/diagnostico/auditoria_simple.py` | 12 | `PASSWORD = "admin0123"` |
| `scripts/diagnostico/auditoria_detallada.py` | 14 | `PASSWORD = "admin0123"` |
| `scripts/diagnostico/auditoria_recaudos_check.py` | 12 | `PASSWORD = "admin0123"` |
| `tests/test_dashboard_row4.py` | 44, 69 | Login hardcodeado en test Playwright |
| `tests/test_playwright_liquidacion_asesores.py` | 38 | Login hardcodeado en test Playwright |
| `tests/test_playwright_filtro_asesores.py` | 32 | Login hardcodeado en test Playwright |
| `test_login_visible.mjs` | 26 | Login hardcodeado en test JS (Node/Playwright) |
| `docs/superpowers/plans/2026-07-02-incident-liquidation-sync.md` | 16 | Documentado literalmente: *"Login: admin / admin0123"* |

### Por qué es crítico
`test_login_produccion.py` no es un script de ejemplo: contiene la **URL real de producción** más la credencial de administrador en texto plano, en un repositorio público. Cualquier persona con acceso de lectura al repo tiene acceso administrativo potencial al sistema en producción sin necesidad de ningún otro paso.

### Remediación
1. **Rotar inmediatamente** la contraseña de la cuenta `admin` en producción (Railway).
2. Revisar logs de acceso de esa cuenta desde el 2026-05-25 (fecha del último cambio a estos archivos) para descartar uso no autorizado.
3. Reemplazar todo hardcode por variables de entorno **sin valor por defecto** (`os.getenv("PLAYWRIGHT_ADMIN_USER")`, `os.getenv("PLAYWRIGHT_ADMIN_PASS")`) y fallar explícitamente si faltan, replicando el patrón ya usado (pero no aplicado aquí) en `specs/008-playwright-prod-diag/plan.md`, que sí exige `os.environ.get("PLAYWRIGHT_PROD_USER")`.

---

## 2. 🟠 ALTO — Password de PostgreSQL hardcodeada (`7323`)

### 2.1 Como fallback de `os.getenv(...)` en código (evidencia parcial — lista completa en el Apéndice A)

| Archivo | Línea |
|---|---|
| `config/shared_db_config.py` | 10 |
| `config/rxconfig.py` *(duplicado obsoleto)* | 18 |
| `config/sanitize_credentials.py` *(irónico: el propio script "saneador")* | 41 |
| `migraciones/database_config.py` | 28, 35 |
| `migraciones/postgres_config.py` | 24, 35, 171 |
| `migraciones/migrate_to_postgresql.py` | 37, 45 |
| `migraciones/verify_connection.py` | 15 |
| `migraciones/run_checklist.py` | 13 |
| `migraciones/sync_schema_columns.py` | 13 |
| `migraciones/create_bonificaciones_table.py` | 13 |
| `migraciones/inspect_migration_conflict.py` | 13 |
| `migraciones/migrate_postgres_local_to_railway.py` | 14 |
| `migraciones/extract_missing_ddl.py` | 10 |
| `migraciones/fix_schema_and_migrate_final.py` | 14 |
| `migraciones/retry_full_migration_v2.py` | 14 |
| + 20 archivos más en `scripts/` (empty_tables.py, unblock_admin.py, create_permissions_tables.py, apply_fix.py, apply_fix_v2.py, apply_audit_final.py, apply_audit_full.py, verify_fix.py, verify_schema.py, verify_local_postgres.py, generate_triggers.py, debug_sql.py, test_simple_trigger.py, create_ipc_table.py, create_bonif_table.py, diagnose_codeudor_35.py, list_local_schema.py, list_local_booleans.py, extract_local_views.py, check_permissions_tables.py, apply_legal_rep_migration_standalone.py, force_clean_incidentes.py) | ver Apéndice A |

### 2.2 Documentada literalmente en texto plano (más grave que el fallback en código)

| Archivo | Línea | Contenido |
|---|---|---|
| `migraciones/README_MIGRACION.md` | 13, 133, 144, 360 | `**Contraseña**: \`7323\`` / `DATABASE_URL = "postgresql://inmo_user:7323@localhost:5432/db_inmo_velar"` |
| `migraciones/REPORTE_MIGRACION.md` | 107, 115, 170 | Idéntico patrón |
| `migraciones/CHECKLIST_VERIFICACION.md` | 138, 147, 211 | Idéntico patrón |
| `migraciones/GUIA_RAPIDA.txt` | 34, 43 | Idéntico patrón |
| `migraciones/AGREGAR_A_ENV.txt` | 20 | `DB_PASSWORD=7323` |

### 2.3 Estado de la remediación previa

`specs/066-security-hardening-remediation/tasks.md:55` marca como completada (`[X]`):
> T008 — Remove fallback password `7323` and missing DB URL logic in `rxconfig.py`.

Y en efecto, **`rxconfig.py` de la raíz** (el que Reflex realmente carga según `app_name="inmobiliaria_velar"`) ya no tiene el fallback: usa `os.getenv('DB_PASSWORD') or ''` y depende de `DATABASE_URL`. **Ese es el único archivo corregido.** El propio `specs/066.../data-model.md:123-124` documenta que además había que purgar `migraciones/AGREGAR_A_ENV.txt` y `migraciones/GUIA_RAPIDA.txt` del historial con `git filter-repo --invert-paths` — algo que, según el estado actual del working tree, **no se ejecutó**.

### Remediación
1. Rotar la contraseña de PostgreSQL en Railway y en cualquier entorno local que la use.
2. Eliminar el fallback `'7323'` de los ~35 archivos listados (comando masivo en la sección 6).
3. Editar los 5 documentos que la citan en texto plano.
4. Purgar el valor del historial de git (no solo del working tree).

---

## 3. 🟡 MEDIO — Credenciales de test de la aplicación (`jsuarcar` / `velarjoan2026`)

| Archivo | Línea |
|---|---|
| `playwright_test.py` | 21 |
| `scripts/validar_liquidacion_572.py` | 33 |
| `scripts/diagnostico/playwright_test.py` | 28 |
| `tests/e2e/conftest.py` | 16 (`os.getenv("PLAYWRIGHT_TEST_PASSWORD", "velarjoan2026")` — mismo patrón de fallback inseguro que el hallazgo #2) |
| `specs/040-personas-module-documentation/spec.md` | 149 |
| `specs/040-personas-module-documentation/tasks.md` | 227 |
| `specs/007-playwright-validation/quickstart.md` | 28 |
| `specs/008-playwright-prod-diag/quickstart.md` | 11 |
| `specs/009-fix-prod-diag-bugs/quickstart.md` | 33 |
| `docs/assets/screenshots/Dashboard/README.md` | 12 |
| `docs/assets/screenshots/Personas/README.md` | 27 |

Nótese la contradicción interna del propio repo: `specs/008-playwright-prod-diag/plan.md:35` afirma *"Zero Leak: Validado. Las contraseñas proporcionadas... no serán hardcodeadas"* — pero el resto de archivos de esa misma iniciativa sí la hardcodean.

### Remediación
Mismo patrón que el hallazgo #1: variable de entorno sin default, y rotar la contraseña si `jsuarcar` es una cuenta real (no solo de prueba local).

---

## 4. 🟡 MEDIO — Información personal (PII) real versionada en el repositorio

No son credenciales, pero es información que se está filtrando y por eso se documenta aquí:

| Ruta | Contenido |
|---|---|
| `assets/exports/personas_export_*.csv` (8 archivos) | Columnas: `Nombre Completo, Tipo Documento, Documento, Telefono, Correo, Direccion, Fecha Creacion, Estado` — datos reales de personas (arrendatarios/propietarios), no anonimizados |
| `assets/pdfs/contrato_*.pdf`, `contrato_mandato_*.pdf` | Contratos de arrendamiento y mandato reales |
| `assets/pdfs/estado_cuenta_*.pdf` | Estados de cuenta con datos financieros reales |
| `assets/pdfs/liquidacion_24_*.pdf` | Liquidación real |

`src/infraestructura/db/db_inmo_velar.sqlite` también está trackeado en git pese a que `*.sqlite` está en `.gitignore` — en el commit actual está vacío (0 bytes), pero conviene revisar si en commits anteriores del historial contuvo datos, ya que `git log` conserva versiones previas del archivo aunque hoy esté vacío.

### Remediación
Eliminar estos archivos del repositorio y del historial (no solo del working tree); si son necesarios para pruebas, usar datos sintéticos/anonimizados y excluir la carpeta vía `.gitignore` (ya existe la entrada `assets/uploaded_files/` pero no cubre `assets/exports/` ni `assets/pdfs/`).

---

## 5. Por qué Gitleaks (ya configurado en `.github/workflows/security-scan.yml`) no detectó nada de esto

El workflow ya ejecuta `gitleaks/gitleaks-action@v2` en cada push/PR a `main`/`develop`. El problema es que **las reglas por defecto de Gitleaks buscan patrones de alta entropía o formatos conocidos** (`AKIA...` de AWS, `sk_live_...` de Stripe, JWT, etc.). Los tres secretos encontrados aquí son **literales cortos de baja entropía** (`7323`, `admin0123`, `velarjoan2026`) usados como valor por defecto de una función — no calzan con ninguna regla genérica. Por eso llevan desde el **2026-05-25** en el repositorio sin ser marcados, a pesar del scanner activo.

Se entrega junto a este informe un archivo `.gitleaks.toml` con reglas propias que sí cubren estos patrones (ver artefacto adjunto).

---

## 6. Plan de remediación consolidado (checklist accionable)

- [ ] Rotar la contraseña de la cuenta `admin` en producción (Railway) — **prioridad 1**
- [ ] Revisar logs de acceso de la cuenta `admin` desde 2026-05-25
- [ ] Rotar la contraseña de PostgreSQL (`7323`) en Railway y entornos locales
- [ ] Rotar/eliminar la cuenta `jsuarcar` de test si tiene privilegios reales, o confirmar que es puramente sintética
- [ ] Ejecutar el reemplazo masivo de fallbacks en código (comando abajo)
- [ ] Editar los 5 documentos `.md`/`.txt` que citan `7323` en texto plano
- [ ] Eliminar `assets/exports/*.csv` y `assets/pdfs/*.pdf` con datos reales del repo
- [ ] Purgar `7323`, `admin0123`, `velarjoan2026` y las rutas de PII del **historial** de git con `git filter-repo`
- [ ] Forzar push del historial reescrito y notificar a cualquier colaborador para que re-clone
- [ ] Instalar el `.gitleaks.toml` custom adjunto en la raíz del repo
- [ ] Re-ejecutar el workflow `security-scan.yml` para confirmar que ya no hay coincidencias
- [ ] Cerrar formalmente `specs/066-security-hardening-remediation/` solo cuando el Apéndice A de este informe esté en cero

### Comandos

```bash
# --- Paso 1: eliminar fallbacks hardcodeados de DB_PASSWORD en Python ---
grep -rlE "os\.getenv\(['\"]DB_PASSWORD['\"],\s*['\"]7323['\"]\)" --include="*.py" . | \
  xargs sed -i -E "s/os\.getenv\(('DB_PASSWORD'|\"DB_PASSWORD\"),\s*('7323'|\"7323\")\)/os.getenv(\1)/g"

# --- Paso 2: eliminar fallback de la credencial de test ---
grep -rlE "velarjoan2026" --include="*.py" . | \
  xargs sed -i -E 's/os\.getenv\((\"|'"'"')PLAYWRIGHT_TEST_PASSWORD(\"|'"'"'),\s*(\"|'"'"')velarjoan2026(\"|'"'"')\)/os.getenv(\1PLAYWRIGHT_TEST_PASSWORD\2)/g'

# --- Paso 3: quitar archivos con PII/credenciales de producción del working tree ---
git rm --cached scripts/diagnostico/test_login_produccion.py  # o mover fuera del repo si aún se necesita localmente
git rm --cached assets/exports/*.csv

# --- Paso 4: purgar valores y rutas del HISTORIAL completo ---
pip install git-filter-repo
git filter-repo --force --replace-text <(cat <<'EOF'
7323==>***ROTATED***
admin0123==>***ROTATED***
velarjoan2026==>***ROTATED***
EOF
)
git filter-repo --force --invert-paths \
  --path assets/exports \
  --path migraciones/AGREGAR_A_ENV.txt \
  --path migraciones/GUIA_RAPIDA.txt

# --- Paso 5: reescribir el remoto (coordinar con el equipo antes de forzar) ---
git push origin --force --all
git push origin --force --tags
```

---

## 7. Verificación posterior a la remediación

```bash
# No debe devolver nada tras la limpieza:
grep -rn "7323\|admin0123\|velarjoan2026" --include="*.py" --include="*.md" --include="*.txt" .

# Confirmar que el historial ya no contiene las cadenas:
git log --all -p | grep -E "7323|admin0123|velarjoan2026"
```

---

## Apéndice A — Listado completo de coincidencias `7323` (39 ubicaciones en 32 archivos, además de `outputs/test_output.txt` como artefacto de test)

```
config/shared_db_config.py:10
config/rxconfig.py:18
config/sanitize_credentials.py:41
migraciones/create_bonificaciones_table.py:13
migraciones/inspect_migration_conflict.py:13
migraciones/migrate_postgres_local_to_railway.py:14
migraciones/database_config.py:28,35
migraciones/extract_missing_ddl.py:10
migraciones/migrate_to_postgresql.py:37,45
migraciones/run_checklist.py:13
migraciones/fix_schema_and_migrate_final.py:14
migraciones/postgres_config.py:24,35,171
migraciones/retry_full_migration_v2.py:14
migraciones/sync_schema_columns.py:13
migraciones/verify_connection.py:15
migraciones/CHECKLIST_VERIFICACION.md:138,147,211
migraciones/REPORTE_MIGRACION.md:107,115,170
migraciones/README_MIGRACION.md:13,133,144,360
migraciones/GUIA_RAPIDA.txt:34,43
migraciones/AGREGAR_A_ENV.txt:20
scripts/force_clean_incidentes.py:19
scripts/verify_local_postgres.py:10
scripts/apply_audit_full.py:22
scripts/extract_local_views.py:10
scripts/diagnose_codeudor_35.py:9
scripts/list_local_schema.py:10
scripts/empty_tables.py:11
scripts/apply_legal_rep_migration_standalone.py:10
scripts/create_bonif_table.py:10
scripts/create_permissions_tables.py:23
scripts/apply_fix_v2.py:23
scripts/debug_sql.py:23
scripts/check_permissions_tables.py:19
scripts/generate_triggers.py:22
scripts/apply_fix.py:24
scripts/test_simple_trigger.py:22
scripts/unblock_admin.py:13
scripts/create_ipc_table.py:9
scripts/verify_fix.py:25
scripts/apply_audit_final.py:22
scripts/verify_schema.py:11
scripts/list_local_booleans.py:10
```

## Apéndice B — Listado completo de coincidencias `velarjoan2026`

```
playwright_test.py:21
specs/040-personas-module-documentation/tasks.md:227
specs/040-personas-module-documentation/spec.md:149
specs/008-playwright-prod-diag/quickstart.md:11
specs/008-playwright-prod-diag/plan.md:35 (mención, no hardcode)
specs/009-fix-prod-diag-bugs/quickstart.md:33
specs/007-playwright-validation/quickstart.md:28
scripts/validar_liquidacion_572.py:33
scripts/diagnostico/playwright_test.py:28
tests/e2e/conftest.py:16
docs/assets/screenshots/Dashboard/README.md:12
docs/assets/screenshots/Personas/README.md:27
```

## Apéndice C — Listado completo de coincidencias `admin0123`

```
scripts/diagnostico/auditoria_reportes.py:13
scripts/diagnostico/auditoria_simple.py:12
scripts/diagnostico/auditoria_detallada.py:14
scripts/diagnostico/auditoria_recaudos_check.py:12
scripts/diagnostico/test_login_produccion.py:25 (+ usuario "admin" en línea 22, + URL de producción en línea 16)
tests/test_dashboard_row4.py:44,69
tests/test_playwright_liquidacion_asesores.py:38
tests/test_playwright_filtro_asesores.py:32
docs/superpowers/plans/2026-07-02-incident-liquidation-sync.md:16
test_login_visible.mjs:26
```

## Apéndice D — Verificaciones negativas (no se encontraron, para que quede documentado)

- Sin coincidencias de claves de AWS (`AKIA...`), Google (`AIza...`), Stripe (`sk_live_/sk_test_`), GitHub (`ghp_/gho_`), Slack (`xox...`) ni JWT embebidos.
- `SECRET_KEY` de la aplicación (`src/infraestructura/configuracion/settings.py`) no tiene valor hardcodeado real: usa el placeholder `CHANGE_ME_IN_PRODUCTION` y además tiene un `field_validator` que **aborta el arranque** si no se sobreescribe con al menos 16 caracteres — buen patrón, a diferencia del resto de la configuración.
- Las credenciales SMTP (`cliente_email_office365.py`, `test_smtp_real.py`, `verify_smtp_config.py`) se leen correctamente desde `Settings`/variables de entorno, sin fallback hardcodeado.
- `.env` nunca fue comiteado en el historial (`.gitignore` lo excluye correctamente y no aparece en `git log --all --full-history`).

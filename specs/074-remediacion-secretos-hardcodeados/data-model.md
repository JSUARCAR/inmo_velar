# Fase 1 — Modelo de Datos: Remediación de Credenciales Hardcodeadas (074)

Entidades conceptuales del inventario y la evidencia. No implican esquema de base de datos: se materializan en un documento enmascarado versionado (`docs/security/INVENTARIO_REMEDIACION_074.md`) y en la configuración de CI.

## Hallazgo (credencial expuesta)

| Campo | Tipo | Regla |
|---|---|---|
| `id` | `H-##` | Único y estable (FR-021); hoy `H-01` administrador, `H-02` BD producción, `H-03` cuenta de prueba |
| `tipo` | enumerado: `cuenta_aplicacion` · `base_datos` · `cuenta_prueba` | Obligatorio |
| `sistemas_afectados` | lista de texto | Producción, base de datos, entorno de pruebas, según aplique |
| `valor` | **nunca se reproduce** | Solo identificador de hallazgo; prohibido cualquier literal o fragmento (FR-003/FR-016) |
| `estado` | `pendiente` → `rotada` · `eliminada` | Transición irreversible; `rotada` registra `fecha_rotacion` y `responsable` |
| `responsable` | texto | Responsable de seguridad (FR-021) |

## Ubicación de exposición

| Campo | Tipo | Regla |
|---|---|---|
| `id` | `U-###` | Único |
| `hallazgo_ref` | `H-##` | Obligatorio; un hallazgo tiene ≥ 1 ubicación |
| `ruta` | ruta relativa | Archivo del repositorio |
| `lineas` | texto | Líneas conocidas (puede ser estimado) |
| `categoria` | `codigo_en_ejecucion` · `script_diagnostico` · `prueba` · `documentacion` · `informe` · `historial` · `canal_externo` | Obligatorio |
| `estado_limpieza` | `pendiente` → `limpiada` → `purgada` | `purgada` aplica solo a categoría `historial`; `limpiada` a canales externos y árbol |
| `fecha` | fecha ISO 8601 | Obligatoria al cambiar de estado |

## Cuenta afectada

| Campo | Tipo | Regla |
|---|---|---|
| `identificador_logico` | texto | Nombre lógico de la cuenta/servicio (sin credenciales) |
| `tipo` | `administracion` · `base_datos` · `prueba` | Obligatorio |
| `propietario` | texto | Quién la administra |
| `privilegios` | texto | Nivel de acceso (p. ej., administrador total, lectura/escritura BD) |
| `credencial_ref` | `H-##` | Hallazgo asociado |
| `estado_acceso` | `vigente` → `revocado` | `revocado` solo cuando el valor comprometido deja de autenticar |

## Dato personal versionado

| Campo | Tipo | Regla |
|---|---|---|
| `ruta` | ruta relativa o patrón | `assets/exports/*.csv`, `assets/pdfs/*.pdf`, base local |
| `tipo_dato` | `identificacion` · `contacto` · `financiero` · `contractual` | Obligatorio |
| `versiones` | texto | Commits/etiquetas donde aparece (sin reproducir datos) |
| `destino_conservacion` | texto o `no_aplica` | Almacenamiento controlado fuera del repositorio si se requiere (FR-010) |
| `estado` | `pendiente` → `retirado` → `purgado` | `retirado` = fuera del árbol; `purgado` = fuera del historial |

## Evidencia de verificación

| Campo | Tipo | Regla |
|---|---|---|
| `id` | `E-###` | Único |
| `fecha` | fecha ISO 8601 | Obligatoria |
| `responsable` | texto | Obligatorio |
| `tipo` | `rotacion` · `busqueda_arbol` · `busqueda_historial` · `escaneo` · `limpieza_canal` · `re_clonado` · `revision_accesos` · `bloqueo_prueba` | Obligatorio |
| `resultado` | texto | Debe ser verificable (p. ej., "0 coincidencias", "escaneo sin hallazgos") |
| `referencia` | texto | Enlace/comando/reporte donde consta (sin literales) |

## Configuración externa (contrato de variables)

| Campo | Tipo | Regla |
|---|---|---|
| `nombre` | texto | Definido en `contracts/configuracion-credenciales.md` |
| `consumidor` | texto | Módulo/script que la requiere |
| `obligatoria` | booleano | Si es credencial, sin valor por defecto (FR-002) |
| `valor_protegido` | booleano | Siempre `true` para credenciales; nunca en el repositorio |
| `patron_validacion` | texto | No vacío; formato mínimo; sin exponer el valor |

## Regla de escaneo

| Campo | Tipo | Regla |
|---|---|---|
| `id` | texto | `inmo-velar-*` |
| `descripcion` | texto | Patrón de riesgo cubierto |
| `patron` | regex generalizada | Versionada en `.gitleaks.toml` (sin literales) |
| `fuente_literales` | `configuracion_protegida` | Solo para la regla de valores exactos (FR-013) |
| `severidad` | `critical` · `high` | Etiqueta informativa |
| `allowlist` | entradas acotadas | Justificadas y revisadas; jamás para valores comprometidos (FR-014) |

## Transiciones de estado (resumen)

```text
Hallazgo:      pendiente ──► rotada | eliminada
Ubicación:     pendiente ──► limpiada ──► purgada (solo historial)
Dato personal: pendiente ──► retirado ──► purgado
Acceso:        vigente   ──► revocado
```

## Validaciones transversales

- Ningún campo puede contener valores comprometidos, ni fragmentos ni cadenas de conexión (FR-003); el propio documento debe pasar el escaneo.
- Todo hallazgo debe tener al menos una ubicación y una entrada de evidencia de rotación (FR-001/FR-016).
- Los identificadores son únicos y referenciables desde el plan y las tareas (US/FR/SC ↔ H/U/E).

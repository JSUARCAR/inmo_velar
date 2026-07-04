# Guía de Despliegue - Inmobiliaria Velar

## Visión General

Este documento describe el proceso de despliegue para la aplicación Inmobiliaria Velar en el entorno de producción (Railway).

## Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────────┐
│                     RAILWAY PRODUCTION                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   CADDY     │───▶│   REFLEX    │───▶│  POSTGRESQL │     │
│  │  (Frontend) │    │  (Backend)  │    │   (DB)      │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                          │                                   │
│                    ┌─────┴─────┐                            │
│                    │ MIGRATIONS│                            │
│                    │ (Auto)    │                            │
│                    └───────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

## Proceso de Despliegue Automático

### 1. Build Phase (Docker)

El build se ejecuta automáticamente al hacer push a la rama `feat/desarrollo-experto-elite`:

```dockerfile
# Dockerfile
RUN python -c "import sys, importlib; ..."  # Verificar estilos
RUN rm -rf .web && RAILWAY_ENVIRONMENT=production DATABASE_URL=sqlite:///dummy_build.db reflex init
RUN RAILWAY_ENVIRONMENT=production DATABASE_URL=sqlite:///dummy_build.db reflex export --frontend-only --no-zip
```

### 2. Deploy Phase (Entrypoint)

El entrypoint ejecuta las migraciones automáticamente:

```bash
# entrypoint.sh
echo "=== Step 3: Running Database Migrations ==="
if [ -n "$DATABASE_URL" ]; then
    python /app/scripts/run_pg_migrations.py
    python /app/scripts/setup_permissions.py
fi
```

## Migraciones Incluidas

### Tablas Nuevas

| Tabla | Propósito |
|-------|-----------|
| `PLAN_PAGO_INCIDENTE` | Planes de pago para incidentes |
| `CUOTA_INCIDENTE` | Cuotas de los planes de pago |
| `INCIDENTE_LIQUIDACION` | Asociación incidentes-liquidaciones |
| `BLOQUEOS_EDICION` | Control de concurrencia |

### Columnas Nuevas

| Tabla | Columna | Propósito |
|-------|---------|-----------|
| `INCIDENTES` | `estado_pago` | Estado de pago del incidente |
| `LIQUIDACIONES` | `valor_incidentes` | Valor total de incidentes asociados |

### Permisos Nuevos

| Módulo | Permiso | Descripción |
|--------|---------|-------------|
| `Liquidaciones` | `ELIMINAR` | Eliminar liquidaciones |
| `Liquidaciones` | `SELECCIONAR_INCIDENTES` | Seleccionar incidentes para asociar |
| `Incidentes` | `DEFINIR_PLAN_PAGO` | Definir planes de pago |
| `Incidentes` | `VER_ESTADO_PAGO` | Visualizar estado de pago |

## Scripts de Mantenimiento

### Verificar Estado de la BD

```bash
python scripts/verify_database.py
```

Salida esperada:
```
=== 1. Tablas Críticas ===
  ✓ incidentes
  ✓ liquidaciones
  ✓ plan_pago_incidente
  ✓ cuota_incidente
  ✓ incidente_liquidacion
  ...

=== 2. Columnas Críticas ===
  ✓ incidentes.estado_pago
  ✓ liquidaciones.valor_incidentes
  ...

=== 3. Permisos Críticos ===
  ✓ Liquidaciones:ELIMINAR
  ✓ Liquidaciones:SELECCIONAR_INCIDENTES
  ✓ Incidentes:DEFINIR_PLAN_PAGO
  ...
```

### Ejecutar Migraciones Manualmente

Si necesitas ejecutar las migraciones manualmente:

```bash
# Conectar a la base de datos de producción
export DATABASE_URL="postgresql://..."

# Ejecutar migraciones
python scripts/run_pg_migrations.py

# Configurar permisos
python scripts/setup_permissions.py

# Verificar estado
python scripts/verify_database.py
```

## Troubleshooting

### Problema: Botones no aparecen en producción

**Causa**: Los permisos no están registrados.

**Solución**:
```bash
python scripts/setup_permissions.py
```

### Problema: Error "relation does not exist"

**Causa**: Las tablas no fueron creadas.

**Solución**:
```bash
python scripts/run_pg_migrations.py
```

### Problema: Migraciones fallan

**Causa**: Posible conflicto con esquema existente.

**Solución**:
1. Verificar el estado actual: `python scripts/verify_database.py`
2. Revisar logs de error
3. Ejecutar migraciones individualmente si es necesario

## Variables de Entorno Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@host:port/db` |
| `PORT` | Puerto para el servidor web | `8080` |
| `RAILWAY_ENVIRONMENT` | Entorno de Railway | `production` |

## Verificación Post-Despliegue

1. **Acceder a la aplicación**: `https://extraordinary-joy-production-2fd2.up.railway.app`
2. **Navegar a Liquidaciones**: Verificar botón de eliminar
3. **Editar una liquidación**: Verificar botón "Seleccionar Incidentes"
4. **Navegar a Incidentes**: Verificar sección "Plan de Pago"

## Comandos Útiles

```bash
# Ver logs de Railway
railway logs

# Verificar estado del servicio
railway status

# Conectar a la base de datos
railway connect postgres

# Ejecutar comandos en el contenedor
railway run python scripts/verify_database.py
```

## Mejores Prácticas

1. **Siempre ejecutar verificaciones post-despliegue**
2. **No saltar migraciones** - cada una es crítica
3. **Hacer backup** antes de migraciones manuales
4. **Probar en staging** antes de producción
5. **Monitorear logs** durante el despliegue

## Contacto

Para soporte técnico, contactar al equipo de desarrollo.

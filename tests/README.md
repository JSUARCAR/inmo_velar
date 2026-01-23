# Tests - Sistema de Gestión Inmobiliaria

## Estructura de Tests

```
tests/
├── unit/                           # Tests unitarios (sin dependencias externas)
│   ├── test_entidades/            # Tests de entidades del dominio
│   ├── test_value_objects/        # Tests de value objects
│   └── test_servicios_dominio/    # Tests de servicios de dominio
│
├── integration/                    # Tests de integración (con BD, servicios)
│   ├── test_repositorios/         # Tests de repositorios SQLite
│   └── test_servicios_aplicacion/ # Tests de servicios de aplicación
│
└── e2e/                           # Tests end-to-end (UI completa)
```

## Tests Disponibles

### Tests de Integración - Servicios de Aplicación

| Archivo | Descripción |
|---------|-------------|
| `test_financiero_integration.py` | Tests del módulo financiero (recaudos, liquidaciones) |
| `test_financiero_integration_v2.py` | Tests financieros v2 (versión actualizada) |
| `test_manual_financiero.py` | Tests manuales del sistema financiero |
| `test_ipc_alert.py` | Tests de alertas de aniversario IPC |
| `test_renovacion.py` | Tests de renovación de contratos de arrendamiento |
| `test_renovacion_mandato.py` | Tests de renovación de contratos de mandato |
| `test_terminacion.py` | Tests de terminación de contratos |

### Tests de Integración - Repositorios

| Archivo | Descripción |
|---------|-------------|
| `test_no_alias.py` | Tests de queries SQL sin aliases |

### Tests E2E

| Archivo | Descripción |
|---------|-------------|
| `test_dashboard_direct.py` | Test directo del dashboard (UI) |

## Cómo Ejecutar los Tests

### Ejecutar todos los tests
```bash
python -m pytest tests/
```

### Ejecutar tests unitarios
```bash
python -m pytest tests/unit/
```

### Ejecutar tests de integración
```bash
python -m pytest tests/integration/
```

### Ejecutar tests E2E
```bash
python -m pytest tests/e2e/
```

### Ejecutar un test específico
```bash
python -m pytest tests/integration/test_servicios_aplicacion/test_financiero_integration.py
```

### Ejecutar con verbose
```bash
python -m pytest tests/ -v
```

### Ejecutar con cobertura
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Convenciones de Naming

- **Archivos de test**: `test_*.py` o `*_test.py`
- **Clases de test**: `Test*` (ej: `TestServicioFinanciero`)
- **Métodos de test**: `test_*` (ej: `test_registrar_recaudo`)

## Fixtures Comunes

Los fixtures compartidos se encuentran en `conftest.py` en cada nivel:
- `tests/conftest.py` - Fixtures globales
- `tests/integration/conftest.py` - Fixtures de integración (BD de prueba)
- `tests/unit/conftest.py` - Fixtures unitarios (mocks)

## Dependencias de Testing

```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
```

## Notas Importantes

1. **Base de Datos de Prueba**: Los tests de integración usan una BD SQLite en memoria o temporal
2. **Aislamiento**: Cada test debe ser independiente y no afectar a otros
3. **Limpieza**: Los fixtures deben limpiar recursos después de cada test
4. **Datos de Prueba**: Usar factories o builders para crear datos de test consistentes

## Estado Actual

- ✅ Tests de integración de servicios financieros
- ✅ Tests de integración de contratos (renovación, terminación)
- ✅ Tests de alertas IPC
- ✅ Test E2E de dashboard
- ⏳ Tests unitarios del dominio (pendiente)
- ⏳ Tests de repositorios completos (pendiente)
- ⏳ Cobertura de código (pendiente)

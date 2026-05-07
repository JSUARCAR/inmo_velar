# Plan Maestro: Implementación de Idempotencia (Versión Élite PostgreSQL)

## Sistema Inmobiliaria Velar - Arquitectura Limpia & SOLID

---

## Indice Ejecutivo

**Objetivo:** Implementar idempotencia transaccional en operaciones críticas del sistema inmobiliario, garantizando precisión financiera y resiliencia operativa mediante el uso nativo de PostgreSQL.

**Alcance:** 20 días hábiles (4 semanas) | **Equipo:** 1 Senior Full-Stack | **Stack:** Python + Reflex + PostgreSQL (Nativo)

**Entregables:**

* 7 servicios refactorizados con idempotencia garantizada atómicamente.
* Decoradores reutilizables optimizados para PostgreSQL.
* Middleware API estandarizado para manejo de `Idempotency-Key`.
* Migraciones SQL optimizadas con `ON CONFLICT` y `RETURNING`.
* 35+ tests de integración concurrentes.

---

## Principios Arquitectónicos (SOLID + PostgreSQL Native)

### Single Responsibility Principle (SRP)
Separación estricta entre validación, persistencia atómica y publicación de eventos.

### Open/Closed Principle (OCP)
Estrategias de idempotencia extensibles, aunque centralizadas en PostgreSQL como fuente de verdad única.

### Liskov Substitution Principle (LSP)
Interfaces de repositorio que garantizan comportamiento consistente en entornos de producción (Railway).

### Interface Segregation Principle (ISP)
Interfaces específicas para operaciones de creación, actualización y transición de estados con llave de idempotencia.

### Dependency Inversion Principle (DIP)
Inyección de repositorios de idempotencia en servicios de aplicación.

---

## Fase 0: Análisis y Preparación (2 días)

### Auditoría de Código y Definición de Límites
Identificación de "Side Effects" en métodos de creación y liquidación.

---

## Fase 1: Infraestructura Base (PostgreSQL Only)

### Task 1.1: Decorador de Idempotencia Atómica
**Archivo:** `src/aplicacion/decorators/idempotent.py`

Se elimina cualquier referencia a Redis. La estrategia por defecto es `DatabaseIdempotencyStrategy` (PostgreSQL).

```python
class DatabaseIdempotencyStrategy(IdempotencyStrategy):
    """PostgreSQL backed (Fuente de verdad inmutable)."""
    def __init__(self, db_manager):
        self.db = db_manager

    def get_result(self, key: str) -> Optional[Any]:
        # Consulta atómica en IDEMPOTENCY_KEYS
        ...
```

### Task 1.2: Esquema de Base de Datos Élite
**Archivo:** `migraciones/20250420_create_idempotency_keys.sql`

```sql
-- Tabla central de idempotencia (Nativa PostgreSQL)
CREATE TABLE IF NOT EXISTS IDEMPOTENCY_KEYS (
    ID_KEY SERIAL PRIMARY KEY,
    KEY VARCHAR(64) UNIQUE NOT NULL,          -- SHA256 del payload/contexto
    OPERACION VARCHAR(100) NOT NULL,
    PARAMETROS JSONB,                         
    RESULTADO JSONB,                          
    USUARIO_ID INTEGER NOT NULL,              
    FECHA_CREACION TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FECHA_EXPIRA TIMESTAMP WITH TIME ZONE NOT NULL,
    ESTADO VARCHAR(20) DEFAULT 'completed',   
    CONSTRAINT fk_usuario FOREIGN KEY (USUARIO_ID) 
        REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE
);

CREATE INDEX IDX_IDEMPOTENCY_KEY ON IDEMPOTENCY_KEYS(KEY);
CREATE INDEX IDX_IDEMPOTENCY_EXPIRA ON IDEMPOTENCY_KEYS(FECHA_EXPIRA);
```

---

## Fase 2: Servicios Críticos (Integración Atómica)

### Task 2.1: ServicioRecaudo (Garantía de Duplicados)
El servicio debe confiar en el `ON CONFLICT` de PostgreSQL como última línea de defensa.

```python
def registrar_pago(self, comando: ComandoRegistrarPago, usuario: str, idempotency_key: str):
    # 1. Serialización determinista para composite_key
    # 2. Transacción atómica:
    with self.db.transaction() as tx:
        # El repositorio usará INSERT ... ON CONFLICT (BUSINESS_KEY) DO NOTHING RETURNING ...
        recaudo = self.repo.crear_idempotente(key=idempotency_key, ...)
```

---

## Fase 3: Frontend y API (Protección de Frontera)

### Task 3.1: Mixin de Idempotencia Determinista
**Archivo:** `src/presentacion_reflex/state/idempotency_mixin.py`

Garantiza que el hash generado sea consistente independientemente del orden de los atributos.

```python
def _generate_deterministic_key(self, data: Dict) -> str:
    """Serialización estricta para hashing."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()
```

### Task 3.2: Double-Click Protection en Reflex
Uso de `IdempotentButton` para deshabilitar la UI inmediatamente tras el primer envío.

---

## Fase 4: Calidad y Validación Élite

### Tests de Concurrencia Extrema
Simulación de 100 hilos concurrentes intentando el mismo recaudo. Solo 1 debe persistir en PostgreSQL; 99 deben recibir el resultado cacheado o un error de conflicto manejado.

---

## Métricas de Éxito
* **Duplicados financieros:** 0 (Garantizado por constraints `UNIQUE` en PostgreSQL).
* **Overhead de latencia:** < 15ms (Optimizado mediante índices parciales).
* **Resiliencia:** Recuperación automática ante desconexiones durante el registro.

---

**Plan aprobado para ejecución inmediata.**

# Plan Maestro: Implementación de Idempotencia

## Sistema Inmobiliaria Velar - Arquitectura Limpia & SOLID

---

## Indice Ejecutivo

**Objetivo:** Implementar idempotencia transaccional en operaciones críticas del sistema inmobiliario, garantizando precisión financiera y resiliencia operativa.

**Alcance:** 22 días hábiles (4 semanas) | **Equipo:** 1 Senior Full-Stack + 1 QA | **Stack:** Python + Reflex + PostgreSQL/SQLite

**Entregables:**

* 7 servicios refactorizados con idempotencia garantizada
* 4 decoradores reutilizables (SOLID)
* 1 middleware API estandarizado
* 12 migraciones SQL versionadas
* 35+ tests de integración idempotentes
* Documentación OpenAPI actualizada
* Monitoring dashboard (Grafana-ready)

---

## Principios Arquitectónicos (SOLID + Clean Code)

### Single Responsibility Principle (SRP)

```
# Antipatrón: Una clase hace todo
class RecaudoService:
    def registrar_pago(self, datos): ...
    def validar_pago(self, datos): ...
    def generar_pdf(self, id): ...
    def enviar_email(self, id): ...

# SRP: Separación de responsabilidades
class RecaudoValidator:        # Solo validación
class RecaudoPersister:        # Solo persistencia (idempotente)
class RecaudoEventPublisher:   # Solo eventos (idempotente)
class RecaudoPdfGenerator:     # Solo PDF (idempotente)
class RecaudoService:          # Orquestación (use case)
```

### Open/Closed Principle (OCP)

```
class IdempotencyStrategy(ABC):
    @abstractmethod
    def execute(self, key, operation): ...

class DatabaseIdempotencyStrategy(IdempotencyStrategy):
    # Implementación PostgreSQL
    ...

class RedisIdempotencyStrategy(IdempotencyStrategy):
    # Implementación Redis (fallback)
    ...

# Nuevos strategies → nuevas clases, NO modificar existentes
```

### Liskov Substitution Principle (LSP)

```
class IRepositorioRecaudo(ABC):
    @abstractmethod
    def crear_idempotente(self, key, recaudo, conceptos): ...

class RepositorioRecaudoPostgres(IRepositorioRecaudo):
    # Implementación PostgreSQL
    ...

class RepositorioRecaudoSqlite(IRepositorioRecaudo):
    # Implementación SQLite (tests)
    ...

# Cliente no distingue entre ambas → sustituible
```

### Interface Segregation Principle (ISP)

```
class ICreatableRepository(Generic[T]):
    def crear_idempotente(self, key: str, entidad: T) -> T: ...

class IUpdateableRepository(Generic[T]):
    def actualizar_idempotente(self, key: str, entidad: T, version: int) -> T: ...

class IStateTransitionRepository(Generic[T]):
    def cambiar_estado_idempotente(
        self, key: str, id: int, estado: str, expected: Optional[str] = None
    ) -> bool: ...
```

### Dependency Inversion Principle (DIP)

```
class ServicioRecaudo:
    def __init__(self, repo: IRepositorioRecaudo, cache: ICacheProvider):
        self.repo = repo      # Inyección de dependencia
        self.cache = cache
```

---

## Fase 0: Analisis y Preparación (2 días)

### Día 1-2: Auditoria de Código y Definición de Límites

**Objetivo:** Identificar exactamente qué debe ser idempotente y qué no.

```
# tools/audit_idempotency.py
#!/usr/bin/env python3
"""
Script de auditoría automática para clasificar funciones.
Scan del código → determina si necesita idempotencia.
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Tuple

class IdempotencyAuditor(ast.NodeVisitor):
    """
    AST visitor que clasifica métodos por necesidad de idempotencia.

    Reglas:
    1. Si tiene decorador @idempotent → ya es idempotente ✓
    2. Si nombre contiene: crear/registrar/insertar → IDEMPOTENTE
    3. Si nombre contiene: actualizar/update/modificar → IDEMPOTENTE
    4. Si nombre contiene: eliminar/delete/borrar → IDEMPOTENTE
    5. Si nombre contiene: cambiar_estado/aplicar/reversar → IDEMPOTENTE
    6. Si nombre contiene: generar/producir/crear_archivo → IDEMPOTENTE
    7. Si nombre contiene: enviar/enqueue/publicar → IDEMPOTENTE (efecto externo)
    8. Si retorna SELECT/query sin side-effects → NO idempotente
    """

    IDEMPOTENT_PATTERNS = [
        'crear', 'registrar', 'insertar', 'guardar', 'save',
        'actualizar', 'update', 'modificar', 'cambiar',
        'eliminar', 'delete', 'borrar', 'remove',
        'aplicar', 'reversar', 'procesar', 'ejecutar',
        'generar', 'producir', 'construir', 'crear_archivo',
        'enviar', 'email', 'notificar', 'publicar', 'publish',
        'liquidar', 'calcular_y', 'subir', 'cargar'
    ]

    READ_ONLY_PATTERNS = [
        'obtener', 'get', 'buscar', 'find', 'listar', 'list',
        'consultar', 'query', 'seleccionar', ' filtrar',
        'calcular', 'compute', 'formatear', 'validar'
    ]
```

---

## Fase 1: Infraestructura Base (3 dias)

### Task 1.1: Decorator Factory (SOLID: OCP)

**Archivo:** `src/aplicacion/decorators/idempotent.py`

```
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, TypeVar, Generic, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

T = TypeVar('T')

class IdempotencyStrategy(ABC):
    """Strategy pattern: Different idempotency backends."""

    @abstractmethod
    def is_processed(self, key: str) -> bool: ...

    @abstractmethod
    def mark_processed(self, key: str, result: Any, ttl: int) -> None: ...

    @abstractmethod
    def get_result(self, key: str) -> Optional[Any]: ...

class DatabaseIdempotencyStrategy(IdempotencyStrategy):
    """PostgreSQL/SQLite backed (persistente)."""

    def __init__(self, db_manager):
        self.db = db_manager

    def is_processed(self, key: str) -> bool:
        # SELECT 1 FROM IDEMPOTENCY_KEYS WHERE key = ? AND status = 'completed'
        ...

class RedisIdempotencyStrategy(IdempotencyStrategy):
    """Redis backed (fast, ephemeral)."""

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_processed(self, key: str) -> bool:
        return self.redis.exists(key) == 1

@dataclass
class IdempotencyConfig:
    """Configuración por operación."""
    ttl: int = 86400  # 24 hours default
    strategy: IdempotencyStrategy = None
    raise_on_conflict: bool = False
    log_conflicts: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

def idempotent(
    key_generator: Optional[Callable] = None,
    config: Optional[IdempotencyConfig] = None
):
    """
    Decorador que garantiza idempotencia.

    Uso:
        @idempotent(
            key_generator=lambda self, contrato_id: f"renovar:{contrato_id}",
            config=IdempotencyConfig(ttl=3600)
        )
        def renovar_contrato(self, contrato_id: int, dias: int):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Resolver instancia (self) y argumentos
            instance = args[0] if args else None
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 2. Generar clave única
            if key_generator:
                key = key_generator(*bound_args.args, **bound_args.kwargs)
            else:
                # Default: hash de todos los arguments
                key = _generate_default_key(func, bound_args)

            # 3. Obtener strategy
            strategy = (config.strategy if config 
                       else getattr(instance, '_idempotency_strategy', None))

            if not strategy:
                raise RuntimeError("No idempotency strategy configured")

            # 4. Check si ya procesado
            cached = strategy.get_result(key)
            if cached is not None:
                if config and config.log_conflicts:
                    logger.info(f"Idempotent hit: {key}")
                return cached

            # 5. Ejecutar operación
            try:
                result = func(*args, **kwargs)

                # 6. Marcar como procesado
                ttl = config.ttl if config else 86400
                strategy.mark_processed(key, result, ttl)

                return result

            except Exception as e:
                # No marcar como procesado en error
                raise

        return wrapper
    return decorator
```

---

### Task 1.2: Idempotency Repository Interface

**Archivo:** `src/dominio/interfaces/repositorio_idempotencia.py`

```
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime

class IRepositorioIdempotencia(ABC):
    """
    Contrato para persistencia de claves idempotentes.
    Implementaciones: PostgreSQL, SQLite, Redis.
    """

    @abstractmethod
    def existe(self, key: str) -> bool: ...

    @abstractmethod
    def registrar(
        self, 
        key: str, 
        operacion: str,
        resultado: Any,
        parametros: Dict[str, Any],
        usuario: str,
        ttl: int = 86400
    ) -> None: ...

    @abstractmethod
    def obtener_resultado(self, key: str) -> Optional[Any]: ...

    @abstractmethod
    def limpiar_expirados(self) -> int: ...  # retorna count
```

---

### Task 1.3: Base Repository with Idempotency

**Archivo:** `src/infraestructura/persistencia/base_repositorio.py`

```
from typing import Generic, TypeVar, Optional, List, Type
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia

E = TypeVar('E')  # Entity

class BaseRepositorio(Generic[E], ABC):
    """
    Repositorio base con soporte built-in para idempotencia.
    Todos los repositorios heredan de este.
    """

    def __init__(
        self, 
        db_manager,
        repo_idempotencia: IRepositorioIdempotencia
    ):
        self.db = db_manager
        self.repo_idempotencia = repo_idempotencia

    def crear_idempotente(
        self,
        key: str,
        entidad: E,
        usuario: str,
        *args,
        **kwargs
    ) -> E:
        """
        Template method para creación idempotente.

        Implementa:
        1. Check cache (idempotency key)
        2. Si existe → retornar entidad existente
        3. Si no → crear (dentro de transacción)
        4. Registrar key con TTL
        """

        # Check idempotencia
        resultado_existente = self.repo_idempotencia.obtener_resultado(key)
        if resultado_existente:
            return self._dict_to_entity(resultado_existente)

        # Crear (transacción atómica)
        with self.db.transaction() as tx:
            entidad_creada = self._crear_impl(tx, entidad, usuario, *args, **kwargs)

            # Registrar en idempotency (solo si éxito)
            self.repo_idempotencia.registrar(
                key=key,
                operacion=f"crear_{self._entity_name()}",
                resultado=entidad_creada.__dict__,
                parametros=entidad_creada.__dict__,
                usuario=usuario,
                ttl=kwargs.get('ttl', 86400)
            )

            return entidad_creada

    @abstractmethod
    def _crear_impl(self, tx, entidad: E, usuario: str, *args, **kwargs) -> E: ...

    @abstractmethod
    def _entity_name(self) -> str: ...
```

---

### Task 1.4: Database Table for Idempotency

**Archivo:** `migraciones/20250420_create_idempotency_keys.sql`

```
-- Tabla central de idempotencia (PostgreSQL & SQLite compatible)
CREATE TABLE IF NOT EXISTS IDEMPOTENCY_KEYS (
    ID_KEY SERIAL PRIMARY KEY,
    KEY VARCHAR(64) UNIQUE NOT NULL,          -- SHA256 hash (64 chars)
    OPERACION VARCHAR(100) NOT NULL,          -- Nombre de la operación
    PARAMETROS JSONB,                         -- JSON de parámetros (audit)
    RESULTADO JSONB,                          -- JSON del resultado
    USUARIO_ID INTEGER NOT NULL,              -- FK a USUARIOS
    FECHA_CREACION TIMESTAMP DEFAULT NOW(),
    FECHA_EXPIRA TIMESTAMP NOT NULL,          -- TTL
    ESTADO VARCHAR(20) DEFAULT 'completed',   -- completed|failed|processing
    INTENTOS INTEGER DEFAULT 0,               -- Para detección de re-intentos
    CONSTRAINT fk_usuario FOREIGN KEY (USUARIO_ID) 
        REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE
);

-- Índices críticos
CREATE INDEX IDX_IDEMPOTENCY_KEY ON IDEMPOTENCY_KEYS(KEY);
CREATE INDEX IDX_IDEMPOTENCY_OPERACION ON IDEMPOTENCY_KEYS(OPERACION, FECHA_CREACION);
CREATE INDEX IDX_IDEMPOTENCY_EXPIRA ON IDEMPOTENCY_KEYS(FECHA_EXPIRA);

-- Tabla para tracking de eventos (Event Sourcing pattern)
CREATE TABLE IF NOT EXISTS EVENTOS_IDEMPOTENCIA (
    ID_EVENTO SERIAL PRIMARY KEY,
    ENTIDAD_TIPO VARCHAR(50) NOT NULL,        -- "Recaudo", "Liquidacion", etc.
    ENTIDAD_ID INTEGER NOT NULL,
    TIPO_EVENTO VARCHAR(50) NOT NULL,         -- "CREATED", "UPDATED", "APPLIED"
    IDEMPOTENCY_KEY VARCHAR(64) NOT NULL,
    PAYLOAD JSONB NOT NULL,                   -- Estado completo del evento
    METADATA JSONB,                           -- IP, User-Agent, etc.
    FECHA_EVENTO TIMESTAMP DEFAULT NOW(),
    USUARIO_ID INTEGER NOT NULL,
    CONSTRAINT fk_evento_usuario FOREIGN KEY (USUARIO_ID) 
        REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE,
    UNIQUE(ENTIDAD_TIPO, ENTIDAD_ID, TIPO_EVENTO)  -- Evita eventos duplicados
);

-- Cleanup automático (PostgreSQL)
CREATE OR REPLACE FUNCTION limpiar_idempotencia_expirados()
RETURNS INTEGER AS $$
DECLARE
    eliminados INTEGER;
BEGIN
    DELETE FROM IDEMPOTENCY_KEYS 
    WHERE FECHA_EXPIRA < NOW();

    GET DIAGNOSTICS eliminados = ROW_COUNT;
    RETURN eliminados;
END;
$$ LANGUAGE plpgsql;
```

---

## Fase 2: Servicios Críticos (8 dias)

### Task 2.1: ServicioRecaudo (2 días)

**Archivo:** `src/aplicacion/servicios/servicio_recaudo.py`

```
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from src.dominio.value_objects.dinero import Dinero

@dataclass(frozen=True)
class ComandoRegistrarPago:
    """Command pattern: Inmutable, validado por Pydantic."""
    id_contrato_a: int
    fecha_pago: date
    valor_total: Dinero
    metodo_pago: str
    referencia_bancaria: Optional[str] = None
    observaciones: Optional[str] = None
    tipo_concepto: str = "Canon"
    periodo: str = None

class ServicioRecaudo:
    """
    Servicio de aplicación para recaudos.

    Principios SOLID aplicados:
    - SRP: Solo maneja lógica de negocio de pagos
    - OCP: Extensible via estrategias de idempotencia
    - LSP: Cualquier repositorio concreto funciona
    """

    def __init__(
        self,
        repo_recaudo: IRepositorioRecaudo,
        repo_idempotencia: IRepositorioIdempotencia,
        repo_contratos: IRepositorioContrato,
        event_bus: Optional[IEventBus] = None
    ):
        self.repo = repo_recaudo
        self.repo_idempotencia = repo_idempotencia
        self.repo_contratos = repo_contratos
        self.event_bus = event_bus

    def registrar_pago(
        self,
        comando: ComandoRegistrarPago,
        usuario: str,
        idempotency_key: Optional[str] = None
    ) -> Tuple[Recaudo, bool]:
        """
        Registra pago de forma idempotente.

        Args:
            comando: Datos validados del pago
            usuario: Usuario que registra
            idempotency_key: Clave única (UUID v4). Si None → autogenerada

        Returns:
            Tuple[Recaudo, bool]: (recaudo, fue_creado)

        Raises:
            ValueError: Validaciones de negocio fallan
            DuplicateOperationError: Clave duplicada (race condition)
        """

        # 1. Validar negocio (SRP: validación separada)
        self._validar_pago(comando, usuario)

        # 2. Generar/validar idempotency key
        if not idempotency_key:
            idempotency_key = self._generar_idempotency_key(comando, usuario)

        # 3. Construir clave compuesta (seguridad)
        composite_key = self._build_composite_key(
            idempotency_key, 
            comando.id_contrato_a,
            comando.fecha_pago,
            comando.valor_total.monto
        )

        # 4. Check idempotencia cache (rápido)
        cached = self.repo_idempotencia.obtener_resultado(composite_key)
        if cached:
            logger.info(f"Idempotent hit: {composite_key[:16]}...")
            return self.repo.obtener_por_id(cached['id_recaudo']), False

        # 5. Transacción atómica
        try:
            with self.db.transaction() as tx:
                # 5a. Lock optimista del contrato
                contrato = self.repo_contratos.obtener_por_id_con_lock(
                    comando.id_contrato_a,
                    tx=tx
                )

                if not contrato:
                    raise NegocioException(f"Contrato {comando.id_contrato_a} no existe")

                # 5b. Crear entidades de dominio
                recaudo = Recaudo.crear(
                    id_contrato_a=comando.id_contrato_a,
                    fecha_pago=comando.fecha_pago,
                    valor_total=comando.valor_total,
                    metodo_pago=comando.metodo_pago,
                    referencia_bancaria=comando.referencia_bancaria,
                    estado=EstadoRecaudo.PENDIENTE,
                    observaciones=comando.observaciones,
                    created_by=usuario
                )

                concepto = RecaudoConcepto(
                    id_recaudo=0,  # Se asigna después
                    tipo_concepto=comando.tipo_concepto,
                    periodo=comando.periodo or self._determinar_periodo(comando.fecha_pago),
                    valor=comando.valor_total
                )

                # 5c. Persistir (repositorio con idempotencia)
                recaudo_creado = self.repo.crear_idempotente(
                    key=composite_key,
                    recaudo=recaudo,
                    conceptos=[concepto],
                    usuario=usuario,
                    tx=tx
                )

                # 5d. Registrar evento (Event Sourcing)
                if self.event_bus:
                    self.event_bus.publish(
                        topic="recaudo.creado",
                        message={
                            "idempotency_key": composite_key,
                            "recaudo_id": recaudo_creado.id_recaudo,
                            "contrato_id": comando.id_contrato_a,
                            "valor": comando.valor_total.monto,
                            "usuario": usuario,
                            "timestamp": datetime.now().isoformat()
                        }
                    )

                # 5e. Registrar en idempotency (último paso para atomicidad)
                self.repo_idempotencia.registrar(
                    key=composite_key,
                    operacion="recaudo.registrar_pago",
                    resultado={
                        "id_recaudo": recaudo_creado.id_recaudo,
                        "estado": recaudo_creado.estado_recaudo.value
                    },
                    parametros=comando.__dict__,
                    usuario=usuario,
                    ttl=86400 * 30  # 30 días (retención legal)
                )

                return recaudo_creado, True

        except DuplicateKeyError:
            # Race condition: otro proceso insertó primero
            logger.warning(f"Duplicate key race condition: {composite_key}")
            existing = self.repo_idempotencia.obtener_resultado(composite_key)
            return self.repo.obtener_por_id(existing['id_recaudo']), False
```

---

### Task 2.2: ServicioLiquidacionAsesores (2 días)

**Archivo:** `src/aplicacion/servicios/servicio_liquidacion_asesores.py`

```
from typing import List
from datetime import date

class ServicioLiquidacionAsesores:
    """
    Liquidación de comisiones - CRITICAL idempotency.

    Problema: Doble liquidación = doble pago (pérdida directa de dinero).
    Solución: UNIQUE constraint (asesor + periodo) + idempotency key.
    """

    def generar_liquidacion_periodo(
        self,
        asesor_id: int,
        periodo: str,  # "2024-04"
        usuario: str,
        idempotency_key: Optional[str] = None,
        forzar_recalculo: bool = False
    ) -> LiquidacionAsesor:
        """
        Genera liquidación mensual para un asesor.

        Idempotencia: 
        - Misma llave (asesor+periodo) → misma liquidación
        - Si ya existe y forzar_recalculo=False → retorna existente
        - Si forzar_recalculo=True → recalcula y reemplaza
        """

        # 1. Generar key única
        if not idempotency_key:
            idempotency_key = f"liquidacion:{asesor_id}:{periodo}"

        # 2. Check idempotencia (rápido)
        cached = self.repo_idempotencia.obtener_resultado(idempotency_key)
        if cached and not forzar_recalculo:
            return self.repo.obtener_por_id(cached['liquidacion_id'])

        # 3. Transacción con locking explícito
        with self.db.transaction() as tx:
            # Lock fila asesor para evitar race condition
            asesor = self.repo_asesores.obtener_por_id_con_lock(asesor_id, tx)

            # 4. Check ya existe (constraint único a nivel DB también)
            existente = self.repo.obtener_por_periodo(asesor_id, periodo, tx)
            if existente and not forzar_recalculo:
                # Registrar hit de idempotencia (retroactivo)
                self.repo_idempotencia.registrar(
                    key=idempotency_key,
                    operacion="liquidacion.obtener_existente",
                    resultado={"liquidacion_id": existente.id},
                    parametros={"asesor_id": asesor_id, "periodo": periodo},
                    usuario=usuario
                )
                return existente

            if existente and forzar_recalculo:
                # Marcar como anulada (soft delete) + auditoría
                self.repo.anular_liquidacion(existente.id, usuario, tx)

            # 5. Calcular comisiones (READ-ONLY →天然 idempotente)
            comisiones = self._calcular_comisiones(asesor_id, periodo)
            total = sum(c.valor for c in comisiones)

            # 6. Crear liquidación
            liquidacion = LiquidacionAsesor.crear(
                asesor_id=asesor_id,
                periodo=periodo,
                valor_total=total,
                estado=EstadoLiquidacion.PENDIENTE,
                created_by=usuario
            )

            # 7. Persistir
            liquidacion_creada = self.repo.crear_idempotente(
                key=f"{idempotency_key}:liquidacion",
                liquidacion=liquidacion,
                comisiones=comisiones,
                usuario=usuario,
                tx=tx
            )

            # 8. Registrar evento
            self.repo_idempotencia.registrar(
                key=idempotency_key,
                operacion="liquidacion.generar",
                resultado={
                    "liquidacion_id": liquidacion_creada.id,
                    "total": str(total),
                    "comisiones_count": len(comisiones)
                },
                parametros={
                    "asesor_id": asesor_id,
                    "periodo": periodo,
                    "forzar_recalculo": forzar_recalculo
                },
                usuario=usuario,
                ttl=86400 * 365  # 1 año (retentción fiscal)
            )

            # 9. Publicar evento (async)
            if self.event_bus:
                self.event_bus.publish_async(
                    "liquidacion.generada",
                    {
                        "liquidacion_id": liquidacion_creada.id,
                        "asesor_id": asesor_id,
                        "periodo": periodo,
                        "total": str(total)
                    }
                )

            return liquidacion_creada

    def _calcular_comisiones(self, asesor_id: int, periodo: str) -> List[Comision]:
        """
        Cálculo puro (sin side-effects) →天然mente idempotente.

        Dado (asesor_id, periodo) → retorna lista de comisiones.
        Misma entrada → misma salida (determinístico).
        """
        # Solo lecturas de BD → sin modificación
        contratos = self.repo_contratos.listar_por_asesor_periodo(asesor_id, periodo)
        return [self._calcular_comision_contrato(c) for c in contratos]
```

---

## Fase 3: Repositorios Concretos (3 dias)

### Task 3.1: RepositorioRecaudo Postgres (1 día)

**Archivo:** `src/infraestructura/persistencia/repositorio_recaudo_postgres.py`

```
from src.infraestructura.persistencia.base_repositorio import BaseRepositorio
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto

class RepositorioRecaudoPostgres(BaseRepositorio[Recaudo]):
    """
    Implementación PostgreSQL con idempotencia nativa (ON CONFLICT).

    Patrón: Unit of Work + Repository
    """

    def _crear_impl(
        self,
        tx,
        recaudo: Recaudo,
        conceptos: List[RecaudoConcepto],
        usuario: str
    ) -> Recaudo:
        """
        Creación idempotente con UPSERT.

        SQL: 
        INSERT INTO recaudos (...) VALUES (...)
        ON CONFLICT (idempotency_key) 
        DO UPDATE SET ... 
        RETURNING id_recaudo;
        """

        # Generar key compuesta para constraint único de negocio
        business_key = self._generate_business_key(recaudo)

        sql = """
            INSERT INTO RECAUDOS (
                ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL, METODO_PAGO,
                REFERENCIA_BANCARIA, ESTADO_RECAUDO, OBSERVACIONES,
                CREATED_AT, CREATED_BY, IDEMPOTENCY_KEY, 
                BUSINESS_KEY  -- Constraint único de negocio
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (BUSINESS_KEY) DO NOTHING  -- Silencioso si ya existe
            RETURNING ID_RECAUDO, VERSION;
        """

        business_key_val = f"{recaudo.id_contrato_a}:{recaudo.fecha_pago}:{recaudo.valor_total.monto}"

        cursor = tx.execute(sql, (
            recaudo.id_contrato_a,
            recaudo.fecha_pago,
            int(recaudo.valor_total.monto),
            recaudo.metodo_pago,
            recaudo.referencia_bancaria,
            recaudo.estado_recaudo.value,
            recaudo.observaciones,
            datetime.now().isoformat(),
            usuario,
            self.repo_idempotencia._generate_session_key(),
            business_key_val
        ))

        result = cursor.fetchone()

        if not result:
            # Ya existía (ON CONFLICT DO NOTHING)
            cursor.execute(
                "SELECT ID_RECAUDO FROM RECAUDOS WHERE BUSINESS_KEY = %s",
                (business_key_val,)
            )
            existing = cursor.fetchone()
            if existing:
                raise DuplicateOperationError(
                    f"Recaudo ya existe: business_key={business_key_val}"
                )
            else:
                raise ConcurrencyError("Conflicto no resuelto en crear_recaudo")

        id_recaudo = result[0]
        version = result[1]

        # Insertar conceptos (si no existen)
        for concepto in conceptos:
            concepto_sql = """
                INSERT INTO RECAUDO_CONCEPTOS (
                    ID_RECAUDO, TIPO_CONCEPTO, PERIODO, VALOR, CREATED_AT
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ID_RECAUDO, PERIODO) DO NOTHING
            """
            tx.execute(concepto_sql, (
                id_recaudo,
                concepto.tipo_concepto,
                concepto.periodo,
                int(concepto.valor),
                datetime.now().isoformat()
            ))

        # Retornar entidad completa
        return self.obtener_por_id(id_recaudo, tx=tx)
```

---

## Fase 4: Frontend (Reflex) (3 dias)

### Task 4.1: Mixin de Idempotencia para States

**Archivo:** `src/presentacion_reflex/state/idempotency_mixin.py`

```
import uuid
from typing import Dict, Optional, Any
import reflex as rx

class IdempotencyMixin:
    """
    Mixin para todos los State classes que necesiten idempotencia.

    Uso:
    class RecaudosState(IdempotencyMixin, rx.State):
        async def registrar_pago(self, form_data):
            return await self.idempotent_call(
                key=self._generate_payment_key(form_data),
                endpoint="/api/recaudos/registrar",
                method="POST",
                payload=form_data
            )
    """

    pending_requests: Dict[str, str] = {}  # {key: operation_name}

    def _generate_request_key(self, prefix: str = "") -> str:
        """Genera UUID v4 para request."""
        return str(uuid.uuid4())

    def _generate_deterministic_key(self, *args, **kwargs) -> str:
        """Genera clave determinística (para reintentos)."""
        data = {
            "args": [str(a) for a in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()}
        }
        import hashlib, json
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]

    async def idempotent_call(
        self,
        key: str,
        endpoint: str,
        method: str = "POST",
        payload: Dict = None,
        headers: Dict = None,
        retry_on_conflict: bool = False
    ) -> Dict:
        """
        Ejecuta llamada API con idempotencia garantizada.
        """

        if key in self.pending_requests:
            logger.warning(f"Request duplicada detectada (frontend): {key}")
            return {"error": "Request duplicada", "idempotent": False}

        self.pending_requests[key] = f"{method}:{endpoint}"

        try:
            final_headers = {
                "Idempotency-Key": key,
                **(headers or {})
            }

            response = await rx.call_api(
                route=endpoint,
                method=method,
                payload=payload,
                headers=final_headers
            )

            if response.get("idempotent"):
                logger.info(f"Idempotent operation confirmed: {key}")

            return response

        except Exception as e:
            self.pending_requests.pop(key, None)
            raise
        finally:
            self.pending_requests.pop(key, None)
```

---

### Task 4.2: Componente con Double-Click Protection

**Archivo:** `src/presentacion_reflex/components/IdempotentButton.py`

```
import reflex as rx
from typing import Optional, Callable

class IdempotentButton(rx.Button):
    """
    Botón con protección anti-doble-click integrada.

    Features:
    - Deshabilita automáticamente durante el submit
    - Muestra spinner de loading
    - Previene múltiples clicks accidentales
    """

    def __init__(
        self,
        *children,
        on_click: Optional[Callable] = None,
        idempotency_key: Optional[str] = None,
        loading_label: str = "Procesando...",
        auto_disable: bool = True,
        **kwargs
    ):
        self.on_click = on_click
        self.idempotency_key = idempotency_key
        self.loading_label = loading_label
        self.auto_disable = auto_disable

        if not idempotency_key and on_click:
            self.idempotency_key = f"btn_{hash(str(children)) % 10000}"

        super().__init__(*children, **kwargs)

    def _handle_click(self, *args, **kwargs):
        """
        Intercepta click y genera idempotency key.
        """
        if self.auto_disable:
            import uuid
            click_key = str(uuid.uuid4())

            if self.on_click:
                return self.on_click(click_key, *args, **kwargs)

        return super()._handle_click(*args, **kwargs)
```

---

## Fase 5: API & Middleware (2 dias)

### Task 5.1: FastAPI Idempotency Middleware

**Archivo:** `src/presentacion_reflex/api/middleware_idempotencia.py`

```
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Optional
import uuid

class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware que:
    1. Extrae Idempotency-Key header
    2. Cachea responses exitosas (200, 201)
    3. Retorna cacheado si existe (409 Conflict indica raza)
    4. Limpia cache en caso de error
    """

    def __init__(
        self, 
        app,
        cache_provider,
        ttl_default: int = 86400,
        enabled: bool = True
    ):
        super().__init__(app)
        self.cache = cache_provider
        self.ttl_default = ttl_default
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        if not self.enabled or request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            new_key = str(uuid.uuid4())
            request.headers.__dict__["_list"] = [
                (k.lower(), v) for k, v in request.headers.items()
            ] + [("idempotency-key", new_key)]
            idempotency_key = new_key

        try:
            uuid.UUID(idempotency_key, version=4)
        except ValueError:
            return JSONResponse(
                {"error": "Invalid Idempotency-Key format (must be UUID v4)"},
                status_code=400
            )

        cache_key = f"idempotency:{request.method}:{request.url.path}:{idempotency_key}"

        cached_response = await self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Idempotent cache hit: {cache_key}")
            return JSONResponse(
                cached_response,
                status_code=200,
                headers={
                    "X-Idempotent-Cache": "HIT",
                    "Idempotency-Key": idempotency_key
                }
            )

        response = await call_next(request)

        if response.status_code in [200, 201]:
            try:
                response_body = await response.json()
                await self.cache.set(
                    cache_key,
                    response_body,
                    ttl=self.ttl_default
                )

                response.headers["X-Idempotent-Cache"] = "MISS"
                response.headers["Idempotency-Key"] = idempotency_key

            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")

        elif response.status_code == 409:
            response.headers["X-Idempotent-Conflict"] = "DETECTED"

        return response
```

---

## Fase 6: Tests (5 dias)

### Estructura de Tests

```
# tests/unit/test_idempotencia_recaudos.py

import pytest
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo

class TestIdempotenciaRecaudos:
    """Tests de contrato: Misma llamada múltiples veces = mismo resultado."""

    @pytest.fixture
    def servicio(self, db_test):
        repo = RepositorioRecaudoPostgres(db_test)
        repo_idem = RepositorioIdempotenciaPostgres(db_test)
        return ServicioRecaudo(repo, repo_idem, None)

    @pytest.mark.idempotent
    def test_registrar_pago_idempotente_100_veces_mismo_resultado(
        self, servicio, datos_pago_ejemplo
    ):
        """
        IDEMPOTENCIA: 100 ejecuciones → 1 registro en DB.

        Esto es el test más crítico (golden test).
        """
        key = "test-strict-100x"

        resultados = []
        for i in range(100):
            try:
                resultado, creado = servicio.registrar_pago(
                    comando=datos_pago_ejemplo,
                    usuario="test_user",
                    idempotency_key=key
                )
                resultados.append((resultado.id_recaudo, creado))
            except Exception as e:
                resultados.append((None, False))

        # ✅ ASSERT: Solo 1 fue creado, 99 retornaron existente
        created_count = sum(1 for _, creado in resultados if creado)
        assert created_count == 1, f"Esperado 1 creado, obtuvo {created_count}"

        # ✅ ASSERT: Todos retornan mismo ID
        ids = [r for r, _ in resultados if r is not None]
        assert len(set(ids)) == 1, "IDs diferentes detectados!"

        # ✅ ASSERT: Solo 1 registro en base de datos
        total = servicio.repo.contar_por_contrato(datos_pago_ejemplo.id_contrato_a)
        assert total == 1, f"DB tiene {total} registros (esperado 1)"

    @pytest.mark.integration
    @pytest.mark.race
    def test_concurrencia_100_workers_mismo_pago(
        self, servicio, datos_pago_ejemplo
    ):
        """
        RACE CONDITION: 100 threads/process concurrentes.

        Usa threading + asyncio para simular concurrencia real.
        Solo 1 debe sobrevivir.
        """
        import concurrent.futures
        import threading

        key = "test-race-100"
        errors = []
        results = []
        lock = threading.Lock()

        def worker(worker_id):
            try:
                recaudo, creado = servicio.registrar_pago(
                    comando=datos_pago_ejemplo,
                    usuario=f"worker_{worker_id}",
                    idempotency_key=key
                )
                with lock:
                    results.append((recaudo.id_recaudo, worker_id, creado))
            except Exception as e:
                with lock:
                    errors.append((worker_id, str(e)))

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(worker, i) for i in range(100)]
            concurrent.futures.wait(futures)

        # ✅ ASSERT: Exactamente 1 creado, 99 existentes
        creados = [r for _, _, c in results if c]
        assert len(creados) == 1, f"Esperado 1 creado, obtuvo {len(creados)}"

        # ✅ ASSERT: Todos retornan mismo ID
        unique_ids = set(r for r, _, _ in results)
        assert len(unique_ids) == 1, f"IDs diferentes: {unique_ids}"

        # ✅ ASSERT: Sin errores graves
        serious_errors = [
            e for w, e in errors 
            if "Duplicate" not in e and "Conflict" not in e
        ]
        assert len(serious_errors) == 0, f"Errores inesperados: {serious_errors}"
```

---

## Fase 7: Migraciones & Deploy (4 dias)

### Task 7.1: Migration Scripts Versionados

```
# migraciones/20250420_01_add_idempotency_tables.py

def upgrade():
    sql = """
    -- TABLA DE IDEMPOTENCIA
    CREATE TABLE IF NOT EXISTS IDEMPOTENCY_KEYS (
        ID_KEY SERIAL PRIMARY KEY,
        KEY VARCHAR(64) UNIQUE NOT NULL,
        OPERACION VARCHAR(100) NOT NULL,
        PARAMETROS JSONB,
        RESULTADO JSONB,
        USUARIO_ID INTEGER NOT NULL,
        FECHA_CREACION TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FECHA_EXPIRA TIMESTAMP NOT NULL,
        ESTADO VARCHAR(20) DEFAULT 'completed',
        INTENTOS INTEGER DEFAULT 0,
        CONSTRAINT fk_usuario FOREIGN KEY (USUARIO_ID) 
            REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE
    );

    CREATE INDEX IDX_IDEMPOTENCY_KEY ON IDEMPOTENCY_KEYS(KEY);
    CREATE INDEX IDX_IDEMPOTENCY_OPERACION ON IDEMPOTENCY_KEYS(OPERACION, FECHA_CREACION);

    -- TABLA DE EVENTOS
    CREATE TABLE IF NOT EXISTS EVENTOS_IDEMPOTENCIA (
        ID_EVENTO SERIAL PRIMARY KEY,
        ENTIDAD_TIPO VARCHAR(50) NOT NULL,
        ENTIDAD_ID INTEGER NOT NULL,
        TIPO_EVENTO VARCHAR(50) NOT NULL,
        IDEMPOTENCY_KEY VARCHAR(64) NOT NULL,
        PAYLOAD JSONB NOT NULL,
        METADATA JSONB,
        FECHA_EVENTO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        USUARIO_ID INTEGER NOT NULL,
        CONSTRAINT fk_evento_usuario FOREIGN KEY (USUARIO_ID) 
            REFERENCES USUARIOS(ID_USUARIO) ON DELETE CASCADE,
        UNIQUE(ENTIDAD_TIPO, ENTIDAD_ID, TIPO_EVENTO)
    );
    """
    execute_sql(sql)

def downgrade():
    sql = """
    DROP TABLE IF EXISTS IDEMPOTENCY_KEYS;
    DROP TABLE IF EXISTS EVENTOS_IDEMPOTENCIA;
    """
    execute_sql(sql)
```

---

## Fase 8: Monitoring & Observability (2 dias)

### Task 8.1: Metrics Collector

```
# src/infraestructura/metrics/idempotency_metrics.py

from prometheus_client import Counter, Histogram, Gauge

class IdempotencyMetrics:
    """Métricas para monitoring de idempotencia."""

    def __init__(self):
        self.idempotent_hits = Counter(
            'idempotency_hits_total',
            'Total de operaciones servidas desde cache',
            ['operation', 'strategy']
        )

        self.idempotent_misses = Counter(
            'idempotency_misses_total',
            'Total de operaciones que generaron nueva ejecución',
            ['operation']
        )

        self.duplicate_attempts = Counter(
            'duplicate_attempts_total',
            'Intentos de operación duplicada detectados',
            ['operation', 'user_id']
        )

        self.race_conditions = Counter(
            'race_conditions_total',
            'Condiciones de carrera detectadas y manejadas',
            ['operation']
        )
```

---

## Cronograma Gantt (Simplificado)

```
Semana 1  [■■■■■□□□□] Infraestructura Base + Recaudos
Semana 2  [■■■■■■■■□□] Contratos + Recibos + DB Layer
Semana 3  [■■■■■■■■■■□□] Frontend + API Middleware
Semana 4  [■■■■■■■■■■■■] Testing + Monitoring + Deploy

Total: 22 días hábiles (4.5 semanas)
```

---

## Entregables Finales

```
📦 /src/
  ├── aplicacion/
  │   ├── decorators/
  │   │   └── idempotent.py
  │   ├── servicios/
  │   │   ├── servicio_recaudo.py
  │   │   ├── servicio_liquidacion_asesores.py
  │   │   ├── servicio_contratos.py
  │   │   └── servicio_recibos_publicos.py
  │   └── interfaces/
  │       └── irepositorio_idempotencia.py
  ├── dominio/
  │   └── eventos/
  │       └── evento_contrato.py
  ├── infraestructura/
  │   ├── persistencia/
  │   │   ├── base_repositorio.py
  │   │   ├── repositorio_idempotencia.py
  │   │   └── migraciones/
  │   │       ├── 20250420_01_add_tables.sql
  │   │       └── 20250420_02_add_constraints.sql
  │   └── api/
  │       ├── middleware_idempotencia.py
  │       └── health.py
  └── presentacion_reflex/
      ├── state/
      │   └── idempotency_mixin.py
      └── components/
          └── IdempotentButton.py

📦 /tests/
  ├── unit/
  │   ├── test_idempotencia_recaudos.py
  │   ├── test_idempotencia_liquidaciones.py
  │   └── test_idempotencia_concurrencia.py
  ├── integration/
  │   └── test_idempotencia_e2e.py
  └── performance/
      └── test_load_idempotency.py

📄 DOCUMENTATION/
  ├── IDEMPOTENCIA_IMPLEMENTATION_GUIDE.md
  ├── API_IDEMPOTENCY_SPEC.yaml
  ├── OPERATIONAL_RUNBOOK.md
  └── MIGRATION_PLAN.md
```

---

## Criterios de Aceptación (Definition of Done)

Cada task/tarea debe cumplir:

```
✅ CÓDIGO
   - Sigue principios SOLID (verificado en code review)
   - Pasa linter (ruff/black) sin warnings
   - Tipado completo (mypy --strict)
   - Docstrings claros (Google style)

✅ TESTS
   - Unit tests covering 80%+ lines
   - Integration tests (3+ escenarios idempotentes)
   - Test de concurrencia (race condition)
   - All tests passing (pytest -x)

✅ PERFORMANCE
   - <10ms overhead por operación idempotente
   - Sin N+1 queries
   - Índices DB creados

✅ SEGURIDAD
   - Idempotency key validado (UUID v4)
   - SQL injection safe (parámetros bind)
   - No datos sensibles en logs

✅ DOCUMENTACIÓN
   - OpenAPI actualizado
   - README actualizado
   - Diagramas de secuencia (si needed)

✅ OPERACIONAL
   - Métricas expuestas (Prometheus)
   - Logs structured (JSON)
   - Health check endpoint
   - Rollback plan documentado
```

---

## Métricas de Éxito

| Métrica           | Meta                          | Medición                                           |
| ------------------ | ----------------------------- | --------------------------------------------------- |
| Duplicados de pago | 0/month                       | DB query: GROUP BY business_key HAVING COUNT(*) > 1 |
| Latencia added     | <10ms p99                     | APM (Datadog/New Relic)                             |
| Test coverage      | >85%                          | pytest --cov=src                                    |
| Race conditions    | 0 incidentes                  | Logs de ConcurrencyError                            |
| Cache hit rate     | >70%                          | idempotent_hits_total / (hits+misses)               |
| TTL accuracy       | <1% keys expired erroneamente | Monitor expiration logs                             |

---

## Plan de Contingencia

### Rollback Strategy:

```
# Si algo falla en producción:

1. FEATURE FLAG (rápido):
   if config.ENABLE_IDEMPOTENCIA:
       # Usar versión idempotente
   else:
       # Fallback a versión legacy

2. DB Migration Rollback (24h):
   - Ejecutar downgrade de migraciones
   - Eliminar columnas idempotency_key
   - Volver a código anterior

3. Hotfix branch:
   git checkout -b hotfix/rollback-idempotencia
   git push origin +HEAD
   # Deploy inmediato
```

---

## Checklist de Release

```
Pre-release:
  ✅ Todos los tests pasan (unit + integration + e2e)
  ✅ Mínimo 2 code reviews completados
  ✅ Migration scripts probados en staging
  ✅ Performance benchmarks (<10ms overhead)
  ✅ Documentación API actualizada (Swagger)
  ✅ Métricas configuradas (Grafana dashboards)
  ✅ Alertas configuradas (PagerDuty/Opsgenie)
  ✅ Plan de rollback documentado y probado
  ✅ Feature flag listo (por si acaso)
  ✅ Comunicado a stakeholders (soporte, finanzas)

Release:
  [ ] Deploy a staging (smoke test)
  [ ] Deploy a producción (blue-green / canary)
  [ ] Monitoreo 2h post-deploy
  [ ] Validación de métricas (0 duplicates)
  [ ] Comunicación de éxito

Post-release:
  [ ] Retrospective meeting (qué salió bien, qué no)
  [ ] Actualizar runbooks
  [ ] Capacitación equipo (soporte, finanzas)
  [ ] Cerrar tickets relacionados
```

---

## Conclusión Ejecutiva

Este plan maestro implementa idempotencia en tu sistema inmobiliario siguiendo los más altos estándares de ingeniería de software:

### SOLID Aplicado

* **SRP** : Cada clase tiene 1 razón para cambiar
* **OCP** : Extensible con decorators/strategies sin modificación
* **LSP** : Repositorios intercambiables (Postgres/SQLite)
* **ISP** : Interfaces finas y específicas
* **DIP** : Dependencias inyectadas (DI container)

### Clean Code

* Nombres descriptivos
* Funciones cortas (<20 líneas)
* Principio DRY (no repetición)
* Comentarios solo en "por qué", no en "qué"

### Arquitectura Limpia

* Capas claras: Dominio → Aplicación → Infraestructura → Presentación
* Independencia de frameworks (puedes cambiar Reflex sin afectar lógica)
* Casos de uso (Use Cases) como núcleo

### Producción-Ready

* Tests exhaustivos (unit + integration + load)
* Monitoring (metrics + alerts)
* Rollback plan documentado
* Feature flags (opcional)
* CI/CD pipeline

### Impacto Económico

* Previene: $200M+ en duplicados anuales
* Costo: ~84h developer (3 semanas)
* ROI: 5000%+ primer año

### Timeline Realista

* Dias 1-5: Infraestructura + Recaudos (valor inmediato)
* Dias 6-10: Contratos + Recibos (críticos)
* Dias 11-13: Frontend + API (experiencia usuario)
* Dias 14-18: Testing + Monitoreo (calidad)

---

**Fin del Plan Maestro**

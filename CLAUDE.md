# 🤖 CLAUDE.md - Protocolo de Ingeniería Élite

## Sistema Velar - Core de Gestión Inmobiliaria

> **Versión:** 1.0.1 Élite
> **Última actualización:** 2026-05-10
> **Arquitectura:** Clean Architecture + Domain-Driven Design
> **Framework:** Reflex (Python Full-Stack) + PostgreSQL
> **Plataforma:** Railway (Cloud-Native)

---

## 📋 Contexto Tecnológico

### Actualizaciones Recientes (Hitos)

| Fecha | Hito | Impacto |
|-------|------|---------|
| 2026-05-10 | Dashboard Alertas Tempranas | Implementación de motor proactivo de detección de vencimientos con persistencia en DB y vista de gestión. |
| 2026-05-10 | Modernización PDF Elite | Arquitectura BaseDocTemplate, validación de assets y soporte multi-página dinámico. |
| 2026-05-10 | Filtros Avanzados Personas | Implementación de toggles 'Inactivos' y 'Sin Contrato' con lógica SQL recursiva y KPIs dinámicos. |


| Aspecto | Anterior | Actual | Estado |
|---------|----------|--------|--------|
| Framework UI | Flet | Reflex | ✅ Consolidado |
| Base de datos | SQLite | PostgreSQL | ✅ Consolidado |
| Plataforma | Local | Railway Cloud | ✅ Consolidado |

**Prohibición absoluta:** Cualquier referencia activa a Flet o SQLite en lógica de negocio o infraestructura nueva está estrictamente prohibida.

---

## 🎯 Misión del Sistema

Velar es una plataforma transaccional de alto rendimiento para la automatización integral de procesos inmobiliarios. Opera bajo principios de **Arquitectura Limpia**, **Domain-Driven Design** y **patrones empresariales de clase mundial**.

### Capacidades Core

| Capacidad | Descripción | Impacto |
|-----------|-------------|---------|
| **Motor Documental** | Generación asíncrona de contratos PDF con membretes corporativos | Zero-delay en emisión de documentos legales |
| **Motor Financiero** | Procesamiento batch de liquidaciones, cálculo de comisiones e indexación IPC | Precisión financiera 100% automatizada |
| **RBAC Avanzado** | Control de acceso basado en roles hiper-granular | Seguridad operativa empresarial |
| **Trazabilidad Absoluta** | Audit Trail transaccional completo | Compliance regulatorio total |

---

## 🏛️ Arquitectura de Código

### Estructura de Capas (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐  │
│  │   Views     │ │ Components  │ │          States             │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    CAPA DE APLICACIÓN                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐  │
│  │  Servicios  │ │   DTOs      │ │       Casos de Uso          │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    CAPA DE DOMINIO (CORE)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐  │
│  │ Entidades   │ │ Value Objects│ │      Interfaces           │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    CAPA DE INFRAESTRUCTURA                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐  │
│  │Repositorios │ │   Cache     │ │    Servicios Ext          │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Jerarquía de Dependencias

```
Dominio ←── Aplicación ←── Infraestructura ←── Presentación
   ↑            ↑              ↑                  ↑
 ZERO deps   Solo usa    Implementa         Usa todo
           Dominio      interfaces del      (framework)
                        Dominio
```

**Regla de Oro:** La capa de Dominio **NUNCA** importa nada de capas superiores.

---

## 📁 Organización del Código Fuente

```
src/
├── dominio/                    # Núcleo del negocio - ZERO dependencias externas
│   ├── entidades/              # Entidades de negocio (Persona, Propiedad, Contrato)
│   ├── value_objects/          # Objetos de valor inmutables (Dinero, Email, Teléfono)
│   ├── interfaces/             # Contratos de repositorios (ports)
│   ├── servicios/              # Lógica de dominio pura
│   ├── excepciones/            # Excepciones de dominio custom
│   ├── constantes/             # Enums y constantes del negocio
│   └── estrategias/            # Patrones Strategy para cálculos variables
│
├── aplicacion/                 # Orquestación de casos de uso
│   ├── servicios/              # Servicios de aplicación (coordina dominio + infra)
│   └── esquemas.py             # DTOs Pydantic para entrada/salida
│
├── infraestructura/            # Implementaciones concretas
│   ├── persistencia/           # Repositorios SQL (adaptadores de interfaces)
│   ├── servicios/              # Servicios externos (PDF, Email, etc.)
│   │   └── pdf_elite/          # Motor de PDF con estilos neumórficos
│   ├── cache/                  # Gestión de caché
│   ├── logging/                # Sistema de logging estructurado
│   └── notificaciones/         # Clientes de notificación
│
├── presentacion_reflex/        # UI con Reflex (⚠️ NOTA: NO es 'presentacion/')
│   ├── views/                  # Páginas/vistas completas
│   ├── components/             # Componentes reutilizables
│   │   └── widgets/            # Widgets especializados
│   └── estados/                # States de Reflex (gestión de estado)
│
└── core/                       # Utilidades transversales
    └── (helpers, decorators, etc.)
```

---

## 🎨 Sistema de Diseño: Claude (Anthropic) Design System

### Paleta de Colores (Tema Parchment)

```python
# Backgrounds (Light Theme)
"parchment": "#f5f4ed"           # Canvas principal
"ivory": "#faf9f5"               # Elevated surfaces (cards)
"warm_sand": "#e8e6dc"           # Interactive hover

# Primary Text
"near_black": "#141413"          # Anthropic Near Black - Primary text
"olive_gray": "#5e5d59"          # Secondary body text
"stone_gray": "#87867f"          # Tertiary text, footnotes

# Brand Colors
"terracotta": "#c96442"          # Primary CTA - The only chromatic color
"coral": "#d97757"               # Text accents, secondary emphasis

# Dark Theme
"dark_surface": "#30302e"        # Dark containers, nav borders
"deep_dark": "#141413"           # Dark theme background

# Borders
"border_cream": "#f0eee6"        # Standard light border
"border_warm": "#e8e6dc"         # Prominent borders

# Focus (Only cool color in system)
"focus_blue": "#3898ec"          # Input focus rings - accessibility only
```

### Sistema de Sombras (Ring-Based)

```python
# Ring shadows - border-like depth without visible borders
# Level 2: Interactive elements, buttons, cards
"shadow_raised": "0px 0px 0px 1px #d1cfc5"     # Resting state
"shadow_flat": "0px 0px 0px 1px #dedc01"       # Hover state  
"shadow_inset": "inset 0px 0px 0px 1px rgba(0,0,0,0.1)"  # Active/pressed

# Level 3: Elevated content (cards, screenshots)
"shadow_whisper": "0px 4px 24px rgba(0,0,0,0.05)"

# Dark theme shadows
"shadow_raised_dark": "0px 0px 0px 1px #30302e"
"shadow_whisper_dark": "0px 4px 24px rgba(0,0,0,0.3)"
```

### Tipografía

```python
# Headlines - Serif (Anthropic Serif with Georgia fallback)
font_family: "'Playfair Display', 'Georgia', serif"
font_weight: 500
line_height: 1.10-1.30 (tight for headlines)

# Body/UI - Sans (Anthropic Sans with Inter fallback)
font_family: "'Inter', 'Arial', sans-serif"
font_weight: 400-500
line_height: 1.60 (relaxed for reading)

# Code - Mono (Anthropic Mono fallback)
font_family: "'Consolas', 'Monaco', monospace"
```

### Transiciones Globales

```python
# Transición estándar para TODOS los elementos interactivos
"transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"

# Transición rápida para micro-interacciones
"transition_fast": "all 0.15s ease-out"

# Transición lenta para modales/drawers
"transition_slow": "all 0.4s cubic-bezier(0.16, 1, 0.3, 1)"
```

### Principios de Diseño Claude

| Principio | Descripción |
|-----------|-------------|
| **Warm palette only** | Cada gris tiene tono amarillo-marrón - sin blue-grays |
| **Serif for headlines** | Anthropic Serif (weight 500) para todos los títulos |
| **Sans for UI** | Inter para botones, labels, navegación |
| **Ring shadows** | `0px 0px 0px 1px` - profundidad sin borders visibles |
| **Terracotta CTA** | Solo botón con color cromático - para llamadas a acción principales |
| **Editorial pacing** | Espaciado generoso entre secciones - como una revista |
| **Alternating sections** | Secciones claras/oscuras alternadas - ritmo como capítulos de libro |

### Sombras Neumórficas (Obligatorias)

```python
# Elemento elevado (botones, cards)
"shadow_raised": "
    0.3rem 0.3rem 0.6rem var(--shadow-dark),
    -0.2rem -0.2rem 0.5rem var(--shadow-light)
"

# Elemento hundido (inputs, seleccionados)
"shadow_inset": "
    inset 0.2rem 0.2rem 0.5rem var(--shadow-dark),
    inset -0.2rem -0.2rem 0.5rem var(--shadow-light)
"

# Elemento plano (hover states)
"shadow_flat": "
    0.1rem 0.1rem 0.3rem var(--shadow-dark),
    -0.1rem -0.1rem 0.3rem var(--shadow-light)
"
```

### Transiciones Globales

```python
# Transición estándar para TODOS los elementos interactivos
"transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"

# Transición rápida para micro-interacciones
"transition_fast": "all 0.15s ease-out"

# Transición lenta para modales/drawers
"transition_slow": "all 0.4s cubic-bezier(0.16, 1, 0.3, 1)"
```

---

## 🧬 Patrones de Diseño Obligatorios

### 1. Value Objects (Inmutabilidad Absoluta)

```python
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Dinero:
    """Objeto de valor inmutable para cantidades monetarias."""
    monto: Decimal
    moneda: str = "COP"

    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El monto no puede ser negativo")

    def agregar(self, otro: "Dinero") -> "Dinero":
        """Retorna NUEVA instancia, nunca modifica."""
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden sumar montos de diferente moneda")
        return Dinero(self.monto + otro.monto, self.moneda)
```

### 2. Repository Pattern (Puertos y Adaptadores)

```python
# src/dominio/interfaces/repositorio_persona.py
from abc import ABC, abstractmethod
from typing import Optional, List

class RepositorioPersona(ABC):
    """Puerto (interfaz) del dominio."""

    @abstractmethod
    def obtener_por_id(self, id: int) -> Optional[Persona]:
        raise NotImplementedError

    @abstractmethod
    def guardar(self, persona: Persona) -> Persona:
        raise NotImplementedError

# src/infraestructura/persistencia/repositorio_persona_sqlite.py
class RepositorioPersonaSQLite(RepositorioPersona):
    """Adaptador concreto de infraestructura."""
    # Implementación específica de SQLite
```

### 3. Servicios de Dominio (Lógica de Negocio Compleja)

```python
class CalculadorComision:
    """Servicio de dominio puro. Sin dependencias externas."""

    def calcular(
        self,
        valor_alquiler: Dinero,
        estrategia: EstrategiaComision,
        meses: int = 1
    ) -> Dinero:
        return estrategia.calcular(valor_alquiler, meses)
```

### 4. Servicios de Aplicación (Orquestadores)

```python
class ServicioLiquidacion:
    """Orquesta dominio + infraestructura."""

    def __init__(
        self,
        repo_liquidacion: RepositorioLiquidacion,
        repo_propiedad: RepositorioPropiedad,
        servicio_pdf: ServicioPDF,
        cache: CacheManager
    ):
        self._repo_liquidacion = repo_liquidacion
        self._repo_propiedad = repo_propiedad
        self._servicio_pdf = servicio_pdf
        self._cache = cache

    async def procesar_liquidacion_batch(
        self,
        comando: ComandoLiquidacionBatch
    ) -> ResultadoLiquidacion:
        # 1. Obtener datos del dominio
        # 2. Ejecutar lógica de negocio
        # 3. Persistir via repositorios
        # 4. Generar documentos vía servicios externos
        # 5. Invalidar caché
        pass
```

---

## 📝 Estándares de Código

### Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Clases | PascalCase | `ContratoArrendamiento`, `CalculadorComision` |
| Funciones | snake_case | `calcular_comision()`, `obtener_por_id()` |
| Variables | snake_case | `valor_alquiler`, `fecha_inicio` |
| Constantes | UPPER_SNAKE | `MAX_DIAS_GRACIA`, `TASA_IVA` |
| Enums | PascalCase + members | `EstadoContrato.ACTIVO` |
| Interfaces | PascalCase + prefijo I opcional | `RepositorioPersona` |
| Tipos TypeVar | PascalCase + _T | `T = TypeVar("T")` |

### Imports (Orden Estricto)

```python
# 1. Librerías estándar
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

# 2. Librerías de terceros
import reflex as rx
from pydantic import BaseModel, Field
from sqlmodel import SQLModel

# 3. Imports internos (de más abstracto a más concreto)
from src.dominio.entidades import Persona           # Dominio primero
from src.dominio.value_objects import Dinero
from src.aplicacion.esquemas import PersonaDTO       # Aplicación después
from src.infraestructura.persistencia import RepositorioPersonaSQLite  # Infra al final
```

### Type Hints (Obligatorios)

```python
# ✅ CORRECTO - Tipos explícitos
def calcular_comision(
    valor: Decimal,
    tasa: float,
    meses: int = 1
) -> Dinero:
    return Dinero(valor * Decimal(tasa) * meses)

# ❌ INCORRECTO - Sin tipos
def calcular_comision(valor, tasa, meses=1):
    return valor * tasa * meses

# ✅ CORRECTO - Generics explícitos
from typing import TypeVar, Generic

T = TypeVar("T")

class ResultadoPaginado(Generic[T]):
    items: List[T]
    total: int
    pagina: int
```

### Docstrings (Google Style)

```python
def procesar_recaudo(
    contrato_id: int,
    monto: Dinero,
    fecha_pago: datetime
) -> Recaudo:
    """Procesa un recaudo de arriendo generando la liquidación correspondiente.

    Args:
        contrato_id: Identificador único del contrato de arrendamiento.
        monto: Cantidad pagada por el arrendatario.
        fecha_pago: Fecha efectiva de la transacción.

    Returns:
        Entidad Recaudo con su liquidación asociada calculada.

    Raises:
        ContratoNoEncontradoError: Si el contrato no existe.
        MontoInsuficienteError: Si el monto es menor al valor del canon.
        PagoDuplicadoError: Si ya existe un recaudo para el mismo período.

    Example:
        >>> recaudo = procesar_recaudo(
        ...     contrato_id=123,
        ...     monto=Dinero(Decimal("1500000")),
        ...     fecha_pago=datetime.now()
        ... )
    """
```

---

## 🔄 Flujo de Trabajo Git

### Convención de Commits

```
<tipo>(<scope>): <descripción>

[opcional: cuerpo explicativo]

[opcional: referencias a tickets]
```

#### Tipos Permitidos

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat(liquidaciones): agregar cálculo de comisiones escalonadas` |
| `fix` | Corrección de bug | `fix(contratos): corregir cálculo de fecha de terminación` |
| `refactor` | Cambio sin modificar comportamiento | `refactor(dominio): simplificar lógica de validación de email` |
| `perf` | Mejora de rendimiento | `perf(consultas): agregar índice compuesto en persona.documento` |
| `test` | Pruebas | `test(servicios): agregar tests para CalculadorComision` |
| `docs` | Documentación | `docs(readme): actualizar instrucciones de instalación` |
| `style` | Formato (espacios, comas) | `style(dashboard): aplicar formato black` |
| `chore` | Tareas de mantenimiento | `chore(deps): actualizar reflex a 0.7.x` |

#### Scopes Principales

- `dominio` - Entidades, value objects, lógica de negocio
- `aplicacion` - Servicios de aplicación, DTOs
- `infraestructura` - Repositorios, servicios externos
- `presentacion` - UI, componentes Reflex
- `core` - Utilidades transversales
- `tests` - Suite de pruebas
- `config` - Configuración, variables de entorno

### Flujo de Ramas

```
main (producción)
  ↑
develop (integración)
  ↑
feature/VEL-123-nombre-descriptivo (features)
bugfix/VEL-456-descripcion (bugfixes)
hotfix/VEL-789-descripcion (hotfixes críticos)
```

### Proceso de Merge

1. **Crear rama** desde `develop`: `git checkout -b feature/VEL-123-nombre`
2. **Commits atómicos** siguiendo convención
3. **Tests pasando** localmente: `pytest -v`
4. **Push** y crear Pull Request a `develop`
5. **Code Review** obligatorio (1 aprobación mínimo)
6. **CI/CD verde** antes de merge
7. **Squash and merge** para mantener historia limpia

---

## 🧪 Estrategia de Testing

### Pirámide de Tests

```
         /
        /  \     E2E (5%) - Flujos críticos
       /____\
      /      \   Integración (25%) - Servicios + Repos
     /________\
    /          \  Unitarios (70%) - Dominio puro
   /____________\
```

### Tests Unitarios (Dominio)

```python
import pytest
from src.dominio.value_objects import Dinero
from src.dominio.entidades import ContratoArrendamiento

class TestContratoArrendamiento:
    """Tests de lógica de dominio pura."""

    def test_calcular_dias_mora_con_fecha_posterior(self):
        contrato = ContratoArrendamientoFactory.build(
            fecha_pago_limite=date(2026, 1, 5)
        )
        dias = contrato.calcular_dias_mora(date(2026, 1, 10))

        assert dias == 5

    def test_no_se_puede_crear_con_valor_negativo(self):
        with pytest.raises(ValueError, match="valor.*negativo"):
            ContratoArrendamiento(
                valor_canon=Dinero(Decimal("-1000"))
            )
```

### Tests de Integración (Infraestructura)

```python
import pytest
from src.infraestructura.persistencia import RepositorioPersonaSQLite

@pytest.mark.integration
class TestRepositorioPersonaSQLite:
    """Tests con base de datos real (test container)."""

    def test_guardar_y_recuperar_persona(self, db_session):
        repo = RepositorioPersonaSQLite(db_session)
        persona = PersonaFactory.build()

        guardada = repo.guardar(persona)
        recuperada = repo.obtener_por_id(guardada.id)

        assert recuperada.email == persona.email
        assert recuperada.documento == persona.documento
```

### Cobertura Mínima

| Capa | Cobertura | Excepciones |
|------|-----------|-------------|
| Dominio | 100% | Zero tolerancia |
| Aplicación | > 90% | Solo logging/debug |
| Infraestructura | > 75% | I/O externo mockable |

---

## 🐘 PostgreSQL Native (Protocolo de Persistencia)

### Convenciones Obligatorias

#### INSERT con RETURNING

```python
# ✅ CORRECTO - PostgreSQL nativo
query = """
    INSERT INTO personas (nombre, documento, email)
    VALUES (%s, %s, %s)
    RETURNING id
"""
cursor.execute(query, (nombre, documento, email))
persona_id = cursor.fetchone()[0]  # ID generado directamente

# ❌ PROHIBIDO - SQLite legacy
query = "INSERT INTO personas (nombre, documento, email) VALUES (?, ?, ?)"
cursor.execute(query, (nombre, documento, email))
persona_id = cursor.lastrowid  # No usar en PostgreSQL
```

#### Placeholders PostgreSQL

| Contexto | Placeholder | Ejemplo |
|----------|-------------|---------|
| PostgreSQL | `%s` | `VALUES (%s, %s)` |
| SQLite (obsoleto) | `?` | `VALUES (?, ?)` ❌ |

**Regla:** Usar **ÚNICAMENTE** `%s` en todas las consultas parametrizadas.

#### Validación de Tipos (PostgreSQL es Estricto)

```python
# ✅ CORRECTO - Validación antes de persistir
from datetime import datetime

def guardar_contrato(contrato_data: dict) -> int:
    # Validar booleanos explícitamente
    activo = bool(contrato_data.get("activo", True))

    # Fechas en formato ISO 8601
    fecha_inicio = datetime.fromisoformat(
        contrato_data["fecha_inicio"]
    ).date()

    query = """
        INSERT INTO contratos (propiedad_id, fecha_inicio, activo)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    cursor.execute(query, (
        contrato_data["propiedad_id"],
        fecha_inicio,  # date object, no string
        activo         # bool, no int
    ))
    return cursor.fetchone()[0]

# ❌ PROHIBIDO - Sin validación (falla en PostgreSQL)
cursor.execute(
    "INSERT INTO contratos (activo) VALUES (%s)",
    (1,)  # PostgreSQL espera True/False, no 1/0
)
```

#### Repositorios Agnósticos

```python
# ✅ CORRECTO - Nombre genérico, sin sufijo tecnológico
# src/infraestructura/persistencia/repositorio_persona.py
class RepositorioPersona(RepositorioPersonaPort):
    """Repositorio PostgreSQL sin acoplamiento al nombre."""
    pass

# ❌ PROHIBIDO - Sufijo SQLite legacy
# src/infraestructura/persistencia/repositorio_persona_sqlite.py ❌
class RepositorioPersonaSQLite:  # ❌ NO USAR
    pass
```

**Nota:** Los archivos existentes con sufijo `_sqlite.py` deben renombrarse a `repositorio_[entidad].py`.

---

## 🚀 Guidelines de Implementación

### Al Agregar una Nueva Entidad

1. **Definir en Dominio**:
   - Entidad en `src/dominio/entidades/`
   - Value objects necesarios
   - Interfaz de repositorio en `src/dominio/interfaces/`
   - Excepciones de dominio específicas

2. **Implementar en Infraestructura**:
   - Modelo SQLModel en `src/infraestructura/persistencia/modelos/`
   - Repositorio concreto
   - Mapeadores (si es necesario)

3. **Crear Servicio de Aplicación**:
   - DTOs en `src/aplicacion/esquemas.py`
   - Servicio que orqueste operaciones

4. **Construir UI**:
   - State de Reflex
   - Views y components
   - Integración con servicio

### Al Modificar Lógica Existente

1. **Identificar la capa correcta**:
   - ¿Es regla de negocio? → Dominio
   - ¿Es coordinación? → Aplicación
   - ¿Es presentación? → Reflex

2. **Mantener contratos**:
   - No cambiar interfaces públicas sin deprecación
   - Agregar tests antes de modificar (TDD)

3. **Actualizar documentación**:
   - Docstrings
   - Este archivo si cambia arquitectura

---

## ⚠️ Anti-Patrones Prohibidos

### ❌ Nunca hagas esto:

```python
# 1. Importar infraestructura en dominio
from src.infraestructura import RepositorioPersonaSQLite  # ❌ PROHIBIDO

# 2. Lógica de negocio en componentes UI
def mi_componente():
    if usuario.rol == "admin" and fecha > contrato.fecha_fin:  # ❌ PROHIBIDO
        calcular_penalizacion()  # Lógica debe estar en dominio

# 3. Excepciones genéricas
try:
    proceso()
except Exception as e:  # ❌ PROHIBIDO - Captura específica
    pass

# 4. Estado mutable global
class Config:  # ❌ PROHIBIDO
    valor = "mutable"

# 5. Queries SQL en presentación
def view():
    result = session.execute("SELECT * FROM personas")  # ❌ PROHIBIDO

# 6. Magic numbers
if dias > 30:  # ❌ PROHIBIDO - Usar constante
    pass

# 7. Import circular
# A importa B, B importa A  # ❌ PROHIBIDO - Refactorizar
```

### ✅ En su lugar, haz esto:

```python
# 1. Depender de abstracciones
from src.dominio.interfaces import RepositorioPersona  # ✅ BIEN

# 2. Delegar a servicios de dominio
servicio_dominio.calcular_penalizacion(contrato)  # ✅ BIEN

# 3. Excepciones específicas de dominio
except ContratoVencidoError as e:  # ✅ BIEN
    logger.error("Contrato vencido", exc_info=e)

# 4. Inmutabilidad y configuración inyectada
@dataclass(frozen=True)
class Configuracion:  # ✅ BIEN
    valor: str

# 5. Usar repositorios
personas = repo.obtener_todas()  # ✅ BIEN

# 6. Constantes con nombre
DIAS_GRACIA_MORA = 30  # ✅ BIEN
if dias > DIAS_GRACIA_MORA:
    pass

# 7. Inversión de dependencias
# A depende de interfaz, B implementa interfaz  # ✅ BIEN
```

---

## 🔒 Seguridad

### Validación de Inputs

```python
from pydantic import BaseModel, Field, validator

class CrearContratoInput(BaseModel):
    """DTO con validación estricta."""

    propiedad_id: int = Field(gt=0)
    arrendatario_id: int = Field(gt=0)
    valor_canon: Decimal = Field(gt=0, decimal_places=2)
    duracion_meses: int = Field(ge=1, le=60)  # Máx 5 años

    @validator("valor_canon")
    def validar_valor_rango(cls, v):
        if v > Decimal("100000000"):  # $100M máx
            raise ValueError("Valor excede límite permitido")
        return v
```

### Control de Acceso

```python
from functools import wraps

def requiere_rol(roles: List[Rol]):
    """Decorator para proteger handlers."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.state.user.rol not in roles:
                raise PermisoDenegadoError()
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

# Uso
@requiere_rol([Rol.ADMIN, Rol.GERENTE])
async def eliminar_contrato(self, contrato_id: int):
    pass
```

---

## 📊 Métricas de Calidad

## ✅ Validación y Calidad (CI/CD Manual)

### Checklist Pre-Commit Extendido

- [ ] Tests unitarios pasan: `pytest src/tests/unitarios/ -v`
- [ ] Cobertura > 90% en código nuevo
- [ ] Type checking: `mypy src/ --strict`
- [ ] Linting: `ruff check src/`
- [ ] Formato: `black src/ --check`
- [ ] No hay imports circulares: `python -c "import src"`
- [ ] **NUEVO:** `check_syntax.py` pasa sin errores
- [ ] **NUEVO:** Tests de renderizado Reflex funcionan
- [ ] **NUEVO:** PostgreSQL migration check (si aplica)
- [ ] Documentación actualizada

### Validación de Assets PDF

```python
# Antes de generar cualquier PDF
REQUIRED_ASSETS = {
    "logo_empresa": "assets/img/logo.png",
    "firma_digital": "assets/img/firma.png",
    "fuente_principal": "assets/fonts/OpenSans-Regular.ttf",
}

def validar_assets_pdf() -> list[str]:
    """Valida existencia de assets antes de renderizado."""
    faltantes = []
    for nombre, ruta in REQUIRED_ASSETS.items():
        if not os.path.exists(ruta):
            faltantes.append(f"{nombre}: {ruta}")
    return faltantes

# Uso
if faltantes := validar_assets_pdf():
    raise RuntimeError(f"Assets faltantes: {faltantes}")
```

### Scripts de Validación

```bash
# 1. Validación de sintaxis
python scripts/check_syntax.py

# 2. Tests con cobertura
pytest --cov=src --cov-report=term-missing

# 3. Type checking
mypy src/ --strict --ignore-missing-imports

# 4. Linting
ruff check src/
black src/ --check

# 5. Servidor Reflex en modo debug (captura excepciones)
reflex run --env dev
```

---

## 🔧 Mandatos de Ejecución (Cirugía Técnica)

### Flujo de Trabajo con Herramientas

1. **Investigación previa:** Usar `grep` para mapear dependencias
   ```bash
   # Buscar usos antes de modificar
   grep -r "funcion_a_cambiar" src/ --include="*.py"
   grep -r "import.*modulo_viejo" src/ --include="*.py"
   ```

2. **Cirugía de código:** Preferir `sed`/ediciones sobre reescrituras
   - Mantener integridad de archivos extensos
   - Usar reemplazos quirúrgicos, no regeneración completa

3. **Validación final:** "Si no está probado, está roto"
   - Ejecutar servidor Reflex en modo debug
   - Capturar excepciones de renderizado
   - Confirmar éxito antes de finalizar

### Comunicación Técnica

- **Concisión absoluta:** Priorizar resultados sobre explicaciones
- **Validaciones visibles:** Mostrar checks, no promesas
- **Idioma:** 100% Español en todo código y documentación

---

### Métricas de Arquitectura

| Métrica | Objetivo | Herramienta |
|---------|----------|---------------|
| Acoplamiento aferente | Bajo | `pydeps` |
| Complejidad ciclomática | < 10 por función | `radon` |
| Deuda técnica | < 5% | `sonarqube` |
| Duplicación de código | < 3% | `sonarqube` |

---

## 🆘 Troubleshooting Común

### Problema: Error de tipo en PostgreSQL (migración desde SQLite)

**Síntoma:** `psycopg2.errors.DatatypeMismatch` o `can't adapt type 'int'` para booleanos

**Causa:** SQLite era permisivo con tipos; PostgreSQL es estricto.

**Solución:**
1. **Validar booleanos explícitamente** antes de INSERT:
   ```python
   # ❌ Falla en PostgreSQL
   cursor.execute("INSERT INTO tabla (activo) VALUES (%s)", (1,))

   # ✅ Correcto
   cursor.execute("INSERT INTO tabla (activo) VALUES (%s)", (True,))
   ```

2. **Fechas en formato ISO 8601**:
   ```python
   from datetime import datetime

   # ✅ Correcto
   fecha = datetime.fromisoformat(fecha_str).date()
   cursor.execute("INSERT INTO tabla (fecha) VALUES (%s)", (fecha,))
   ```

3. **Usar placeholders `%s` (no `?`)**:
   ```python
   # ❌ SQLite legacy
   cursor.execute("SELECT * FROM tabla WHERE id = ?", (id,))

   # ✅ PostgreSQL
   cursor.execute("SELECT * FROM tabla WHERE id = %s", (id,))
   ```

### Problema: State de Reflex no se actualiza

**Síntoma:** Cambios en state no reflejan en UI

**Solución:**
1. Verificar que los atributos estén tipados correctamente
2. Para listas/dicts: crear nueva instancia, no mutar
   ```python
   # ❌ No funciona (mutación in-place)
   self.items.append(new_item)
   self.datos.update({"clave": valor})

   # ✅ Funciona (nueva instancia)
   self.items = self.items + [new_item]
   self.datos = {**self.datos, "clave": valor}
   ```
3. Usar `rx.cond()` correctamente para renderizado condicional
4. Verificar uso de `@rx.var` para propiedades computadas

### Problema: ImportError circular

**Síntoma:** `ImportError: cannot import name 'X' from partially initialized module`

**Solución:**
1. Identificar el ciclo con `pydeps` o `import-deps`
2. Mover import al interior de la función (quick fix)
3. Refactorizar extrayendo interfaz al módulo `interfaces/`
4. Considerar si las clases deben estar en módulos separados

## ⚡ Gestión de Estado Reflex (Elite)

### Principios de State Management

```python
import reflex as rx

class EstadoPersonas(rx.State):
    """State centralizado - Única fuente de verdad."""

    # Variables de estado primitivas
    personas: list[Persona] = []
    persona_seleccionada: Persona | None = None
    cargando: bool = False
    error: str = ""

    # ✅ Computed properties (datos derivados)
    @rx.var
    def total_personas(self) -> int:
        """Propiedad computada - se actualiza automáticamente."""
        return len(self.personas)

    @rx.var
    def personas_activas(self) -> list[Persona]:
        """Filtrado computado - sin duplicar estado."""
        return [p for p in self.personas if p.activo]

    # Event handlers con mutaciones atómicas
    async def cargar_personas(self):
        self.cargando = True
        self.error = ""
        try:
            self.personas = await servicio_personas.obtener_todas()
        except Exception as e:
            self.error = str(e)
        finally:
            self.cargando = False
```

### Reglas de Mutación

```python
class EstadoEjemplo(rx.State):
    items: list[str] = []
    datos: dict[str, any] = {}

    # ✅ CORRECTO - Mutación atómica con nueva instancia
    def agregar_item(self, item: str):
        self.items = self.items + [item]  # Nueva lista

    def actualizar_dato(self, clave: str, valor: any):
        self.datos = {**self.datos, clave: valor}  # Nuevo dict

    # ❌ PROHIBIDO - Mutación in-place (no triggera re-render)
    def agregar_item_mal(self, item: str):
        self.items.append(item)  # ❌ No funciona en Reflex
        self.datos.update({clave: valor})  # ❌ Mutación oculta
```

### Validación Backend (Siempre)

```python
class EstadoFormulario(rx.State):
    email: str = ""
    email_error: str = ""

    def validar_email(self) -> bool:
        """Validación en backend antes de procesar."""
        if "@" not in self.email:
            self.email_error = "Email inválido"
            return False
        if len(self.email) < 5:
            self.email_error = "Email demasiado corto"
            return False
        self.email_error = ""
        return True

    async def guardar(self):
        # ✅ Validar antes de procesar
        if not self.validar_email():
            return rx.toast.error(self.email_error)

        # Procesar...
```

---

## 🛡️ Protocolo Zero Leak (Seguridad)

### Protección de Credenciales

```python
# ✅ CORRECTO - Variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
O365_CLIENT_ID = os.getenv("O365_CLIENT_ID")
O365_CLIENT_SECRET = os.getenv("O365_CLIENT_SECRET")

# .env (en .gitignore)
# .env.example (plantilla sin valores)
```

**Archivos críticos protegidos:**
- `.env` - Variables de entorno sensibles
- `railway.json` - Configuración de despliegue
- `*.key` / `*.pem` - Claves criptográficas
- `credentials.json` - Tokens de servicios

### Higiene de Directorio Raíz

```
PYTHON-REFLEX/
├── src/                        # Código fuente
├── docs/                       # Documentación consolidada
├── scripts/                    # Utilidades
│   └── diagnostico/            # Scripts de diagnóstico
├── tests/                      # Suite de pruebas
├── .env                        # Variables (gitignored)
├── .env.example                # Plantilla
├── .gitignore                  # Exclusiones
└── CLAUDE.md                   # Este archivo
```

**Prohibido en raíz:**
- Scripts de diagnóstico (`debug_*.py`, `repro_*.py`, `check_*.py`)
- Archivos `.txt` informativos sueltos
- Archivos temporales o de cache

**Scripts de diagnóstico:** Mover a `scripts/diagnostico/` o eliminar tras uso.

### Sanitización de Datos

```python
# scripts/sanitize_credentials.py
import re

SANITIZE_PATTERNS = [
    (r'password[=:]\s*[^\s]+', 'password=***'),
    (r'api_key[=:]\s*[^\s]+', 'api_key=***'),
    (r'token[=:]\s*[^\s]+', 'token=***'),
]

def sanitize_output(text: str) -> str:
    """Sanitiza credenciales antes de logging/export."""
    for pattern, replacement in SANITIZE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
```

---

## 📊 Documentación Dinámica

### Archivos de Estado a Mantener

| Archivo | Propósito | Actualizar tras... |
|---------|-----------|---------------------|
| `ESTADO_TAREAS.md` | Tareas pendientes/en progreso | Completar hito |
| `auditoria_GEMINI_CLI.md` | Auditoría de cambios | Cada sesión |
| `CLAUDE.md` | Este documento | Cambios arquitectónicos |

### Template de Actualización

```markdown
## [FECHA] - [HITO COMPLETADO]

### Cambios Realizados
- [ ] Feature implementada
- [ ] Tests actualizados
- [ ] Documentación actualizada

### Validaciones
- [ ] `check_syntax.py` pasa
- [ ] Tests de Reflex renderizan
- [ ] PostgreSQL migración compatible
```

---

### Problema: Tests lentos

**Síntoma:** Suite de tests toma > 2 minutos

**Solución:**
1. Usar pytest fixtures con `scope="session"` para recursos compartidos
2. Mockear servicios externos (email, pdf)
3. Usar base de datos en memoria para tests unitarios
4. Paralelizar: `pytest -n auto`

---

## 📚 Recursos de Referencia

### Lecturas Obligatorias

1. **Clean Architecture** - Robert C. Martin
2. **Domain-Driven Design** - Eric Evans
3. **Refactoring** - Martin Fowler
4. **Python Type Hints** - docs.python.org/3/library/typing.html

### Documentación Interna

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Este documento - Protocolo de ingeniería élite |
| `GEMINI.md` | Protocolo de operaciones élite (complementario) |
| `ESTADO_TAREAS.md` | Tareas pendientes y estado del proyecto |
| `auditoria_GEMINI_CLI.md` | Auditoría de cambios y sesiones |
| `docs/arquitectura/` | Diagramas C4 y documentación técnica |
| `docs/api/` | Especificaciones OpenAPI |
| `docs/temas/` | Guía de estilos UI y componentes |
| `scripts/diagnostico/` | Scripts de diagnóstico y utilidades |

---

## 🎯 Principios No Negociables

1. **Inmutabilidad Primera**: Value objects nunca mutan. Dataclasses con `frozen=True`.

2. **Dependencias Unidireccionales**: Dominio → Aplicación → Infra → Presentación. Nunca al revés.

3. **Explicit over Implicit**: Tipos explícitos, imports explícitos, configuración explícita.

4. **Fail Fast**: Validar inputs en los límites del sistema. Excepciones específicas inmediatamente.

5. **Single Responsibility**: Una clase = un motivo para cambiar. Funciones < 50 líneas.

6. **Testabilidad**: Todo código debe ser testeable sin I/O real. Inyectar dependencias.

7. **Claude Design System**: Cada componente UI sigue el sistema de diseño Claude (Anthropic). Sin referencias a Neumorphism. Fondos Parchment (#f5f4ed), sombras ring-based, botón Terracotta para CTAs.

8. **PostgreSQL Nativo**: Sin referencias a SQLite. Placeholders `%s`, INSERT con `RETURNING`, tipos estrictos.

9. **Reflex como Único Framework**: Flet está obsoleto. Todo nuevo código usa Reflex.

10. **100% Español**: Código, variables, comentarios y documentación en español. Solo términos técnicos de librerías en inglés.

11. **Zero Leak**: Credenciales protegidas, directorio raíz limpio, sanitización antes de logs.

12. **Documentación Viva**: `ESTADO_TAREAS.md` y `auditoria_GEMINI_CLI.md` actualizados tras cada hito.

---

## 🧠 Skills Registry

Skills son paquetes de instrucciones especializadas que extienden las capacidades del agente. Se cargan **on-demand** vía el tool `skill` — no están en contexto permanente. Esta sección es un índice para saber cuándo invocar cada skill.

| Skill | Descripción | Cuándo Usar |
|---|---|---|
| `api-and-interface-design` | Diseño de APIs estables y contratos entre módulos | Crear endpoints REST/GraphQL, definir boundaries entre frontend y backend, diseñar interfaces públicas |
| `browser-testing-with-devtools` | Testing visual con Chrome DevTools MCP | Debugging UI, análisis de red y consola, profiling de rendimiento, verificación visual |
| `ci-cd-and-automation` | Automatización de pipelines CI/CD | Setup de GitHub Actions, quality gates, despliegue automatizado, debugging de CI |
| `code-review-and-quality` | Code review multi-eje (correctitud, legibilidad, arquitectura, seguridad, performance) | Antes de mergear cualquier PR, después de implementar una feature, al evaluar código de otro agente |
| `code-simplification` | Simplificación quirúrgica de código sin cambiar comportamiento | Refactoring post-feature, reducción de complejidad ciclomática, eliminación de dead code |
| `context-engineering` | Optimización del contexto del agente para máxima calidad de output | Iniciar sesión nueva, cambiar de tarea mayor, calidad del output degradada |
| `debugging-and-error-recovery` | Debugging sistemático con triage estructurado | Tests fallando, builds rotos, bugs en producción, comportamiento inesperado |
| `deprecation-and-migration` | Deprecación y migración segura de sistemas legacy | Reemplazar APIs viejas, consolidar implementaciones duplicadas, sunset de features |
| `documentation-and-adrs` | ADRs y documentación de decisiones arquitectónicas | Decisiones técnicas significativas, cambios de API pública, onboarding de nuevos miembros |
| `frontend-ui-engineering` | UI de calidad profesional con accesibilidad y diseño system | Componentes nuevos, layouts responsive, estados vacío/error/carga, evitar "AI aesthetic" |
| `idea-refine` | Refinamiento de ideas mediante pensamiento divergente/convergente | Ideas vagas, brainstorming estructurado, stress-test de conceptos, definición de MVP |
| `incremental-implementation` | Implementación en slices verticales delgados | Features multi-archivo, cambios > 100 líneas, refactoring que toca varios módulos |
| `performance-optimization` | Optimización basada en medición (no guessing) | Core Web Vitals, N+1 queries, bundle size, crawling lento, TTFB alto |
| `planning-and-task-breakdown` | Descomposición de trabajo en tareas ordenadas con acceptance criteria | Features grandes, estimación de scope, trabajo en paralelo multi-agente |
| `security-and-hardening` | Hardening contra OWASP Top 10 y manejo seguro de datos | Auth, validación de input, almacenamiento de datos sensibles, integraciones externas |
| `shipping-and-launch` | Preparación de lanzamiento a producción con rollout gradual | Deploy a producción, pre-launch checklist, monitoreo post-deploy, rollback plan |
| `source-driven-development` | Implementación basada en documentación oficial (no memoria) | Uso de frameworks/librerías donde la corrección importa, código boilerplate |
| `spec-driven-development` | Especificación escrita antes de codificar | Nuevos proyectos, features con requerimientos ambiguos, cambios multi-módulo |
| `test-driven-development` | TDD: test rojo → código verde → refactor | Lógica nueva con requirements claros, bug fixes con regression test |

### Ciclo de Vida del Desarrollo

El flujo recomendado para features nuevas sigue esta secuencia de skills:

```
DEFINE ──→ PLAN ──→ BUILD ──→ VERIFY ──→ REVIEW ──→ SHIP
  │          │        │          │          │         │
  ▼          ▼        ▼          ▼          ▼         ▼
 spec     planning  incremental  debug    code-    shipping
-driven   + task    + TDD       + browser review  + launch
          breakdown             testing  + quality
```

Cada flecha representa invocar la skill correspondiente vía `skill` tool. No implementar manualmente lo que una skill puede resolver.

---

## 🤝 Comunicación con Claude

Cuando solicites ayuda, proporciona:

1. **Contexto**: ¿Qué módulo estás modificando?
2. **Objetivo**: ¿Qué comportamiento esperas?
3. **Problema actual**: ¿Qué error o comportamiento observas?
4. **Código relevante**: Mínimo reproducible

### Templates de Prompt

**Para nuevas features:**
```
Necesito implementar [feature] en el módulo [módulo].
- Debe seguir el patrón [patrón si aplica]
- Depende de [entidades/servicios existentes]
- Debe incluir [criterios de aceptación]
```

**Para debugging:**
```
Tengo un error en [archivo:linea]:
[traceback completo]

Código relevante:
[snippet mínimo]

Comportamiento esperado: [X]
Comportamiento actual: [Y]
```

---

> **Recuerda**: La calidad del código es no negociable.
> *"Código que funciona pero no es mantenible, técnicamente no funciona."*

---

**Copyright © 2026 Inmobiliaria Velar SAS**
*Documento Confidencial - Uso Interno Únicamente*

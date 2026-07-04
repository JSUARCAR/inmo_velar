# Quickstart: Integración Incidentes y Liquidaciones de Propietarios

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Overview

This guide provides step-by-step instructions for implementing the integration between Incidents and Owner Settlements modules.

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database (or SQLite for development)
- Reflex >= 0.6.0
- Project dependencies installed (`pip install -r requirements.txt`)

## Implementation Steps

### Step 1: Database Migration

Run the migration scripts to create new tables and add fields:

```bash
# Navigate to project root
cd /path/to/PYTHON-REFLEX

# Run migration script
python -c "
import sqlite3
import os

# Connect to database
db_path = 'instance/development.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Migration 001: Add fields to existing tables
try:
    cursor.execute('ALTER TABLE INCIDENTES ADD COLUMN estado_pago TEXT DEFAULT \"Pendiente\"')
    print('Added estado_pago to INCIDENTES')
except sqlite3.OperationalError as e:
    print(f'Note: {e}')

try:
    cursor.execute('ALTER TABLE LIQUIDACIONES ADD COLUMN valor_incidentes INTEGER DEFAULT 0')
    print('Added valor_incidentes to LIQUIDACIONES')
except sqlite3.OperationalError as e:
    print(f'Note: {e}')

# Migration 002: Create PLAN_PAGO_INCIDENTE
cursor.execute('''
CREATE TABLE IF NOT EXISTS PLAN_PAGO_INCIDENTE (
    ID_PLAN_PAGO INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_INCIDENTE INTEGER NOT NULL,
    NUM_CUOTAS INTEGER NOT NULL CHECK(NUM_CUOTAS > 0),
    VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
    TOTAL_PLAN INTEGER NOT NULL,
    ESTADO TEXT NOT NULL DEFAULT 'Activo',
    CREADO_POR TEXT NOT NULL,
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UPDATED_AT TEXT,
    FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE),
    UNIQUE(ID_INCIDENTE)
)
''')
print('Created PLAN_PAGO_INCIDENTE table')

# Migration 003: Create CUOTA_INCIDENTE
cursor.execute('''
CREATE TABLE IF NOT EXISTS CUOTA_INCIDENTE (
    ID_CUOTA INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_PLAN_PAGO INTEGER NOT NULL,
    NUMERO_CUOTA INTEGER NOT NULL CHECK(NUMERO_CUOTA > 0),
    VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
    ID_LIQUIDACION INTEGER,
    ESTADO_PAGO TEXT NOT NULL DEFAULT 'Pendiente',
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ID_PLAN_PAGO) REFERENCES PLAN_PAGO_INCIDENTE(ID_PLAN_PAGO),
    FOREIGN KEY (ID_LIQUIDACION) REFERENCES LIQUIDACIONES(ID_LIQUIDACION),
    UNIQUE(ID_PLAN_PAGO, NUMERO_CUOTA)
)
''')
print('Created CUOTA_INCIDENTE table')

# Migration 004: Create INCIDENTE_LIQUIDACION
cursor.execute('''
CREATE TABLE IF NOT EXISTS INCIDENTE_LIQUIDACION (
    ID_RELACION INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_INCIDENTE INTEGER NOT NULL,
    ID_LIQUIDACION INTEGER NOT NULL,
    NUMERO_CUOTA INTEGER NOT NULL,
    VALOR_DESCUENTO INTEGER NOT NULL CHECK(VALOR_DESCUENTO > 0),
    ASOCIADO_POR TEXT NOT NULL,
    FECHA_ASOCIACION TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE),
    FOREIGN KEY (ID_LIQUIDACION) REFERENCES LIQUIDACIONES(ID_LIQUIDACION),
    UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)
)
''')
print('Created INCIDENTE_LIQUIDACION table')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS IDX_CUOTA_PLAN_PAGO ON CUOTA_INCIDENTE(ID_PLAN_PAGO)')
cursor.execute('CREATE INDEX IF NOT EXISTS IDX_CUOTA_LIQUIDACION ON CUOTA_INCIDENTE(ID_LIQUIDACION)')
cursor.execute('CREATE INDEX IF NOT EXISTS IDX_INCIDENTE_LIQ_INCIDENTE ON INCIDENTE_LIQUIDACION(ID_INCIDENTE)')
cursor.execute('CREATE INDEX IF NOT EXISTS IDX_INCIDENTE_LIQ_LIQUIDACION ON INCIDENTE_LIQUIDACION(ID_LIQUIDACION)')
print('Created indexes')

conn.commit()
conn.close()
print('Migration completed successfully!')
"
```

### Step 2: Create Domain Entities

Create the new domain entities:

```bash
# Create PlanPagoIncidente entity
cat > src/dominio/entidades/plan_pago_incidente.py << 'EOF'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PlanPagoIncidente:
    """Entidad que representa un plan de pago para un incidente."""
    
    id_plan_pago: Optional[int] = None
    id_incidente: int = 0
    num_cuotas: int = 0
    valor_cuota: int = 0
    total_plan: int = 0
    estado: str = "Activo"
    creado_por: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones post inicialización."""
        if self.num_cuotas < 1:
            raise ValueError("El número de cuotas debe ser mayor a 0")
        if self.valor_cuota <= 0:
            raise ValueError("El valor de la cuota debe ser mayor a 0")
        if self.total_plan != self.num_cuotas * self.valor_cuota:
            raise ValueError("El total del plan no coincide con num_cuotas * valor_cuota")
    
    @classmethod
    def crear(cls, id_incidente: int, num_cuotas: int, valor_cuota: int, creado_por: str) -> "PlanPagoIncidente":
        """Factory method para crear un nuevo plan de pago."""
        total_plan = num_cuotas * valor_cuota
        return cls(
            id_incidente=id_incidente,
            num_cuotas=num_cuotas,
            valor_cuota=valor_cuota,
            total_plan=total_plan,
            estado="Activo",
            creado_por=creado_por,
            created_at=datetime.now().isoformat()
        )
EOF

# Create CuotaIncidente entity
cat > src/dominio/entidades/cuota_incidente.py << 'EOF'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CuotaIncidente:
    """Entidad que representa una cuota individual del plan de pago."""
    
    id_cuota: Optional[int] = None
    id_plan_pago: int = 0
    numero_cuota: int = 0
    valor_cuota: int = 0
    id_liquidacion: Optional[int] = None
    estado_pago: str = "Pendiente"
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones post inicialización."""
        if self.numero_cuota < 1:
            raise ValueError("El número de cuota debe ser mayor a 0")
        if self.valor_cuota <= 0:
            raise ValueError("El valor de la cuota debe ser mayor a 0")
    
    @classmethod
    def crear(cls, id_plan_pago: int, numero_cuota: int, valor_cuota: int) -> "CuotaIncidente":
        """Factory method para crear una nueva cuota."""
        return cls(
            id_plan_pago=id_plan_pago,
            numero_cuota=numero_cuota,
            valor_cuota=valor_cuota,
            estado_pago="Pendiente",
            created_at=datetime.now().isoformat()
        )
EOF

# Create IncidenteLiquidacion entity
cat > src/dominio/entidades/incidente_liquidacion.py << 'EOF'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class IncidenteLiquidacion:
    """Entidad que representa la relación entre un incidente y una liquidación."""
    
    id_relacion: Optional[int] = None
    id_incidente: int = 0
    id_liquidacion: int = 0
    numero_cuota: int = 0
    valor_descuento: int = 0
    asociado_por: str = ""
    fecha_asociacion: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones post inicialización."""
        if self.valor_descuento <= 0:
            raise ValueError("El valor del descuento debe ser mayor a 0")
    
    @classmethod
    def crear(cls, id_incidente: int, id_liquidacion: int, numero_cuota: int, 
              valor_descuento: int, asociado_por: str) -> "IncidenteLiquidacion":
        """Factory method para crear una nueva relación."""
        return cls(
            id_incidente=id_incidente,
            id_liquidacion=id_liquidacion,
            numero_cuota=numero_cuota,
            valor_descuento=valor_descuento,
            asociado_por=asociado_por,
            fecha_asociacion=datetime.now().isoformat()
        )
EOF
```

### Step 3: Create Repository Interfaces

Create the repository interfaces:

```bash
# Create repository interfaces
cat > src/dominio/interfaces/repositorio_plan_pago.py << 'EOF'
from abc import ABC, abstractmethod
from typing import List, Optional
from src.dominio.entidades.plan_pago_incidente import PlanPagoIncidente


class RepositorioPlanPago(ABC):
    """Interfaz abstracta para repositorio de planes de pago."""
    
    @abstractmethod
    def crear(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Crea un nuevo plan de pago."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_plan_pago: int) -> Optional[PlanPagoIncidente]:
        """Obtiene un plan de pago por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_incidente(self, id_incidente: int) -> Optional[PlanPagoIncidente]:
        """Obtiene el plan activo de pago para un incidente."""
        pass
    
    @abstractmethod
    def actualizar(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Actualiza un plan de pago existente."""
        pass
    
    @abstractmethod
    def eliminar(self, id_plan_pago: int) -> bool:
        """Elimina un plan de pago (soft delete)."""
        pass
EOF

cat > src/dominio/interfaces/repositorio_cuota.py << 'EOF'
from abc import ABC, abstractmethod
from typing import List, Optional
from src.dominio.entidades.cuota_incidente import CuotaIncidente


class RepositorioCuota(ABC):
    """Interfaz abstracta para repositorio de cuotas."""
    
    @abstractmethod
    def crear(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Crea una nueva cuota."""
        pass
    
    @abstractmethod
    def crear_desde_plan(self, id_plan_pago: int, num_cuotas: int, valor_cuota: int) -> List[CuotaIncidente]:
        """Crea todas las cuotas para un plan."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_cuota: int) -> Optional[CuotaIncidente]:
        """Obtiene una cuota por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_plan(self, id_plan_pago: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas de un plan."""
        pass
    
    @abstractmethod
    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas asociadas a una liquidación."""
        pass
    
    @abstractmethod
    def actualizar(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Actualiza una cuota existente."""
        pass
    
    @abstractmethod
    def eliminar(self, id_cuota: int) -> bool:
        """Elimina una cuota."""
        pass
EOF

cat > src/dominio/interfaces/repositorio_incidente_liq.py << 'EOF'
from abc import ABC, abstractmethod
from typing import List, Optional
from src.dominio.entidades.incidente_liquidacion import IncidenteLiquidacion


class RepositorioIncidenteLiquidacion(ABC):
    """Interfaz abstracta para repositorio de relaciones incidente-liquidación."""
    
    @abstractmethod
    def crear(self, relacion: IncidenteLiquidacion) -> IncidenteLiquidacion:
        """Crea una nueva relación."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_relacion: int) -> Optional[IncidenteLiquidacion]:
        """Obtiene una relación por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_incidente(self, id_incidente: int) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de un incidente."""
        pass
    
    @abstractmethod
    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de una liquidación."""
        pass
    
    @abstractmethod
    def eliminar(self, id_relacion: int) -> bool:
        """Elimina una relación."""
        pass
    
    @abstractmethod
    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """Calcula el total de descuentos para una liquidación."""
        pass
EOF
```

### Step 4: Create Repository Implementations

Create the PostgreSQL repository implementations:

```bash
# Create PostgreSQL repositories
cat > src/infraestructura/persistencia/repositorio_plan_pago_postgres.py << 'EOF'
from typing import Optional, List
from src.dominio.entidades.plan_pago_incidente import PlanPagoIncidente
from src.dominio.interfaces.repositorio_plan_pago import RepositorioPlanPago
from src.infraestructura.persistencia.repositorio_base import RepositorioBase


class RepositorioPlanPagoPostgres(RepositorioBase, RepositorioPlanPago):
    """Implementación PostgreSQL del repositorio de planes de pago."""
    
    def crear(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Crea un nuevo plan de pago."""
        query = """
        INSERT INTO PLAN_PAGO_INCIDENTE 
        (ID_INCIDENTE, NUM_CUOTAS, VALOR_CUOTA, TOTAL_PLAN, ESTADO, CREADO_POR)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ID_PLAN_PAGO, CREATED_AT
        """
        params = (plan.id_incidente, plan.num_cuotas, plan.valor_cuota, 
                 plan.total_plan, plan.estado, plan.creado_por)
        
        resultado = self._ejecutar_consulta_retornar_uno(query, params)
        plan.id_plan_pago = resultado['id_plan_pago']
        plan.created_at = resultado['created_at']
        return plan
    
    def obtener_por_id(self, id_plan_pago: int) -> Optional[PlanPagoIncidente]:
        """Obtiene un plan de pago por su ID."""
        query = "SELECT * FROM PLAN_PAGO_INCIDENTE WHERE ID_PLAN_PAGO = %s"
        resultado = self._ejecutar_consulta_retornar_uno(query, (id_plan_pago,))
        if resultado:
            return PlanPagoIncidente(**resultado)
        return None
    
    def obtener_por_incidente(self, id_incidente: int) -> Optional[PlanPagoIncidente]:
        """Obtiene el plan activo de pago para un incidente."""
        query = """
        SELECT * FROM PLAN_PAGO_INCIDENTE 
        WHERE ID_INCIDENTE = %s AND ESTADO = 'Activo'
        """
        resultado = self._ejecutar_consulta_retornar_uno(query, (id_incidente,))
        if resultado:
            return PlanPagoIncidente(**resultado)
        return None
    
    def actualizar(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """Actualiza un plan de pago existente."""
        query = """
        UPDATE PLAN_PAGO_INCIDENTE 
        SET NUM_CUOTAS = %s, VALOR_CUOTA = %s, TOTAL_PLAN = %s, 
            ESTADO = %s, UPDATED_AT = datetime('now', 'localtime')
        WHERE ID_PLAN_PAGO = %s
        """
        params = (plan.num_cuotas, plan.valor_cuota, plan.total_plan, 
                 plan.estado, plan.id_plan_pago)
        self._ejecutar_consulta(query, params)
        return plan
    
    def eliminar(self, id_plan_pago: int) -> bool:
        """Elimina un plan de pago (soft delete)."""
        query = """
        UPDATE PLAN_PAGO_INCIDENTE 
        SET ESTADO = 'Cancelado', UPDATED_AT = datetime('now', 'localtime')
        WHERE ID_PLAN_PAGO = %s
        """
        self._ejecutar_consulta(query, (id_plan_pago,))
        return True
EOF

cat > src/infraestructura/persistencia/repositorio_cuota_postgres.py << 'EOF'
from typing import Optional, List
from src.dominio.entidades.cuota_incidente import CuotaIncidente
from src.dominio.interfaces.repositorio_cuota import RepositorioCuota
from src.infraestructura.persistencia.repositorio_base import RepositorioBase


class RepositorioCuotaPostgres(RepositorioBase, RepositorioCuota):
    """Implementación PostgreSQL del repositorio de cuotas."""
    
    def crear(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Crea una nueva cuota."""
        query = """
        INSERT INTO CUOTA_INCIDENTE 
        (ID_PLAN_PAGO, NUMERO_CUOTA, VALOR_CUOTA, ESTADO_PAGO)
        VALUES (%s, %s, %s, %s)
        RETURNING ID_CUOTA, CREATED_AT
        """
        params = (cuota.id_plan_pago, cuota.numero_cuota, cuota.valor_cuota, cuota.estado_pago)
        
        resultado = self._ejecutar_consulta_retornar_uno(query, params)
        cuota.id_cuota = resultado['id_cuota']
        cuota.created_at = resultado['created_at']
        return cuota
    
    def crear_desde_plan(self, id_plan_pago: int, num_cuotas: int, valor_cuota: int) -> List[CuotaIncidente]:
        """Crea todas las cuotas para un plan."""
        cuotas_creadas = []
        for i in range(1, num_cuotas + 1):
            cuota = CuotaIncidente.crear(id_plan_pago, i, valor_cuota)
            cuota = self.crear(cuota)
            cuotas_creadas.append(cuota)
        return cuotas_creadas
    
    def obtener_por_id(self, id_cuota: int) -> Optional[CuotaIncidente]:
        """Obtiene una cuota por su ID."""
        query = "SELECT * FROM CUOTA_INCIDENTE WHERE ID_CUOTA = %s"
        resultado = self._ejecutar_consulta_retornar_uno(query, (id_cuota,))
        if resultado:
            return CuotaIncidente(**resultado)
        return None
    
    def obtener_por_plan(self, id_plan_pago: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas de un plan."""
        query = """
        SELECT * FROM CUOTA_INCIDENTE 
        WHERE ID_PLAN_PAGO = %s 
        ORDER BY NUMERO_CUOTA
        """
        resultados = self._ejecutar_consulta(query, (id_plan_pago,))
        return [CuotaIncidente(**r) for r in resultados]
    
    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[CuotaIncidente]:
        """Obtiene todas las cuotas asociadas a una liquidación."""
        query = """
        SELECT * FROM CUOTA_INCIDENTE 
        WHERE ID_LIQUIDACION = %s 
        ORDER BY NUMERO_CUOTA
        """
        resultados = self._ejecutar_consulta(query, (id_liquidacion,))
        return [CuotaIncidente(**r) for r in resultados]
    
    def actualizar(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """Actualiza una cuota existente."""
        query = """
        UPDATE CUOTA_INCIDENTE 
        SET ID_LIQUIDACION = %s, ESTADO_PAGO = %s
        WHERE ID_CUOTA = %s
        """
        params = (cuota.id_liquidacion, cuota.estado_pago, cuota.id_cuota)
        self._ejecutar_consulta(query, params)
        return cuota
    
    def eliminar(self, id_cuota: int) -> bool:
        """Elimina una cuota."""
        query = "DELETE FROM CUOTA_INCIDENTE WHERE ID_CUOTA = %s"
        self._ejecutar_consulta(query, (id_cuota,))
        return True
EOF

cat > src/infraestructura/persistencia/repositorio_incidente_liq_postgres.py << 'EOF'
from typing import Optional, List
from src.dominio.entidades.incidente_liquidacion import IncidenteLiquidacion
from src.dominio.interfaces.repositorio_incidente_liq import RepositorioIncidenteLiquidacion
from src.infraestructura.persistencia.repositorio_base import RepositorioBase


class RepositorioIncidenteLiquidacionPostgres(RepositorioBase, RepositorioIncidenteLiquidacion):
    """Implementación PostgreSQL del repositorio de relaciones incidente-liquidación."""
    
    def crear(self, relacion: IncidenteLiquidacion) -> IncidenteLiquidacion:
        """Crea una nueva relación."""
        query = """
        INSERT INTO INCIDENTE_LIQUIDACION 
        (ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA, VALOR_DESCUENTO, ASOCIADO_POR)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING ID_RELACION, FECHA_ASOCIACION
        """
        params = (relacion.id_incidente, relacion.id_liquidacion, 
                 relacion.numero_cuota, relacion.valor_descuento, relacion.asociado_por)
        
        resultado = self._ejecutar_consulta_retornar_uno(query, params)
        relacion.id_relacion = resultado['id_relacion']
        relacion.fecha_asociacion = resultado['fecha_asociacion']
        return relacion
    
    def obtener_por_id(self, id_relacion: int) -> Optional[IncidenteLiquidacion]:
        """Obtiene una relación por su ID."""
        query = "SELECT * FROM INCIDENTE_LIQUIDACION WHERE ID_RELACION = %s"
        resultado = self._ejecutar_consulta_retornar_uno(query, (id_relacion,))
        if resultado:
            return IncidenteLiquidacion(**resultado)
        return None
    
    def obtener_por_incidente(self, id_incidente: int) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de un incidente."""
        query = """
        SELECT * FROM INCIDENTE_LIQUIDACION 
        WHERE ID_INCIDENTE = %s 
        ORDER BY FECHA_ASOCIACION
        """
        resultados = self._ejecutar_consulta(query, (id_incidente,))
        return [IncidenteLiquidacion(**r) for r in resultados]
    
    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[IncidenteLiquidacion]:
        """Obtiene todas las relaciones de una liquidación."""
        query = """
        SELECT * FROM INCIDENTE_LIQUIDACION 
        WHERE ID_LIQUIDACION = %s 
        ORDER BY FECHA_ASOCIACION
        """
        resultados = self._ejecutar_consulta(query, (id_liquidacion,))
        return [IncidenteLiquidacion(**r) for r in resultados]
    
    def eliminar(self, id_relacion: int) -> bool:
        """Elimina una relación."""
        query = "DELETE FROM INCIDENTE_LIQUIDACION WHERE ID_RELACION = %s"
        self._ejecutar_consulta(query, (id_relacion,))
        return True
    
    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """Calcula el total de descuentos para una liquidación."""
        query = """
        SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) as total
        FROM INCIDENTE_LIQUIDACION 
        WHERE ID_LIQUIDACION = %s
        """
        resultado = self._ejecutar_consulta_retornar_uno(query, (id_liquidacion,))
        return resultado['total'] if resultado else 0
EOF
```

### Step 5: Create Service Layer Extensions

Extend existing services:

```bash
# Extend servicio_financiero.py
cat >> src/aplicacion/servicios/servicio_financiero.py << 'EOF'


class ServicioPlanPagoIncidente:
    """Servicio para gestionar planes de pago de incidentes."""
    
    def __init__(self, repositorio_plan, repositorio_cuota, repositorio_incidente):
        self.repositorio_plan = repositorio_plan
        self.repositorio_cuota = repositorio_cuota
        self.repositorio_incidente = repositorio_incidente
    
    def crear_plan(self, id_incidente: int, num_cuotas: int, valor_cuota: int, 
                   creado_por: str) -> dict:
        """Crea un nuevo plan de pago para un incidente."""
        # Validar que el incidente existe y está calificado
        incidente = self.repositorio_incidente.obtener_por_id(id_incidente)
        if not incidente:
            return {"success": False, "error": "INCIDENTE_NO_ENCONTRADO"}
        
        if incidente.estado not in ['Aprobado', 'En Reparacion', 'Finalizado']:
            return {"success": False, "error": "INCIDENTE_NO_CALIFICADO"}
        
        # Verificar que no exista un plan activo
        plan_existente = self.repositorio_plan.obtener_por_incidente(id_incidente)
        if plan_existente:
            return {"success": False, "error": "PLAN_YA_EXISTE"}
        
        # Crear el plan
        plan = PlanPagoIncidente.crear(id_incidente, num_cuotas, valor_cuota, creado_por)
        plan = self.repositorio_plan.crear(plan)
        
        # Crear las cuotas
        cuotas = self.repositorio_cuota.crear_desde_plan(
            plan.id_plan_pago, num_cuotas, valor_cuota
        )
        
        return {
            "success": True,
            "data": {
                "plan": plan,
                "cuotas": cuotas
            }
        }
EOF
```

### Step 6: Create UI Components

Create the modal components:

```bash
# Create payment plan modal
cat > src/presentacion_reflex/components/incidentes/modal_plan_pago.py << 'EOF'
import reflex as rx
from src.presentacion_reflex.styles.styles import BASE_STYLE
from src.presentacion_reflex.state.incidentes_state import IncidentesState


def modal_plan_pago() -> rx.Component:
    """Modal para definir plan de pago del incidente."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Definir Plan de Pago"),
            rx.dialog.description(
                "Defina el número de cuotas y valor por cuota para el plan de pago."
            ),
            rx.form(
                rx.flex(
                    rx.text("Número de Cuotas:"),
                    rx.input(
                        name="num_cuotas",
                        type="number",
                        min_=1,
                        required=True,
                    ),
                    rx.text("Valor por Cuota:"),
                    rx.input(
                        name="valor_cuota",
                        type="number",
                        min_=1,
                        required=True,
                    ),
                    direction="column",
                    gap="4",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray")
                    ),
                    rx.button("Crear Plan", type="submit"),
                    justify="end",
                    gap="2",
                ),
                on_submit=IncidentesState.crear_plan_pago,
            ),
        ),
        open=IncidentesState.show_plan_pago_modal,
    )
EOF
```

### Step 7: Run Tests

Run the test suite to verify implementation:

```bash
# Run unit tests
pytest tests/unit/test_plan_pago.py -v

# Run integration tests
pytest tests/integration/test_pago_liquidacion_integration.py -v

# Run all tests with coverage
pytest --cov=src tests/
```

### Step 8: Start Application

Start the Reflex application:

```bash
# Start development server
reflex run

# Or export for production
reflex export --frontend-only --no-zip
```

## Verification Checklist

- [ ] Database migration completed successfully
- [ ] New entities created and validated
- [ ] Repository interfaces defined
- [ ] Repository implementations working
- [ ] Service layer extended
- [ ] UI components created
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Application starts without errors
- [ ] UI displays correctly

## Troubleshooting

### Common Issues

1. **Database connection errors**: Check database configuration in `rxconfig.py`
2. **Import errors**: Verify all modules are in correct paths
3. **UI not updating**: Ensure state variables are properly defined
4. **Tests failing**: Check test fixtures and mock data

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Review and test all business rules
2. Add comprehensive error handling
3. Implement audit logging
4. Add UI validation feedback
5. Performance testing with large datasets

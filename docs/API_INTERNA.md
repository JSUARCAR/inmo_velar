# Documentación de API Interna - InmoVelar

**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Audiencia:** Desarrolladores

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Capa de Dominio](#capa-de-dominio)
3. [Capa de Repositorios](#capa-de-repositorios)
4. [Capa de Servicios](#capa-de-servicios)
5. [Patrones y Estrategias](#patrones-y-estrategias)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Introducción

Esta documentación describe la API interna del Sistema de Gestión Inmobiliaria InmoVelar. El sistema sigue **Clean Architecture** con separación estricta de responsabilidades.

### Convenciones

- **Entidades**: Clases de dominio que representan conceptos de negocio
- **Value Objects**: Objetos inmutables que representan valores
- **Repositories**: Interfaces y implementaciones para persistencia
- **Services**: Lógica de aplicación y casos de uso
- **DTOs**: Objetos de transferencia de datos entre capas

---

## Capa de Dominio

La capa de dominio contiene la lógica de negocio pura sin dependencias externas.

### Entidades Principales

#### Persona

**Archivo**: `src/dominio/entidades/persona.py`

Entidad base para el Party Model. Una persona puede tener múltiples roles.

```python
@dataclass
class Persona:
    """
    Entidad: Persona
    Tabla: PERSONAS
    """
    id_persona: Optional[int] = None
    tipo_documento: Optional[str] = None
    numero_documento: str = ""
    nombre_completo: str = ""
    telefono_principal: Optional[str] = None
    correo_electronico: Optional[str] = None
    direccion_principal: Optional[str] = None
    estado_registro: Optional[int] = 1
    motivo_inactivacion: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
```

**Notas**:
- Mapeo 1:1 con la tabla `PERSONAS`
- `estado_registro`: 1 = Activo, 0 = Inactivo
- No contiene campos "fantasma" (todos los campos existen en BD)

---

#### Propiedad

**Archivo**: `src/dominio/entidades/propiedad.py`

Representa un inmueble en el sistema.

```python
@dataclass
class Propiedad:
    """
    Entidad: Propiedad
    Tabla: PROPIEDADES
    """
    id_propiedad: Optional[int] = None
    matricula_inmobiliaria: str = ""
    tipo_inmueble: str = ""
    id_municipio: Optional[int] = None
    direccion: str = ""
    barrio: Optional[str] = None
    area_m2: Optional[Decimal] = None
    num_habitaciones: Optional[int] = None
    num_banos: Optional[int] = None
    num_parqueaderos: Optional[int] = None
    estrato: Optional[int] = None
    valor_administracion: Optional[Decimal] = None
    canon_arrendamiento: Optional[Decimal] = None
    valor_venta: Optional[Decimal] = None
    porcentaje_comision: Optional[Decimal] = None
    disponible_arriendo: Optional[bool] = True
    disponible_venta: Optional[bool] = False
    observaciones: Optional[str] = None
    estado_registro: Optional[int] = 1
    # ... campos de auditoría
```

**Métodos de Negocio**:
- `esta_disponible() -> bool`: Verifica si la propiedad está disponible
- `marcar_como_ocupada()`: Cambia disponibilidad a False
- `marcar_como_disponible()`: Cambia disponibilidad a True

---

#### ContratoArrendamiento

**Archivo**: `src/dominio/entidades/contrato_arrendamiento.py`

Representa un contrato de arrendamiento (inquilino).

```python
@dataclass
class ContratoArrendamiento:
    """
    Entidad: Contrato de Arrendamiento
    Tabla: CONTRATOS_ARRENDAMIENTO
    """
    id_contrato_arrendamiento: Optional[int] = None
    id_propiedad: int = 0
    id_arrendatario: int = 0
    id_codeudor: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    duracion_meses: Optional[int] = None
    canon_mensual: Decimal = Decimal('0')
    valor_administracion: Decimal = Decimal('0')
    deposito: Decimal = Decimal('0')
    dia_pago: int = 5
    incremento_anual_porcentaje: Decimal = Decimal('0')
    fecha_ultimo_incremento: Optional[date] = None
    estado: str = "Activo"
    observaciones: Optional[str] = None
    # ... campos de auditoría
```

**Métodos de Negocio**:
- `calcular_dias_para_vencimiento() -> int`: Días hasta el vencimiento
- `esta_por_vencer(dias: int = 90) -> bool`: Verifica si está próximo a vencer
- `esta_vencido() -> bool`: Verifica si ya venció

---

#### Recaudo

**Archivo**: `src/dominio/entidades/recaudo.py`

Representa un pago de inquilino.

```python
@dataclass
class Recaudo:
    """
    Entidad: Recaudo (Pago de Inquilino)
    Tabla: RECAUDOS
    """
    id_recaudo: Optional[int] = None
    id_contrato_arrendamiento: int = 0
    fecha_pago: Optional[date] = None
    valor_total: Decimal = Decimal('0')
    metodo_pago: str = ""
    referencia_bancaria: Optional[str] = None
    estado: str = "Pendiente"  # Pendiente, Aplicado, Reversado
    observaciones: Optional[str] = None
    # ... campos de auditoría
```

**Estados**:
- `Pendiente`: Registrado pero no aplicado
- `Aplicado`: Confirmado y aplicado al contrato
- `Reversado`: Anulado

---

#### Liquidacion

**Archivo**: `src/dominio/entidades/liquidacion.py`

Representa un estado de cuenta mensual para propietarios.

```python
@dataclass
class Liquidacion:
    """
    Entidad: Liquidación (Estado de Cuenta)
    Tabla: LIQUIDACIONES
    """
    id_liquidacion: Optional[int] = None
    id_contrato_arrendamiento: int = 0
    periodo: str = ""  # Formato: YYYY-MM
    ingresos_totales: Decimal = Decimal('0')
    egresos_totales: Decimal = Decimal('0')
    neto_pagar: Decimal = Decimal('0')
    estado: str = "Generada"  # Generada, Aprobada, Pagada, Cancelada
    comprobante_pago: Optional[str] = None
    observaciones: Optional[str] = None
    # ... campos de auditoría
```

**Fórmula**:
```
Neto a Pagar = Ingresos Totales - Egresos Totales
```

---

#### Incidente

**Archivo**: `src/dominio/entidades/incidente.py`

Representa un mantenimiento o reparación.

```python
@dataclass
class Incidente:
    """
    Entidad: Incidente (Mantenimiento)
    Tabla: INCIDENTES
    """
    id_incidente: Optional[int] = None
    id_propiedad: int = 0
    titulo: str = ""
    descripcion: str = ""
    prioridad: str = "Media"  # Baja, Media, Alta, Crítica
    estado: str = "Reportado"  # Reportado, Cotizado, Aprobado, En Reparación, Finalizado
    categoria: Optional[str] = None
    responsable_costo: str = "Propietario"  # Propietario, Arrendatario
    id_proveedor_asignado: Optional[int] = None
    costo_final: Optional[Decimal] = None
    fecha_finalizacion: Optional[date] = None
    # ... campos de auditoría
```

**Estados**:
1. `Reportado`: Incidente recién creado
2. `Cotizado`: Con cotización registrada
3. `Aprobado`: Cotización aprobada
4. `En Reparación`: Trabajo en progreso
5. `Finalizado`: Completado

---

### Value Objects

#### Dinero

**Archivo**: `src/dominio/value_objects/dinero.py`

Representa valores monetarios con operaciones aritméticas.

```python
@dataclass(frozen=True)
class Dinero:
    """
    Value Object: Dinero
    Inmutable, con operaciones aritméticas
    """
    monto: Decimal
    moneda: str = "COP"
    
    def __add__(self, otro: 'Dinero') -> 'Dinero':
        """Suma de dinero"""
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden sumar monedas diferentes")
        return Dinero(self.monto + otro.monto, self.moneda)
    
    def __sub__(self, otro: 'Dinero') -> 'Dinero':
        """Resta de dinero"""
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden restar monedas diferentes")
        return Dinero(self.monto - otro.monto, self.moneda)
    
    def multiplicar(self, factor: Decimal) -> 'Dinero':
        """Multiplica el monto por un factor"""
        return Dinero(self.monto * factor, self.moneda)
    
    def porcentaje(self, porcentaje: Decimal) -> 'Dinero':
        """Calcula un porcentaje del monto"""
        return Dinero(self.monto * (porcentaje / Decimal('100')), self.moneda)
```

**Ejemplo**:
```python
canon = Dinero(Decimal('1000000'), 'COP')
comision = canon.porcentaje(Decimal('10'))  # 10% = 100,000
total = canon + comision  # 1,100,000
```

---

#### DocumentoIdentidad

**Archivo**: `src/dominio/value_objects/documento_identidad.py`

Representa un documento de identificación con validación.

```python
@dataclass(frozen=True)
class DocumentoIdentidad:
    """
    Value Object: Documento de Identidad
    """
    tipo: str  # CC, CE, NIT, Pasaporte
    numero: str
    
    def __post_init__(self):
        """Validación"""
        if not self.numero:
            raise ValueError("El número de documento es obligatorio")
        if self.tipo not in ['CC', 'CE', 'NIT', 'Pasaporte']:
            raise ValueError(f"Tipo de documento inválido: {self.tipo}")
```

---

### Interfaces (Protocols)

#### IRepositorio[T]

**Archivo**: `src/dominio/interfaces/repositorio.py`

Interfaz genérica para repositorios.

```python
from typing import Protocol, TypeVar, Generic, Optional, List

T = TypeVar('T')

class IRepositorio(Protocol, Generic[T]):
    """
    Interfaz genérica para repositorios
    """
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad"""
        ...
    
    def obtener_por_id(self, id: int) -> Optional[T]:
        """Obtiene una entidad por ID"""
        ...
    
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente"""
        ...
    
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad"""
        ...
    
    def listar_todos(self) -> List[T]:
        """Lista todas las entidades"""
        ...
```

---

## Capa de Repositorios

Los repositorios implementan la persistencia en SQLite.

### RepositorioPersonaSQLite

**Archivo**: `src/infraestructura/persistencia/repositorio_persona_sqlite.py`

```python
class RepositorioPersonaSQLite:
    """
    Implementación SQLite del repositorio de Persona
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def crear(self, persona: Persona) -> Persona:
        """Crea una nueva persona en la BD"""
        query = """
            INSERT INTO PERSONAS (
                TIPO_DOCUMENTO, NUMERO_DOCUMENTO, NOMBRE_COMPLETO,
                TELEFONO_PRINCIPAL, CORREO_ELECTRONICO, DIRECCION_PRINCIPAL,
                ESTADO_REGISTRO, CREATED_BY
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        # ... implementación
    
    def obtener_por_id(self, id_persona: int) -> Optional[Persona]:
        """Obtiene una persona por ID"""
        query = "SELECT * FROM PERSONAS WHERE ID_PERSONA = ?"
        # ... implementación
    
    def buscar_por_documento(self, numero_documento: str) -> Optional[Persona]:
        """Busca una persona por número de documento"""
        query = "SELECT * FROM PERSONAS WHERE NUMERO_DOCUMENTO = ?"
        # ... implementación
    
    def listar_activos(self) -> List[Persona]:
        """Lista todas las personas activas"""
        query = "SELECT * FROM PERSONAS WHERE ESTADO_REGISTRO = 1"
        # ... implementación
```

**Métodos Adicionales**:
- `buscar_por_documento(numero: str) -> Optional[Persona]`
- `listar_activos() -> List[Persona]`
- `listar_por_rol(rol: str) -> List[Persona]`

---

### RepositorioPropiedadSQLite

**Archivo**: `src/infraestructura/persistencia/repositorio_propiedad_sqlite.py`

```python
class RepositorioPropiedadSQLite:
    """
    Implementación SQLite del repositorio de Propiedad
    """
    def listar_disponibles(self) -> List[Propiedad]:
        """Lista propiedades disponibles para arriendo"""
        query = """
            SELECT * FROM PROPIEDADES 
            WHERE DISPONIBLE_ARRIENDO = 1 
            AND ESTADO_REGISTRO = 1
        """
        # ... implementación
    
    def buscar_por_matricula(self, matricula: str) -> Optional[Propiedad]:
        """Busca una propiedad por matrícula inmobiliaria"""
        # ... implementación
    
    def listar_por_municipio(self, id_municipio: int) -> List[Propiedad]:
        """Lista propiedades de un municipio específico"""
        # ... implementación
```

---

## Capa de Servicios

Los servicios orquestan la lógica de aplicación y casos de uso.

### ServicioAutenticacion

**Archivo**: `src/aplicacion/servicios/servicio_autenticacion.py`

```python
class ServicioAutenticacion:
    """
    Servicio de autenticación de usuarios
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_usuario = RepositorioUsuarioSQLite(db_manager)
        self.repo_sesion = RepositorioSesionSQLite(db_manager)
    
    def autenticar(self, nombre_usuario: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario
        
        Args:
            nombre_usuario: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Usuario si las credenciales son correctas, None en caso contrario
        """
        # Hash de contraseña con SHA256
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Buscar usuario
        usuario = self.repo_usuario.obtener_por_nombre(nombre_usuario)
        
        if usuario and usuario.password_hash == password_hash:
            # Crear sesión
            self.repo_sesion.crear_sesion(usuario.id_usuario)
            return usuario
        
        return None
    
    def cerrar_sesion(self, id_sesion: int) -> bool:
        """Cierra una sesión activa"""
        return self.repo_sesion.cerrar_sesion(id_sesion)
```

---

### ServicioPersonas

**Archivo**: `src/aplicacion/servicios/servicio_personas.py`

```python
class ServicioPersonas:
    """
    Servicio de gestión de personas y roles
    """
    def crear_persona_con_roles(
        self, 
        datos_persona: Dict, 
        roles: List[str],
        datos_extras: Optional[Dict[str, Dict]] = None,
        usuario_sistema: str = "sistema"
    ) -> PersonaConRoles:
        """
        Crea una nueva persona y le asigna roles
        
        Args:
            datos_persona: Datos de la persona (nombre, documento, etc.)
            roles: Lista de roles a asignar ["Propietario", "Asesor", etc.]
            datos_extras: Datos adicionales por rol
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            PersonaConRoles con la persona creada y sus roles
        
        Example:
            >>> servicio = ServicioPersonas(db)
            >>> persona = servicio.crear_persona_con_roles(
            ...     datos_persona={
            ...         'tipo_documento': 'CC',
            ...         'numero_documento': '123456789',
            ...         'nombre_completo': 'Juan Pérez',
            ...         'telefono_principal': '3001234567',
            ...         'correo_electronico': 'juan@example.com'
            ...     },
            ...     roles=['Propietario', 'Asesor'],
            ...     datos_extras={
            ...         'Propietario': {
            ...             'banco': 'Bancolombia',
            ...             'tipo_cuenta': 'Ahorros',
            ...             'numero_cuenta': '12345678'
            ...         },
            ...         'Asesor': {
            ...             'porcentaje_comision': 3.0
            ...         }
            ...     }
            ... )
        """
        # Crear persona
        persona = Persona(**datos_persona)
        persona.created_by = usuario_sistema
        persona = self.repo_persona.crear(persona)
        
        # Asignar roles
        for rol in roles:
            datos_rol = datos_extras.get(rol, {}) if datos_extras else {}
            self._asignar_rol_interno(persona.id_persona, rol, datos_rol, usuario_sistema)
        
        # Retornar persona completa con roles
        return self.obtener_persona_completa(persona.id_persona)
    
    def listar_personas(
        self, 
        filtro_rol: Optional[str] = None, 
        solo_activos: bool = True,
        busqueda: Optional[str] = None
    ) -> List[PersonaConRoles]:
        """
        Lista personas con sus roles
        
        Args:
            filtro_rol: Filtrar por rol específico
            solo_activos: Solo personas activas
            busqueda: Búsqueda por nombre o documento
        
        Returns:
            Lista de PersonaConRoles
        """
        # ... implementación
```

---

### ServicioPropiedades

**Archivo**: `src/aplicacion/servicios/servicio_propiedades.py`

```python
class ServicioPropiedades:
    """
    Servicio de gestión de propiedades
    """
    def crear_propiedad(self, datos: Dict, usuario_sistema: str = "sistema") -> Propiedad:
        """
        Crea una nueva propiedad
        
        Args:
            datos: Datos de la propiedad
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            Propiedad creada
        
        Example:
            >>> servicio = ServicioPropiedades(db)
            >>> propiedad = servicio.crear_propiedad({
            ...     'matricula_inmobiliaria': '001-2023',
            ...     'tipo_inmueble': 'Apartamento',
            ...     'id_municipio': 1,
            ...     'direccion': 'Calle 123 #45-67',
            ...     'area_m2': 80.0,
            ...     'num_habitaciones': 3,
            ...     'num_banos': 2,
            ...     'canon_arrendamiento': 1500000
            ... })
        """
        propiedad = Propiedad(**datos)
        propiedad.created_by = usuario_sistema
        return self.repo_propiedad.crear(propiedad)
    
    def listar_propiedades(self, filtros: Dict = None) -> List[Propiedad]:
        """
        Lista propiedades con filtros opcionales
        
        Args:
            filtros: {
                'tipo_inmueble': str,
                'disponible': bool,
                'id_municipio': int,
                'busqueda': str
            }
        
        Returns:
            Lista de propiedades
        """
        # ... implementación con filtros
```

---

### ServicioFinanciero

**Archivo**: `src/aplicacion/servicios/servicio_financiero.py`

```python
class ServicioFinanciero:
    """
    Servicio de gestión financiera (recaudos y liquidaciones)
    """
    def registrar_recaudo(self, datos: Dict, usuario_sistema: str = "sistema") -> Recaudo:
        """
        Registra un nuevo recaudo (pago de inquilino)
        
        Args:
            datos: {
                'id_contrato_arrendamiento': int,
                'fecha_pago': date,
                'metodo_pago': str,
                'referencia_bancaria': str (opcional),
                'conceptos': [
                    {'concepto': 'Canon', 'valor': Decimal},
                    {'concepto': 'Administración', 'valor': Decimal},
                    {'concepto': 'Mora', 'valor': Decimal}
                ]
            }
        
        Returns:
            Recaudo creado
        
        Example:
            >>> servicio = ServicioFinanciero(db)
            >>> recaudo = servicio.registrar_recaudo({
            ...     'id_contrato_arrendamiento': 1,
            ...     'fecha_pago': date(2025, 1, 10),
            ...     'metodo_pago': 'Transferencia',
            ...     'referencia_bancaria': 'TRF123456',
            ...     'conceptos': [
            ...         {'concepto': 'Canon', 'valor': Decimal('1500000')},
            ...         {'concepto': 'Administración', 'valor': Decimal('150000')}
            ...     ]
            ... })
        """
        # Calcular mora automáticamente si hay retraso
        mora = self.calcular_mora(
            datos['id_contrato_arrendamiento'], 
            datos['fecha_pago']
        )
        
        # Sumar conceptos
        valor_total = sum(c['valor'] for c in datos['conceptos']) + mora
        
        # Crear recaudo
        recaudo = Recaudo(
            id_contrato_arrendamiento=datos['id_contrato_arrendamiento'],
            fecha_pago=datos['fecha_pago'],
            valor_total=valor_total,
            metodo_pago=datos['metodo_pago'],
            referencia_bancaria=datos.get('referencia_bancaria'),
            estado='Pendiente',
            created_by=usuario_sistema
        )
        
        return self.repo_recaudo.crear(recaudo)
    
    def calcular_mora(self, id_contrato: int, fecha_pago: date) -> Decimal:
        """
        Calcula mora automáticamente
        
        Fórmula: (Canon + Admin) × (6% / 365) × Días de Retraso
        
        Args:
            id_contrato: ID del contrato
            fecha_pago: Fecha en que se realizó el pago
        
        Returns:
            Valor de la mora
        """
        contrato = self.repo_contrato.obtener_por_id(id_contrato)
        
        # Calcular días de retraso
        dia_pago_esperado = contrato.dia_pago
        fecha_esperada = date(fecha_pago.year, fecha_pago.month, dia_pago_esperado)
        
        if fecha_pago <= fecha_esperada:
            return Decimal('0')
        
        dias_retraso = (fecha_pago - fecha_esperada).days
        
        # Calcular mora (6% anual)
        base = contrato.canon_mensual + contrato.valor_administracion
        tasa_diaria = Decimal('0.06') / Decimal('365')
        mora = base * tasa_diaria * Decimal(dias_retraso)
        
        return mora.quantize(Decimal('0.01'))
    
    def generar_liquidacion_mensual(
        self, 
        id_contrato: int, 
        periodo: str,
        usuario_sistema: str = "sistema"
    ) -> Liquidacion:
        """
        Genera una liquidación mensual para un propietario
        
        Args:
            id_contrato: ID del contrato de arrendamiento
            periodo: Período en formato YYYY-MM
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            Liquidación generada
        
        Fórmula:
            Ingresos = Canon Bruto + Otros Ingresos
            Egresos = Comisión + IVA + 4x1000 + Costos Incidentes
            Neto = Ingresos - Egresos
        """
        # Obtener contrato y mandato
        contrato = self.repo_contrato.obtener_por_id(id_contrato)
        mandato = self.repo_mandato.obtener_por_propiedad(contrato.id_propiedad)
        
        # Calcular ingresos
        ingresos = contrato.canon_mensual
        
        # Calcular egresos
        comision = ingresos * (mandato.porcentaje_comision / Decimal('100'))
        iva = comision * Decimal('0.19')
        cuatro_mil = ingresos * Decimal('0.004')
        costos_incidentes = self._obtener_costos_incidentes(id_contrato, periodo)
        
        egresos = comision + iva + cuatro_mil + costos_incidentes
        neto = ingresos - egresos
        
        # Crear liquidación
        liquidacion = Liquidacion(
            id_contrato_arrendamiento=id_contrato,
            periodo=periodo,
            ingresos_totales=ingresos,
            egresos_totales=egresos,
            neto_pagar=neto,
            estado='Generada',
            created_by=usuario_sistema
        )
        
        return self.repo_liquidacion.crear(liquidacion)
```

---

### ServicioIncidentes

**Archivo**: `src/aplicacion/servicios/servicio_incidentes.py`

```python
class ServicioIncidentes:
    """
    Servicio de gestión de incidentes y mantenimientos
    """
    def reportar_incidente(self, datos: Dict, usuario_sistema: str = "sistema") -> Incidente:
        """
        Reporta un nuevo incidente
        
        Args:
            datos: {
                'id_propiedad': int,
                'titulo': str,
                'descripcion': str,
                'prioridad': str,
                'categoria': str,
                'responsable_costo': str
            }
        
        Returns:
            Incidente creado
        """
        incidente = Incidente(**datos)
        incidente.estado = 'Reportado'
        incidente.created_by = usuario_sistema
        return self.repo_incidente.crear(incidente)
    
    def registrar_cotizacion(
        self, 
        id_incidente: int, 
        datos: Dict,
        usuario_sistema: str = "sistema"
    ) -> Cotizacion:
        """
        Registra una cotización para un incidente
        
        Args:
            id_incidente: ID del incidente
            datos: {
                'id_proveedor': int,
                'valor_cotizado': Decimal,
                'descripcion_trabajo': str,
                'tiempo_estimado_dias': int
            }
        
        Returns:
            Cotización creada
        """
        cotizacion = Cotizacion(
            id_incidente=id_incidente,
            **datos,
            aprobada=False,
            created_by=usuario_sistema
        )
        
        cotizacion = self.repo_cotizacion.crear(cotizacion)
        
        # Actualizar estado del incidente a "Cotizado"
        incidente = self.repo_incidente.obtener_por_id(id_incidente)
        incidente.estado = 'Cotizado'
        self.repo_incidente.actualizar(incidente)
        
        return cotizacion
    
    def aprobar_cotizacion(self, id_cotizacion: int) -> bool:
        """
        Aprueba una cotización
        
        Args:
            id_cotizacion: ID de la cotización
        
        Returns:
            True si se aprobó correctamente
        """
        cotizacion = self.repo_cotizacion.obtener_por_id(id_cotizacion)
        cotizacion.aprobada = True
        self.repo_cotizacion.actualizar(cotizacion)
        
        # Actualizar estado del incidente a "Aprobado"
        incidente = self.repo_incidente.obtener_por_id(cotizacion.id_incidente)
        incidente.estado = 'Aprobado'
        self.repo_incidente.actualizar(incidente)
        
        return True
    
    def avanzar_estado(self, id_incidente: int) -> bool:
        """
        Avanza el estado del incidente al siguiente
        
        Flujo: Reportado → Cotizado → Aprobado → En Reparación → Finalizado
        
        Args:
            id_incidente: ID del incidente
        
        Returns:
            True si se avanzó correctamente
        
        Raises:
            ValueError: Si no se puede avanzar (falta cotización, etc.)
        """
        incidente = self.repo_incidente.obtener_por_id(id_incidente)
        
        if incidente.estado == 'Reportado':
            # Verificar que tenga cotización
            cotizaciones = self.repo_cotizacion.listar_por_incidente(id_incidente)
            if not cotizaciones:
                raise ValueError("El incidente debe tener al menos una cotización")
            incidente.estado = 'Cotizado'
        
        elif incidente.estado == 'Cotizado':
            # Verificar que tenga cotización aprobada
            cotizacion_aprobada = self.repo_cotizacion.obtener_aprobada(id_incidente)
            if not cotizacion_aprobada:
                raise ValueError("Debe aprobar una cotización primero")
            incidente.estado = 'Aprobado'
        
        elif incidente.estado == 'Aprobado':
            incidente.estado = 'En Reparación'
        
        elif incidente.estado == 'En Reparación':
            incidente.estado = 'Finalizado'
            incidente.fecha_finalizacion = date.today()
        
        else:
            raise ValueError(f"No se puede avanzar desde el estado {incidente.estado}")
        
        self.repo_incidente.actualizar(incidente)
        return True
```

---

## Patrones y Estrategias

### Patrón Repository

El patrón Repository abstrae la persistencia de datos.

**Beneficios**:
- Desacopla la lógica de negocio de la persistencia
- Facilita el testing (mocks)
- Permite cambiar la implementación de BD sin afectar el dominio

**Ejemplo**:
```python
# Interfaz (Protocol)
class IRepositorioPersona(Protocol):
    def crear(self, persona: Persona) -> Persona: ...
    def obtener_por_id(self, id: int) -> Optional[Persona]: ...

# Implementación SQLite
class RepositorioPersonaSQLite:
    def crear(self, persona: Persona) -> Persona:
        # SQL INSERT
        pass

# Uso en servicio
class ServicioPersonas:
    def __init__(self, repo: IRepositorioPersona):
        self.repo = repo  # Depende de la interfaz, no de la implementación
```

---

### Patrón DTO (Data Transfer Object)

Los DTOs transfieren datos entre capas sin exponer entidades de dominio.

**Ejemplo**:
```python
@dataclass
class PersonaDTO:
    """DTO para transferir datos de Persona"""
    id_persona: Optional[int]
    nombre_completo: str
    numero_documento: str
    telefono_principal: Optional[str]
    correo_electronico: Optional[str]
    roles: List[str]

# Mapper: Entity ↔ DTO
class PersonaMapper:
    @staticmethod
    def to_dto(persona: Persona, roles: List[str]) -> PersonaDTO:
        return PersonaDTO(
            id_persona=persona.id_persona,
            nombre_completo=persona.nombre_completo,
            numero_documento=persona.numero_documento,
            telefono_principal=persona.telefono_principal,
            correo_electronico=persona.correo_electronico,
            roles=roles
        )
```

---

### Strategy Pattern - Cálculo de Comisiones

El patrón Strategy permite diferentes algoritmos de cálculo.

**Interfaz**:
```python
class EstrategiaComision(Protocol):
    """Interfaz para estrategias de cálculo de comisión"""
    def calcular(self, monto: Decimal) -> Decimal:
        ...
```

**Implementaciones**:
```python
class EstrategiaComisionFija:
    """Comisión con porcentaje fijo"""
    def __init__(self, porcentaje: Decimal):
        self.porcentaje = porcentaje
    
    def calcular(self, monto: Decimal) -> Decimal:
        return monto * (self.porcentaje / Decimal('100'))

class EstrategiaComisionEscalonada:
    """Comisión por rangos de valor"""
    def __init__(self, rangos: List[Tuple[Decimal, Decimal, Decimal]]):
        # rangos: [(min, max, porcentaje), ...]
        self.rangos = rangos
    
    def calcular(self, monto: Decimal) -> Decimal:
        for min_val, max_val, porcentaje in self.rangos:
            if min_val <= monto <= max_val:
                return monto * (porcentaje / Decimal('100'))
        return Decimal('0')
```

**Uso**:
```python
# Comisión fija del 10%
estrategia = EstrategiaComisionFija(Decimal('10'))
comision = estrategia.calcular(Decimal('1500000'))  # 150,000

# Comisión escalonada
estrategia = EstrategiaComisionEscalonada([
    (Decimal('0'), Decimal('1000000'), Decimal('8')),
    (Decimal('1000001'), Decimal('2000000'), Decimal('10')),
    (Decimal('2000001'), Decimal('999999999'), Decimal('12'))
])
comision = estrategia.calcular(Decimal('1500000'))  # 10% = 150,000
```

---

## Ejemplos de Uso

### Ejemplo 1: Crear Persona con Múltiples Roles

```python
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios import ServicioPersonas

# Inicializar
db = DatabaseManager()
servicio = ServicioPersonas(db)

# Crear persona con roles Propietario y Asesor
persona = servicio.crear_persona_con_roles(
    datos_persona={
        'tipo_documento': 'CC',
        'numero_documento': '123456789',
        'nombre_completo': 'María García López',
        'telefono_principal': '3001234567',
        'correo_electronico': 'maria@example.com',
        'direccion_principal': 'Calle 123 #45-67'
    },
    roles=['Propietario', 'Asesor'],
    datos_extras={
        'Propietario': {
            'banco': 'Bancolombia',
            'tipo_cuenta': 'Ahorros',
            'numero_cuenta': '12345678901'
        },
        'Asesor': {
            'porcentaje_comision': Decimal('3.5'),
            'observaciones': 'Asesor senior'
        }
    },
    usuario_sistema='admin'
)

print(f"Persona creada: {persona.nombre_completo}")
print(f"Roles: {persona.roles()}")
```

---

### Ejemplo 2: Registrar Recaudo con Mora

```python
from src.aplicacion.servicios import ServicioFinanciero
from datetime import date
from decimal import Decimal

# Inicializar
servicio = ServicioFinanciero(db)

# Registrar pago con 10 días de retraso
# (contrato con día de pago = 5, pago realizado el 15)
recaudo = servicio.registrar_recaudo(
    datos={
        'id_contrato_arrendamiento': 1,
        'fecha_pago': date(2025, 1, 15),
        'metodo_pago': 'Transferencia',
        'referencia_bancaria': 'TRF20250115001',
        'conceptos': [
            {'concepto': 'Canon', 'valor': Decimal('1500000')},
            {'concepto': 'Administración', 'valor': Decimal('150000')}
        ]
    },
    usuario_sistema='admin'
)

print(f"Recaudo registrado: {recaudo.id_recaudo}")
print(f"Valor total (con mora): {recaudo.valor_total}")
```

---

### Ejemplo 3: Generar Liquidación Mensual

```python
from src.aplicacion.servicios import ServicioFinanciero

servicio = ServicioFinanciero(db)

# Generar liquidación de enero 2025
liquidacion = servicio.generar_liquidacion_mensual(
    id_contrato=1,
    periodo='2025-01',
    usuario_sistema='admin'
)

print(f"Liquidación generada: {liquidacion.id_liquidacion}")
print(f"Ingresos: {liquidacion.ingresos_totales}")
print(f"Egresos: {liquidacion.egresos_totales}")
print(f"Neto a pagar: {liquidacion.neto_pagar}")
```

---

### Ejemplo 4: Flujo Completo de Incidente

```python
from src.aplicacion.servicios import ServicioIncidentes
from decimal import Decimal

servicio = ServicioIncidentes(db)

# 1. Reportar incidente
incidente = servicio.reportar_incidente(
    datos={
        'id_propiedad': 1,
        'titulo': 'Fuga de agua en baño',
        'descripcion': 'Fuga en la tubería del lavamanos',
        'prioridad': 'Alta',
        'categoria': 'Plomería',
        'responsable_costo': 'Propietario'
    },
    usuario_sistema='admin'
)

print(f"Incidente reportado: {incidente.id_incidente}")
print(f"Estado: {incidente.estado}")  # Reportado

# 2. Registrar cotización
cotizacion = servicio.registrar_cotizacion(
    id_incidente=incidente.id_incidente,
    datos={
        'id_proveedor': 1,
        'valor_cotizado': Decimal('250000'),
        'descripcion_trabajo': 'Cambio de tubería y sifón',
        'tiempo_estimado_dias': 1
    },
    usuario_sistema='admin'
)

print(f"Cotización registrada: {cotizacion.id_cotizacion}")
# Estado del incidente ahora es: Cotizado

# 3. Aprobar cotización
servicio.aprobar_cotizacion(cotizacion.id_cotizacion)
# Estado del incidente ahora es: Aprobado

# 4. Avanzar a "En Reparación"
servicio.avanzar_estado(incidente.id_incidente)
# Estado: En Reparación

# 5. Finalizar incidente
servicio.avanzar_estado(incidente.id_incidente)
# Estado: Finalizado
```

---

## Conclusiones

Esta API interna está diseñada para:

1. **Claridad**: Nombres descriptivos y documentación completa
2. **Consistencia**: Patrones uniformes en toda la aplicación
3. **Mantenibilidad**: Código limpio y bien organizado
4. **Testabilidad**: Interfaces y dependencias inyectadas
5. **Extensibilidad**: Fácil agregar nuevas funcionalidades

> [!TIP]
> Consulte los tests en `tests/` para ver más ejemplos de uso de cada servicio.

---

**Fin de la Documentación de API Interna**

*Última actualización: Diciembre 2025*  
*Versión del Sistema: 1.0*

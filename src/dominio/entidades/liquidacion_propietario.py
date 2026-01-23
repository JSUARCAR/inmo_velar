"""
Entidad de Dominio: Liquidación Propietario
Representa la liquidación consolidada de todos los contratos de mandato activos de un propietario.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class LiquidacionPropietario:
    """
    Entidad que representa la liquidación consolidada de un propietario.
    
    Agrupa todas las liquidaciones de los contratos de mandato activos del propietario
    para un período determinado, calculando totales consolidados.
    
    Business Rules:
    - Un propietario puede tener múltiples contratos de mandato activos simultáneamente
    - La liquidación consolidada suma los valores de todas las liquidaciones individuales
    - El estado consolidado refleja: 'En Proceso' si alguna está en proceso, sino el mayoritario
    """
    
    # Identificación del Propietario
    id_propietario: int
    nombre_propietario: str
    documento_propietario: str
    
    # Período
    periodo: str  # Formato 'YYYY-MM' (ej: '2024-10')
    
    # Liquidaciones Individuales (una por cada contrato)
    liquidaciones_contratos: List = field(default_factory=list)  # List[Liquidacion]
    
    # Cantidad de contratos/propiedades
    cantidad_contratos: int = 0
    
    # Totales Consolidados - Ingresos
    total_canon_bruto: int = 0
    total_otros_ingresos: int = 0
    total_ingresos: int = 0
    
    # Totales Consolidados - Egresos
    total_comision_monto: int = 0
    total_iva_comision: int = 0
    total_impuesto_4x1000: int = 0
    total_gastos_administracion: int = 0
    total_gastos_servicios: int = 0
    total_gastos_reparaciones: int = 0
    total_otros_egresos: int = 0
    total_egresos: int = 0
    
    # Resultado Final Consolidado
    neto_total_a_pagar: int = 0
    
    # Estado Consolidado
    estado_consolidado: str = "En Proceso"
    # Lógica: 'En Proceso' si alguna lo está, 
    # 'Aprobada' si todas están aprobadas,
    # 'Pagada' si todas están pagadas,
    # 'Mixto' en otros casos
    
    # Observaciones y Metadata
    observaciones_consolidadas: Optional[str] = None
    fecha_generacion: Optional[str] = field(default_factory=lambda: datetime.now().date().isoformat())
    
    # Información de Pago (si todas están pagadas)
    fecha_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    referencia_pago: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.estado_consolidado not in ['En Proceso', 'Aprobada', 'Pagada', 'Mixto', 'Cancelada']:
            raise ValueError(f"Estado consolidado inválido: {self.estado_consolidado}")
        
        # Validar formato de período (YYYY-MM)
        if len(self.periodo) != 7 or self.periodo[4] != '-':
            raise ValueError(f"Formato de período inválido: {self.periodo}. Use YYYY-MM")
    
    def consolidar(self):
        """
        Calcula los totales consolidados sumando todas las liquidaciones individuales.
        También determina el estado consolidado según las reglas de negocio.
        """
        from src.dominio.entidades.liquidacion import Liquidacion
        
        if not self.liquidaciones_contratos:
            raise ValueError("No hay liquidaciones para consolidar")
        
        # Resetear totales
        self.total_canon_bruto = 0
        self.total_otros_ingresos = 0
        self.total_ingresos = 0
        
        self.total_comision_monto = 0
        self.total_iva_comision = 0
        self.total_impuesto_4x1000 = 0
        self.total_gastos_administracion = 0
        self.total_gastos_servicios = 0
        self.total_gastos_reparaciones = 0
        self.total_otros_egresos = 0
        self.total_egresos = 0
        
        self.neto_total_a_pagar = 0
        self.cantidad_contratos = len(self.liquidaciones_contratos)
        
        # Contadores para determinar estado consolidado
        estados = {
            'En Proceso': 0,
            'Aprobada': 0,
            'Pagada': 0,
            'Cancelada': 0
        }
        
        # Sumar todas las liquidaciones
        for liq in self.liquidaciones_contratos:
            # Sumar ingresos
            self.total_canon_bruto += liq.canon_bruto
            self.total_otros_ingresos += liq.otros_ingresos
            self.total_ingresos += liq.total_ingresos
            
            # Sumar egresos
            self.total_comision_monto += liq.comision_monto
            self.total_iva_comision += liq.iva_comision
            self.total_impuesto_4x1000 += liq.impuesto_4x1000
            self.total_gastos_administracion += liq.gastos_administracion
            self.total_gastos_servicios += liq.gastos_servicios
            self.total_gastos_reparaciones += liq.gastos_reparaciones
            self.total_otros_egresos += liq.otros_egresos
            self.total_egresos += liq.total_egresos
            
            # Sumar neto
            self.neto_total_a_pagar += liq.neto_a_pagar
            
            # Contar estados
            if liq.estado_liquidacion in estados:
                estados[liq.estado_liquidacion] += 1
        
        # Determinar estado consolidado según reglas de negocio
        total_liquidaciones = len(self.liquidaciones_contratos)
        
        if estados['En Proceso'] > 0:
            self.estado_consolidado = 'En Proceso'
        elif estados['Aprobada'] == total_liquidaciones:
            self.estado_consolidado = 'Aprobada'
        elif estados['Pagada'] == total_liquidaciones:
            self.estado_consolidado = 'Pagada'
            # Si todas están pagadas, tomar datos de pago de la primera (deberían ser iguales)
            primera_pagada = next((liq for liq in self.liquidaciones_contratos if liq.esta_pagada), None)
            if primera_pagada:
                self.fecha_pago = primera_pagada.fecha_pago
                self.metodo_pago = primera_pagada.metodo_pago
                self.referencia_pago = primera_pagada.referencia_pago
        elif estados['Cancelada'] == total_liquidaciones:
            self.estado_consolidado = 'Cancelada'
        else:
            self.estado_consolidado = 'Mixto'
    
    @property
    def esta_en_proceso(self) -> bool:
        """Verifica si la liquidación consolidada está siendo editada"""
        return self.estado_consolidado == "En Proceso"
    
    @property
    def esta_aprobada(self) -> bool:
        """Verifica si todas las liquidaciones fueron aprobadas"""
        return self.estado_consolidado == "Aprobada"
    
    @property
    def esta_pagada(self) -> bool:
        """Verifica si todas las liquidaciones fueron pagadas"""
        return self.estado_consolidado == "Pagada"
    
    @property
    def esta_cancelada(self) -> bool:
        """Verifica si todas las liquidaciones fueron canceladas"""
        return self.estado_consolidado == "Cancelada"
    
    @property
    def es_mixto(self) -> bool:
        """Verifica si hay liquidaciones en estados diferentes"""
        return self.estado_consolidado == "Mixto"
    
    def obtener_resumen_dict(self) -> dict:
        """
        Retorna un diccionario con el resumen consolidado para la UI.
        """
        return {
            'id_propietario': self.id_propietario,
            'nombre_propietario': self.nombre_propietario,
            'documento_propietario': self.documento_propietario,
            'periodo': self.periodo,
            'cantidad_contratos': self.cantidad_contratos,
            'total_canon_bruto': self.total_canon_bruto,
            'total_ingresos': self.total_ingresos,
            'total_egresos': self.total_egresos,
            'neto_total_a_pagar': self.neto_total_a_pagar,
            'estado_consolidado': self.estado_consolidado,
            'fecha_pago': self.fecha_pago,
            'observaciones': self.observaciones_consolidadas
        }

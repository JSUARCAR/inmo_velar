"""
Mock Data Repository para PDFs
===============================
Repositorio de datos mock para desarrollo y testing del sistema PDF.

Este módulo proporciona datos de prueba realistas que simulan la DB PostgreSQL.
Cuando estés listo para producción, reemplaza estos métodos con queries reales.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random


class MockPDFRepository:
    """
    Repositorio Mock para datos de PDFs
    
    Simula conexión a base de datos PostgreSQL con datos realistas.
    
    IMPORTANTE: En producción, reemplazar con queries reales a tu DB.
    Ver documentación en docs/DB_INTEGRATION_GUIDE.md
    """
    
    # Datos mock de contratos
    _contratos_mock = {
        1: {
            'id': 1,
            'fecha_inicio': '2026-01-15',
            'duracion_meses': 12,
            'canon': 1500000,
            'deposito': 1500000,
            'administracion': 150000,
            'dia_pago': 5,
            'estado': 'ACTIVO',
            'arrendador_id': 1,
            'arrendatario_id': 2,
            'inmueble_id': 1
        },
        2: {
            'id': 2,
            'fecha_inicio': '2026-01-10',
            'duracion_meses': 24,
            'canon': 2000000,
            'deposito': 2000000,
            'administracion': 200000,
            'dia_pago': 10,
            'estado': 'ACTIVO',
            'arrendador_id': 3,
            'arrendatario_id': 4,
            'inmueble_id': 2
        }
    }
    
    # Datos mock de personas
    _personas_mock = {
        1: {
            'id': 1,
            'nombre': 'Juan Pérez García',
            'tipo_documento': 'CC',
            'documento': '1234567',
            'telefono': '(601) 555-0001',
            'email': 'jperez@email.com',
            'direccion': 'Calle 100 #15-20, Bogotá'
        },
        2: {
            'id': 2,
            'nombre': 'María López Ruiz',
            'tipo_documento': 'CC',
            'documento': '7890123',
            'telefono': '(601) 555-0002',
            'email': 'mlopez@email.com',
            'direccion': 'Avenida 19 #80-40, Bogotá'
        },
        3: {
            'id': 3,
            'nombre': 'Carlos Ruiz Mendoza',
            'tipo_documento': 'CC',
            'documento': '5678901',
            'telefono': '(601) 555-0003',
            'email': 'cruiz@email.com',
            'direccion': 'Carrera 15 #90-30, Bogotá'
        },
        4: {
            'id': 4,
            'nombre': 'Ana Gómez Torres',
            'tipo_documento': 'CC',
            'documento': '2345678',
            'telefono': '(601) 555-0004',
            'email': 'agomez@email.com',
            'direccion': 'Calle 80 #10-15, Bogotá'
        }
    }
    
    # Datos mock de inmuebles
    _inmuebles_mock = {
        1: {
            'id': 1,
            'direccion': 'Carrera 7 #45-67 Apto 501',
            'tipo': 'Apartamento',
            'area': 65,
            'habitaciones': 3,
            'banos': 2,
            'estrato': 3,
            'propietario_id': 1
        },
        2: {
            'id': 2,
            'direccion': 'Avenida Principal #10-20 Casa 15',
            'tipo': 'Casa',
            'area': 120,
            'habitaciones': 4,
            'banos': 3,
            'estrato': 4,
            'propietario_id': 3
        }
    }
    
    @classmethod
    def get_contrato_data(cls, contrato_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos completos de un contrato
        
        Args:
            contrato_id: ID del contrato
            
        Returns:
            Diccionario con todos los datos del contrato o None
            
        TODO PRODUCCIÓN:
            Reemplazar con query real:
            ```python
            from src.infraestructura.persistencia.database import SessionLocal
            from src.dominio.entidades import Contrato, Persona, Inmueble
            
            with SessionLocal() as db:
                contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
                # ... construir diccionario con datos
            ```
        """
        contrato = cls._contratos_mock.get(contrato_id)
        if not contrato:
            return None
        
        arrendador = cls._personas_mock.get(contrato['arrendador_id'])
        arrendatario = cls._personas_mock.get(contrato['arrendatario_id'])
        inmueble = cls._inmuebles_mock.get(contrato['inmueble_id'])
        
        return {
            'contrato_id': contrato['id'],
            'fecha': contrato['fecha_inicio'],
            'estado': contrato['estado'],
            'arrendador': {
                'nombre': arrendador['nombre'],
                'documento': f"{arrendador['tipo_documento']} {arrendador['documento']}",
                'telefono': arrendador['telefono'],
                'email': arrendador['email'],
                'direccion': arrendador['direccion']
            },
            'arrendatario': {
                'nombre': arrendatario['nombre'],
                'documento': f"{arrendatario['tipo_documento']} {arrendatario['documento']}",
                'telefono': arrendatario['telefono'],
                'email': arrendatario['email'],
                'direccion': arrendatario['direccion']
            },
            'inmueble': {
                'direccion': inmueble['direccion'],
                'tipo': inmueble['tipo'],
                'area': str(inmueble['area']),
                'habitaciones': str(inmueble['habitaciones']),
                'banos': str(inmueble['banos']),
                'estrato': str(inmueble['estrato'])
            },
            'condiciones': {
                'canon': contrato['canon'],
                'duracion_meses': contrato['duracion_meses'],
                'dia_pago': contrato['dia_pago'],
                'deposito': contrato['deposito'],
                'administracion': contrato['administracion']
            }
        }
    
    @classmethod
    def get_estado_cuenta_data(
        cls,
        propietario_id: int,
        periodo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos para estado de cuenta de un propietario
        
        Args:
            propietario_id: ID del propietario
            periodo: Período en formato YYYY-MM
            
        Returns:
            Diccionario con datos del estado de cuenta
            
        TODO PRODUCCIÓN:
            Implementar query que obtenga:
            - Datos del propietario
            - Inmuebles del propietario
            - Movimientos (recaudos, descuentos) del período
            - Calcular resumen financiero
        """
        propietario = cls._personas_mock.get(propietario_id)
        if not propietario:
            return None
        
        # Buscar inmueble del propietario
        inmueble = None
        for inm in cls._inmuebles_mock.values():
            if inm['propietario_id'] == propietario_id:
                inmueble = inm
                break
        
        if not inmueble:
            return None
        
        # Obtener contrato activo del inmueble
        contrato = None
        for cont in cls._contratos_mock.values():
            if cont['inmueble_id'] == inmueble['id'] and cont['estado'] == 'ACTIVO':
                contrato = cont
                break
        
        # Generar movimientos mock del período
        movimientos = cls._generar_movimientos_mock(periodo, contrato)
        resumen = cls._calcular_resumen(movimientos)
        
        # Obtener arrendatario si hay contrato
        arrendatario_nombre = "Sin arrendar"
        if contrato:
            arrendatario = cls._personas_mock.get(contrato['arrendatario_id'])
            if arrendatario:
                arrendatario_nombre = arrendatario['nombre']
        
        return {
            'estado_id': propietario_id * 100 + int(periodo.replace('-', '')),
            'periodo': periodo,
            'propietario': {
                'nombre': propietario['nombre'],
                'documento': f"{propietario['tipo_documento']} {propietario['documento']}",
                'telefono': propietario['telefono'],
                'email': propietario['email']
            },
            'inmueble': {
                'direccion': inmueble['direccion'],
                'tipo': inmueble['tipo'],
                'canon': contrato['canon'] if contrato else 0,
                'arrendatario': arrendatario_nombre
            },
            'movimientos': movimientos,
            'resumen': resumen
        }
    
    @classmethod
    def _generar_movimientos_mock(
        cls,
        periodo: str,
        contrato: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Genera movimientos mock para un período"""
        if not contrato:
            return []
        
        movimientos = [
            {
                'fecha': f"{periodo}-05",
                'concepto': 'Canon de arrendamiento',
                'ingreso': contrato['canon'],
                'egreso': 0
            },
            {
                'fecha': f"{periodo}-05",
                'concepto': 'Administración',
                'ingreso': contrato['administracion'],
                'egreso': 0
            },
            {
                'fecha': f"{periodo}-10",
                'concepto': 'Honorarios administración 10%',
                'ingreso': 0,
                'egreso': int(contrato['canon'] * 0.10)
            }
        ]
        
        # Agregar movimientos aleatorios (reparaciones, etc.)
        if random.random() > 0.5:
            movimientos.append({
                'fecha': f"{periodo}-15",
                'concepto': 'Reparación plomería',
                'ingreso': 0,
                'egreso': 150000
            })
        
        return movimientos
    
    @classmethod
    def _calcular_resumen(cls, movimientos: List[Dict]) -> Dict[str, Any]:
        """Calcula resumen financiero de movimientos"""
        total_ingresos = sum(m['ingreso'] for m in movimientos)
        total_egresos = sum(m['egreso'] for m in movimientos)
        
        return {
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'honorarios': int(total_ingresos * 0.10),
            'otros_descuentos': total_egresos - int(total_ingresos * 0.10),
            'valor_neto': total_ingresos - total_egresos,
            'cuenta_bancaria': 'Bancolombia ****1234',
            'fecha_pago': f"{datetime.now().strftime('%Y-%m')}-15"
        }
    
    @classmethod
    def get_certificado_data(
        cls,
        contrato_id: int,
        tipo: str = 'paz_y_salvo'
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos para generar certificado
        
        Args:
            contrato_id: ID del contrato
            tipo: Tipo de certificado
            
        Returns:
            Diccionario con datos del certificado
        """
        contrato = cls._contratos_mock.get(contrato_id)
        if not contrato:
            return None
        
        arrendatario = cls._personas_mock.get(contrato['arrendatario_id'])
        
        contenidos = {
            'paz_y_salvo': (
                f"El señor(a) {arrendatario['nombre']} se encuentra a PAZ Y SALVO "
                f"con la INMOBILIARIA VELAR SAS por concepto de arrendamiento "
                f"del inmueble objeto del contrato No. {contrato_id}.\n\n"
                f"No presenta deudas pendientes por canon de arrendamiento, "
                f"servicios públicos, ni otras obligaciones contractuales."
            ),
            'cumplimiento': (
                f"Certificamos que el señor(a) {arrendatario['nombre']} ha cumplido "
                f"satisfactoriamente con todas las obligaciones derivadas del "
                f"contrato de arrendamiento No. {contrato_id} durante el período de vigencia."
            ),
            'residencia': (
                f"Certificamos que el señor(a) {arrendatario['nombre']} reside en el "
                f"inmueble ubicado en {cls._inmuebles_mock[contrato['inmueble_id']]['direccion']} "
                f"bajo contrato de arrendamiento No. {contrato_id}."
            )
        }
        
        return {
            'certificado_id': contrato_id * 1000 + int(datetime.now().strftime('%H%M')),
            'tipo': tipo,
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'beneficiario': {
                'nombre': arrendatario['nombre'],
                'tipo_documento': arrendatario['tipo_documento'],
                'documento': arrendatario['documento']
            },
            'contenido': contenidos.get(tipo, contenidos['paz_y_salvo']),
            'firmante': {
                'nombre': 'Gerencia General',
                'cargo': 'Representante Legal',
                'documento': 'NIT 900.123.456-7'
            },
            'validez_dias': 30
        }


__all__ = ['MockPDFRepository']

"""
Tests Unitarios: Entidad LiquidacionAsesor
Verifica reglas de negocio y validaciones del dominio.
"""

import pytest
from datetime import datetime
from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor


class TestLiquidacionAsesorCreacion:
    """Tests de creación y validación básica."""
    
    def test_creacion_valida(self):
        """Test: Crear liquidación con datos válidos."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,  # 5%
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Pendiente"
        )
        
        assert liq.id_liquidacion_asesor == 1
        assert liq.id_contrato_a == 100
        assert liq.id_asesor == 5
        assert liq.periodo_liquidacion == "2024-12"
        assert liq.porcentaje_comision == 500
        assert liq.estado_liquidacion == "Pendiente"
    
    def test_porcentaje_real(self):
        """Test: Conversión de porcentaje a decimal."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=550,  # 5.5%
            comision_bruta=82500,
            total_descuentos=0,
            valor_neto_asesor=82500,
            estado_liquidacion="Pendiente"
        )
        
        assert liq.porcentaje_real == 5.5


class TestLiquidacionAsesorValidaciones:
    """Tests de validaciones de reglas de negocio."""
    
    def test_comision_bruta_negativa_falla(self):
        """Test: Comisión bruta negativa debe fallar."""
        with pytest.raises(ValueError, match="comisión bruta"):
            LiquidacionAsesor(
                id_liquidacion_asesor=1,
                id_contrato_a=100,
                id_asesor=5,
                periodo_liquidacion="2024-12",
                canon_arrendamiento_liquidado=1500000,
                porcentaje_comision=500,
                comision_bruta=-1000,  # Inválido
                total_descuentos=0,
                valor_neto_asesor=0,
                estado_liquidacion="Pendiente"
            )
    
    def test_porcentaje_fuera_rango_falla(self):
        """Test: Porcentaje fuera de rango 0-10000 debe fallar."""
        with pytest.raises(ValueError, match="porcentaje"):
            LiquidacionAsesor(
                id_liquidacion_asesor=1,
                id_contrato_a=100,
                id_asesor=5,
                periodo_liquidacion="2024-12",
                canon_arrendamiento_liquidado=1500000,
                porcentaje_comision=15000,  # > 100%, inválido
                comision_bruta=75000,
                total_descuentos=0,
                valor_neto_asesor=75000,
                estado_liquidacion="Pendiente"
            )
    
    def test_estado_invalido_falla(self):
        """Test: Estado no válido debe fallar."""
        with pytest.raises(ValueError, match="Estado"):
            LiquidacionAsesor(
                id_liquidacion_asesor=1,
                id_contrato_a=100,
                id_asesor=5,
                periodo_liquidacion="2024-12",
                canon_arrendamiento_liquidado=1500000,
                porcentaje_comision=500,
                comision_bruta=75000,
                total_descuentos=0,
                valor_neto_asesor=75000,
                estado_liquidacion="EstadoInvalido"  # Inválido
            )
    
    def test_periodo_formato_invalido(self):
        """Test: Período con formato inválido debe fallar."""
        with pytest.raises(ValueError, match="período"):
            LiquidacionAsesor(
                id_liquidacion_asesor=1,
                id_contrato_a=100,
                id_asesor=5,
                periodo_liquidacion="12-2024",  # Formato incorrecto
                canon_arrendamiento_liquidado=1500000,
                porcentaje_comision=500,
                comision_bruta=75000,
                total_descuentos=0,
                valor_neto_asesor=75000,
                estado_liquidacion="Pendiente"
            )


class TestLiquidacionAsesorPropiedadesNegocio:
    """Tests de propiedades de lógica de negocio."""
    
    @pytest.fixture
    def liquidacion_pendiente(self):
        return LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=10000,
            valor_neto_asesor=65000,
            estado_liquidacion="Pendiente"
        )
    
    @pytest.fixture
    def liquidacion_aprobada(self):
        return LiquidacionAsesor(
            id_liquidacion_asesor=2,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-11",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Aprobada"
        )
    
    @pytest.fixture
    def liquidacion_pagada(self):
        return LiquidacionAsesor(
            id_liquidacion_asesor=3,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-10",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Pagada"
        )
    
    def test_esta_pendiente(self, liquidacion_pendiente, liquidacion_aprobada):
        """Test: Propiedad esta_pendiente."""
        assert liquidacion_pendiente.esta_pendiente == True
        assert liquidacion_aprobada.esta_pendiente == False
    
    def test_esta_aprobada(self, liquidacion_pendiente, liquidacion_aprobada):
        """Test: Propiedad esta_aprobada."""
        assert liquidacion_pendiente.esta_aprobada == False
        assert liquidacion_aprobada.esta_aprobada == True
    
    def test_esta_pagada(self, liquidacion_pagada, liquidacion_aprobada):
        """Test: Propiedad esta_pagada."""
        assert liquidacion_pagada.esta_pagada == True
        assert liquidacion_aprobada.esta_pagada == False
    
    def test_puede_editarse(self, liquidacion_pendiente, liquidacion_aprobada, liquidacion_pagada):
        """Test: Solo liquidaciones pendientes se pueden editar."""
        assert liquidacion_pendiente.puede_editarse == True
        assert liquidacion_aprobada.puede_editarse == False
        assert liquidacion_pagada.puede_editarse == False
    
    def test_puede_aprobarse(self, liquidacion_pendiente, liquidacion_aprobada):
        """Test: Solo liquidaciones pendientes se pueden aprobar."""
        assert liquidacion_pendiente.puede_aprobarse == True
        assert liquidacion_aprobada.puede_aprobarse == False
    
    def test_puede_anularse(self, liquidacion_pendiente, liquidacion_aprobada, liquidacion_pagada):
        """Test: Pendientes y aprobadas se pueden anular, pagadas no."""
        assert liquidacion_pendiente.puede_anularse == True
        assert liquidacion_aprobada.puede_anularse == True
        assert liquidacion_pagada.puede_anularse == False


class TestLiquidacionAsesorCalculos:
    """Tests de métodos de cálculo."""
    
    def test_calcular_comision_bruta(self):
        """Test: Cálculo de comisión bruta."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=2000000,
            porcentaje_comision=500,  # 5%
            comision_bruta=0,
            total_descuentos=0,
            valor_neto_asesor=0,
            estado_liquidacion="Pendiente"
        )
        
        # 2,000,000 * 5% = 100,000
        comision = liq.calcular_comision_bruta(liq.canon_arrendamiento_liquidado, liq.porcentaje_comision)
        assert comision == 100000
    
    def test_calcular_valor_neto(self):
        """Test: Cálculo de valor neto."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=2000000,
            porcentaje_comision=500,
            comision_bruta=100000,
            total_descuentos=25000,
            valor_neto_asesor=0,
            estado_liquidacion="Pendiente"
        )
        
        # 100,000 - 25,000 = 75,000
        valor_neto = liq.calcular_valor_neto(liq.total_descuentos)
        assert valor_neto == 75000


class TestLiquidacionAsesorAcciones:
    """Tests de métodos de acción (transiciones de estado)."""
    
    def test_aprobar_liquidacion_pendiente(self):
        """Test: Aprobar liquidación pendiente cambia estado."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Pendiente"
        )
        
        liq.aprobar("admin")
        
        assert liq.estado_liquidacion == "Aprobada"
        assert liq.updated_by == "admin"
    
    def test_marcar_como_pagada(self):
        """Test: Marcar liquidación aprobada como pagada."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Aprobada"
        )
        
        liq.marcar_como_pagada("admin")
        
        assert liq.estado_liquidacion == "Pagada"
    
    def test_anular_liquidacion(self):
        """Test: Anular liquidación pendiente."""
        liq = LiquidacionAsesor(
            id_liquidacion_asesor=1,
            id_contrato_a=100,
            id_asesor=5,
            periodo_liquidacion="2024-12",
            canon_arrendamiento_liquidado=1500000,
            porcentaje_comision=500,
            comision_bruta=75000,
            total_descuentos=0,
            valor_neto_asesor=75000,
            estado_liquidacion="Pendiente"
        )
        
        liq.anular("Duplicado por error", "admin")
        
        assert liq.estado_liquidacion == "Anulada"
        # El motivo de anulación se guarda en motivo_anulacion, no en observaciones
        assert liq.motivo_anulacion is not None
        assert "Duplicado" in liq.motivo_anulacion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests Unitarios: Entidad PagoAsesor
Verifica validaciones de estados y medios de pago.
"""

import pytest
from datetime import datetime
from src.dominio.entidades.pago_asesor import PagoAsesor


class TestPagoAsesorCreacion:
    """Tests de creación válida."""
    
    def test_creacion_valida(self):
        """Test: Crear pago con datos válidos."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Pendiente"
        )
        
        assert pago.id_pago_asesor == 1
        assert pago.valor_pago == 75000
        assert pago.estado_pago == "Pendiente"


class TestPagoAsesorValidacionEstados:
    """Tests de validación de estados."""
    
    def test_todos_estados_validos(self):
        """Test: Todos los estados de pago válidos."""
        estados_validos = ["Pendiente", "Programado", "Pagado", "Rechazado", "Anulado"]
        
        for i, estado in enumerate(estados_validos):
            pago = PagoAsesor(
                id_pago_asesor=i+1,
                id_liquidacion_asesor=10,
                valor_pago=75000,
                estado_pago=estado
            )
            assert pago.estado_pago == estado
    
    def test_estado_invalido_falla(self):
        """Test: Estado inválido debe fallar."""
        with pytest.raises(ValueError, match="Estado"):
            PagoAsesor(
                id_pago_asesor=1,
                id_liquidacion_asesor=10,
                valor_pago=75000,
                estado_pago="EstadoInvalido"
            )


class TestPagoAsesorValidacionMetodosPago:
    """Tests de validación de métodos de pago."""
    
    def test_todos_metodos_validos(self):
        """Test: Todos los métodos de pago válidos."""
        metodos_validos = ["Transferencia", "Cheque", "Efectivo", "PSE"]
        
        for i, metodo in enumerate(metodos_validos):
            pago = PagoAsesor(
                id_pago_asesor=i+1,
                id_liquidacion_asesor=10,
                valor_pago=75000,
                estado_pago="Pagado",
                medio_pago=metodo
            )
            assert pago.medio_pago == metodo
    
    def test_metodo_invalido_falla(self):
        """Test: Método de pago inválido debe fallar."""
        with pytest.raises(ValueError, match="Medio"):
            PagoAsesor(
                id_pago_asesor=1,
                id_liquidacion_asesor=10,
                valor_pago=75000,
                estado_pago="Pagado",
                medio_pago="Bitcoin"  # Inválido
            )


class TestPagoAsesorPropiedades:
    """Tests de propiedades de negocio."""
    
    def test_esta_pendiente(self):
        """Test: Propiedad esta_pendiente."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Pendiente"
        )
        assert pago.esta_pendiente == True
    
    def test_esta_pagado(self):
        """Test: Propiedad esta_pagado."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Pagado"
        )
        assert pago.esta_pagado == True


class TestPagoAsesorAcciones:
    """Tests de métodos de acción."""
    
    def test_programar_pago(self):
        """Test: Programar pago pendiente."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Pendiente"
        )
        
        pago.programar("2024-12-31", "admin")
        
        assert pago.estado_pago == "Programado"
        assert pago.fecha_programada == "2024-12-31"
    
    def test_marcar_como_pagado(self):
        """Test: Registrar pago."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Programado"
        )
        
        pago.marcar_como_pagado("Transferencia", "REF123456", "admin")
        
        assert pago.estado_pago == "Pagado"
        # El método puede almacenar en fecha_pago o medio_pago según implementación
        # Verificamos que el estado cambio correctamente
        assert pago.comprobante_pago == "REF123456"
    
    def test_rechazar_pago(self):
        """Test: Rechazar pago programado."""
        pago = PagoAsesor(
            id_pago_asesor=1,
            id_liquidacion_asesor=10,
            valor_pago=75000,
            estado_pago="Programado"
        )
        
        pago.rechazar("Fondos insuficientes", "admin")
        
        assert pago.estado_pago == "Rechazado"
        # El motivo puede estar en motivo_rechazo o observaciones
        assert pago.motivo_rechazo is not None
        assert "Fondos" in pago.motivo_rechazo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

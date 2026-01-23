
import pytest
from datetime import date, timedelta, datetime
from src.dominio.entidades.recibo_publico import ReciboPublico

class TestReciboPublico:
    def test_creacion_recibo_valido(self):
        """Test que verifica la creación correcta de un recibo válido"""
        recibo = ReciboPublico(
            id_propiedad=1,
            periodo_recibo="2025-12",
            tipo_servicio="Agua",
            valor_recibo=150000
        )
        
        assert recibo.id_propiedad == 1
        assert recibo.periodo_recibo == "2025-12"
        assert recibo.tipo_servicio == "Agua"
        assert recibo.valor_recibo == 150000
        assert recibo.estado == "Pendiente"
        
    def test_valor_negativo_lanza_error(self):
        """Test que verifica que no se permitan valores negativos"""
        with pytest.raises(ValueError, match="El valor del recibo debe ser mayor o igual a cero"):
            ReciboPublico(
                id_propiedad=1,
                valor_recibo=-5000
            )
            
    def test_tipo_servicio_invalido(self):
        """Test que verifica validación de tipos de servicio"""
        with pytest.raises(ValueError, match="Tipo de servicio inválido"):
            ReciboPublico(
                id_propiedad=1,
                tipo_servicio="Netflix"
            )
            
    def test_estado_invalido(self):
        """Test que verifica validación de estados"""
        with pytest.raises(ValueError, match="Estado inválido"):
            ReciboPublico(
                id_propiedad=1,
                estado="En Proceso"
            )
            
    def test_validacion_formato_periodo(self):
        """Test que verifica el formato del período YYYY-MM"""
        # Formato inválido
        with pytest.raises(ValueError, match="Formato de período inválido"):
            ReciboPublico(
                id_propiedad=1,
                periodo_recibo="2025/12"
            )
            
        # Formato válido no debe lanzar error
        ReciboPublico(id_propiedad=1, periodo_recibo="2025-12")

    def test_esta_vencido_pendiente_vencido(self):
        """Test que verifica lógica de vencimiento para recibos pendientes"""
        ayer = (date.today() - timedelta(days=1)).isoformat()
        
        recibo = ReciboPublico(
            id_propiedad=1,
            fecha_vencimiento=ayer,
            estado="Pendiente"
        )
        
        # Aunque el estado sea Pendiente, si la fecha pasó, la propiedad esta_vencido retorna True
        assert recibo.esta_vencido is True
        
    def test_esta_vencido_pendiente_no_vencido(self):
        """Test que verifica lógica de vencimiento para recibos pendientes no vencidos"""
        manana = (date.today() + timedelta(days=1)).isoformat()
        
        recibo = ReciboPublico(
            id_propiedad=1,
            fecha_vencimiento=manana,
            estado="Pendiente"
        )
        
        assert recibo.esta_vencido is False

    def test_esta_vencido_pagado(self):
        """Test que verifica que un recibo pagado no está vencido"""
        ayer = (date.today() - timedelta(days=1)).isoformat()
        
        recibo = ReciboPublico(
            id_propiedad=1,
            fecha_vencimiento=ayer,
            estado="Pagado"
        )
        
        assert recibo.esta_vencido is False

    def test_marcar_como_pagado(self):
        """Test que verifica el marcado como pagado"""
        recibo = ReciboPublico(
            id_propiedad=1,
            estado="Pendiente"
        )
        
        hoy = date.today().isoformat()
        recibo.marcar_como_pagado(fecha_pago=hoy, comprobante="REF123")
        
        assert recibo.estado == "Pagado"
        assert recibo.fecha_pago == hoy
        assert recibo.comprobante == "REF123"
        assert recibo.updated_at is not None
        
    def test_marcar_pagado_error_si_ya_pagado(self):
        """Test que no se puede marcar pagado dos veces"""
        recibo = ReciboPublico(id_propiedad=1, estado="Pagado")
        
        with pytest.raises(ValueError, match="El recibo ya está marcado como pagado"):
            recibo.marcar_como_pagado("2025-12-24", "123")
            
    def test_actualizar_estado_vencimiento(self):
        """Test del método que actualiza el estado a Vencido"""
        ayer = (date.today() - timedelta(days=1)).isoformat()
        
        recibo = ReciboPublico(
            id_propiedad=1,
            fecha_vencimiento=ayer,
            estado="Pendiente"
        )
        
        cambio = recibo.actualizar_estado_vencimiento()
        
        assert cambio is True
        assert recibo.estado == "Vencido"
        
    def test_actualizar_estado_vencimiento_sin_cambios(self):
        """Test del método actualizar cuando no hay cambios"""
        manana = (date.today() + timedelta(days=1)).isoformat()
        
        recibo = ReciboPublico(
            id_propiedad=1,
            fecha_vencimiento=manana,
            estado="Pendiente"
        )
        
        cambio = recibo.actualizar_estado_vencimiento()
        
        assert cambio is False
        assert recibo.estado == "Pendiente"

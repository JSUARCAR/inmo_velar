"""
Tests de Integración: ServicioLiquidacionAsesores
Verifica lógica de negocio completa del servicio.
"""

import pytest
import os
import tempfile
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores


@pytest.fixture
def setup_completo():
    """Setup completo con BD temporal y todos los repositorios."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    manager = DatabaseManager(path)
    manager.inicializar_base_datos()
    
    repo_liq = RepositorioLiquidacionAsesorSQLite(manager)
    repo_desc = RepositorioDescuentoAsesorSQLite(manager)
    repo_pago = RepositorioPagoAsesorSQLite(manager)
    
    servicio = ServicioLiquidacionAsesores(repo_liq, repo_desc, repo_pago)
    
    yield servicio, manager
    
    manager.cerrar_conexion()
    os.unlink(path)


class TestServicioGenerarLiquidacion:
    """Tests de generación de liquidaciones."""
    
    def test_generar_liquidacion(self, setup_completo):
        """Test: Generar liquidación calcula comisión correctamente."""
        servicio, _ = setup_completo
        
        liquidacion = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,  # 5%
            usuario="test"
        )
        
        assert liquidacion is not None
        assert liquidacion.comision_bruta == 100000  # 2M * 5%
        assert liquidacion.valor_neto_asesor == 100000
        assert liquidacion.estado_liquidacion == "Pendiente"
    
    def test_generar_duplicado_falla(self, setup_completo):
        """Test: Intentar generar duplicado debe fallar."""
        servicio, _ = setup_completo
        
        servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        with pytest.raises(ValueError, match="ya existe"):
            servicio.generar_liquidacion(
                id_contrato_a=100,
                id_asesor=5,
                periodo="2024-12",
                canon_arrendamiento=2000000,
                porcentaje_comision=500,
                usuario="test"
            )


class TestServicioDescuentos:
    """Tests de gestión de descuentos."""
    
    def test_agregar_descuento(self, setup_completo):
        """Test: Agregar descuento y recalcular valor neto."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        servicio.agregar_descuento(
            liq.id_liquidacion_asesor,
            "Préstamo",
            "Abono préstamo",
            25000,
            "test"
        )
        
        # Verificar recálculo
        liq_actualizada = servicio.obtener_liquidacion(liq.id_liquidacion_asesor)
        assert liq_actualizada.total_descuentos == 25000
        assert liq_actualizada.valor_neto_asesor == 75000  # 100k - 25k
    
    def test_eliminar_descuento_recalcula(self, setup_completo):
        """Test: Eliminar descuento recalcula valor neto."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        desc = servicio.agregar_descuento(
            liq.id_liquidacion_asesor,
            "Anticipo",
            "Anticipo mensual",
            30000,
            "test"
        )
        
        servicio.eliminar_descuento(desc.id_descuento_asesor, "test")
        
        liq_actualizada = servicio.obtener_liquidacion(liq.id_liquidacion_asesor)
        assert liq_actualizada.total_descuentos == 0
        assert liq_actualizada.valor_neto_asesor == 100000


class TestServicioAprobacion:
    """Tests de aprobación de liquidaciones."""
    
    def test_aprobar_liquidacion(self, setup_completo):
        """Test: Aprobar liquidación cambia estado."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        servicio.aprobar_liquidacion(liq.id_liquidacion_asesor, "admin")
        
        liq_aprobada = servicio.obtener_liquidacion(liq.id_liquidacion_asesor)
        assert liq_aprobada.estado_liquidacion == "Aprobada"


class TestServicioPagos:
    """Tests de gestión de pagos."""
    
    def test_programar_y_registrar_pago(self, setup_completo):
        """Test: Programar y registrar pago completo."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        servicio.aprobar_liquidacion(liq.id_liquidacion_asesor, "admin")
        
        pago = servicio.programar_pago(liq.id_liquidacion_asesor, "admin")
        assert pago.estado_pago == "Pendiente"
        
        servicio.registrar_pago(
            pago.id_pago_asesor,
            "Transferencia",
            "REF123456",
            "admin"
        )
        
        liq_pagada = servicio.obtener_liquidacion(liq.id_liquidacion_asesor)
        assert liq_pagada.estado_liquidacion == "Pagada"


class TestServicioAnulacion:
    """Tests de anulación de liquidaciones."""
    
    def test_anular_liquidacion_pendiente(self, setup_completo):
        """Test: Anular liquidación pendiente."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        servicio.anular_liquidacion(
            liq.id_liquidacion_asesor,
            "Duplicado por error",
            "admin"
        )
        
        liq_anulada = servicio.obtener_liquidacion(liq.id_liquidacion_asesor)
        assert liq_anulada.estado_liquidacion == "Anulada"
    
    def test_anular_liquidacion_pagada_falla(self, setup_completo):
        """Test: No se puede anular liquidación pagada."""
        servicio, _ = setup_completo
        
        liq = servicio.generar_liquidacion(
            id_contrato_a=100,
            id_asesor=5,
            periodo="2024-12",
            canon_arrendamiento=2000000,
            porcentaje_comision=500,
            usuario="test"
        )
        
        servicio.aprobar_liquidacion(liq.id_liquidacion_asesor, "admin")
        pago = servicio.programar_pago(liq.id_liquidacion_asesor, "admin")
        servicio.registrar_pago(pago.id_pago_asesor, "Transferencia", "REF", "admin")
        
        with pytest.raises(ValueError, match="no puede"):
            servicio.anular_liquidacion(
                liq.id_liquidacion_asesor,
                "Intento anular pagada",
                "admin"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

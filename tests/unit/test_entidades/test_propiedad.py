"""
Tests unitarios para la entidad Propiedad.
"""
import pytest
from datetime import datetime
from src.dominio.entidades.propiedad import Propiedad


class TestPropiedad:
    """Tests para la entidad Propiedad."""
    
    def test_crear_propiedad_basica(self):
        """Test: Crear una propiedad con datos mínimos."""
        propiedad = Propiedad(
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento"
        )
        
        assert propiedad.matricula_inmobiliaria == "001-2023"
        assert propiedad.id_municipio == 1
        assert propiedad.direccion_propiedad == "Calle 123 #45-67"
        assert propiedad.tipo_propiedad == "Apartamento"
        assert propiedad.disponibilidad_propiedad == 1
        assert propiedad.estado_registro == 1
    
    def test_crear_propiedad_completa(self):
        """Test: Crear una propiedad con todos los datos."""
        propiedad = Propiedad(
            id_propiedad=1,
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento",
            disponibilidad_propiedad=1,
            area_m2=85.5,
            habitaciones=3,
            bano=2,
            parqueadero=1,
            estrato=4,
            valor_administracion=150000,
            canon_arrendamiento_estimado=1500000,
            valor_venta_propiedad=250000000,
            comision_venta_propiedad=7500000,
            observaciones_propiedad="Propiedad en excelente estado",
            fecha_ingreso_propiedad="2023-01-15",
            created_by="admin"
        )
        
        assert propiedad.id_propiedad == 1
        assert propiedad.area_m2 == 85.5
        assert propiedad.habitaciones == 3
        assert propiedad.bano == 2
        assert propiedad.parqueadero == 1
        assert propiedad.estrato == 4
        assert propiedad.valor_administracion == 150000
        assert propiedad.canon_arrendamiento_estimado == 1500000
        assert propiedad.valor_venta_propiedad == 250000000
        assert propiedad.comision_venta_propiedad == 7500000
        assert propiedad.observaciones_propiedad == "Propiedad en excelente estado"
        assert propiedad.fecha_ingreso_propiedad == "2023-01-15"
    
    def test_propiedad_no_disponible(self):
        """Test: Crear una propiedad no disponible."""
        propiedad = Propiedad(
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento",
            disponibilidad_propiedad=0
        )
        
        assert propiedad.disponibilidad_propiedad == 0
    
    def test_propiedad_inactiva(self):
        """Test: Crear una propiedad inactiva con motivo."""
        propiedad = Propiedad(
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento",
            estado_registro=0,
            motivo_inactivacion="Vendida"
        )
        
        assert propiedad.estado_registro == 0
        assert propiedad.motivo_inactivacion == "Vendida"
    
    def test_propiedad_tiene_created_at_por_defecto(self):
        """Test: Verificar que created_at se genera automáticamente."""
        propiedad = Propiedad(
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento"
        )
        
        assert propiedad.created_at is not None
        assert len(propiedad.created_at) > 0
    
    def test_propiedad_diferentes_tipos(self):
        """Test: Crear propiedades de diferentes tipos."""
        tipos = ["Apartamento", "Casa", "Local Comercial", "Bodega", "Oficina"]
        
        for tipo in tipos:
            propiedad = Propiedad(
                matricula_inmobiliaria=f"001-{tipo}",
                id_municipio=1,
                direccion_propiedad="Calle 123",
                tipo_propiedad=tipo
            )
            assert propiedad.tipo_propiedad == tipo
    
    def test_propiedad_con_valores_opcionales_none(self):
        """Test: Verificar que valores opcionales pueden ser None."""
        propiedad = Propiedad(
            matricula_inmobiliaria="001-2023",
            id_municipio=1,
            direccion_propiedad="Calle 123",
            tipo_propiedad="Apartamento"
        )
        
        assert propiedad.habitaciones is None
        assert propiedad.bano is None
        assert propiedad.parqueadero is None
        assert propiedad.valor_administracion is None
        assert propiedad.canon_arrendamiento_estimado is None
        assert propiedad.observaciones_propiedad is None

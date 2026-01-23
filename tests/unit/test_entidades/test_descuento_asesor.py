"""
Tests Unitarios: Entidad DescuentoAsesor
Verifica validaciones de tipos y valores de descuentos.
"""

import pytest
from src.dominio.entidades.descuento_asesor import DescuentoAsesor


class TestDescuentoAsesorCreacion:
    """Tests de creación válida."""
    
    def test_creacion_valida(self):
        """Test: Crear descuento con datos válidos."""
        descuento = DescuentoAsesor(
            id_descuento_asesor=1,
            id_liquidacion_asesor=10,
            tipo_descuento="Préstamo",
            descripcion_descuento="Abono préstamo mensual",
            valor_descuento=50000
        )
        
        assert descuento.id_descuento_asesor == 1
        assert descuento.tipo_descuento == "Préstamo"
        assert descuento.valor_descuento == 50000
    
    def test_todos_tipos_validos(self):
        """Test: Todos los tipos de descuento válidos."""
        tipos_validos = ["Préstamo", "Anticipo", "Sanción", "Ajuste", "Otros"]
        
        for i, tipo in enumerate(tipos_validos):
            descuento = DescuentoAsesor(
                id_descuento_asesor=i+1,
                id_liquidacion_asesor=10,
                tipo_descuento=tipo,
                descripcion_descuento=f"Descuento tipo {tipo}",
                valor_descuento=10000
            )
            assert descuento.tipo_descuento == tipo


class TestDescuentoAsesorValidaciones:
    """Tests de validaciones."""
    
    def test_tipo_invalido_falla(self):
        """Test: Tipo de descuento inválido debe fallar."""
        with pytest.raises(ValueError, match="Tipo"):
            DescuentoAsesor(
                id_descuento_asesor=1,
                id_liquidacion_asesor=10,
                tipo_descuento="TipoInvalido",
                descripcion_descuento="Test",
                valor_descuento=50000
            )
    
    def test_valor_negativo_falla(self):
        """Test: Valor negativo debe fallar."""
        with pytest.raises(ValueError, match="valor"):
            DescuentoAsesor(
                id_descuento_asesor=1,
                id_liquidacion_asesor=10,
                tipo_descuento="Préstamo",
                descripcion_descuento="Test",
                valor_descuento=-1000
            )
    
    def test_valor_cero_valido(self):
        """Test: Valor cero es válido."""
        descuento = DescuentoAsesor(
            id_descuento_asesor=1,
            id_liquidacion_asesor=10,
            tipo_descuento="Ajuste",
            descripcion_descuento="Ajuste a cero",
            valor_descuento=0
        )
        assert descuento.valor_descuento == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

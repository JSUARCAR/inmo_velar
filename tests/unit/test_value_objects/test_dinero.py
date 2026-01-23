"""
Tests unitarios para el Value Object Dinero.
"""
import pytest
from decimal import Decimal
from src.dominio.value_objects.dinero import Dinero


class TestDinero:
    """Tests para el Value Object Dinero."""
    
    def test_crear_dinero_basico(self):
        """Test: Crear un objeto Dinero con monto básico."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        assert dinero.monto == Decimal("1000000")
        assert dinero.moneda == "COP"
    
    def test_crear_dinero_sin_moneda_usa_cop_por_defecto(self):
        """Test: Verificar que la moneda por defecto es COP."""
        dinero = Dinero(monto=Decimal("500000"))
        
        assert dinero.moneda == "COP"
    
    def test_moneda_se_convierte_a_mayusculas(self):
        """Test: Verificar que la moneda se convierte a mayúsculas."""
        dinero = Dinero(monto=Decimal("1000"), moneda="usd")
        
        assert dinero.moneda == "USD"
    
    def test_no_permite_monto_negativo(self):
        """Test: No se permite crear dinero con monto negativo."""
        with pytest.raises(ValueError, match="El monto no puede ser negativo"):
            Dinero(monto=Decimal("-1000"), moneda="COP")
    
    def test_no_permite_moneda_invalida(self):
        """Test: No se permite moneda con formato inválido."""
        with pytest.raises(ValueError, match="Moneda inválida"):
            Dinero(monto=Decimal("1000"), moneda="CO")
        
        with pytest.raises(ValueError, match="Moneda inválida"):
            Dinero(monto=Decimal("1000"), moneda="")
    
    def test_sumar_dinero_misma_moneda(self):
        """Test: Sumar dos montos de la misma moneda."""
        dinero1 = Dinero(monto=Decimal("1000000"), moneda="COP")
        dinero2 = Dinero(monto=Decimal("500000"), moneda="COP")
        
        resultado = dinero1 + dinero2
        
        assert resultado.monto == Decimal("1500000")
        assert resultado.moneda == "COP"
    
    def test_no_permite_sumar_monedas_diferentes(self):
        """Test: No se permite sumar monedas diferentes."""
        dinero_cop = Dinero(monto=Decimal("1000000"), moneda="COP")
        dinero_usd = Dinero(monto=Decimal("100"), moneda="USD")
        
        with pytest.raises(ValueError, match="No se pueden sumar monedas diferentes"):
            dinero_cop + dinero_usd
    
    def test_restar_dinero_misma_moneda(self):
        """Test: Restar dos montos de la misma moneda."""
        dinero1 = Dinero(monto=Decimal("1000000"), moneda="COP")
        dinero2 = Dinero(monto=Decimal("300000"), moneda="COP")
        
        resultado = dinero1 - dinero2
        
        assert resultado.monto == Decimal("700000")
        assert resultado.moneda == "COP"
    
    def test_no_permite_restar_monedas_diferentes(self):
        """Test: No se permite restar monedas diferentes."""
        dinero_cop = Dinero(monto=Decimal("1000000"), moneda="COP")
        dinero_usd = Dinero(monto=Decimal("100"), moneda="USD")
        
        with pytest.raises(ValueError, match="No se pueden restar monedas diferentes"):
            dinero_cop - dinero_usd
    
    def test_multiplicar_dinero_por_factor(self):
        """Test: Multiplicar dinero por un factor."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        resultado = dinero * Decimal("1.5")
        
        assert resultado.monto == Decimal("1500000")
        assert resultado.moneda == "COP"
    
    def test_dividir_dinero_por_divisor(self):
        """Test: Dividir dinero por un divisor."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        resultado = dinero / Decimal("2")
        
        assert resultado.monto == Decimal("500000")
        assert resultado.moneda == "COP"
    
    def test_no_permite_division_por_cero(self):
        """Test: No se permite dividir por cero."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        with pytest.raises(ValueError, match="No se puede dividir por cero"):
            dinero / Decimal("0")
    
    def test_es_cero(self):
        """Test: Verificar si el monto es cero."""
        dinero_cero = Dinero(monto=Decimal("0"), moneda="COP")
        dinero_positivo = Dinero(monto=Decimal("1000"), moneda="COP")
        
        assert dinero_cero.es_cero() is True
        assert dinero_positivo.es_cero() is False
    
    def test_es_positivo(self):
        """Test: Verificar si el monto es positivo."""
        dinero_cero = Dinero(monto=Decimal("0"), moneda="COP")
        dinero_positivo = Dinero(monto=Decimal("1000"), moneda="COP")
        
        assert dinero_cero.es_positivo() is False
        assert dinero_positivo.es_positivo() is True
    
    def test_formatear_con_moneda(self):
        """Test: Formatear dinero con código de moneda."""
        dinero = Dinero(monto=Decimal("1500000"), moneda="COP")
        
        formateado = dinero.formatear(incluir_moneda=True)
        
        assert "1.500.000" in formateado or "1500000" in formateado
        assert "COP" in formateado
    
    def test_formatear_sin_moneda(self):
        """Test: Formatear dinero sin código de moneda."""
        dinero = Dinero(monto=Decimal("1500000"), moneda="COP")
        
        formateado = dinero.formatear(incluir_moneda=False)
        
        assert "COP" not in formateado
        assert "$" in formateado
    
    def test_dinero_es_inmutable(self):
        """Test: Verificar que Dinero es inmutable (frozen dataclass)."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            dinero.monto = Decimal("2000000")
    
    def test_str_representation(self):
        """Test: Verificar representación en string."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        str_repr = str(dinero)
        
        assert "$" in str_repr
        assert "COP" in str_repr
    
    def test_repr_representation(self):
        """Test: Verificar representación para debugging."""
        dinero = Dinero(monto=Decimal("1000000"), moneda="COP")
        
        repr_str = repr(dinero)
        
        assert "Dinero" in repr_str
        assert "1000000" in repr_str
        assert "COP" in repr_str

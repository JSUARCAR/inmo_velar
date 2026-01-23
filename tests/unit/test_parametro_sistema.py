"""
Tests unitarios para la entidad ParametroSistema.
"""

import pytest
from decimal import Decimal

from src.dominio.entidades.parametro_sistema import ParametroSistema


class TestParametroSistema:
    """Tests para la entidad ParametroSistema."""
    
    def test_creacion_valida(self):
        """Test: Creación válida de ParametroSistema."""
        parametro = ParametroSistema(
            id_parametro=1,
            nombre_parametro="TEST_PARAMETRO",
            valor_parametro="100",
            tipo_dato="INTEGER",
            descripcion="Parámetro de prueba",
            categoria="PRUEBAS",
            modificable=1
        )
        
        assert parametro.id_parametro == 1
        assert parametro.nombre_parametro == "TEST_PARAMETRO"
        assert parametro.valor_parametro == "100"
        assert parametro.tipo_dato == "INTEGER"
        assert parametro.es_modificable is True
    
    def test_tipo_dato_invalido(self):
        """Test: Tipo de dato inválido debe lanzar ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ParametroSistema(
                nombre_parametro="TEST",
                valor_parametro="100",
                tipo_dato="INVALID_TYPE"
            )
        
        assert "Tipo de dato inválido" in str(exc_info.value)
    
    def test_modificable_invalido(self):
        """Test: Valor modificable inválido debe lanzar ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ParametroSistema(
                nombre_parametro="TEST",
                valor_parametro="100",
                modificable=5  # Debe ser 0 o 1
            )
        
        assert "Modificable debe ser 0 o 1" in str(exc_info.value)
    
    def test_es_modificable_true(self):
        """Test: Propiedad es_modificable retorna True cuando modificable=1."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="100",
            modificable=1
        )
        
        assert parametro.es_modificable is True
    
    def test_es_modificable_false(self):
        """Test: Propiedad es_modificable retorna False cuando modificable=0."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="100",
            modificable=0
        )
        
        assert parametro.es_modificable is False
    
    def test_valor_como_int(self):
        """Test: Conversión de valor a entero."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="500",
            tipo_dato="INTEGER"
        )
        
        assert parametro.valor_como_int == 500
    
    def test_valor_como_int_tipo_incorrecto(self):
        """Test: Conversión a int con tipo incorrecto debe lanzar TypeError."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="texto",
            tipo_dato="TEXT"
        )
        
        with pytest.raises(TypeError):
            _ = parametro.valor_como_int
    
    def test_valor_como_decimal(self):
        """Test: Conversión de valor a Decimal."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="19.5",
            tipo_dato="DECIMAL"
        )
        
        assert parametro.valor_como_decimal == Decimal("19.5")
    
    def test_valor_como_bool_true(self):
        """Test: Conversión de valor a booleano True."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="1",
            tipo_dato="BOOLEAN"
        )
        
        assert parametro.valor_como_bool is True
    
    def test_valor_como_bool_false(self):
        """Test: Conversión de valor a booleano False."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="0",
            tipo_dato="BOOLEAN"
        )
        
        assert parametro.valor_como_bool is False
    
    def test_valor_como_porcentaje(self):
        """Test: Conversión de valor base 100 a porcentaje decimal."""
        parametro = ParametroSistema(
            nombre_parametro="COMISION",
            valor_parametro="800",  # 8% en base 100
            tipo_dato="INTEGER"
        )
        
        assert parametro.valor_como_porcentaje == Decimal("8.00")
    
    def test_actualizar_valor_exitoso(self):
        """Test: Actualizar valor en parámetro modificable."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="100",
            tipo_dato="INTEGER",
            modificable=1
        )
        
        parametro.actualizar_valor("200", "admin")
        
        assert parametro.valor_parametro == "200"
        assert parametro.updated_by == "admin"
        assert parametro.updated_at is not None
    
    def test_actualizar_valor_no_modificable(self):
        """Test: Actualizar valor en parámetro no modificable debe lanzar PermissionError."""
        parametro = ParametroSistema(
            nombre_parametro="IMPUESTO_FIJO",
            valor_parametro="4",
            tipo_dato="INTEGER",
            modificable=0
        )
        
        with pytest.raises(PermissionError) as exc_info:
            parametro.actualizar_valor("5", "admin")
        
        assert "no es modificable" in str(exc_info.value)
    
    def test_actualizar_valor_validacion_tipo(self):
        """Test: Actualizar con valor inválido para el tipo debe lanzar ValueError."""
        parametro = ParametroSistema(
            nombre_parametro="TEST",
            valor_parametro="100",
            tipo_dato="INTEGER",
            modificable=1
        )
        
        with pytest.raises(ValueError):
            parametro.actualizar_valor("texto_invalido", "admin")

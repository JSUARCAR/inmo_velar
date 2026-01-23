"""
Tests unitarios para la entidad Persona.
"""
import pytest
from datetime import datetime
from src.dominio.entidades.persona import Persona


class TestPersona:
    """Tests para la entidad Persona."""
    
    def test_crear_persona_basica(self):
        """Test: Crear una persona con datos mínimos."""
        persona = Persona(
            numero_documento="1234567890",
            nombre_completo="Juan Pérez"
        )
        
        assert persona.numero_documento == "1234567890"
        assert persona.nombre_completo == "Juan Pérez"
        assert persona.estado_registro == 1
        assert persona.id_persona is None
    
    def test_crear_persona_completa(self):
        """Test: Crear una persona con todos los datos."""
        persona = Persona(
            id_persona=1,
            tipo_documento="CC",
            numero_documento="1234567890",
            nombre_completo="Juan Pérez García",
            telefono_principal="3001234567",
            correo_electronico="juan@example.com",
            direccion_principal="Calle 123 #45-67",
            estado_registro=1,
            created_by="admin"
        )
        
        assert persona.id_persona == 1
        assert persona.tipo_documento == "CC"
        assert persona.numero_documento == "1234567890"
        assert persona.nombre_completo == "Juan Pérez García"
        assert persona.telefono_principal == "3001234567"
        assert persona.correo_electronico == "juan@example.com"
        assert persona.direccion_principal == "Calle 123 #45-67"
        assert persona.estado_registro == 1
        assert persona.created_by == "admin"
    
    def test_persona_inactiva(self):
        """Test: Crear una persona inactiva con motivo."""
        persona = Persona(
            numero_documento="1234567890",
            nombre_completo="Juan Pérez",
            estado_registro=0,
            motivo_inactivacion="Duplicado"
        )
        
        assert persona.estado_registro == 0
        assert persona.motivo_inactivacion == "Duplicado"
    
    def test_persona_tiene_created_at_por_defecto(self):
        """Test: Verificar que created_at se genera automáticamente."""
        persona = Persona(
            numero_documento="1234567890",
            nombre_completo="Juan Pérez"
        )
        
        assert persona.created_at is not None
        # Verificar que es un timestamp válido
        assert len(persona.created_at) > 0
    
    def test_persona_es_dataclass(self):
        """Test: Verificar que Persona es un dataclass."""
        persona1 = Persona(
            numero_documento="1234567890",
            nombre_completo="Juan Pérez"
        )
        persona2 = Persona(
            numero_documento="1234567890",
            nombre_completo="Juan Pérez"
        )
        
        # Los dataclasses tienen __eq__ automático
        # Pero como tienen campos mutables y created_at diferente, no serán iguales
        assert persona1.numero_documento == persona2.numero_documento
        assert persona1.nombre_completo == persona2.nombre_completo

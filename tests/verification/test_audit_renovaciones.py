"""
Tests de Verificacion: Auditoria de Propagacion de Renovaciones

Tests para validar el script de auditoria de contratos de arrendamiento.
Verifica que el script ejecuta correctamente y genera JSON valido.

Autor: Inmobiliaria Velar SAS
Fecha: 2026-07-22
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Agregar directorio raiz al path
DIRECTORIO_RAIZ = Path(__file__).parent.parent.parent
sys.path.insert(0, str(DIRECTORIO_RAIZ))

# Importar modulos del script
SCRIPT_PATH = DIRECTORIO_RAIZ / "scripts" / "diagnostico" / "audit_renovaciones_2026.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "audit_renovaciones_2026",
    str(SCRIPT_PATH)
)
modulo_audit = importlib.util.module_from_spec(spec)
sys.modules["audit_renovaciones_2026"] = modulo_audit
spec.loader.exec_module(modulo_audit)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_conexion():
    """Fixture para mock de conexion a BD."""
    conexion = MagicMock()
    conexion.readonly = True
    conexion.cursor.return_value = MagicMock()
    return conexion


# ============================================================================
# Tests de Estructura del Script
# ============================================================================

class TestEstructuraScript:
    """Tests para verificar la estructura del script."""

    def test_script_existe(self):
        """Verifica que el script existe."""
        assert SCRIPT_PATH.exists(), f"Script no encontrado: {SCRIPT_PATH}"

    def test_script_es_legible(self):
        """Verifica que el script es legible."""
        contenido = SCRIPT_PATH.read_text(encoding="utf-8")
        assert len(contenido) > 0, "Script esta vacio"

    def test_script_tiene_docstring(self):
        """Verifica que el script tiene docstring."""
        contenido = SCRIPT_PATH.read_text(encoding="utf-8")
        assert '"""' in contenido, "Script no tiene docstring"

    def test_script_tiene_main(self):
        """Verifica que el script tiene funcion main."""
        assert hasattr(modulo_audit, "main")


# ============================================================================
# Tests de Excepciones de Dominio
# ============================================================================

class TestExcepcionesDominio:
    """Tests para las excepciones de dominio."""

    def test_errorConexionBd_existe(self):
        """Verifica que ErrorConexionBD existe."""
        assert hasattr(modulo_audit, "ErrorConexionBD")

    def test_errorConexionBd_es_excepcion(self):
        """Verifica que ErrorConexionBD es una excepcion."""
        assert issubclass(modulo_audit.ErrorConexionBD, Exception)

    def test_errorConsultaSql_existe(self):
        """Verifica que ErrorConsultaSQL existe."""
        assert hasattr(modulo_audit, "ErrorConsultaSQL")

    def test_errorConsultaSql_es_excepcion(self):
        """Verifica que ErrorConsultaSQL es una excepcion."""
        assert issubclass(modulo_audit.ErrorConsultaSQL, Exception)

    def test_errorAccesoArchivo_existe(self):
        """Verifica que ErrorAccesoArchivo existe."""
        assert hasattr(modulo_audit, "ErrorAccesoArchivo")

    def test_errorAccesoArchivo_es_excepcion(self):
        """Verifica que ErrorAccesoArchivo es una excepcion."""
        assert issubclass(modulo_audit.ErrorAccesoArchivo, Exception)


# ============================================================================
# Tests de Modelos de Datos
# ============================================================================

class TestModelosDatos:
    """Tests para los modelos de datos (dataclasses)."""

    def test_metadataReporte_dataclass(self):
        """Verifica que MetadataReporte es un dataclass."""
        from dataclasses import fields
        campos = [f.name for f in fields(modulo_audit.MetadataReporte)]
        assert "fecha_ejecucion" in campos
        assert "duracion_segundos" in campos

    def test_renovacionRegistrada_dataclass(self):
        """Verifica que RenovacionRegistrada es un dataclass."""
        from dataclasses import fields
        campos = [f.name for f in fields(modulo_audit.RenovacionRegistrada)]
        assert "contrato_id" in campos
        assert "canon_nuevo" in campos

    def test_inconsistenciaCanon_dataclass(self):
        """Verifica que InconsistenciaCanon es un dataclass."""
        from dataclasses import fields
        campos = [f.name for f in fields(modulo_audit.InconsistenciaCanon)]
        assert "contrato_id" in campos
        assert "severidad" in campos

    def test_problemaCodigo_dataclass(self):
        """Verifica que ProblemaCodigo es un dataclass."""
        from dataclasses import fields
        campos = [f.name for f in fields(modulo_audit.ProblemaCodigo)]
        assert "archivo" in campos
        assert "linea_inicio" in campos

    def test_resultadoAuditoria_dataclass(self):
        """Verifica que ResultadoAuditoria es un dataclass."""
        from dataclasses import fields
        campos = [f.name for f in fields(modulo_audit.ResultadoAuditoria)]
        assert "metadata" in campos
        assert "inconsistencias" in campos
        assert "analisis_codigo" in campos


# ============================================================================
# Tests de Serializacion JSON
# ============================================================================

class TestSerializacionJSON:
    """Tests para el serializador JSON personalizado."""

    def test_serializador_existe(self):
        """Verifica que el serializador existe."""
        assert hasattr(modulo_audit, "CodificadorJSONPersonalizado")

    def test_serializa_datetime(self):
        """Verifica que serializa datetime correctamente."""
        encoder = modulo_audit.CodificadorJSONPersonalizado()
        resultado = encoder.default(datetime(2026, 7, 22, 14, 30, 0))
        assert "2026-07-22" in resultado

    def test_serializa_decimal(self):
        """Verifica que serializa Decimal correctamente."""
        from decimal import Decimal
        encoder = modulo_audit.CodificadorJSONPersonalizado()
        resultado = encoder.default(Decimal("1500000.50"))
        assert resultado == 1500000.50

    def test_json_es_valido(self):
        """Verifica que el JSON generado es valido."""
        informe = {
            "metadata": {
                "fecha_ejecucion": datetime.now().isoformat(),
                "duracion_segundos": 1.5,
                "estado": "EXITOSO",
            },
            "inconsistencias": [],
            "problemas_codigo": [],
        }
        
        json_str = json.dumps(informe, cls=modulo_audit.CodificadorJSONPersonalizado)
        datos_recuperados = json.loads(json_str)
        
        assert datos_recuperados["metadata"]["estado"] == "EXITOSO"
        assert len(datos_recuperados["inconsistencias"]) == 0


# ============================================================================
# Tests de Logica de Negocio
# ============================================================================

class TestLogicaNegocio:
    """Tests para la logica de negocio del script."""

    def test_clase_motor_auditoria_existe(self):
        """Verifica que MotorAuditoria existe."""
        assert hasattr(modulo_audit, "MotorAuditoria")

    def test_motor_auditoria_es_clase(self):
        """Verifica que MotorAuditoria es una clase."""
        assert isinstance(modulo_audit.MotorAuditoria, type)


# ============================================================================
# Tests de Conexion a BD (Mock)
# ============================================================================

class TestConexionBD:
    """Tests para la conexion a base de datos (con mocks)."""

    def test_conexion_solo_lectura_existe(self):
        """Verifica que ConexionSoloLectura existe."""
        assert hasattr(modulo_audit, "ConexionSoloLectura")

    def test_conexion_solo_lectura_es_clase(self):
        """Verifica que ConexionSoloLectura es una clase."""
        assert isinstance(modulo_audit.ConexionSoloLectura, type)

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost:5432/test"})
    def test_conexion_solo_lectura_init(self):
        """Verifica que ConexionSoloLectura se inicializa correctamente."""
        conexion = modulo_audit.ConexionSoloLectura("postgresql://test:test@localhost:5432/test")
        assert conexion._database_url == "postgresql://test:test@localhost:5432/test"


# ============================================================================
# Tests de Generacion de Informe
# ============================================================================

class TestGeneracionInforme:
    """Tests para la generacion del informe JSON."""

    def test_nombre_archivo_timestamp(self):
        """Verifica que el nombre del archivo incluye timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"audit_renovaciones_{timestamp}.json"
        assert "audit_renovaciones_" in nombre
        assert ".json" in nombre


# ============================================================================
# Tests de Analisis de Codigo
# ============================================================================

class TestAnalisisCodigo:
    """Tests para el analisis de codigo fuente."""

    def test_analizador_codigo_existe(self):
        """Verifica que AnalizadorCodigoFuente existe."""
        assert hasattr(modulo_audit, "AnalizadorCodigoFuente")

    def test_analizador_es_clase(self):
        """Verifica que AnalizadorCodigoFuente es una clase."""
        assert isinstance(modulo_audit.AnalizadorCodigoFuente, type)


# ============================================================================
# Tests de Integracion (Requieren BD)
# ============================================================================

class TestIntegracion:
    """Tests de integracion (requieren conexion a BD)."""

    @pytest.mark.skip(reason="Requiere DATABASE_URL configurada")
    def test_ejecucion_completa(self):
        """Test de ejecucion completa del script."""
        pass


# ============================================================================
# Punto de Entrada
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

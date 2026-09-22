from unittest.mock import MagicMock, patch
import pytest

from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
from src.dominio.excepciones.excepciones_liquidacion import LiquidacionNoElegibleError
from src.dominio.entidades.contrato_mandato import ContratoMandato

@pytest.fixture
def repos():
    return {
        "repo_mandato": MagicMock(),
        "repo_arriendo": MagicMock(),
        "repo_liquidacion": MagicMock(),
        "repo_recaudo": MagicMock(),
        "repo_cuota": MagicMock(),
        "servicio_contratos": MagicMock()
    }

@pytest.fixture
def servicio_financiero(repos):
    mock_db_manager = MagicMock()
    servicio = ServicioFinanciero(db_manager=mock_db_manager)
    servicio.repo_mandato = repos["repo_mandato"]
    servicio.repo_arriendo = repos["repo_arriendo"]
    servicio.repo_liquidacion = repos["repo_liquidacion"]
    servicio.repo_recaudo = repos["repo_recaudo"]
    servicio.repo_cuota = repos["repo_cuota"]
    servicio.servicio_contratos = repos["servicio_contratos"]
    return servicio

def test_generacion_individual_elegible(servicio_financiero, repos):
    # Setup mock para que sea elegible (combinacion 1)
    contrato = MagicMock(spec=ContratoMandato)
    contrato.id_contrato_m = 1
    contrato.id_propiedad = 100
    contrato.estado_contrato_m = "ACTIVO"
    
    repos["repo_mandato"].obtener_por_id.return_value = contrato
    repos["repo_arriendo"].obtener_activo_por_propiedad.return_value = True
    repos["repo_liquidacion"].obtener_por_contrato_y_periodo.return_value = None
    
    # Mock para dependencias de generación (para que no falle la lógica interna financiera)
    repos["servicio_contratos"].obtener_parametros_financieros_mandato.return_value = {}
    repos["repo_recaudo"].obtener_recaudos_pendientes_por_propiedad_y_periodo.return_value = []
    repos["repo_cuota"].obtener_cuotas_incidentes_pendientes_por_propiedad_y_periodo.return_value = []
    repos["repo_liquidacion"].crear.return_value = MagicMock(id_liquidacion=1)

    # Act
    liq = servicio_financiero.generar_liquidacion_mensual(
        id_contrato_m=1,
        periodo="2023-10",
        datos_adicionales={},
        usuario_sistema="test_user"
    )

    # Assert
    assert liq is not None
    repos["repo_liquidacion"].crear.assert_called_once()

def test_generacion_individual_no_elegible_mandato_inactivo(servicio_financiero, repos):
    contrato = MagicMock(spec=ContratoMandato)
    contrato.id_contrato_m = 1
    contrato.id_propiedad = 100
    contrato.estado_contrato_m = "CANCELADO"
    
    repos["repo_mandato"].obtener_por_id.return_value = contrato

    with pytest.raises(LiquidacionNoElegibleError) as exc_info:
        servicio_financiero.generar_liquidacion_mensual(
            id_contrato_m=1,
            periodo="2023-10",
            datos_adicionales={},
            usuario_sistema="test_user"
        )
    
    assert "sin contrato de mandato activo" in str(exc_info.value)

def test_generacion_individual_no_elegible_sin_arrendamiento(servicio_financiero, repos):
    contrato = MagicMock(spec=ContratoMandato)
    contrato.id_contrato_m = 1
    contrato.id_propiedad = 100
    contrato.estado_contrato_m = "ACTIVO"
    
    repos["repo_mandato"].obtener_por_id.return_value = contrato
    repos["repo_arriendo"].obtener_activo_por_propiedad.return_value = False

    with pytest.raises(LiquidacionNoElegibleError) as exc_info:
        servicio_financiero.generar_liquidacion_mensual(
            id_contrato_m=1,
            periodo="2023-10",
            datos_adicionales={},
            usuario_sistema="test_user"
        )
    
    assert "sin contrato de arrendamiento activo en esta propiedad" in str(exc_info.value)

@patch("src.infraestructura.persistencia.database.db_manager")
def test_generacion_masiva_cuenta_no_elegibles(mock_db, servicio_financiero):
    # Configurar el mock de base de datos
    mock_conn = MagicMock()
    mock_db.obtener_conexion.return_value.__enter__.return_value = mock_conn
    mock_cur = mock_conn.cursor.return_value
    mock_db.get_dict_cursor.return_value = mock_cur
    
    # 3 contratos de mandato:
    # - C1: tiene arriendo (elegible) -> generar_liquidacion_mensual normal
    # - C2: no tiene arriendo (inelegible) -> se cuenta como no_elegible sin llamar a generar
    # - C3: tiene arriendo pero generar_liquidacion_mensual lanza un ValueError -> cuenta como error (o si es "Ya existe" omitida, simularemos error)
    mock_cur.fetchall.return_value = [
        {"ID_CONTRATO_M": 1, "tiene_arriendo": True, "ESTADO_CONTRATO_M": "ACTIVO", "DIRECCION_PROPIEDAD": "A"},
        {"ID_CONTRATO_M": 2, "tiene_arriendo": False, "ESTADO_CONTRATO_M": "ACTIVO", "DIRECCION_PROPIEDAD": "B"},
        {"ID_CONTRATO_M": 3, "tiene_arriendo": True, "ESTADO_CONTRATO_M": "ACTIVO", "DIRECCION_PROPIEDAD": "C"},
    ]
    
    def mock_generar(id_contrato_m, periodo, datos_adicionales, usuario_sistema):
        if id_contrato_m == 1:
            return MagicMock(id_liquidacion=10)
        elif id_contrato_m == 3:
            raise ValueError("Error DB desconocido")
    
    servicio_financiero.generar_liquidacion_mensual = MagicMock(side_effect=mock_generar)
    
    resultado = servicio_financiero.generar_liquidacion_propietario(
        id_propietario=99,
        periodo="2023-10",
        datos_adicionales_por_contrato={},
        usuario_sistema="test"
    )
    
    assert resultado.generadas == 1
    assert resultado.no_elegibles == 1
    assert resultado.errores == 1
    assert resultado.omitidas == 0

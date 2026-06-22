import pytest
from unittest.mock import MagicMock
from src.dominio.entidades.documento import Documento
from src.infraestructura.repositorios.repositorio_documento import RepositorioDocumento
from src.infraestructura.persistencia.database import DatabaseManager


def test_consulta_documento_vigente_con_booleano_nativo() -> None:
    """
    Verifica que la consulta SQL delegue un tipo Booleano nativo (True)
    en el bind parameter en lugar de un string ('1'), garantizando compatibilidad 
    con las validaciones de tipo de PostgreSQL ('boolean = unknown' err prevention).
    """
    # Arrange: Mock del DatabaseManager y su cursor
    mock_db = MagicMock(spec=DatabaseManager)
    mock_db.get_placeholder.return_value = "%s"
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.obtener_conexion.return_value = mock_conn

    # Setup list return value
    mock_cursor.fetchall.return_value = [
        {
            "ID": 1,
            "ENTIDAD_TIPO": "CLIENTE",
            "ENTIDAD_ID": "123",
            "NOMBRE_ARCHIVO": "cedula.pdf",
            "EXTENSION": ".pdf",
            "MIME_TYPE": "application/pdf",
            "DESCRIPCION": "Doc Identidad",
            "VERSION": 1,
            "ES_VIGENTE": 1,
            "CREATED_AT": "2026-01-01",
            "CREATED_BY": "system"
        }
    ]

    repo = RepositorioDocumento(db_manager=mock_db)

    # Act
    resultados = repo.listar_por_entidad("CLIENTE", "123")

    # Assert: Se debe llamar a execute con un booleano literal True en el tercer argumento
    mock_cursor.execute.assert_called_once()
    args_llamada = mock_cursor.execute.call_args[0]
    
    # args_llamada[0] = SQL query, args_llamada[1] = Tupla de params
    params = args_llamada[1]
    
    # Comprobación Crítica: El tercer parámetro DEBE ser True booleano, no "1"
    assert params == ("CLIENTE", "123", True), "El driver debe recibir el primitivo True de Python para compatibilidad con PostgreSQL"
    assert len(resultados) == 1

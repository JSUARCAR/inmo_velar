import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")
from src.scripts import limpiar_datos_test_bitacora_pg


def test_parse_bitacora(tmp_path):
    bitacora_path = tmp_path / "bitacora_test.json"
    data = {
        "personas": [1, 2],
        "propiedades": [3],
        "contratos_arrendamientos": [4],
        "contratos_mandatos": [5],
        "recaudos": [6],
        "liquidaciones": [7],
        "propietarios": [8],
        "arrendatarios": [9]
    }
    bitacora_path.write_text(json.dumps(data))
    
    with patch("sys.argv", ["script", "--bitacora", str(bitacora_path), "--dry-run"]):
        with patch("src.scripts.limpiar_datos_test_bitacora_pg.db_manager") as mock_db:
            mock_conn = MagicMock()
            mock_db.obtener_conexion.return_value = mock_conn
            mock_cur = mock_conn.cursor.return_value
            mock_cur.fetchone.return_value = {"COUNT": 1}
            mock_cur.fetchall.return_value = [{"ID_INCIDENTE": 10, "ID_PLAN_PAGO": 11}]
            
            limpiar_datos_test_bitacora_pg.main()
            
            # Check dry run only counts
            mock_db.obtener_conexion.assert_called_once()
            
            # Ensure SELECT counts are called for the correct tables
            queries = [call.args[0] for call in mock_cur.execute.call_args_list]
            assert any("SELECT COUNT(*) FROM recaudo_conceptos" in q for q in queries)
            assert any("SELECT COUNT(*) FROM propiedades" in q for q in queries)


def test_ejecutar_orden_fk(tmp_path):
    bitacora_path = tmp_path / "bitacora_test.json"
    data = {
        "personas": [1],
        "propiedades": [2],
        "liquidaciones": [3],
    }
    bitacora_path.write_text(json.dumps(data))
    
    with patch("sys.argv", ["script", "--bitacora", str(bitacora_path), "--ejecutar"]):
        with patch("src.scripts.limpiar_datos_test_bitacora_pg.db_manager") as mock_db:
            mock_conn = MagicMock()
            mock_db.obtener_conexion.return_value = mock_conn
            
            mock_tx = MagicMock()
            mock_db.transaccion.return_value.__enter__.return_value = mock_tx
            mock_cur = mock_tx.cursor.return_value
            
            # For select returning incidents
            mock_cur.fetchall.return_value = []
            
            mock_conn_cur = mock_conn.cursor.return_value
            mock_conn_cur.fetchone.return_value = {"COUNT": 0}  # for verification
            
            limpiar_datos_test_bitacora_pg.main()
            
            queries = [call.args[0] for call in mock_cur.execute.call_args_list]
            
            # Find the index of DELETE queries to verify order
            idx_recaudos = -1
            idx_liquidaciones = -1
            idx_propiedades = -1
            idx_personas = -1
            
            for i, q in enumerate(queries):
                if "DELETE FROM recaudos" in q: idx_recaudos = i
                elif "DELETE FROM liquidaciones" in q: idx_liquidaciones = i
                elif "DELETE FROM propiedades" in q: idx_propiedades = i
                elif "DELETE FROM personas" in q: idx_personas = i
            
            assert idx_liquidaciones < idx_propiedades, "liquidaciones should be deleted before propiedades"
            assert idx_propiedades < idx_personas, "propiedades should be deleted before personas"

            # Check if file was deleted
            assert not os.path.exists(bitacora_path)

def test_idempotencia_ignorados(tmp_path):
    bitacora_path = tmp_path / "bitacora_test.json"
    data = {"personas": []}
    bitacora_path.write_text(json.dumps(data))
    
    with patch("sys.argv", ["script", "--bitacora", str(bitacora_path), "--ejecutar"]):
        with patch("src.scripts.limpiar_datos_test_bitacora_pg.db_manager") as mock_db:
            mock_conn = MagicMock()
            mock_tx = MagicMock()
            mock_db.transaccion.return_value.__enter__.return_value = mock_tx
            mock_db.obtener_conexion.return_value = mock_conn
            
            mock_cur = mock_tx.cursor.return_value
            mock_cur.fetchone.return_value = {"COUNT": 0}
            
            limpiar_datos_test_bitacora_pg.main()
            
            # Since empty array, should skip delete
            for call in mock_cur.execute.call_args_list:
                assert "DELETE FROM personas" not in call.args[0]

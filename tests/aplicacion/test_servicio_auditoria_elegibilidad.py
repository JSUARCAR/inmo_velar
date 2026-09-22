from unittest.mock import MagicMock, patch

from src.aplicacion.servicios.servicio_auditoria_elegibilidad import ServicioAuditoriaElegibilidad

@patch("src.aplicacion.servicios.servicio_auditoria_elegibilidad.db_manager")
def test_auditoria_solo_lectura_y_motivos(mock_db):
    mock_conn = MagicMock()
    mock_db.obtener_conexion.return_value.__enter__.return_value = mock_conn
    mock_cur = mock_conn.cursor.return_value
    mock_db.get_dict_cursor.return_value = mock_cur
    
    # Simulate DB returning records with different state combinations
    mock_cur.fetchall.return_value = [
        # 1. Ambos inactivos
        {
            "ID_LIQUIDACION": 1, "PERIODO": "2023-10", "FECHA_GENERACION": "2023-10-01",
            "ID_PROPIEDAD": 100, "DIRECCION_PROPIEDAD": "A", "ID_PROPIETARIO": 10,
            "NOMBRE_PROPIETARIO": "Prop A", "ESTADO_CONTRATO_M": "TERMINADO", "ESTADO_CONTRATO_A": "FINALIZADO"
        },
        # 2. Mandato inactivo, arriendo activo
        {
            "ID_LIQUIDACION": 2, "PERIODO": "2023-10", "FECHA_GENERACION": "2023-10-01",
            "ID_PROPIEDAD": 101, "DIRECCION_PROPIEDAD": "B", "ID_PROPIETARIO": 11,
            "NOMBRE_PROPIETARIO": "Prop B", "ESTADO_CONTRATO_M": "TERMINADO", "ESTADO_CONTRATO_A": "ACTIVO"
        },
        # 3. Mandato activo, arriendo inactivo
        {
            "ID_LIQUIDACION": 3, "PERIODO": "2023-10", "FECHA_GENERACION": "2023-10-01",
            "ID_PROPIEDAD": 102, "DIRECCION_PROPIEDAD": "C", "ID_PROPIETARIO": 12,
            "NOMBRE_PROPIETARIO": "Prop C", "ESTADO_CONTRATO_M": "ACTIVO", "ESTADO_CONTRATO_A": "FINALIZADO"
        },
        # 4. Ambos activos (Elegible, no debe salir en no_elegibles)
        {
            "ID_LIQUIDACION": 4, "PERIODO": "2023-10", "FECHA_GENERACION": "2023-10-01",
            "ID_PROPIEDAD": 103, "DIRECCION_PROPIEDAD": "D", "ID_PROPIETARIO": 13,
            "NOMBRE_PROPIETARIO": "Prop D", "ESTADO_CONTRATO_M": "ACTIVO", "ESTADO_CONTRATO_A": "ACTIVO"
        }
    ]
    
    servicio = ServicioAuditoriaElegibilidad()
    resultado = servicio.auditar(periodo="2023-10")
    
    # Verifica que solo sea SELECT
    query = mock_cur.execute.call_args[0][0]
    assert query.strip().upper().startswith("SELECT")
    assert "INSERT" not in query.upper()
    assert "UPDATE" not in query.upper()
    assert "DELETE" not in query.upper()
    
    # Verificar motivos y clasificación
    assert resultado.liquidaciones_auditadas == 4
    assert len(resultado.no_elegibles) == 3
    
    no_elegibles_dict = {l.id_liquidacion: l.motivo for l in resultado.no_elegibles}
    assert "sin contrato de mandato activo y sin contrato de arrendamiento activo" in no_elegibles_dict[1]
    assert "sin contrato de mandato activo" in no_elegibles_dict[2]
    assert "sin contrato de arrendamiento activo" in no_elegibles_dict[3]
    
    # Verificar criterios registrados
    assert resultado.criterios.periodo == "2023-10"
    assert resultado.criterios.fecha_reconstruccion is not None

@patch("src.aplicacion.servicios.servicio_auditoria_elegibilidad.db_manager")
def test_auditoria_reporte_regenerable(mock_db):
    mock_conn = MagicMock()
    mock_db.obtener_conexion.return_value.__enter__.return_value = mock_conn
    mock_cur = mock_conn.cursor.return_value
    mock_db.get_dict_cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = []
    
    servicio = ServicioAuditoriaElegibilidad()
    # Ejecutamos con fecha fija
    resultado1 = servicio.auditar(fecha_reconstruccion="2023-12-01T00:00:00")
    resultado2 = servicio.auditar(fecha_reconstruccion="2023-12-01T00:00:00")
    
    # Debería registrar el mismo criterio (re-generable)
    assert resultado1.criterios.fecha_reconstruccion == resultado2.criterios.fecha_reconstruccion
    assert resultado1.criterios == resultado2.criterios

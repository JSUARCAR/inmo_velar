
import pytest
from unittest.mock import MagicMock
from datetime import date
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos

# Schema con FK activas
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS PROPIEDADES (
    ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE IF NOT EXISTS RECIBOS_PUBLICOS (
    ID_RECIBO_PUBLICO INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_PROPIEDAD INTEGER NOT NULL,
    PERIODO_RECIBO TEXT NOT NULL,
    TIPO_SERVICIO TEXT NOT NULL,
    VALOR_RECIBO INTEGER NOT NULL,
    FECHA_VENCIMIENTO TEXT,
    FECHA_PAGO TEXT,
    COMPROBANTE TEXT,
    ESTADO TEXT DEFAULT 'Pendiente',
    FECHA_DESDE TEXT,
    FECHA_HASTA TEXT,
    DIAS_FACTURADOS INTEGER DEFAULT 0,
    CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
    CREATED_BY TEXT,
    UPDATED_AT TEXT,
    UPDATED_BY TEXT,
    FOREIGN KEY(ID_PROPIEDAD) REFERENCES PROPIEDADES(ID_PROPIEDAD),
    UNIQUE(ID_PROPIEDAD, PERIODO_RECIBO, TIPO_SERVICIO)
);
"""

@pytest.fixture
def db_manager(tmp_path):
    db_file = tmp_path / "test_servicio.db"
    # Reiniciar Singleton para test
    DatabaseManager._instance = None
    import src.infraestructura.persistencia.database as db_module
    db_module.USE_POSTGRESQL = False
    db_module.DB_MODE = 'sqlite'
    
    manager = DatabaseManager()
    manager.use_postgresql = False
    manager.database_path = db_file
    manager._connection_pool = {}
    manager.ejecutar_script(SCHEMA_SQL)
    # Insertar propiedad dummy para FK
    manager.ejecutar_script("INSERT INTO PROPIEDADES (ID_PROPIEDAD) VALUES (1)")
    yield manager
    manager.cerrar_todas_conexiones()

@pytest.fixture
def servicio_recibos(db_manager):
    repo_recibo = RepositorioReciboPublicoSQLite(db_manager)
    repo_propiedad_mock = MagicMock()
    
    # Configurar mock para que retorne algo cuando buscan propiedad ID 1
    repo_propiedad_mock.obtener_por_id.side_effect = lambda id_p: MagicMock() if id_p == 1 else None
    
    return ServicioRecibosPublicos(repo_recibo, repo_propiedad_mock)

class TestServicioRecibosPublicos:
    
    def test_registrar_recibo_exitoso(self, servicio_recibos):
        datos = {
            'id_propiedad': 1,
            'periodo_recibo': '2025-01',
            'tipo_servicio': 'Agua',
            'valor_recibo': 50000,
            'fecha_vencimiento': '2025-01-20',
            'fecha_desde': '2025-01-01',
            'fecha_hasta': '2025-01-31'
        }
        
        recibo = servicio_recibos.registrar_recibo(datos, "admin")
        
        assert recibo.id_recibo_publico is not None
        assert recibo.estado == "Pendiente"
        assert recibo.dias_facturados == 30 # 31 - 1
        
    def test_registrar_recibo_dates_invalidas(self, servicio_recibos):
        datos = {
            'id_propiedad': 1,
            'periodo_recibo': '2025-01',
            'tipo_servicio': 'Agua',
            'valor_recibo': 50000,
            'fecha_vencimiento': '2025-01-20',
            'fecha_desde': '2025-01-31',
            'fecha_hasta': '2025-01-01' # Hasta < Desde
        }
        
        with pytest.raises(ValueError, match="La fecha hasta no puede ser menor"):
            servicio_recibos.registrar_recibo(datos, "admin")
        
    def test_registrar_recibo_propiedad_inexistente(self, servicio_recibos):
        datos = {
            'id_propiedad': 999, # No existe en mock ni DB
            'periodo_recibo': '2025-01',
            'tipo_servicio': 'Agua',
            'valor_recibo': 50000
        }
        
        with pytest.raises(ValueError, match="No existe la propiedad"):
            servicio_recibos.registrar_recibo(datos, "admin")
            
    def test_validaciones_registro(self, servicio_recibos):
        # Falta periodo
        with pytest.raises(ValueError, match="El período es obligatorio"):
            servicio_recibos.registrar_recibo({'id_propiedad': 1}, "admin")
            
        # Formato periodo
        with pytest.raises(ValueError, match="formato YYYY-MM"):
            servicio_recibos.registrar_recibo({
                'id_propiedad': 1, 
                'periodo_recibo': '2025/01'
            }, "admin")
            
    def test_marcar_pagado(self, servicio_recibos):
        # Crear primero
        datos = {
            'id_propiedad': 1,
            'periodo_recibo': '2025-03',
            'tipo_servicio': 'Luz',
            'valor_recibo': 20000
        }
        creado = servicio_recibos.registrar_recibo(datos, "admin")
        
        # Pagar
        pagado = servicio_recibos.marcar_como_pagado(
            id_recibo=creado.id_recibo_publico,
            fecha_pago="2025-03-05",
            comprobante="CMP-001",
            usuario="admin"
        )
        
        assert pagado.estado == "Pagado"
        assert pagado.fecha_pago == "2025-03-05"
        assert pagado.comprobante == "CMP-001"
        
        # Intentar pagar de nuevo
        with pytest.raises(ValueError, match="ya está marcado como pagado"):
            servicio_recibos.marcar_como_pagado(creado.id_recibo_publico, "2025-03-06", "C", "u")

    def test_verificar_vencimientos(self, servicio_recibos):
        # Crear recibo vencido
        datos = {
            'id_propiedad': 1,
            'periodo_recibo': '2024-01', # Pasado
            'tipo_servicio': 'Gas',
            'valor_recibo': 10000,
            'fecha_vencimiento': '2024-01-15' # Vencido
        }
        recibo = servicio_recibos.registrar_recibo(datos, "admin")
        assert recibo.estado == "Pendiente" # Inicialmente pendiente
        
        # Ejecutar job
        num_actualizados = servicio_recibos.verificar_vencimientos("system")
        
        assert num_actualizados == 1
        
        # Verificar estado
        repo = servicio_recibos.repo_recibo
        actualizado = repo.obtener_por_id(recibo.id_recibo_publico)
        assert actualizado.estado == "Vencido"

    def test_obtener_resumen(self, servicio_recibos):
        # Crear 2 recibos mismo periodo
        servicio_recibos.registrar_recibo({
            'id_propiedad': 1, 'periodo_recibo': '2025-05', 
            'tipo_servicio': 'Agua', 'valor_recibo': 100
        }, "admin")
        
        servicio_recibos.registrar_recibo({
            'id_propiedad': 1, 'periodo_recibo': '2025-05', 
            'tipo_servicio': 'Luz', 'valor_recibo': 200
        }, "admin")
        
        resumen = servicio_recibos.obtener_resumen_por_propiedad(1, '2025-05')
        
        assert resumen['total'] == 300
        assert resumen['pendiente'] == 300
        assert len(resumen['recibos']) == 2

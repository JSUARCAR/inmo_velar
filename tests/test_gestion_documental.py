import unittest
import os
import shutil
import sqlite3
from datetime import datetime
from src.dominio.entidades.documento import Documento
from src.infraestructura.repositorios.repositorio_documento_sqlite import RepositorioDocumentoSQLite
from src.aplicacion.servicios.servicio_documental import ServicioDocumental
from src.infraestructura.persistencia.database import DatabaseManager

class TestGestionDocumental(unittest.TestCase):
    
    def setUp(self):
        # Usar una BD en memoria para tests para evitar bloqueos de archivo en Windows
        self.db_path = ":memory:"
        
        # Configurar DatabaseManager para usar la BD en memoria
        self.db_manager = DatabaseManager()
        # Forzamos cierre de conexiones anteriores
        try:
            self.db_manager.cerrar_todas_conexiones()
        except:
            pass

        # Resetear pool y path
        self.db_manager._connection_pool = {} 
        self.db_manager.database_path = self.db_path 
        
        # Crear conexión directa para setup inicial
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        # Hack: Inyectar esta conexión en el pool del manager para el thread actual
        # O mejor, dejar que el manager cree su conexión, pero como es :memory:, cada connect crea una nueva DB vacía.
        # Para compartir la misma :memory: DB entre threads/conexiones, necesitamos trucos, o mejor:
        # Usar un archivo temporal ÚNICO por ejecución de test si :memory: es problemático con múltiples conexiones.
        # Pero intentemos con archivo temporal con nombre único.
        
        # CAMBIO DE ESTRATEGIA: Archivo temporal único
        import time
        self.db_path = f"test_docs_{int(time.time()*1000)}.db"
        self.db_manager.database_path = self.db_path
        
        # Crear tabla DOCUMENTOS
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DOCUMENTOS (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ENTIDAD_TIPO TEXT NOT NULL,
                    ENTIDAD_ID TEXT NOT NULL,
                    NOMBRE_ARCHIVO TEXT NOT NULL,
                    EXTENSION TEXT,
                    MIME_TYPE TEXT,
                    DESCRIPCION TEXT,
                    CONTENIDO BLOB,
                    VERSION INTEGER DEFAULT 1,
                    ES_VIGENTE INTEGER DEFAULT 1,
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CREATED_BY TEXT
                )
            """)
            conn.commit()
            
        self.repo = RepositorioDocumentoSQLite(self.db_manager)
        self.servicio = ServicioDocumental(self.repo)

    def tearDown(self):
        # Cerrar conexiones del manager
        try:
            self.db_manager.cerrar_todas_conexiones()
        except:
            pass
            
        # Borrar archivo temporal
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                # Si falla borrar, cambiar nombre para siguiente test
                pass

    def test_entidad_documento_validacion(self):
        """Prueba las validaciones de la entidad Documento"""
        doc = Documento(
            entidad_tipo="TEST",
            entidad_id="1",
            nombre_archivo="test.txt",
            contenido=b"123"
        )
        self.assertEqual(doc.nombre_archivo, "test.txt")
        self.assertEqual(doc.version, 1) # Default
        
        with self.assertRaises(ValueError):
            Documento(entidad_tipo="", entidad_id="1", nombre_archivo="f.txt")

    def test_repositorio_crud_blob(self):
        """Prueba CRUD básico y manejo de BLOB en repositorio"""
        contenido = b"CONTENIDO BINARIO DE PRUEBA"
        doc = Documento(
            entidad_tipo="PRUEBA",
            entidad_id="100",
            nombre_archivo="prueba.bin",
            extension=".bin",
            mime_type="application/octet-stream",
            descripcion="Doc Prueba",
            contenido=contenido,
            created_by="tester"
        )
        
        doc_creado = self.repo.crear(doc)
        self.assertIsNotNone(doc_creado.id)
        
        lista = self.repo.listar_por_entidad("PRUEBA", "100")
        self.assertEqual(len(lista), 1)
        self.assertIsNone(lista[0].contenido)
        self.assertEqual(lista[0].descripcion, "Doc Prueba")
        
        doc_full = self.repo.obtener_por_id_con_contenido(doc_creado.id)
        self.assertIsNotNone(doc_full.contenido)
        self.assertEqual(doc_full.contenido, contenido)

    def test_versionamiento(self):
        """Prueba que el versionamiento funcione"""
        # Versión 1
        self.servicio.subir_documento(
            entidad_tipo="CONTRATO",
            entidad_id="50",
            nombre_archivo="contrato.pdf",
            contenido_bytes=b"v1",
            descripcion="Version 1",
            usuario="user1"
        )
        
        docs_v1 = self.repo.listar_por_entidad("CONTRATO", "50")
        self.assertEqual(len(docs_v1), 1)
        self.assertEqual(docs_v1[0].version, 1)
        self.assertTrue(docs_v1[0].es_vigente)
        
        # Versión 2
        self.servicio.subir_documento(
            entidad_tipo="CONTRATO",
            entidad_id="50",
            nombre_archivo="contrato.pdf",
            contenido_bytes=b"v2",
            descripcion="Version 2",
            usuario="user1"
        )
        
        docs_v2 = self.repo.listar_por_entidad("CONTRATO", "50")
        self.assertEqual(len(docs_v2), 1)
        self.assertEqual(docs_v2[0].version, 2)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM DOCUMENTOS WHERE ENTIDAD_ID='50' AND ES_VIGENTE=0")
            count_old = cursor.fetchone()[0]
            self.assertEqual(count_old, 1)

    def test_soft_delete(self):
        """Prueba eliminación lógica"""
        doc = self.servicio.subir_documento(
            entidad_tipo="BORRAR",
            entidad_id="99",
            nombre_archivo="delete.txt",
            contenido_bytes=b"del",
            usuario="admin"
        )
        
        self.servicio.eliminar_documento(doc.id)
        
        lista = self.repo.listar_por_entidad("BORRAR", "99")
        self.assertEqual(len(lista), 0)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ES_VIGENTE FROM DOCUMENTOS WHERE ID=?", (doc.id,))
            vigente = cursor.fetchone()[0]
            self.assertEqual(vigente, 0)

if __name__ == '__main__':
    unittest.main()

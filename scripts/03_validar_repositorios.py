"""
Script 3: Validar Repositorios
Ejecuta pruebas de CRUD en todos los repositorios.
"""

import sys
from pathlib import Path

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
from src.infraestructura.persistencia.repositorio_municipio_sqlite import RepositorioMunicipioSQLite


class ValidadorRepositorios:
    """Validador de repositorios."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.errores = []
        self.exitos = 0
    
    def validar(self, nombre_test, funcion):
        """Ejecuta una validacion."""
        try:
            funcion()
            print("  [OK]", nombre_test)
            self.exitos += 1
        except Exception as e:
            print("  [ERROR]", nombre_test, ":", str(e))
            self.errores.append((nombre_test, str(e)))
    
    def validar_repositorio_usuario(self):
        """Valida RepositorioUsuario."""
        print("Validando RepositorioUsuario...")
        repo = RepositorioUsuarioSQLite(self.db)
        
        # Test: Listar usuarios
        self.validar("Listar usuarios", lambda: repo.listar_todos())
        
        # Test: Obtener usuario admin
        def test_obtener_admin():
            admin = repo.obtener_por_nombre("admin")
            assert admin is not None, "Usuario admin no encontrado"
            assert admin.rol == "Administrador", "Rol incorrecto"
        
        self.validar("Obtener usuario admin", test_obtener_admin)
        
        # Test: Obtener por ID
        def test_obtener_por_id():
            admin = repo.obtener_por_nombre("admin")
            usuario = repo.obtener_por_id(admin.id_usuario)
            assert usuario is not None, "Usuario no encontrado por ID"
        
        self.validar("Obtener usuario por ID", test_obtener_por_id)
    
    def validar_repositorio_persona(self):
        """Valida RepositorioPersona."""
        print("Validando RepositorioPersona...")
        repo = RepositorioPersonaSQLite(self.db)
        
        # Test: Listar personas activas
        self.validar("Listar personas activas", lambda: repo.listar_activos())
        
        # Test: Obtener persona por documento
        def test_obtener_por_doc():
            persona = repo.obtener_por_documento("1234567890")
            assert persona is not None, "Persona no encontrada"
            assert "JUAN" in persona.nombre_completo, "Nombre incorrecto"
        
        self.validar("Obtener persona por documento", test_obtener_por_doc)
    
    def validar_repositorio_municipio(self):
        """Valida RepositorioMunicipio."""
        print("Validando RepositorioMunicipio...")
        repo = RepositorioMunicipioSQLite(self.db)
        
        # Test: Listar municipios
        def test_listar():
            municipios = repo.listar_todos()
            assert len(municipios) > 0, "No hay municipios"
        
        self.validar("Listar municipios", test_listar)
        
        # Test: Buscar por departamento
        def test_por_depto():
            bogota = repo.listar_por_departamento("BOGOTA D.C.")
            assert len(bogota) > 0, "No se encontro Bogota"
        
        self.validar("Buscar por departamento", test_por_depto)
    
    def validar_auditoria(self):
        """Valida que la auditoria este funcionando."""
        print("Validando auditoria...")
        
        def test_auditoria():
            with self.db.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM AUDITORIA_CAMBIOS")
                count = cursor.fetchone()[0]
                assert count > 0, "No hay registros de auditoria"
        
        self.validar("Registros de auditoria presentes", test_auditoria)
    
    def generar_reporte(self):
        """Genera el reporte final."""
        print()
        print("=" * 60)
        print("REPORTE DE VALIDACION")
        print("=" * 60)
        print("[OK] Pruebas exitosas:", self.exitos)
        print("[ERROR] Pruebas fallidas:", len(self.errores))
        
        if self.errores:
            print()
            print("ERRORES DETECTADOS:")
            for nombre, error in self.errores:
                print("  -", nombre, ":", error)
            print()
            print("=" * 60)
            print("[ERROR] VALIDACION FALLIDA")
            print("=" * 60)
            return False
        else:
            print()
            print("=" * 60)
            print("[OK] VALIDACION EXITOSA - TODO FUNCIONA CORRECTAMENTE")
            print("=" * 60)
            return True


def main():
    """Ejecuta la validacion de repositorios."""
    print("=" * 60)
    print("SCRIPT 3: VALIDACION DE REPOSITORIOS")
    print("=" * 60)
    print()
    
    try:
        db_manager = DatabaseManager()
        print("[OK] Conexion a base de datos establecida")
        print()
        
        validador = ValidadorRepositorios(db_manager)
        
        validador.validar_repositorio_usuario()
        print()
        
        validador.validar_repositorio_persona()
        print()
        
        validador.validar_repositorio_municipio()
        print()
        
        validador.validar_auditoria()
        print()
        
        exito = validador.generar_reporte()
        
        sys.exit(0 if exito else 1)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] ERROR EN LA VALIDACION")
        print("=" * 60)
        print("Error:", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
